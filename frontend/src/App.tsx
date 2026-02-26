import { Routes, Route, Navigate } from 'react-router-dom';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import Positions from './pages/Positions';
import PositionDetail from './pages/PositionDetail';
import Trades from './pages/Trades';
import StrategyAnalysis from './pages/StrategyAnalysis';
import Daily from './pages/Daily';
import DataQuery from './pages/DataQuery';
import './styles/index.css';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/daily" replace />} />

        {/* 计划与复盘 - 核心功能 */}
        <Route path="/daily" element={<Daily />} />

        {/* 持仓与交易 */}
        <Route path="/positions" element={<Positions />} />
        <Route path="/positions/:id" element={<PositionDetail />} />
        <Route path="/trades" element={<Trades />} />

        {/* 策略分析 */}
        <Route path="/strategy-analysis" element={<StrategyAnalysis />} />

        {/* 数据查询 */}
        <Route path="/data-query" element={<DataQuery />} />

        {/* 设置 */}
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;
