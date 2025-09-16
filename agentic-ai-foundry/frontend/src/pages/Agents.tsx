import useSWR from 'swr';
import { API_BASE, Agent } from '../types';
import AgentCard from '../components/AgentCard';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export default function Agents() {
  const { data } = useSWR<{ agents: Agent[] }>(`${API_BASE}/agents`, fetcher);
  const agents = data?.agents ?? [];
  const rows = Array.from({ length: 3 }, () => agents).flat();
  return (
    <div className="page">
      <h2 className="page-title">AI Agents</h2>
      <hr className="divider" />
      <div className="agents-grid">
        {rows.map((a, i) => (
          <AgentCard key={`${a?.slug ?? 'slot'}-${i}`} agent={a ?? { name: '—', slug: `slot-${i}`, description: '' }} />
        ))}
      </div>
    </div>
  );
}

