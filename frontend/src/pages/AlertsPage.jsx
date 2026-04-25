import { useEffect, useMemo, useState } from 'react'
import DataTable from '../components/DataTable'
import FilterBar from '../components/FilterBar'
import { fetchAlerts } from '../services/api'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [severityFilter, setSeverityFilter] = useState('all')

  useEffect(() => {
    fetchAlerts()
      .then(setAlerts)
      .catch(() => setAlerts([]))
  }, [])

  const filtered = useMemo(() => {
    return alerts.filter(
      (alert) => severityFilter === 'all' || alert.severity === severityFilter
    )
  }, [alerts, severityFilter])

  return (
    <section className="page">
      <header className="page-header">
        <h2>Alerts</h2>
        <p>Active alert table with severity filtering.</p>
      </header>

      <FilterBar>
        <label>
          Severity
          <select
            value={severityFilter}
            onChange={(event) => setSeverityFilter(event.target.value)}
          >
            <option value="all">all</option>
            <option value="critical">critical</option>
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
          </select>
        </label>
      </FilterBar>

      <DataTable
        columns={[
          { key: 'id', label: 'Alert ID' },
          { key: 'event_id', label: 'Event ID' },
          {
            key: 'severity',
            label: 'Severity',
            render: (value) => (
              <span className={`badge badge-${value}`}>{value}</span>
            ),
          },
          { key: 'status', label: 'Status' },
          { key: 'message', label: 'Message' },
          { key: 'created_at', label: 'Created' },
        ]}
        rows={filtered}
      />
    </section>
  )
}
