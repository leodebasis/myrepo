import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Agents from './pages/Agents';
import AgentDetail from './pages/AgentDetail';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Agents />} />
        <Route path="/agents/:slug" element={<AgentDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

