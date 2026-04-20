import { useEffect, useMemo, useState } from 'react';
import LineChart from '../components/LineChart';
import MetricCard from '../components/MetricCard';
import { fetchAlerts, fetchEvents } from '../services/api';

export default function MetricsPage() {
  const [events, setEvents] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchEvents().then(setEvents).catch(() => setEvents([]));
    fetchAlerts().then(setAlerts).catch(() => setAlerts([]));
  }, []);

  const p95 = useMemo(() => {
    const values = events.map((event) => Number(event.value || 0)).sort((a, b) => a - b);
    if (!values.length) return '0';
    const index = Math.floor(values.length * 0.95) - 1;
    return values[Math.max(index, 0)].toFixed(2);
  }, [events]);

  const errorLike = useMemo(
    () => events.filter((event) => event.event_type.toLowerCase().includes('error')).length,
    [events]
  );

  return (
    <section className="page">
      <header className="page-header">
        <h2>Metrics</h2>
        <p>Operational metrics and anomaly signal behavior.</p>
      </header>

      <div className="metric-grid metric-grid-3">
        <MetricCard label="P95 Signal" value={p95} />
        <MetricCard label="Error-like Events" value={errorLike} />
        <MetricCard label="Total Alerts" value={alerts.length} />
      </div>

      <div className="chart-grid">
        <LineChart
          title="Signal Distribution (recent)"
          points={events.slice(0, 30).map((event) => Number(event.value || 0)).reverse()}
        />
        <LineChart
          title="Alert Volume"
          points={alerts.slice(0, 30).map((_, index) => index + 1).reverse()}
        />
      </div>
    </section>
  );
}
