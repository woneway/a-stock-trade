# A股智能交易信号系统 - MVP 1.0

> 游资超短线交易辅助系统 — 项目前期探讨、调研与设计文档

## 核心主线：闭环工作流

```
复盘 → 制定计划 → 盘中监控 → 执行 → 记录 → (再复盘)
```

**核心问题解答**：[查看完整工作流设计](workflow.md)

---

## 文档结构（简化版）

```
mvp1.0/
├── README.md                    ← 你在这里（项目索引）
├── workflow.md                  ← 核心：闭环工作流设计（重点阅读）
├── user-profile.md              # 用户画像与痛点
├── problem-statement.md         # 问题陈述
├── competitive-analysis.md      # 竞品分析
├── data-source-analysis.md      # 数据源评估
├── tech-stack.md               # 技术选型
└── db-schema.md                # 数据库设计
```

## 快速导航

| 想了解... | 看这个文件 |
|-----------|-----------|
| 完整工作流逻辑？ | [workflow.md](workflow.md) |
| 这个产品是做什么的？ | [problem-statement.md](problem-statement.md) |
| 目标用户是谁？ | [user-profile.md](user-profile.md) |
| 竞品有哪些？ | [competitive-analysis.md](competitive-analysis.md) |
| 数据从哪来？ | [data-source-analysis.md](data-source-analysis.md) |
| 用什么技术？ | [tech-stack.md](tech-stack.md) |
| 数据库怎么设计？ | [db-schema.md](db-schema.md) |

---

## MVP核心页面优先级

| 优先级 | 页面 | 状态 |
|--------|------|------|
| P0 | 复盘 | 核心 |
| P0 | 交易计划 | 核心 |
| P0 | 监控 | 核心 |
| P0 | 交易记录 | 核心 |
| P1 | 持仓 | 其次 |
| P2 | 目标股池 | 后续 |
| - | Dashboard | 暂不急 |

---

*项目：A股智能交易信号系统 V1.0*
*创建日期：2026-02-20*
