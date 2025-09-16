export type Agent = {
  name: string;
  slug: string;
  description: string;
};

export type StreamEvent = {
  type: 'log' | 'user' | 'artifact';
  message?: string;
  file?: string;
};

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

