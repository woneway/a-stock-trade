import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TodayPlan from './pages/TodayPlan';
import Strategy from './pages/Strategy';
import PlanList from './pages/PlanList';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import './App.css';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/today" element={<TodayPlan />} />
        <Route path="/strategy" element={<Strategy />} />
        <Route path="/plans" element={<PlanList />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;
