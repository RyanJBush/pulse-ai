import { useEffect, useMemo, useState } from 'react'
import DataTable from '../components/DataTable'
import FilterBar from '../components/FilterBar'
import { fetchAlerts } from '../services/api'

function LikelyCauses({ causes = [] }) {
  if (!causes.length) return <span>No RCA suggestions</span>
  return (
    <details>
      <summary>Likely Causes</summary>
      <ul>
        {causes.map((cause, idx) => (
          <li key={`${cause.cause}-${idx}`}>
            <strong>{cause.cause}</strong> ({Math.round(cause.confidence * 100)}%)
            <div>{cause.evidence.join(', ')}</div>
          </li>
        ))}
      </ul>
    </details>
  )
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [severityFilter, setSeverityFilter] = useState('all')

  useEffect(() => {
    fetchAlerts().then(setAlerts).catch(() => setAlerts([]))
  }, [])

  const filtered = useMemo(() => alerts.filter((alert) => severityFilter === 'all' || alert.severity === severityFilter), [alerts, severityFilter])

  return (
    <section className="page">
      <header className="page-header">
        <h2>Alerts</h2>
        <p>Active alert table with severity filtering.</p>
      </header>

      <FilterBar>
        <label>
          Severity
          <select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}>
            <option value="all">all</option><option value="critical">critical</option><option value="high">high</option><option value="medium">medium</option><option value="low">low</option>
          </select>
        </label>
      </FilterBar>

      <DataTable
        columns={[
          { key: 'id', label: 'Alert ID' },
          { key: 'event_id', label: 'Event ID' },
          { key: 'severity', label: 'Severity', render: (value) => <span className={`badge badge-${value}`}>{value}</span> },
          { key: 'status', label: 'Status' },
          { key: 'message', label: 'Message' },
          { key: 'rca_suggestions', label: 'Likely Causes', render: (value) => <LikelyCauses causes={value} /> },
          { key: 'created_at', label: 'Created' },
        ]}
        rows={filtered}
      />
    </section>
  )
}
