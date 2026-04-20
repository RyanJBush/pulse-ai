export default function MetricCard({ label, value, trend = '' }) {
  return (
    <section className="metric-card">
      <p className="metric-label">{label}</p>
      <h3>{value}</h3>
      {trend ? <span className="trend">{trend}</span> : null}
    </section>
  );
}
