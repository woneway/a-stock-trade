# 决策提示词

DECISION_PROMPT_TEMPLATE = """## 当前分析状态
已完成的数据收集：
{completed_data}

当前分析进度：
{analysis_progress}

## 你的任务
根据当前的分析进度，决定下一步行动。

## 可选行动
1. **complete** - 分析已完成，可以输出报告
2. **fetch_news** - 需要查询新闻，补充市场情绪/板块动量信息
3. **fetch_more_data** - 需要更多数据（如具体个股详情、板块资金流等）
4. **retry** - 当前数据有问题，需要重新获取

## 迭代终止条件
你（Llm）需要自行判断当前分析是否足够完成报告。

判断标准：
1. 核心数据已获取（市场情绪、涨跌停）
2. 关键问题已解答
3. 不需要更多数据/新闻补充

如果满足以下条件，选择 **complete**：
- 已明确市场情绪判断
- 已识别主线板块
- 已完成风险评估
- 已给出策略建议

## 输出格式
```json
{{
  "action": "complete/fetch_news/fetch_more_data/retry",
  "reason": "为什么做这个决定",
  "params": {{
    // 需要的具体数据或参数
  }},
  "analysis_update": "当前分析结论的更新"
}}
```"""


def build_decision_prompt(context_data: dict, analysis_progress: str) -> str:
    """构建决策提示词"""
    # 格式化已完成的数据
    completed_parts = []

    if context_data.get("market_emotion"):
        completed_parts.append(f"- 市场情绪: 已获取")

    if context_data.get("zt_pool"):
        completed_parts.append(f"- 涨停板: {len(context_data['zt_pool'])}只")

    if context_data.get("zbgc"):
        completed_parts.append(f"- 炸板股: {len(context_data['zbgc'])}只")

    if context_data.get("margin"):
        completed_parts.append(f"- 两融数据: 已获取")

    if context_data.get("news"):
        completed_parts.append(f"- 新闻: {len(context_data['news'])}条")

    completed_data = "\n".join(completed_parts) if completed_parts else "暂无数据"

    return DECISION_PROMPT_TEMPLATE.format(
        completed_data=completed_data,
        analysis_progress=analysis_progress
    )
