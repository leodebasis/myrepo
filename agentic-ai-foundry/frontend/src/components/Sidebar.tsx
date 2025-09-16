import { NavLink } from 'react-router-dom';
import { FaHome } from 'react-icons/fa';
import useSWR from 'swr';
import { API_BASE, Agent } from '../types';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export default function Sidebar() {
  const { data } = useSWR<{ agents: Agent[] }>(`${API_BASE}/agents`, fetcher);
  const agents = data?.agents ?? [];
  return (
    <aside className="app-sidebar">
      <div className="sidebar-home">
        <FaHome className="home-icon" />
      </div>

      <nav className="sidebar-section">
        <div className="sidebar-section-title">AI Agents</div>
        <ul className="sidebar-list">
          <li>
            <NavLink to="/" className="sidebar-link">All Agents</NavLink>
          </li>
          {agents.map((a) => (
            <li key={a.slug}>
              <NavLink to={`/agents/${a.slug}`} className="sidebar-link">{a.name}</NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <nav className="sidebar-section">
        <div className="sidebar-section-title">Workflows</div>
        <ul className="sidebar-list">
          <li className="sidebar-link disabled">Invoice processing workflow</li>
          <li className="sidebar-link disabled">Patient health records workflow</li>
        </ul>
      </nav>

      <nav className="sidebar-section">
        <ul className="sidebar-list">
          <li className="sidebar-link disabled">Show History</li>
        </ul>
      </nav>
    </aside>
  );
}

