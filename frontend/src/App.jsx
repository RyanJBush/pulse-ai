import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const pages = ['Dashboard', 'Events', 'Alerts', 'Metrics']
const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const fetchJson = async (path) => {
  const response = await fetch(`${apiBase}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`)
  }
  return response.json()
}

function App() {
  const [page, setPage] = useState('Dashboard')
  const [state, setState] = useState({
    events: [],
    alerts: [],
    metrics: null,
    error: '',
  })
  const [sourceFilter, setSourceFilter] = useState('all')

  useEffect(() => {
    let alive = true

    const refresh = async () => {
      try {
        const [events, alerts, metrics] = await Promise.all([
          fetchJson('/api/events?limit=100'),
          fetchJson('/api/alerts'),
          fetchJson('/api/metrics/summary'),
        ])
        if (alive) {
          setState({ events, alerts, metrics, error: '' })
        }
      } catch (error) {
        if (alive) {
          setState((prev) => ({ ...prev, error: error.message }))
        }
      }
    }

    refresh()
    const id = setInterval(refresh, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  const sourceOptions = useMemo(() => {
    const unique = new Set(state.events.map((event) => event.source_id))
    return ['all', ...unique]
  }, [state.events])

  const filteredEvents = useMemo(() => {
    if (sourceFilter === 'all') {
      return state.events
    }
    return state.events.filter((event) => event.source_id === sourceFilter)
  }, [state.events, sourceFilter])

  const eventsByType = useMemo(() => {
    const buckets = {}
    for (const event of filteredEvents) {
      buckets[event.event_type] = (buckets[event.event_type] ?? 0) + 1
    }
    return Object.entries(buckets).map(([name, count]) => ({ name, count }))
  }, [filteredEvents])

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-6 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold">Pulse AI</h1>
          <div className="flex gap-2">
            {pages.map((item) => (
              <button
                key={item}
                className={`rounded-md px-3 py-1 text-sm ${
                  page === item
                    ? 'bg-cyan-500 text-slate-950'
                    : 'bg-slate-800 text-slate-200'
                }`}
                onClick={() => setPage(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </header>

        <div className="flex flex-wrap items-center gap-3 rounded-md bg-slate-900 p-3">
          <label htmlFor="source-filter" className="text-sm">
            Source filter
          </label>
          <select
            id="source-filter"
            value={sourceFilter}
            className="rounded-md bg-slate-800 px-2 py-1 text-sm"
            onChange={(event) => setSourceFilter(event.target.value)}
          >
            {sourceOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          {state.error ? (
            <p className="text-sm text-rose-400">{state.error}</p>
          ) : null}
          <p className="ml-auto text-xs text-slate-400">
            Auto-refresh every 5s
          </p>
        </div>

        {(page === 'Dashboard' || page === 'Metrics') && state.metrics ? (
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ['Events', state.metrics.total_events],
              ['Scores', state.metrics.total_scores],
              ['Alerts', state.metrics.total_alerts],
              ['Open alerts', state.metrics.open_alerts],
            ].map(([label, value]) => (
              <article key={label} className="rounded-lg bg-slate-900 p-4">
                <p className="text-sm text-slate-400">{label}</p>
                <p className="text-2xl font-semibold">{value}</p>
              </article>
            ))}
          </section>
        ) : null}

        {(page === 'Dashboard' || page === 'Events') && (
          <section className="rounded-lg bg-slate-900 p-4">
            <h2 className="mb-3 text-lg font-semibold">Events by type</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={eventsByType}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#cbd5e1" />
                  <YAxis stroke="#cbd5e1" />
                  <Tooltip />
                  <Bar dataKey="count" fill="#06b6d4" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>
        )}

        {(page === 'Dashboard' || page === 'Alerts') && (
          <section className="grid gap-4 lg:grid-cols-2">
            <article className="rounded-lg bg-slate-900 p-4">
              <h2 className="mb-3 text-lg font-semibold">Alert timeline</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={state.alerts.map((alert, index) => ({
                      index,
                      severity: alert.severity,
                      id: alert.id,
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="id" stroke="#cbd5e1" />
                    <YAxis stroke="#cbd5e1" />
                    <Tooltip />
                    <Line dataKey="index" stroke="#f43f5e" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </article>
            <article className="rounded-lg bg-slate-900 p-4">
              <h2 className="mb-3 text-lg font-semibold">Top sources</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={state.metrics?.top_sources ?? []}
                      dataKey="count"
                      nameKey="source_id"
                      outerRadius={90}
                      fill="#38bdf8"
                    />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </article>
          </section>
        )}

        {(page === 'Events' || page === 'Alerts' || page === 'Metrics') && (
          <section className="rounded-lg bg-slate-900 p-4">
            <h2 className="mb-3 text-lg font-semibold">Recent events</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="text-slate-400">
                    <th className="px-2 py-1">ID</th>
                    <th className="px-2 py-1">Source</th>
                    <th className="px-2 py-1">Type</th>
                    <th className="px-2 py-1">Value</th>
                    <th className="px-2 py-1">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEvents.slice(0, 20).map((event) => (
                    <tr key={event.id} className="border-t border-slate-800">
                      <td className="px-2 py-1">{event.id}</td>
                      <td className="px-2 py-1">{event.source_id}</td>
                      <td className="px-2 py-1">{event.event_type}</td>
                      <td className="px-2 py-1">{event.value ?? '-'}</td>
                      <td className="px-2 py-1">
                        {new Date(event.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

export default App
