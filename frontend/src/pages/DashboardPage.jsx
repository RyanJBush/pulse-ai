import { useEffect, useMemo, useState } from 'react';
import MetricCard from '../components/MetricCard';
import LineChart from '../components/LineChart';
import { fetchAlerts, fetchEvents } from '../services/api';

export default function DashboardPage() {
  const [events, setEvents] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchEvents().then(setEvents).catch(() => setEvents([]));
    fetchAlerts().then(setAlerts).catch(() => setAlerts([]));
  }, []);

  const kpis = useMemo(() => {
    const anomalous = events.filter((item) => item.value > 80).length;
    const anomalyRate = events.length ? ((anomalous / events.length) * 100).toFixed(1) : '0.0';
    const avgValue = events.length
      ? (events.reduce((sum, item) => sum + Number(item.value || 0), 0) / events.length).toFixed(2)
      : '0.00';

    return {
      eventsPerMin: events.length,
      anomalyRate,
      openAlerts: alerts.filter((alert) => alert.status !== 'resolved').length,
      avgValue
    };
  }, [alerts, events]);

  const anomalySeries = events.slice(0, 24).map((event) => Number(event.value || 0));
  const alertSeries = alerts.slice(0, 24).map((alert) => (alert.severity === 'critical' ? 4 : alert.severity === 'high' ? 3 : 1));

  return (
    <section className="page">
      <header className="page-header">
        <h2>Dashboard</h2>
        <p>Live anomaly and operational health view.</p>
      </header>

      <div className="metric-grid metric-grid-4">
        <MetricCard label="Events (window)" value={kpis.eventsPerMin} trend="+12.4%" />
        <MetricCard label="Anomaly Rate" value={`${kpis.anomalyRate}%`} trend="-0.3%" />
        <MetricCard label="Open Alerts" value={kpis.openAlerts} trend="+2" />
        <MetricCard label="Avg Signal Value" value={kpis.avgValue} trend="stable" />
      </div>

      <div className="chart-grid">
        <LineChart title="Signal Trend" points={anomalySeries.length ? anomalySeries : [10, 18, 14, 22, 30, 26]} />
        <LineChart title="Alert Severity Trend" points={alertSeries.length ? alertSeries : [1, 1, 2, 3, 2, 4]} />
      </div>
    </section>
  );
}
