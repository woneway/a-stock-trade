import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';

interface TradingPlan {
  id: number;
  stock_code: string;
  stock_name?: string;
  plan_date: string;
  target_price?: number;
  quantity?: number;
  strategy_type: string;
  trade_mode?: string;
  stop_loss?: number;
  take_profit_1?: number;
  take_profit_2?: number;
  reason?: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export default function TradingPlans() {
  const [plans, setPlans] = useState<TradingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState<TradingPlan | null>(null);
  const [stats, setStats] = useState({ total: 0, draft: 0, executed: 0, abandoned: 0 });
  const [form, setForm] = useState({
    stock_code: '',
    stock_name: '',
    plan_date: dayjs().format('YYYY-MM-DD'),
    target_price: '',
    quantity: '',
    strategy_type: 'custom',
    trade_mode: '',
    stop_loss: '',
    take_profit_1: '',
    reason: '',
    status: 'draft',
  });

  useEffect(() => {
    loadPlans();
    loadStats();
  }, []);

  const loadPlans = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/plans', { params: { limit: 100 } });
      setPlans(res.data || []);
    } catch (err) {
      console.error('Failed to load plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await axios.get('/api/plans/stats/summary');
      setStats(res.data || { total: 0, draft: 0, executed: 0, abandoned: 0 });
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleSubmit = async () => {
    if (!form.stock_code) {
      alert('请输入股票代码');
      return;
    }
    try {
      const data = {
        stock_code: form.stock_code,
        stock_name: form.stock_name || form.stock_code,
        plan_date: form.plan_date,
        target_price: form.target_price ? parseFloat(form.target_price) : undefined,
        quantity: form.quantity ? parseInt(form.quantity) : undefined,
        strategy_type: form.strategy_type,
        trade_mode: form.trade_mode || undefined,
        stop_loss: form.stop_loss ? parseFloat(form.stop_loss) : undefined,
        take_profit_1: form.take_profit_1 ? parseFloat(form.take_profit_1) : undefined,
        reason: form.reason || undefined,
        status: form.status,
      };

      if (editingPlan) {
        await axios.put(`/api/plans/${editingPlan.id}`, data);
      } else {
        await axios.post('/api/plans', data);
      }

      setShowModal(false);
      setEditingPlan(null);
      resetForm();
      loadPlans();
      loadStats();
    } catch (err) {
      alert('保存失败');
    }
  };

  const handleEdit = (plan: TradingPlan) => {
    setEditingPlan(plan);
    setForm({
      stock_code: plan.stock_code,
      stock_name: plan.stock_name || '',
      plan_date: plan.plan_date,
      target_price: plan.target_price?.toString() || '',
      quantity: plan.quantity?.toString() || '',
      strategy_type: plan.strategy_type,
      trade_mode: plan.trade_mode || '',
      stop_loss: plan.stop_loss?.toString() || '',
      take_profit_1: plan.take_profit_1?.toString() || '',
      reason: plan.reason || '',
      status: plan.status,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个计划吗？')) return;
    try {
      await axios.delete(`/api/plans/${id}`);
      loadPlans();
      loadStats();
    } catch (err) {
      alert('删除失败');
    }
  };

  const resetForm = () => {
    setForm({
      stock_code: '',
      stock_name: '',
      plan_date: dayjs().format('YYYY-MM-DD'),
      target_price: '',
      quantity: '',
      strategy_type: 'custom',
      trade_mode: '',
      stop_loss: '',
      take_profit_1: '',
      reason: '',
      status: 'draft',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return '#999';
      case 'executed': return '#52c41a';
      case 'abandoned': return '#ff4d4f';
      case 'expired': return '#faad14';
      default: return '#999';
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>交易计划</h2>
        <button
          onClick={() => { resetForm(); setEditingPlan(null); setShowModal(true); }}
          style={{
            padding: '8px 16px',
            background: '#1890ff',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          + 新建计划
        </button>
      </div>

      {/* 统计卡片 */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '20px' }}>
        <div style={{ flex: 1, padding: '16px', background: '#f5f5f5', borderRadius: '8px' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.total}</div>
          <div style={{ color: '#666' }}>总计划数</div>
        </div>
        <div style={{ flex: 1, padding: '16px', background: '#e6f7ff', borderRadius: '8px' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>{stats.draft}</div>
          <div style={{ color: '#666' }}>待执行</div>
        </div>
        <div style={{ flex: 1, padding: '16px', background: '#f6ffed', borderRadius: '8px' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>{stats.executed}</div>
          <div style={{ color: '#666' }}>已执行</div>
        </div>
        <div style={{ flex: 1, padding: '16px', background: '#fff1f0', borderRadius: '8px' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff4d4f' }}>{stats.abandoned}</div>
          <div style={{ color: '#666' }}>已放弃</div>
        </div>
      </div>

      {/* 计划列表 */}
      {loading ? (
        <div>加载中...</div>
      ) : plans.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          暂无交易计划，点击"新建计划"创建
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
          <thead>
            <tr style={{ background: '#fafafa' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>股票</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>计划日期</th>
              <th style={{ padding: '12px', textAlign: 'right' }}>目标价</th>
              <th style={{ padding: '12px', textAlign: 'right' }}>数量</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>交易模式</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>止损</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>状态</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((plan) => (
              <tr key={plan.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                <td style={{ padding: '12px' }}>
                  <div style={{ fontWeight: 'bold' }}>{plan.stock_name || plan.stock_code}</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>{plan.stock_code}</div>
                </td>
                <td style={{ padding: '12px' }}>{plan.plan_date}</td>
                <td style={{ padding: '12px', textAlign: 'right' }}>
                  {plan.target_price ? `¥${plan.target_price.toFixed(2)}` : '-'}
                </td>
                <td style={{ padding: '12px', textAlign: 'right' }}>{plan.quantity || '-'}</td>
                <td style={{ padding: '12px' }}>{plan.trade_mode || '-'}</td>
                <td style={{ padding: '12px' }}>
                  {plan.stop_loss ? `¥${plan.stop_loss.toFixed(2)}` : '-'}
                </td>
                <td style={{ padding: '12px' }}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    background: getStatusColor(plan.status),
                    color: '#fff',
                  }}>
                    {plan.status === 'draft' ? '待执行' : plan.status === 'executed' ? '已执行' : plan.status === 'abandoned' ? '已放弃' : '已过期'}
                  </span>
                </td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  <button onClick={() => handleEdit(plan)} style={{ marginRight: '8px', cursor: 'pointer' }}>编辑</button>
                  <button onClick={() => handleDelete(plan.id)} style={{ color: '#ff4d4f', cursor: 'pointer' }}>删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* 新建/编辑弹窗 */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            background: '#fff',
            padding: '24px',
            borderRadius: '8px',
            width: '500px',
            maxHeight: '80vh',
            overflow: 'auto',
          }}>
            <h3>{editingPlan ? '编辑计划' : '新建交易计划'}</h3>

            <div style={{ marginTop: '16px' }}>
              <label>股票代码 *</label>
              <input
                type="text"
                value={form.stock_code}
                onChange={(e) => setForm({ ...form, stock_code: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                placeholder="如: 600000"
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>股票名称</label>
              <input
                type="text"
                value={form.stock_name}
                onChange={(e) => setForm({ ...form, stock_name: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px' }}
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>计划日期 *</label>
              <input
                type="date"
                value={form.plan_date}
                onChange={(e) => setForm({ ...form, plan_date: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
              <div style={{ flex: 1 }}>
                <label>目标价</label>
                <input
                  type="number"
                  value={form.target_price}
                  onChange={(e) => setForm({ ...form, target_price: e.target.value })}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  step="0.01"
                />
              </div>
              <div style={{ flex: 1 }}>
                <label>数量</label>
                <input
                  type="number"
                  value={form.quantity}
                  onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
              <div style={{ flex: 1 }}>
                <label>交易模式</label>
                <select
                  value={form.trade_mode}
                  onChange={(e) => setForm({ ...form, trade_mode: e.target.value })}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                >
                  <option value="">请选择</option>
                  <option value="低吸">低吸</option>
                  <option value="半路">半路</option>
                  <option value="打板">打板</option>
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label>状态</label>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                >
                  <option value="draft">待执行</option>
                  <option value="executed">已执行</option>
                  <option value="abandoned">已放弃</option>
                  <option value="expired">已过期</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
              <div style={{ flex: 1 }}>
                <label>止损价</label>
                <input
                  type="number"
                  value={form.stop_loss}
                  onChange={(e) => setForm({ ...form, stop_loss: e.target.value })}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  step="0.01"
                />
              </div>
              <div style={{ flex: 1 }}>
                <label>止盈价</label>
                <input
                  type="number"
                  value={form.take_profit_1}
                  onChange={(e) => setForm({ ...form, take_profit_1: e.target.value })}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  step="0.01"
                />
              </div>
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>买入理由</label>
              <textarea
                value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px', minHeight: '60px' }}
              />
            </div>

            <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button onClick={() => { setShowModal(false); setEditingPlan(null); }} style={{ padding: '8px 16px' }}>
                取消
              </button>
              <button onClick={handleSubmit} style={{ padding: '8px 16px', background: '#1890ff', color: '#fff', border: 'none', borderRadius: '4px' }}>
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
