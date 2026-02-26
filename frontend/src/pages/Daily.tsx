import { useState, useEffect } from 'react';
import axios from 'axios';
import './Daily.css';

interface Plan {
  id: number;
  type: 'plan' | 'review';
  trade_date: string;
  status: string;
  template: string | null;
  content: string | null;
  related_id: number | null;
  stock_count: number;
  execution_rate: number;
  pnl: number;
  tags: string | null;
  created_at: string;
  updated_at: string;
  related_plan?: {
    id: number;
    type: string;
    content: string;
    trade_date: string;
  };
}

// 计划模板
const PLAN_TEMPLATE = `## 今日计划

### 大盘环境
- 市场情绪：[旺盛/一般/低迷]
- 指数位置：[上涨中/横盘/下跌中]
- 成交量：[放大/缩量/持平]

### 重点板块
1.
2.
3.

### 目标股票
| 股票代码 | 股票名称 | 买入理由 | 预期价位 |
|---------|---------|---------|---------|
|       |         |         |         |

### 仓位计划
- 总仓位：[ ]%
- 单股仓位：[ ]%
- 止损线：[ ]%

### 风险提示
-
`;

// 复盘模板（可以带入计划内容）
const REVIEW_TEMPLATE = (planContent: string) => `## 今日复盘

### 今日计划回顾
${planContent ? planContent.substring(0, 500) : '(无计划)'}

---

### 大盘回顾
- 指数表现：[ ]
- 成交量：[ ]亿
- 涨跌家数：上涨[ ]家 / 下跌[ ]家

### 今日操作
| 股票代码 | 买入/卖出 | 价格 | 数量 | 盈亏 |
|---------|----------|------|------|------|
|         |          |      |      |      |

### 盈亏分析
- 总盈亏：[ ]元
- 胜率：[ ]%
- 最大盈利：[ ]
- 最大亏损：[ ]

### 反思与改进
1.
2.
3.

### 明日计划
1.
2.
3.
`;

