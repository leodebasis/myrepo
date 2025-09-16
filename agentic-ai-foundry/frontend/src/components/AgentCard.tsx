import { useNavigate } from 'react-router-dom';
import { Agent } from '../types';

export default function AgentCard({ agent }: { agent: Agent }) {
  const navigate = useNavigate();
  return (
    <button className="agent-card" onClick={() => navigate(`/agents/${agent.slug}`)}>
      <div className="agent-card-title">{agent.name}</div>
    </button>
  );
}

