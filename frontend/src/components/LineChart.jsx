export default function LineChart({ title, points }) {
  const width = 420;
  const height = 140;
  const padding = 16;
  const max = Math.max(...points, 1);
  const min = Math.min(...points, 0);
  const range = max - min || 1;

  const path = points
    .map((point, index) => {
      const x = padding + (index * (width - padding * 2)) / (points.length - 1 || 1);
      const y = height - padding - ((point - min) / range) * (height - padding * 2);
      return `${index === 0 ? 'M' : 'L'}${x},${y}`;
    })
    .join(' ');

  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <h3>{title}</h3>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
        <path d={path} fill="none" stroke="#22d3ee" strokeWidth="2.5" />
      </svg>
    </section>
  );
}
