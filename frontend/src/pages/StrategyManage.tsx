import { useState, useEffect } from 'react';
import axios from 'axios';

interface Strategy {
  id: number;
  name: string;
  description?: string;
  strategy_type: string;
  code?: string;
  is_builtin: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function StrategyManage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    strategy_type: 'custom',
    code: '',
    is_active: true,
  });

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/strategies', { params: { limit: 100 } });
      setStrategies(res.data || []);
    } catch (err) {
      console.error('Failed to load strategies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!form.name) {
      alert('请输入策略名称');
      return;
    }
    try {
      const data = {
        name: form.name,
        description: form.description || undefined,
        strategy_type: form.strategy_type,
        code: form.code || undefined,
        is_active: form.is_active,
      };

      if (editingStrategy) {
        await axios.put(`/api/strategies/${editingStrategy.id}`, data);
      } else {
        await axios.post('/api/strategies', data);
      }

      setShowModal(false);
      setEditingStrategy(null);
      resetForm();
      loadStrategies();
    } catch (err: any) {
      alert(err.response?.data?.detail || '保存失败');
    }
  };

  const handleEdit = (strategy: Strategy) => {
    setEditingStrategy(strategy);
    setForm({
      name: strategy.name,
      description: strategy.description || '',
      strategy_type: strategy.strategy_type,
      code: strategy.code || '',
      is_active: strategy.is_active,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个策略吗？')) return;
    try {
      await axios.delete(`/api/strategies/${id}`);
      loadStrategies();
    } catch (err: any) {
      alert(err.response?.data?.detail || '删除失败');
    }
  };

  const handleToggle = async (id: number) => {
    try {
      await axios.put(`/api/strategies/${id}/toggle`);
      loadStrategies();
    } catch (err) {
      alert('操作失败');
    }
  };

  const resetForm = () => {
    setForm({
      name: '',
      description: '',
      strategy_type: 'custom',
      code: '',
      is_active: true,
    });
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>策略管理</h2>
        <button
          onClick={() => { resetForm(); setEditingStrategy(null); setShowModal(true); }}
          style={{
            padding: '8px 16px',
            background: '#1890ff',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          + 新建策略
        </button>
      </div>

      {loading ? (
        <div>加载中...</div>
      ) : strategies.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          暂无策略，点击"新建策略"创建
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
          <thead>
            <tr style={{ background: '#fafafa' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>策略名称</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>类型</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>描述</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>内置</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>状态</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((strategy) => (
              <tr key={strategy.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                <td style={{ padding: '12px', fontWeight: 'bold' }}>{strategy.name}</td>
                <td style={{ padding: '12px' }}>{strategy.strategy_type === 'custom' ? '自定义' : '内置'}</td>
                <td style={{ padding: '12px', color: '#666' }}>{strategy.description || '-'}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  {strategy.is_builtin ? '是' : '否'}
                </td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    background: strategy.is_active ? '#52c41a' : '#999',
                    color: '#fff',
                  }}>
                    {strategy.is_active ? '启用' : '禁用'}
                  </span>
                </td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  <button onClick={() => handleToggle(strategy.id)} style={{ marginRight: '8px', cursor: 'pointer' }}>
                    {strategy.is_active ? '禁用' : '启用'}
                  </button>
                  <button onClick={() => handleEdit(strategy)} style={{ marginRight: '8px', cursor: 'pointer' }}>
                    编辑
                  </button>
                  {!strategy.is_builtin && (
                    <button onClick={() => handleDelete(strategy.id)} style={{ color: '#ff4d4f', cursor: 'pointer' }}>
                      删除
                    </button>
                  )}
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
            <h3>{editingStrategy ? '编辑策略' : '新建策略'}</h3>

            <div style={{ marginTop: '16px' }}>
              <label>策略名称 *</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                placeholder="如: 均线突破策略"
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>描述</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px', minHeight: '60px' }}
                placeholder="策略描述"
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>策略类型</label>
              <select
                value={form.strategy_type}
                onChange={(e) => setForm({ ...form, strategy_type: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px' }}
              >
                <option value="custom">自定义</option>
                <option value="builtin">内置</option>
              </select>
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>策略代码</label>
              <textarea
                value={form.code}
                onChange={(e) => setForm({ ...form, code: e.target.value })}
                style={{ width: '100%', padding: '8px', marginTop: '4px', minHeight: '100px', fontFamily: 'monospace' }}
                placeholder="策略代码"
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <label>
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  style={{ marginRight: '8px' }}
                />
                启用策略
              </label>
            </div>

            <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button onClick={() => { setShowModal(false); setEditingStrategy(null); }} style={{ padding: '8px 16px' }}>
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
