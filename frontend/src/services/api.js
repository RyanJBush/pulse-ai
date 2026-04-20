const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const mockEvents = [
  { id: 101, source: 'edge-gw-1', event_type: 'cpu', value: 42.1, created_at: '2026-04-20T10:00:00Z' },
  { id: 102, source: 'edge-gw-2', event_type: 'latency', value: 80.4, created_at: '2026-04-20T10:01:00Z' },
  { id: 103, source: 'payments', event_type: 'error_rate', value: 91.2, created_at: '2026-04-20T10:02:00Z' },
  { id: 104, source: 'auth', event_type: 'cpu', value: 51.7, created_at: '2026-04-20T10:03:00Z' }
];

const mockAlerts = [
  {
    id: 1,
    event_id: 103,
    severity: 'high',
    status: 'open',
    message: 'Anomalous event detected: source=payments, type=error_rate',
    created_at: '2026-04-20T10:02:30Z'
  }
];

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchEvents() {
  try {
    return await request('/events');
  } catch {
    return mockEvents;
  }
}

export async function fetchAlerts() {
  try {
    return await request('/alerts');
  } catch {
    return mockAlerts;
  }
}
