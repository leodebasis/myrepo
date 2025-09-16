import { useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import useSWR from 'swr';
import { API_BASE, Agent, StreamEvent } from '../types';
import { FaPaperPlane, FaUpload, FaFileAlt } from 'react-icons/fa';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

type ChatMessage = { id: string; role: 'user' | 'agent'; text: string };

export default function AgentDetail() {
  const { slug = '' } = useParams();
  const { data } = useSWR<Agent>(`${API_BASE}/agents/${slug}`, fetcher);
  const agent = data;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [uploads, setUploads] = useState<string[]>([]);
  const [downloads, setDownloads] = useState<string[]>([]);
  const fileRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/files/uploads`).then(r => r.json()).then(d => setUploads(d.files || []));
    fetch(`${API_BASE}/files/outputs`).then(r => r.json()).then(d => setDownloads(d.files || []));
  }, [slug]);

  useEffect(() => {
    const el = document.querySelector('.chat-messages');
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (files.length === 0) return;
    const fd = new FormData();
    files.forEach((f) => fd.append('files', f));
    await fetch(`${API_BASE}/upload`, { method: 'POST', body: fd });
    const res = await fetch(`${API_BASE}/files/uploads`).then(r => r.json());
    setUploads(res.files || []);
    if (fileRef.current) fileRef.current.value = '';
  }

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;
    setMessages((m) => [...m, { id: crypto.randomUUID(), role: 'user', text }]);
    setInput('');

    const fd = new FormData();
    fd.append('prompt', text);
    const response = await fetch(`${API_BASE}/run/${slug}`, { method: 'POST', body: fd });
    const reader = response.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';
      for (const chunk of parts) {
        if (!chunk.startsWith('data:')) continue;
        const payload = chunk.replace(/^data:\s*/, '');
        try {
          const evt: StreamEvent = JSON.parse(payload);
          if (evt.type === 'log') {
            setMessages((m) => [...m, { id: crypto.randomUUID(), role: 'agent', text: evt.message || '' }]);
          } else if (evt.type === 'artifact' && evt.file) {
            setDownloads((d) => Array.from(new Set([...d, evt.file!])));
          }
        } catch {}
      }
    }
  }

  if (!agent) {
    return (
      <div className="page">
        <h2 className="page-title">Loading...</h2>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="agent-detail-header">
        <div className="agent-avatar">{agent.name.split(' ').map(w => w[0]).join('').slice(0,2)}</div>
        <div className="agent-detail-meta">
          <h2 className="page-title">{agent.name}</h2>
          <p className="agent-description">{agent.description}</p>
        </div>
      </div>

      <hr className="divider" />

      <div className="detail-layout">
        <section className="chat-panel">
          <div className="chat-messages">
            {messages.map((m) => (
              <div key={m.id} className={`chat-message ${m.role}`}>{m.text}</div>
            ))}
          </div>
          <div className="chat-input-row">
            <label className="upload-btn">
              <FaUpload />
              <input ref={fileRef} type="file" multiple onChange={onUpload} />
            </label>
            <input
              className="chat-input"
              placeholder="Provide your prompt here"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button className="send-btn" onClick={sendMessage} aria-label="Send">
              <FaPaperPlane />
            </button>
          </div>
        </section>

        <aside className="files-panel">
          <div className="files-section">
            <div className="files-title">Uploaded Files</div>
            <ul className="files-list">
              {uploads.map((name) => (
                <li key={name} className="file-row">
                  <FaFileAlt className="file-icon" />
                  <a href={`${API_BASE}/download/uploads/${encodeURIComponent(name)}`} target="_blank" rel="noreferrer">{name}</a>
                </li>
              ))}
            </ul>
          </div>

          <div className="files-section">
            <div className="files-title">Download Files</div>
            <ul className="files-list">
              {downloads.map((name) => (
                <li key={name} className="file-row">
                  <FaFileAlt className="file-icon" />
                  <a href={`${API_BASE}/download/outputs/${encodeURIComponent(name)}`} target="_blank" rel="noreferrer">{name}</a>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}

