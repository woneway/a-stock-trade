"""
游资复盘 Agent 核心实现
基于 ReAct 模式的迭代分析
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import json

from app.agents.models import (
    AgentState, Action, ReviewContext, ReviewStep,
    ReviewResult, DecisionResult
)
from app.agents.tools import MCPClient, AkshareTool, NewsTool, fetch_with_retry
from app.agents.prompts import SYSTEM_PROMPT, build_decision_prompt, build_report_prompt


class ReviewAgent:
    """游资复盘 Agent - 迭代分析模式"""

    def __init__(self, mcp_client: MCPClient = None, max_iterations: int = 15):
        self.mcp = mcp_client
        self.max_iterations = max_iterations
        self.max_retries = 3

        # 初始化工具
        self.akshare_tool = AkshareTool()
        self.news_tool = NewsTool()

    async def run(self, date: str) -> ReviewResult:
        """
        执行复盘分析

        Args:
            date: 复盘日期，格式 YYYYMMDD

        Returns:
            ReviewResult: 复盘结果
        """
        # 初始化上下文
        context = ReviewContext(date=date)
        step_count = 0

        try:
            # ===== 第一次迭代：获取基础数据 =====
            step_count += 1
            await self._fetch_basic_data(context, step_count)

            # ===== 迭代分析循环 =====
            for iteration in range(self.max_iterations):
                # 构建当前数据状态
                context_data = self._get_context_data(context)

                # 调用 LLM 进行分析和决策
                decision = await self._analyze_and_decide(context_data, iteration)

                # 记录步骤
                step = ReviewStep(
                    step=step_count,
                    state=AgentState.ANALYZING,
                    action=f"分析+决策 (迭代{iteration + 1})",
                    result=decision.reason,
                    data_used=list(context_data.keys())
                )
                context.steps.append(step)
                step_count += 1

                # 根据决策执行动作
                if decision.action == Action.COMPLETE:
                    # 分析完成，生成报告
                    break

                elif decision.action == Action.FETCH_NEWS:
                    await self._fetch_news(context, decision.params, step_count)
                    step_count += 1

                elif decision.action == Action.FETCH_MORE_DATA:
                    await self._fetch_more_data(context, decision.params, step_count)
                    step_count += 1

                elif decision.action == Action.RETRY:
                    await self._retry_data(context, decision.params, step_count)
                    step_count += 1

                # 更新分析结果
                if decision.analysis_update:
                    context.analysis = {
                        "last_update": decision.analysis_update,
                        "iteration": iteration + 1
                    }

            # ===== 生成最终报告 =====
            await self._generate_report(context)

            return ReviewResult(
                date=date,
                iterations_used=step_count,
                steps=context.steps,
                analysis=context.analysis,
                final_report=context.final_report
            )

        except Exception as e:
            return ReviewResult(
                date=date,
                iterations_used=step_count,
                steps=context.steps,
                error=str(e)
            )

    async def _fetch_basic_data(self, context: ReviewContext, step: int):
        """获取基础数据"""
        # 并行获取多个数据源
        emotion, zt_pool, zbgc, margin, sectors, lhb = await asyncio.gather(
            fetch_with_retry(self.akshare_tool.get_market_emotion, max_retries=self.max_retries),
            fetch_with_retry(self.akshare_tool.get_zt_pool, context.date, max_retries=self.max_retries),
            fetch_with_retry(self.akshare_tool.get_zbgc, context.date, max_retries=self.max_retries),
            fetch_with_retry(self.akshare_tool.get_margin, context.date, context.date, max_retries=self.max_retries),
            fetch_with_retry(self.akshare_tool.get_sectors, max_retries=self.max_retries),
            fetch_with_retry(self.akshare_tool.get_lhb_detail, context.date, max_retries=self.max_retries),
        )

        context.market_emotion = emotion
        context.zt_pool = zt_pool
        context.zbgc = zbgc
        context.margin = margin
        context.sectors = sectors
        context.lhb = lhb

        # 记录步骤
        context.steps.append(ReviewStep(
            step=step,
            state=AgentState.FETCHING_DATA,
            action="获取基础数据",
            result=f"情绪: {'✓' if emotion else '✗'}, 涨停: {len(zt_pool or [])}, 炸板: {len(zbgc or [])}, 板块: {len(sectors or [])}, 龙虎榜: {len(lhb or [])}",
            data_used=["market_emotion", "zt_pool", "zbgc", "margin", "sectors", "lhb"]
        ))

    def _get_context_data(self, context: ReviewContext) -> Dict[str, Any]:
        """获取当前上下文数据"""
        return {
            "market_emotion": context.market_emotion,
            "zt_pool": context.zt_pool,
            "zbgc": context.zbgc,
            "margin": context.margin,
            "news": context.news,
            "lhb": context.lhb,
            "sectors": context.sectors,
        }

    async def _analyze_and_decide(self, context_data: Dict[str, Any], iteration: int) -> DecisionResult:
        """
        调用 LLM 进行分析和决策

        由于目前 MiniMax MCP 可能不支持直接的 LLM 调用，
        这里使用简化的决策逻辑作为后备
        """
        # 构建分析进度
        analysis_parts = []
        if context_data.get("zt_pool"):
            zt_count = len(context_data["zt_pool"])
            analysis_parts.append(f"涨停板: {zt_count}只")
        if context_data.get("zbgc"):
            zbgc_count = len(context_data["zbgc"])
            analysis_parts.append(f"炸板股: {zbgc_count}只")
        if context_data.get("news"):
            news_count = len(context_data["news"])
            analysis_parts.append(f"新闻: {news_count}条")

        analysis_progress = ", ".join(analysis_parts) if analysis_parts else "数据已获取，等待分析"

        # 构建提示词
        prompt = build_decision_prompt(context_data, analysis_progress)

        # TODO: 实际调用 LLM
        # 由于 LLM 调用需要配置，这里先用规则作为后备决策
        # 实际使用时，应该调用 self.mcp.call_llm(SYSTEM_PROMPT, prompt)

        # 简化决策逻辑（后备方案）
        decision = self._simple_decide(context_data, iteration)

        return decision

    def _simple_decide(self, context_data: Dict[str, Any], iteration: int) -> DecisionResult:
        """
        简化决策逻辑（后备方案）
        实际使用时应该用 LLM
        """
        # 第一次迭代，检查是否需要获取新闻
        if iteration == 0:
            # 如果没有新闻，且有涨停板，建议获取新闻
            if not context_data.get("news") and context_data.get("zt_pool"):
                return DecisionResult(
                    action=Action.FETCH_NEWS,
                    reason="涨停板数据已获取，需要查询相关新闻了解驱动因素",
                    params={"keywords": ["电力", "小金属", "AI", "政策"]},
                    analysis_update="涨停板数据已获取"
                )

        # 第二次迭代，检查是否需要更多数据
        if iteration == 1:
            if not context_data.get("news"):
                return DecisionResult(
                    action=Action.FETCH_NEWS,
                    reason="需要更多新闻来确认市场主线",
                    params={"keywords": ["电力", "新能源", "科技"]},
                    analysis_update="市场情绪初步判断完成"
                )

        # 默认完成
        return DecisionResult(
            action=Action.COMPLETE,
            reason="数据收集足够，可以生成报告",
            analysis_update="分析完成"
        )

    async def _fetch_news(self, context: ReviewContext, params: Dict[str, Any], step: int):
        """获取新闻"""
        keywords = params.get("keywords", ["A股", "政策", "股市"])
        news = await self.news_tool.search_news(keywords, context.date)

        context.news = news

        # 记录步骤
        context.steps.append(ReviewStep(
            step=step,
            state=AgentState.FETCHING_NEWS,
            action="获取新闻",
            result=f"获取到 {len(news)} 条新闻",
            data_used=["news"]
        ))

    async def _fetch_more_data(self, context: ReviewContext, params: Dict[str, Any], step: int):
        """获取更多数据"""
        # 根据 params 决定获取什么数据
        data_type = params.get("type", "sectors")

        if data_type == "sectors":
            sectors = await fetch_with_retry(
                self.akshare_tool.get_sectors,
                max_retries=self.max_retries
            )
            context.sectors = sectors
            data_key = "sectors"
        elif data_type == "lhb":
            lhb = await fetch_with_retry(
                self.akshare_tool.get_lhb_detail,
                context.date,
                max_retries=self.max_retries
            )
            context.lhb = lhb
            data_key = "lhb"

        # 记录步骤
        context.steps.append(ReviewStep(
            step=step,
            state=AgentState.FETCHING_MORE_DATA,
            action=f"获取更多数据 ({data_type})",
            result="成功获取",
            data_used=[data_key]
        ))

    async def _retry_data(self, context: ReviewContext, params: Dict[str, Any], step: int):
        """重试获取数据"""
        # 记录步骤
        context.steps.append(ReviewStep(
            step=step,
            state=AgentState.FETCHING_DATA,
            action="重试获取数据",
            result=f"重试: {params.get('reason', '未知')}",
            data_used=[]
        ))

    def _calculate_emotion_cycle(self, zt_count: int, zbgc_count: int, dtgc_count: int, highest_board: int) -> Dict:
        """
        情绪周期判断
        做什么：判断当前处于哪个情绪周期阶段
        为什么做：周期决定仓位和策略
        怎么做：通过涨停家数、炸板率、跌停家数、最高板等指标综合判断
        判断标准：基于游资实战经验总结的量化标准
        """
        # 计算炸板率
        zbgc_rate = zbgc_count / max(zt_count, 1) * 100 if zt_count > 0 else 100

        # 判断逻辑
        if zt_count >= 80 and zbgc_rate < 15:
            # 高潮期：涨停多、炸板少
            return {
                "phase": "高潮",
                "description": "市场情绪高涨，涨停家数多，炸板率低",
                "reason": "涨停家数>=80且炸板率<15%，市场处于明显多头状态",
                "basis": "历史数据显示，此时往往伴随主线板块加速，是赚钱效应最好的阶段",
                "position": 80,
                "strategy": "积极做多，跟随主线龙头",
                "risk": "注意分化风险，随时准备撤退"
            }
        elif zt_count >= 50 and zbgc_rate < 25:
            # 发酵期：涨停增加，炸板可控
            return {
                "phase": "发酵",
                "description": "市场情绪回暖，涨停家数增加，炸板率适中",
                "reason": "涨停家数50-80，炸板率<25%，市场处于上升周期",
                "basis": "赚钱效应扩散，跟风股开始表现，是介入主线的好时机",
                "position": 70,
                "strategy": "积极做多，寻找主线龙头",
                "risk": "关注炸板率变化"
            }
        elif zt_count >= 30 and zbgc_rate < 30:
            # 启动期：涨停数量回升
            return {
                "phase": "启动",
                "description": "市场开始活跃，涨停家数增加",
                "reason": "涨停家数30-50，市场情绪从冰点恢复",
                "basis": "资金开始试盘，出现首个主线板块，是试错买入的阶段",
                "position": 50,
                "strategy": "轻仓试盘，关注首板和二板机会",
                "risk": "不确定性强，控制仓位"
            }
        elif zt_count >= 20 and zbgc_rate >= 30:
            # 分歧期：炸板增多
            return {
                "phase": "分歧",
                "description": "市场出现分歧，炸板率上升",
                "reason": "涨停家数20-50，但炸板率>=30%，资金出现分歧",
                "basis": "高位股开始兑现利润，注意高低切换",
                "position": 30,
                "strategy": "谨慎操作，关注低位首板",
                "risk": "追高容易被套"
            }
        elif zt_count >= 10 and zt_count < 20:
            # 退潮期：涨停减少
            return {
                "phase": "退潮",
                "description": "市场情绪衰退，涨停家数明显减少",
                "reason": "涨停家数10-20，市场情绪持续走弱",
                "basis": "亏钱效应明显，减少出手频率",
                "position": 20,
                "strategy": "防守为主，尽量空仓或轻仓",
                "risk": "容易出现大幅亏损"
            }
        elif zt_count < 10 or dtgc_count > 20:
            # 冰点：涨停极少或跌停增多
            return {
                "phase": "冰点",
                "description": "市场情绪冰点，涨停极少或跌停增多",
                "reason": "涨停<10家或跌停>20家，市场极度弱势",
                "basis": "否极泰来，冰点之后往往孕育反弹机会",
                "position": 10,
                "strategy": "空仓等待，等待冰点后的反弹机会",
                "risk": "随时可能出现反弹，但难以预测"
            }
        else:
            # 震荡期
            return {
                "phase": "震荡",
                "description": "市场处于震荡状态",
                "reason": "涨停数量和炸板率处于中间水平",
                "basis": "没有明显的情绪方向，保持中性仓位",
                "position": 40,
                "strategy": "控制仓位，快进快出",
                "risk": "注意大盘方向选择"
            }

    async def _generate_report(self, context: ReviewContext):
        """
        生成最终报告
        按照模板格式：做什么 → 为什么做 → 怎么做 → 判断标准 → 为什么是这个标准 → 怎么定的标准
        """
        # 收集数据
        zt_pool = context.zt_pool or []
        zbgc = context.zbgc or []
        sectors = context.sectors or []
        lhb = context.lhb or []

        zt_count = len(zt_pool)
        zbgc_count = len(zbgc)

        # 获取跌停数据
        dtgc_count = 0
        highest_board = 0
        if zt_pool:
            # 尝试获取最高板
            boards = [s.get("连板数", 1) for s in zt_pool if isinstance(s, dict)]
            highest_board = max(boards) if boards else 1

        # 计算情绪周期
        emotion_cycle = self._calculate_emotion_cycle(zt_count, zbgc_count, dtgc_count, highest_board)

        # 计算炸板率
        zbgc_rate = zbgc_count / max(zt_count, 1) * 100 if zt_count > 0 else 0

        # 构建报告
        report_lines = []

        # 标题
        report_lines.append(f"# 游资复盘分析报告\n")
        report_lines.append(f"**日期**: {context.date}")
        report_lines.append(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")

        # 一、基础数据记录（做什么 → 记录什么数据）
        report_lines.append("## 一、基础数据记录\n")
        report_lines.append("| 项目 | 今日数据 | 备注 |")
        report_lines.append("|------|----------|------|")
        report_lines.append(f"| 涨停家数 | **{zt_count}** | 市场活跃度 |")
        report_lines.append(f"| 炸板家数 | **{zbgc_count}** | 追高风险 |")
        report_lines.append(f"| 炸板率 | **{zbgc_rate:.1f}%** | 追高风险指标 |")
        report_lines.append(f"| 最高板 | **{highest_board}** 板 | 市场空间 |")
        report_lines.append("")

        # 二、情绪周期判断（做什么 → 为什么做 → 判断标准）
        report_lines.append("## 二、情绪周期判断\n")
        report_lines.append(f"**当前周期阶段**: {emotion_cycle['phase']}期\n")
        report_lines.append(f"**描述**: {emotion_cycle['description']}\n")
        report_lines.append("")

        report_lines.append("### 判断依据\n")
        report_lines.append(f"- **做什么**: 判断当前市场处于哪个情绪周期阶段\n")
        report_lines.append(f"- **为什么做**: 周期决定仓位和策略，不同周期采用不同打法\n")
        report_lines.append(f"- **判断标准**:\n")
        report_lines.append(f"  - 涨停家数: {zt_count}\n")
        report_lines.append(f"  - 炸板率: {zbgc_rate:.1f}%\n")
        report_lines.append(f"  - 最高板: {highest_board}板\n")
        report_lines.append(f"- **为什么是这个标准**: {emotion_cycle['reason']}\n")
        report_lines.append(f"- **怎么定的标准**: 基于游资实战经验总结，参考了淘股吧等社区的经典战法\n")
        report_lines.append("")

        # 三、涨停板复盘
        report_lines.append("## 三、涨停板分析\n")
        report_lines.append("### 做什么：复盘今日涨停板，找出明日潜在标的\n")

        if zt_count > 0:
            # 统计板块分布
            sector_count = {}
            for stock in zt_pool[:30]:
                if isinstance(stock, dict):
                    sector = stock.get("所属行业", stock.get("所属板块", "未知"))
                    sector_count[sector] = sector_count.get(sector, 0) + 1

            if sector_count:
                report_lines.append("#### 热点板块\n")
                report_lines.append("| 板块 | 数量 | 备注 |\n")
                report_lines.append("|------|------|------|")
                sorted_sectors = sorted(sector_count.items(), key=lambda x: x[1], reverse=True)
                for sector, count in sorted_sectors[:8]:
                    report_lines.append(f"| {sector} | {count} | {'主线' if count >= 3 else '支线'} |")
            report_lines.append("")

            # 展示前10只涨停股
            report_lines.append("#### 今日涨停股（前10）\n")
            report_lines.append("| 序号 | 代码 | 名称 | 涨跌幅 | 连板数 | 涨停原因 | 所属行业 |\n")
            report_lines.append("|------|------|------|--------|--------|----------|------|")
            for i, stock in enumerate(zt_pool[:10], 1):
                if isinstance(stock, dict):
                    code = stock.get("代码", "")
                    name = stock.get("名称", "")
                    pct = stock.get("涨跌幅", 0)
                    boards = stock.get("连板数", stock.get("涨停统计", ""))
                    reason = stock.get("涨停原因", "未知")
                    sector = stock.get("所属行业", "")
                    report_lines.append(f"| {i} | {code} | {name} | {pct:.2f}% | {boards} | {reason} | {sector} |")
        else:
            report_lines.append("今日无涨停板\n")
        report_lines.append("")

        # 四、炸板复盘
        report_lines.append("## 四、炸板分析\n")
        report_lines.append("### 做什么：分析炸板股，反思错误\n")

        if zbgc_count > 0:
            report_lines.append(f"今日炸板 **{zbgc_count}** 只\n")
            report_lines.append("| 代码 | 名称 | 炸板次数 | 反思 |\n")
            report_lines.append("|------|------|----------|------|")
            for stock in zbgc[:10]:
                if isinstance(stock, dict):
                    code = stock.get("代码", "")
                    name = stock.get("名称", "")
                    times = stock.get("炸板次数", 0)
                    # 反思：跟风/板块回调/量能不足/大盘拖累
                    reflection = "跟风炸板" if times < 3 else "板块回调或量能不足"
                    report_lines.append(f"| {code} | {name} | {times} | {reflection} |")
            report_lines.append("")

            # 炸板原因分析
            report_lines.append("#### 炸板原因分类\n")
            report_lines.append("- [ ] 跟风炸板：板块后排跟风股\n")
            report_lines.append("- [ ] 板块回调：板块整体走弱\n")
            report_lines.append("- [ ] 量能不足：资金接力不够\n")
            report_lines.append("- [ ] 大盘拖累：整体市场下跌\n")
        else:
            report_lines.append("今日无炸板股\n")
        report_lines.append("")

        # 五、龙虎榜复盘
        report_lines.append("## 五、龙虎榜分析\n")
        report_lines.append("### 做什么：跟随主力资金，寻找机构+游资合力股\n")

        if lhb:
            report_lines.append("| 代码 | 名称 | 上榜日 | 买入营业部 | 卖出营业部 | 净额 |\n")
            report_lines.append("|------|------|--------|------------|------------|------|")
            for item in lhb[:10]:
                if isinstance(item, dict):
                    code = item.get("代码", "")
                    name = item.get("名称", "")
                    date = item.get("上榜日", "")
                    # 简化的营业部信息
                    buy = item.get("买入营业部", "")[:20] if item.get("买入营业部") else ""
                    sell = item.get("卖出营业部", "")[:20] if item.get("卖出营业部") else ""
                    net = item.get("净额", 0)
                    report_lines.append(f"| {code} | {name} | {date} | {buy} | {sell} | {net}万 |")
        else:
            report_lines.append("暂无龙虎榜数据\n")
        report_lines.append("")

        # 六、资金流向
        report_lines.append("## 六、资金流向分析\n")
        report_lines.append("### 做什么：找出主力资金动向，确定主线板块\n")

        if sectors:
            report_lines.append("#### 主力净流入板块\n")
            report_lines.append("| 排名 | 板块 | 净流入 | 备注 |\n")
            report_lines.append("|------|------|--------|------|")
            for i, item in enumerate(sectors[:10], 1):
                if isinstance(item, dict):
                    sector = item.get("名称", item.get("板块名称", "未知"))
                    inflow = item.get("主力净流入", item.get("净额", 0))
                    report_lines.append(f"| {i} | {sector} | {inflow} | {'主线' if i <= 3 else '支线'} |")
            report_lines.append("")
        else:
            report_lines.append("暂无资金流向数据\n")
        report_lines.append("")

        # 七、风险预警
        report_lines.append("## 七、风险预警\n")
        report_lines.append(f"**做什么**: 识别风险，控制回撤\n")

        risk_items = []
        if zbgc_rate > 30:
            risk_items.append(f"- 炸板率 {zbgc_rate:.1f}% 过高，追高风险大")
        if zbgc_count > 20:
            risk_items.append(f"- 炸板股数量 {zbgc_count} 较多，情绪可能退潮")
        if zt_count < 20:
            risk_items.append(f"- 涨停家数 {zt_count} 较少，市场弱势")

        if risk_items:
            report_lines.append("### 风险点\n")
            for item in risk_items:
                report_lines.append(item)
        else:
            report_lines.append("### 风险评估\n")
            report_lines.append("- 市场情绪稳定，风险可控\n")
        report_lines.append("")

        # 八、明日计划
        report_lines.append("## 八、明日计划\n")
        report_lines.append("### 做什么：制定明日交易计划\n")

        report_lines.append(f"**当前周期**: {emotion_cycle['phase']}期\n")
        report_lines.append(f"**建议仓位**: {emotion_cycle['position']}%\n")
        report_lines.append(f"**策略**: {emotion_cycle['strategy']}\n")
        report_lines.append(f"**风险提示**: {emotion_cycle['risk']}\n")
        report_lines.append("")

        # 仓位计划表格
        report_lines.append("### 仓位计划\n")
        report_lines.append(f"根据今日情绪周期判断，当前处于【{emotion_cycle['phase']}】期\n")
        report_lines.append("")
        report_lines.append("| 项目 | 建议 |\n")
        report_lines.append("|------|------|\n")
        report_lines.append(f"| 建议仓位 | {emotion_cycle['position']}% |\n")
        report_lines.append(f"| 方向 | {'看多' if emotion_cycle['position'] >= 50 else '震荡' if emotion_cycle['position'] >= 30 else '看空'} |\n")
        report_lines.append(f"| 策略 | {emotion_cycle['strategy']} |\n")
        report_lines.append("")

        # 重点关注
        report_lines.append("### 明日重点关注\n")
        if zt_count > 0:
            # 找出首板和二板
            focus_stocks = []
            for stock in zt_pool:
                if isinstance(stock, dict):
                    boards = stock.get("连板数", 1)
                    if boards <= 2:
                        focus_stocks.append(stock)

            report_lines.append("| 代码 | 名称 | 连板 | 板块 | 关注理由 |\n")
            report_lines.append("|------|------|------|------|----------|")
            for stock in focus_stocks[:5]:
                code = stock.get("代码", "")
                name = stock.get("名称", "")
                boards = stock.get("连板数", 1)
                sector = stock.get("所属行业", "")
                reason = "首板试错" if boards == 1 else "二板确认"
                report_lines.append(f"| {code} | {name} | {boards} | {sector} | {reason} |")
        else:
            report_lines.append("无涨停股，关注空仓等待\n")
        report_lines.append("")

        # 买入条件
        report_lines.append("### 买入条件（全部满足才买）\n")
        report_lines.append("- [ ] 竞价高开 2% 以上\n")
        report_lines.append("- [ ] 竞价量能符合预期\n")
        report_lines.append("- [ ] 大盘环境配合\n")
        report_lines.append("- [ ] 板块效应明显\n")
        report_lines.append("")

        # 止损规则
        report_lines.append("### 止损规则（必须执行）\n")
        report_lines.append("- [ ] 单笔亏损 5% 必须止损\n")
        report_lines.append("- [ ] 收盘跌破日K线必须走\n")
        report_lines.append("- [ ] 大盘急跌必须走\n")
        report_lines.append("")

        # 结尾
        report_lines.append("---\n")
        report_lines.append("*本报告由 AI 自动生成，仅供参考，不构成投资建议。*\n")
        report_lines.append("*判断标准基于游资实战经验，具体操作需结合个人风险偏好。*")

        context.final_report = "\n".join(report_lines)

        # 记录步骤
        context.steps.append(ReviewStep(
            step=len(context.steps) + 1,
            state=AgentState.COMPLETED,
            action="生成报告",
            result="报告生成完成",
            data_used=["final_report"]
        ))


# 全局 Agent 实例
_agent: Optional[ReviewAgent] = None


def get_review_agent() -> ReviewAgent:
    """获取 Review Agent 单例"""
    global _agent
    if _agent is None:
        mcp_client = MCPClient()
        _agent = ReviewAgent(mcp_client)
    return _agent