export default function Daily() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [showEditor, setShowEditor] = useState(false);
  const [editingPlan, setEditingPlan] = useState<Plan | null>(null);
  const [content, setContent] = useState('');
  const [template, setTemplate] = useState('daily');
  const [editType, setEditType] = useState<'plan' | 'review'>('plan');
  const [loading, setLoading] = useState(false);
  const [relatedPlanId, setRelatedPlanId] = useState<number | null>(null);

  // 过滤状态
  const [filter, setFilter] = useState<'all' | 'plan' | 'review'>('all');
  const [searchDate, setSearchDate] = useState('');

  // 预览状态
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const res = await axios.get('/api/daily/plans', { params: { limit: 100 } });
      setPlans(res.data);
    } catch (err) {
      console.error('Failed to fetch plans:', err);
    }
  };

  // 过滤计划
  const filteredPlans = plans.filter(p => {
    if (filter !== 'all' && p.type !== filter) return false;
    if (searchDate && p.trade_date !== searchDate) return false;
    return true;
  });

  // 按日期分组
  const groupedPlans = filteredPlans.reduce((acc, plan) => {
    const date = plan.trade_date;
    if (!acc[date]) acc[date] = [];
    acc[date].push(plan);
    return acc;
  }, {} as Record<string, Plan[]>);

  // 新建计划
  const handleNewPlan = () => {
    setEditingPlan(null);
    setContent(PLAN_TEMPLATE);
    setTemplate('daily');
    setEditType('plan');
    setRelatedPlanId(null);
    setShowEditor(true);
    setShowPreview(false);
  };

  // 基于计划创建复盘
  const handleNewReview = (relatedPlan?: Plan) => {
    const planContent = relatedPlan?.content || '';
    setEditingPlan(null);
    setContent(REVIEW_TEMPLATE(planContent));
    setTemplate('daily');
    setEditType('review');
    setRelatedPlanId(relatedPlan?.id || null);
    setShowEditor(true);
    setShowPreview(false);
  };

  // 编辑
  const handleEdit = (plan: Plan) => {
    setEditingPlan(plan);
    setContent(plan.content || (plan.type === 'plan' ? PLAN_TEMPLATE : REVIEW_TEMPLATE('')));
    setTemplate(plan.template || 'daily');
    setEditType(plan.type);
    setShowEditor(true);
    setShowPreview(false);
  };

  // 保存
  const handleSave = async () => {
    if (!content.trim()) {
      alert('请输入内容');
      return;
    }

    setLoading(true);
    try {
      const today = new Date().toISOString().split('T')[0];

      if (editingPlan) {
        await axios.put(`/api/daily/plans/${editingPlan.id}`, {
          content,
          status: 'completed'
        });
      } else {
        await axios.post('/api/daily/plans', {
          type: editType,
          trade_date: today,
          content,
          template,
          status: 'completed',
          related_id: editType === 'review' ? relatedPlanId : null
        });
      }

      fetchPlans();
      setShowEditor(false);
    } catch (err) {
      console.error('Failed to save:', err);
      alert('保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除
  const handleDelete = async (id: number) => {
    if (!confirm('确定删除?')) return;
    try {
      await axios.delete(`/api/daily/plans/${id}`);
      fetchPlans();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  // 渲染Markdown预览
  const renderPreview = () => {
    return content.split('\n').map((line, i) => {
      if (line.startsWith('## ')) {
        return <h3 key={i}>{line.replace('## ', '')}</h3>;
      } else if (line.startsWith('### ')) {
        return <h4 key={i}>{line.replace('### ', '')}</h4>;
      } else if (line.startsWith('- ')) {
        return <li key={i}>{line.replace('- ', '')}</li>;
      } else if (line.startsWith('| ')) {
        return <div key={i} className="table-row">{line}</div>;
      } else if (line.trim() === '') {
        return <br key={i} />;
      }
      return <p key={i}>{line}</p>;
    });
  };

  // 编辑器
  if (showEditor) {
    return (
      <div className="daily-page">
        <div className="page-header">
          <h1>
            {editingPlan ? '编辑' : '新建'}
            {editType === 'plan' ? '计划' : '复盘'}
          </h1>
          <div className="header-actions">
            <button
              className={`btn ${showPreview ? '' : 'btn-primary'}`}
              onClick={() => setShowPreview(false)}
            >
              编辑
            </button>
            <button
              className={`btn ${showPreview ? 'btn-primary' : ''}`}
              onClick={() => setShowPreview(true)}
            >
              预览
            </button>
            <button className="btn btn-secondary" onClick={() => setShowEditor(false)}>
              取消
            </button>
            <button className="btn btn-primary" onClick={handleSave} disabled={loading}>
              {loading ? '保存中...' : '保存'}
            </button>
          </div>
        </div>

        <div className="editor-container">
          {showPreview ? (
            <div className="preview-content">
              {renderPreview()}
            </div>
          ) : (
            <textarea
              className="content-editor"
              value={content}
              onChange={e => setContent(e.target.value)}
              placeholder="在此输入内容..."
            />
          )}
        </div>

        <div className="editor-tips">
          <p>💡 支持 Markdown 语法：# 标题、**粗体**、- 列表、| 表格</p>
        </div>
      </div>
    );
  }

  // 列表页面
  return (
    <div className="daily-page">
      <div className="page-header">
        <h1>计划与复盘</h1>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => handleNewReview()}>
            + 写复盘
          </button>
          <button className="btn btn-primary" onClick={handleNewPlan}>
            + 写计划
          </button>
        </div>
      </div>

      {/* 过滤栏 */}
      <div className="filter-bar">
        <div className="filter-group">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            全部
          </button>
          <button
            className={`filter-btn ${filter === 'plan' ? 'active' : ''}`}
            onClick={() => setFilter('plan')}
          >
            📋 计划
          </button>
          <button
            className={`filter-btn ${filter === 'review' ? 'active' : ''}`}
            onClick={() => setFilter('review')}
          >
            📝 复盘
          </button>
        </div>
        <input
          type="date"
          className="date-filter"
          value={searchDate}
          onChange={e => setSearchDate(e.target.value)}
          placeholder="筛选日期"
        />
        {searchDate && (
          <button className="clear-btn" onClick={() => setSearchDate('')}>
            清除
          </button>
        )}
      </div>

      <div className="plans-container">
        {Object.keys(groupedPlans).length === 0 ? (
          <div className="empty-state">
            <p>暂无记录</p>
            <p className="empty-hint">点击上方按钮创建计划或复盘</p>
          </div>
        ) : (
          <div className="plans-list">
            {Object.entries(groupedPlans).sort(([a], [b]) => b.localeCompare(a)).map(([date, datePlans]) => (
              <div key={date} className="date-group">
                <div className="date-header">{date}</div>
                {datePlans.map(plan => (
                  <div key={plan.id} className={`plan-card ${plan.type}`}>
                    <div className="plan-header">
                      <span className={`plan-type ${plan.type}`}>
                        {plan.type === 'plan' ? '📋 计划' : '📝 复盘'}
                      </span>
                      <span className="plan-status">
                        {plan.status === 'completed' ? '✅ 已完成' : '📝 草稿'}
                      </span>
                    </div>

                    <div className="plan-content" onClick={() => handleEdit(plan)}>
                      {plan.content ? (
                        <pre>{plan.content.substring(0, 150)}{plan.content.length > 150 ? '...' : ''}</pre>
                      ) : (
                        <span className="empty-content">点击编辑</span>
                      )}
                    </div>

                    {/* 关联的计划 */}
                    {plan.type === 'review' && plan.related_plan && (
                      <div className="related-plan">
                        <span className="related-label">📋 关联计划:</span>
                        <span>{plan.related_plan.content?.substring(0, 80)}...</span>
                      </div>
                    )}

                    {/* 复盘统计 */}
                    {plan.type === 'review' && (
                      <div className="plan-stats">
                        <span>📊 股票数: {plan.stock_count}</span>
                        <span>📈 执行率: {plan.execution_rate}%</span>
                        <span className={plan.pnl >= 0 ? 'positive' : 'negative'}>
                          💰 盈亏: {plan.pnl >= 0 ? '+' : ''}{plan.pnl}%
                        </span>
                      </div>
                    )}

                    <div className="plan-actions">
                      {plan.type === 'plan' && (
                        <button
                          className="action-btn success"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleNewReview(plan);
                          }}
                        >
                          创建复盘
                        </button>
                      )}
                      <button
                        className="action-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(plan);
                        }}
                      >
                        编辑
                      </button>
                      <button
                        className="action-btn danger"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(plan.id);
                        }}
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
