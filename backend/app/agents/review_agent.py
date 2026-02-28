"""
游资复盘 Agent 核心实现
基于 ReAct 模式的迭代分析
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from app.agents.models import (
    AgentState, Action, ReviewContext, ReviewStep,
    ReviewResult, DecisionResult
)
from app.agents.tools import (
    MCPClient, get_mcp_client,
    fetch_with_retry
)


class ReviewAgent:
    """游资复盘 Agent - 迭代分析模式"""

    def __init__(self, mcp_client: MCPClient = None, max_iterations: int = 15):
        self.mcp = mcp_client or get_mcp_client()
        self.max_iterations = max_iterations
        self.max_retries = 3

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
        # 使用 MCP ak_call 调用，函数名需要正确
        zt_pool, zbgc, sectors, lhb = await asyncio.gather(
            fetch_with_retry(self.mcp.call_akshare, "stock_zt_pool_em", {"date": context.date}, max_retries=self.max_retries),
            fetch_with_retry(self.mcp.call_akshare, "stock_zt_pool_zbgc_em", {"date": context.date}, max_retries=self.max_retries),
            fetch_with_retry(self.mcp.call_akshare, "stock_sector_fund_flow_rank", {"indicator": "今日", "sector_type": "行业资金流"}, max_retries=self.max_retries),
            fetch_with_retry(self.mcp.call_akshare, "stock_lhb_detail_em", {"start_date": context.date, "end_date": context.date}, max_retries=self.max_retries),
        )

        context.zt_pool = zt_pool
        context.zbgc = zbgc
        context.sectors = sectors
        context.lhb = lhb

        # 记录步骤
        context.steps.append(ReviewStep(
            step=step,
            state=AgentState.FETCHING_DATA,
            action="获取基础数据",
            result=f"涨停: {len(zt_pool or [])}, 炸板: {len(zbgc or [])}, 板块: {len(sectors or [])}, 龙虎榜: {len(lhb or [])}",
            data_used=["zt_pool", "zbgc", "sectors", "lhb"]
        ))

    def _get_context_data(self, context: ReviewContext) -> Dict[str, Any]:
        """获取当前上下文数据"""
        return {
            "zt_pool": context.zt_pool,
            "zbgc": context.zbgc,
            "news": context.news,
            "lhb": context.lhb,
            "sectors": context.sectors,
        }

    async def _analyze_and_decide(self, context_data: Dict[str, Any], iteration: int) -> DecisionResult:
        """
        调用 LLM 进行分析和决策

        由于目前 MiniMax MCP 可能没有配置，
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
        """获取新闻（使用 MiniMax MCP）"""
        keywords = params.get("keywords", ["A股", "政策", "股市"])
        query = " ".join(keywords) + " " + context.date

        result = await self.mcp.search_news(query, max_results=10)

        # 解析返回格式（MiniMax 返回 {"organic": [...]}）
        if isinstance(result, dict) and "organic" in result:
            news = result["organic"]
        elif isinstance(result, list):
            news = result
        else:
            news = []

        context.news = news

        # 记录步骤
        context.steps.append(ReviewStep(
            step=step,
            state=AgentState.FETCHING_NEWS,
            action="获取新闻",
            result=f"获取到 {len(news or [])} 条新闻",
            data_used=["news"]
        ))

    async def _fetch_more_data(self, context: ReviewContext, params: Dict[str, Any], step: int):
        """获取更多数据"""
        data_type = params.get("type", "sectors")

        if data_type == "sectors":
            sectors = await fetch_with_retry(
                self.mcp.call_akshare,
                "stock_sector_fund_flow_rank",
                {"indicator": "今日", "sector_type": "行业资金流"},
                max_retries=self.max_retries
            )
            context.sectors = sectors
            data_key = "sectors"
        elif data_type == "lhb":
            lhb = await fetch_with_retry(
                self.mcp.call_akshare,
                "stock_lhb_detail_em",
                {"start_date": context.date, "end_date": context.date},
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
        zbgc_rate = zbgc_count / max(zt_count, 1) * 100 if zt_count > 0 else 100

        if zt_count >= 80 and zbgc_rate < 15:
            return {"phase": "高潮", "description": "市场情绪高涨，涨停家数多，炸板率低", "reason": "涨停家数>=80且炸板率<15%", "basis": "赚钱效应最好阶段", "position": 80, "strategy": "积极做多，跟随主线龙头", "risk": "注意分化风险"}
        elif zt_count >= 50 and zbgc_rate < 25:
            return {"phase": "发酵", "description": "市场情绪回暖，涨停家数增加", "reason": "涨停家数50-80，炸板率<25%", "basis": "赚钱效应扩散", "position": 70, "strategy": "积极做多，寻找主线龙头", "risk": "关注炸板率变化"}
        elif zt_count >= 30 and zbgc_rate < 30:
            return {"phase": "启动", "description": "市场开始活跃", "reason": "涨停家数30-50", "basis": "资金开始试盘", "position": 50, "strategy": "轻仓试盘，关注首板和二板机会", "risk": "不确定性强，控制仓位"}
        elif zt_count >= 20 and zbgc_rate >= 30:
            return {"phase": "分歧", "description": "市场出现分歧", "reason": "涨停家数20-50，炸板率>=30%", "basis": "高位股开始兑现", "position": 30, "strategy": "谨慎操作，关注低位首板", "risk": "追高容易被套"}
        elif zt_count >= 10 and zt_count < 20:
            return {"phase": "退潮", "description": "市场情绪衰退", "reason": "涨停家数10-20", "basis": "亏钱效应明显", "position": 20, "strategy": "防守为主，尽量空仓或轻仓", "risk": "容易出现大幅亏损"}
        elif zt_count < 10 or dtgc_count > 20:
            return {"phase": "冰点", "description": "市场情绪冰点", "reason": "涨停<10或跌停>20", "basis": "否极泰来", "position": 10, "strategy": "空仓等待，等待反弹机会", "risk": "难以预测"}
        else:
            return {"phase": "震荡", "description": "市场处于震荡状态", "reason": "中间状态", "basis": "无明显方向", "position": 40, "strategy": "控制仓位，快进快出", "risk": "注意大盘方向"}

    async def _generate_report(self, context: ReviewContext):
        """生成最终报告"""
        zt_pool = context.zt_pool or []
        zbgc = context.zbgc or []
        sectors = context.sectors or []
        lhb = context.lhb or []
        news = context.news or []
        # 提取数据列表（API 返回格式为 {"data": [...]}）
        zt_pool_data = zt_pool.get("data", zt_pool) if isinstance(zt_pool, dict) else (zt_pool or [])
        zbgc_data = zbgc.get("data", zbgc) if isinstance(zbgc, dict) else (zbgc or [])
        sectors_data = sectors.get("data", sectors) if isinstance(sectors, dict) else (sectors or [])
        lhb_data = lhb.get("data", lhb) if isinstance(lhb, dict) else (lhb or [])

        zt_count = len(zt_pool_data)
        zbgc_count = len(zbgc_data)

        dtgc_count = 0
        highest_board = 0
        if zt_pool_data:
            boards = [s.get("连板数", 1) for s in zt_pool_data if isinstance(s, dict)]
            highest_board = max(boards) if boards else 1

        emotion_cycle = self._calculate_emotion_cycle(zt_count, zbgc_count, dtgc_count, highest_board)
        zbgc_rate = zbgc_count / max(zt_count, 1) * 100 if zt_count > 0 else 0

        report_lines = []

        report_lines.append(f"# 游资复盘分析报告\n")
        report_lines.append(f"**日期**: {context.date}")
        report_lines.append(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")

        # 一、基础数据
        report_lines.append("## 一、基础数据记录\n")
        report_lines.append("| 项目 | 今日数据 | 备注 |\n")
        report_lines.append("|------|----------|------|\n")
        report_lines.append(f"| 涨停家数 | **{zt_count}** | 市场活跃度 |\n")
        report_lines.append(f"| 炸板家数 | **{zbgc_count}** | 追高风险 |\n")
        report_lines.append(f"| 炸板率 | **{zbgc_rate:.1f}%** | 追高风险指标 |\n")
        report_lines.append(f"| 最高板 | **{highest_board}** 板 | 市场空间 |\n")
        report_lines.append("")

        # 二、情绪周期
        report_lines.append("## 二、情绪周期判断\n")
        report_lines.append(f"**当前周期阶段**: {emotion_cycle['phase']}期\n")
        report_lines.append(f"**描述**: {emotion_cycle['description']}\n")
        report_lines.append("")

        # 三、涨停板分析
        report_lines.append("## 三、涨停板分析\n")
        if zt_count > 0:
            sector_count = {}
            for stock in zt_pool_data[:30]:
                if isinstance(stock, dict):
                    sector = stock.get("所属行业", "未知")
                    sector_count[sector] = sector_count.get(sector, 0) + 1

            if sector_count:
                report_lines.append("#### 热点板块\n")
                report_lines.append("| 板块 | 数量 | 备注 |\n")
                report_lines.append("|------|------|------|\n")
                sorted_sectors = sorted(sector_count.items(), key=lambda x: x[1], reverse=True)
                for sector, count in sorted_sectors[:8]:
                    report_lines.append(f"| {sector} | {count} | {'主线' if count >= 3 else '支线'} |\n")

        report_lines.append("")

        # 四、炸板分析
        report_lines.append("## 四、炸板分析\n")
        if zbgc_count > 0:
            report_lines.append(f"今日炸板 **{zbgc_count}** 只\n")
        else:
            report_lines.append("今日无炸板股\n")
        report_lines.append("")

        # 五、风险预警
        report_lines.append("## 五、风险预警\n")
        risk_items = []
        if zbgc_rate > 30:
            risk_items.append(f"- 炸板率 {zbgc_rate:.1f}% 过高")
        if zt_count < 20:
            risk_items.append(f"- 涨停家数 {zt_count} 较少")

        if risk_items:
            for item in risk_items:
                report_lines.append(item)
        else:
            report_lines.append("- 市场情绪稳定\n")
        report_lines.append("")

        # 六、新闻热点
        report_lines.append("## 六、新闻热点\n")
        if news and len(news) > 0:
            for item in news[:5]:
                title = item.get("title", "无标题")
                source = item.get("source", item.get("source", ""))
                date = item.get("date", "")
                report_lines.append(f"- **{title}**\n")
                if source or date:
                    report_lines.append(f"  - 来源: {source} | {date}\n")
        else:
            report_lines.append("暂无相关新闻\n")
        report_lines.append("")

        # 七、明日计划
        report_lines.append("## 六、明日计划\n")
        report_lines.append(f"**当前周期**: {emotion_cycle['phase']}期\n")
        report_lines.append(f"**建议仓位**: {emotion_cycle['position']}%\n")
        report_lines.append(f"**策略**: {emotion_cycle['strategy']}\n")
        report_lines.append("")

        report_lines.append("---\n")
        report_lines.append("*本报告由 AI 自动生成，仅供参考，不构成投资建议。*")

        context.final_report = "\n".join(report_lines)

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
        _agent = ReviewAgent()
    return _agent
