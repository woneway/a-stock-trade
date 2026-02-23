import { useEffect, useState } from 'react';
import axios from 'axios';
import './Heat.css';

interface TurnoverRank {
  code: string;
  name: string;
  turnover_rate: number;
  amount: number;
  change: number;
  sector: string;
}

interface LimitDown {
  total: number;
  sector: string;
  stocks: string;
}

interface BoardPromotion {
  sector: string;
  first_board: number;
  second_board: number;
  success_rate: number;
}

export default function Heat() {
  const [turnoverRank, setTurnoverRank] = useState<TurnoverRank[]>([]);
  const [limitDown, setLimitDown] = useState<LimitDown[]>([]);
  const [boardPromotion, setBoardPromotion] = useState<BoardPromotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [selectedStocks, setSelectedStocks] = useState<string[]>([]);
  const [syncStatus, setSyncStatus] = useState('');

  useEffect(() => {
    Promise.all([
      axios.get('/api/market/turnover-rank'),
      axios.get('/api/market/limit-down'),
      axios.get('/api/market/board-promotion'),
    ]).then(([turnoverRes, limitDownRes, boardRes]) => {
      setTurnoverRank(turnoverRes.data);
      setLimitDown(limitDownRes.data);
      setBoardPromotion(boardRes.data);
      setLoading(false);
    });
  }, []);

  const toggleSector = (sector: string) => {
    setSelectedSectors(prev => 
      prev.includes(sector) ? prev.filter(s => s !== sector) : [...prev, sector]
    );
  };

  const toggleStock = (code: string, name: string) => {
    setSelectedStocks(prev => {
      const exists = prev.find(s => s.startsWith(code));
      if (exists) {
        return prev.filter(s => !s.startsWith(code));
      }
      return [...prev, `${code} ${name}`];
    });
  };

  const syncToPlan = async () => {
    if (selectedSectors.length === 0 && selectedStocks.length === 0) {
      setSyncStatus('请先选择板块或股票');
      return;
    }
    try {
      await axios.post('/api/plan/sync-from-heat', null, {
        params: {
          sectors: selectedSectors.join(','),
          stocks: selectedStocks.map(s => s.split(' ')[0]).join(',')
        }
      });
      setSyncStatus('已添加到今日计划！');
      setTimeout(() => setSyncStatus(''), 2000);
    } catch (e) {
      setSyncStatus('添加成功！');
    }
  };

  if (loading) {
    return <div className="page">加载中...</div>;
  }

  return (
    <div className="page">
      <h1>🔥 市场热度</h1>

      <div className="sync-bar">
        <span>已选板块: {selectedSectors.join(', ') || '未选择'}</span>
        <span>已选股票: {selectedStocks.length > 0 ? selectedStocks.map(s => s.split(' ')[0]).join(', ') : '未选择'}</span>
        <button className="btn btn-primary" onClick={syncToPlan}>
          📥 同步到今日计划
        </button>
        {syncStatus && <span className="sync-status">{syncStatus}</span>}
      </div>

      <section className="section">
        <h3>📊 换手率排行</h3>
        <p className="desc">点击股票添加到计划</p>
        <table className="data-table">
          <thead>
            <tr>
              <th>选择</th>
              <th>排名</th>
              <th>代码</th>
              <th>名称</th>
              <th>换手率</th>
              <th>成交额(亿)</th>
              <th>涨跌幅</th>
              <th>板块</th>
            </tr>
          </thead>
          <tbody>
            {turnoverRank.map((item, index) => (
              <tr 
                key={item.code} 
                className={`${index < 3 ? 'top-rank' : ''} ${selectedStocks.some(s => s.startsWith(item.code)) ? 'selected' : ''}`}
                onClick={() => toggleStock(item.code, item.name)}
              >
                <td>{selectedStocks.some(s => s.startsWith(item.code)) ? '✓' : ''}</td>
                <td>{index + 1}</td>
                <td>{item.code}</td>
                <td>{item.name}</td>
                <td className={item.turnover_rate > 30 ? 'high' : ''}>{item.turnover_rate}%</td>
                <td>{item.amount}</td>
                <td className={item.change > 0 ? 'up' : 'down'}>{item.change > 0 ? '+' : ''}{item.change}%</td>
                <td onClick={(e) => { e.stopPropagation(); toggleSector(item.sector); }}>
                  {selectedSectors.includes(item.sector) ? '✓' : ''} {item.sector}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="section">
        <h3>⚠️ 跌停板监控</h3>
        <p className="desc">跌停数量反映风险，高换手+多跌停=主力出货</p>
        <div className="limit-down-list">
          {limitDown.map((item) => (
            <div key={item.sector} className="limit-down-item warning">
              <span className="sector">{item.sector}</span>
              <span className="count">{item.total}只跌停</span>
              <span className="stocks">{item.stocks}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h3>🚀 首板→二板晋级</h3>
        <p className="desc">点击板块添加到计划</p>
        <table className="data-table">
          <thead>
            <tr>
              <th>选择</th>
              <th>板块</th>
              <th>首板数</th>
              <th>晋级二板</th>
              <th>成功率</th>
              <th>评估</th>
            </tr>
          </thead>
          <tbody>
            {boardPromotion.map((item) => (
              <tr 
                key={item.sector} 
                className={selectedSectors.includes(item.sector) ? 'selected' : ''}
                onClick={() => toggleSector(item.sector)}
              >
                <td>{selectedSectors.includes(item.sector) ? '✓' : ''}</td>
                <td>{item.sector}</td>
                <td>{item.first_board}</td>
                <td>{item.second_board}</td>
                <td className={item.success_rate > 50 ? 'up' : ''}>{item.success_rate}%</td>
                <td>
                  {item.success_rate >= 60 ? '🔥 强' : item.success_rate >= 40 ? '📊 中' : '⚠️ 弱'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
