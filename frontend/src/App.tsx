import { Routes, Route, Navigate } from 'react-router-dom';
import TodayPlan from './pages/TodayPlan';
import Strategy from './pages/Strategy';
import PlanList from './pages/PlanList';
import Settings from './pages/Settings';
import Backtest from './pages/Backtest';
import Layout from './components/Layout';
import ReviewList from './pages/ReviewList';
import ReviewDetail from './pages/ReviewDetail';
import Positions from './pages/Positions';
import PositionDetail from './pages/PositionDetail';
import Trades from './pages/Trades';
import Review from './pages/Review';
import Plan from './pages/Plan';
import Plaza from './pages/Plaza';
import HistoryList from './pages/HistoryList';
import HistoryDetail from './pages/HistoryDetail';
import './styles/index.css';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/review" replace />} />
        <Route path="/review" element={<Review />} />
        <Route path="/plan" element={<Plan />} />
        <Route path="/history" element={<HistoryList />} />
        <Route path="/history/:id" element={<HistoryDetail />} />
        <Route path="/reviews" element={<ReviewList />} />
        <Route path="/reviews/:id" element={<ReviewDetail />} />
        <Route path="/positions" element={<Positions />} />
        <Route path="/positions/:id" element={<PositionDetail />} />
        <Route path="/trades" element={<Trades />} />
        <Route path="/today" element={<TodayPlan />} />
        <Route path="/strategies" element={<Strategy />} />
        <Route path="/plans" element={<PlanList />} />
        <Route path="/plaza" element={<Plaza />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/backtest" element={<Backtest />} />
      </Routes>
    </Layout>
  );
}

export default App;
