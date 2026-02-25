import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';

interface ReviewDetail {
  id: number;
  review_date: string;
  limit_up_stocks?: Array<{ code: string; name: string; reason?: string; sector?: string }>;
  broken_stocks?: Array<{ code: string; name: string; reason?: string }>;
  yesterday_limit_up_performance?: Array<{ code: string; name: string; change_pct?: number }>;
  hot_sectors?: string[];
  market_cycle?: string;
  position_advice?: string;
  risk_warning?: string;
  broken_plate_ratio?: number;
  highest_board?: number;
  up_count?: number;
  turnover?: number;
  above_20ma?: boolean;
  index_trend?: string;
  main_sectors?: string[];
  tomorrow_strategy?: { position_pct?: number; focus_sectors?: string[] };
  notes?: string;
  created_at: string;
  updated_at: string;
}

export default function ReviewDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [review, setReview] = useState<ReviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isNew, setIsNew] = useState(false);

  // 编辑状态
  const [editData, setEditData] = useState<Partial<ReviewDetail>>({});

  useEffect(() => {
    if (id === 'new') {
      setIsNew(true);
      const today = dayjs().format('YYYY-MM-DD');
      setReview({
        id: 0,
        review_date: today,
        created_at: '',
        updated_at: '',
      });
      setEditData({ review_date: today });
      setLoading(false);
    } else if (id) {
      loadReview(parseInt(id));
    }
  }, [id]);

  const loadReview = async (reviewId: number) => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/reviews/${reviewId}`);
      setReview(res.data);
      setEditData(res.data);
    } catch (err) {
      console.error('Failed to load review:', err);
      alert('加载失败');
      navigate('/reviews');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!editData.review_date) {
      alert('请选择日期');
      return;
    }

    setSaving(true);
    try {
      if (isNew) {
        await axios.post('/api/reviews', editData);
        alert('创建成功');
      } else if (review?.id) {
        await axios.put(`/api/reviews/${review.id}`, editData);
        alert('保存成功');
      }
      navigate('/reviews');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      alert(error.response?.data?.detail || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!review?.id || !confirm('确定要删除这条复盘吗？')) return;

    try {
      await axios.delete(`/api/reviews/${review.id}`);
      alert('删除成功');
      navigate('/reviews');
    } catch (err) {
      alert('删除失败');
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">加载中...</div></div>;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/reviews" className="back-link">← 返回列表</Link>
          <h1>{isNew ? '新建复盘' : `复盘详情 - ${dayjs(review?.review_date).format('YYYY-MM-DD')}`}</h1>
        </div>
        <div className="header-actions">
          {!isNew && (
            <button className="btn btn-danger" onClick={handleDelete}>删除</button>
          )}
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>

      <div className="review-detail">
        <div className="detail-section">
          <h3>基本信息</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>复盘日期</label>
              <input
                type="date"
                value={editData.review_date || ''}
                onChange={(e) => setEditData({ ...editData, review_date: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>情绪周期</label>
              <select
                value={editData.market_cycle || ''}
                onChange={(e) => setEditData({ ...editData, market_cycle: e.target.value })}
              >
                <option value="">请选择</option>
                <option value="冰点">冰点</option>
                <option value="启动">启动</option>
                <option value="分歧">分歧</option>
                <option value="高潮">高潮</option>
                <option value="退潮">退潮</option>
                <option value="震荡">震荡</option>
              </select>
            </div>
            <div className="form-group">
              <label>仓位建议</label>
              <input
                type="text"
                value={editData.position_advice || ''}
                onChange={(e) => setEditData({ ...editData, position_advice: e.target.value })}
                placeholder="如: 80%"
              />
            </div>
            <div className="form-group">
              <label>风险提示</label>
              <input
                type="text"
                value={editData.risk_warning || ''}
                onChange={(e) => setEditData({ ...editData, risk_warning: e.target.value })}
                placeholder="风险提示"
              />
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>大盘数据</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>上涨家数</label>
              <input
                type="number"
                value={editData.up_count ?? ''}
                onChange={(e) => setEditData({ ...editData, up_count: parseInt(e.target.value) || undefined })}
              />
            </div>
            <div className="form-group">
              <label>成交额(亿)</label>
              <input
                type="number"
                step="0.1"
                value={editData.turnover ?? ''}
                onChange={(e) => setEditData({ ...editData, turnover: parseFloat(e.target.value) || undefined })}
              />
            </div>
            <div className="form-group">
              <label>炸板率(%)</label>
              <input
                type="number"
                step="0.1"
                value={editData.broken_plate_ratio ?? ''}
                onChange={(e) => setEditData({ ...editData, broken_plate_ratio: parseFloat(e.target.value) || undefined })}
              />
            </div>
            <div className="form-group">
              <label>最高连板</label>
              <input
                type="number"
                value={editData.highest_board ?? ''}
                onChange={(e) => setEditData({ ...editData, highest_board: parseInt(e.target.value) || undefined })}
              />
            </div>
            <div className="form-group">
              <label>是否在20日线上</label>
              <select
                value={editData.above_20ma === true ? 'true' : editData.above_20ma === false ? 'false' : ''}
                onChange={(e) => setEditData({ ...editData, above_20ma: e.target.value === '' ? undefined : e.target.value === 'true' })}
              >
                <option value="">请选择</option>
                <option value="true">是</option>
                <option value="false">否</option>
              </select>
            </div>
            <div className="form-group">
              <label>指数趋势</label>
              <select
                value={editData.index_trend || ''}
                onChange={(e) => setEditData({ ...editData, index_trend: e.target.value })}
              >
                <option value="">请选择</option>
                <option value="上涨">上涨</option>
                <option value="下跌">下跌</option>
                <option value="震荡">震荡</option>
              </select>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>热门板块</h3>
          <div className="form-group">
            <label>热门板块 (逗号分隔)</label>
            <input
              type="text"
              value={editData.hot_sectors?.join(', ') || ''}
              onChange={(e) => setEditData({
                ...editData,
                hot_sectors: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              })}
              placeholder="如: AI应用, 低空经济, 机器人"
            />
          </div>
          <div className="form-group">
            <label>主流板块 (逗号分隔)</label>
            <input
              type="text"
              value={editData.main_sectors?.join(', ') || ''}
              onChange={(e) => setEditData({
                ...editData,
                main_sectors: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              })}
              placeholder="如: 新能源, 半导体"
            />
          </div>
        </div>

        <div className="detail-section">
          <h3>备注</h3>
          <div className="form-group">
            <textarea
              rows={4}
              value={editData.notes || ''}
              onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
              placeholder="其他备注信息..."
            />
          </div>
        </div>
      </div>
    </div>
  );
}
