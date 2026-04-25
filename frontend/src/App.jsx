import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
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
    scoredEvents: [],
    alerts: [],
    metrics: null,
    bufferStats: null,
    error: '',
  })
  const [replayState, setReplayState] = useState({
    loading: false,
    result: null,
    error: '',
  })
  const [replayForm, setReplayForm] = useState({
    seed: 42,
    count: 60,
    interval_seconds: 15,
    inject_spike_every: 10,
    allow_out_of_order: true,
    source: 'demo-stream',
    workspace_id: 'default',
    event_type: 'latency',
    signal_type: 'latency',
    entity_id: 'entity-demo-1',
  })
  const [sourceFilter, setSourceFilter] = useState('all')

  useEffect(() => {
    let alive = true

    const refresh = async () => {
      try {
        const [events, scoredEvents, alerts, metrics, bufferStats] =
          await Promise.all([
            fetchJson('/api/v1/events?limit=100'),
            fetchJson('/api/v1/events/scored?limit=100'),
            fetchJson('/api/v1/alerts'),
            fetchJson('/api/v1/metrics/summary'),
            fetchJson('/api/v1/events/buffer/stats'),
          ])
        const [events, alerts, metrics] = await Promise.all([
          fetchJson('/api/v1/events?limit=100'),
          fetchJson('/api/v1/alerts'),
          fetchJson('/api/v1/metrics/summary'),
        ])
        if (alive) {
          setState({
            events,
            scoredEvents,
            alerts,
            metrics,
            bufferStats,
            error: '',
          })
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
    const unique = new Set(state.events.map((event) => event.source))
    return ['all', ...unique]
  }, [state.events])

  const filteredEvents = useMemo(() => {
    if (sourceFilter === 'all') {
      return state.events
    }
    return state.events.filter((event) => event.source === sourceFilter)
  }, [state.events, sourceFilter])

  const eventsByType = useMemo(() => {
    const buckets = {}
    for (const event of filteredEvents) {
      buckets[event.event_type] = (buckets[event.event_type] ?? 0) + 1
    }
    return Object.entries(buckets).map(([name, count]) => ({ name, count }))
  }, [filteredEvents])

  const alertsBySeverity = useMemo(() => {
    const buckets = { critical: 0, high: 0, medium: 0, low: 0 }
    for (const alert of state.alerts) {
      if (alert.severity in buckets) {
        buckets[alert.severity] += 1
      }
    }
    return Object.entries(buckets).map(([severity, count]) => ({
      severity,
      count,
    }))
  }, [state.alerts])

  const topAnomalies = useMemo(() => {
    return state.scoredEvents
      .filter((item) => item.score?.is_anomalous)
      .slice(0, 8)
  }, [state.scoredEvents])

  const onReplayChange = (key, value) => {
    setReplayForm((prev) => ({ ...prev, [key]: value }))
  }

  const runReplay = async () => {
    setReplayState({ loading: true, result: null, error: '' })
    try {
      const response = await fetch(`${apiBase}/api/v1/events/replay`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          ...replayForm,
          seed: Number(replayForm.seed),
          count: Number(replayForm.count),
          interval_seconds: Number(replayForm.interval_seconds),
          inject_spike_every: Number(replayForm.inject_spike_every),
        }),
      })
      if (!response.ok) {
        throw new Error(`Replay failed (${response.status})`)
      }
      const result = await response.json()
      setReplayState({ loading: false, result, error: '' })
    } catch (error) {
      setReplayState({ loading: false, result: null, error: error.message })
    }
  }

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

        {(page === 'Dashboard' || page === 'Events') && (
          <section className="rounded-lg bg-slate-900 p-4">
            <h2 className="mb-3 text-lg font-semibold">Replay control</h2>
            <div className="grid gap-3 md:grid-cols-4">
              <label className="text-sm text-slate-300">
                Count
                <input
                  type="number"
                  min={1}
                  max={1000}
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={replayForm.count}
                  onChange={(event) =>
                    onReplayChange('count', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Interval seconds
                <input
                  type="number"
                  min={1}
                  max={3600}
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={replayForm.interval_seconds}
                  onChange={(event) =>
                    onReplayChange('interval_seconds', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Spike every N
                <input
                  type="number"
                  min={0}
                  max={500}
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={replayForm.inject_spike_every}
                  onChange={(event) =>
                    onReplayChange('inject_spike_every', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Seed
                <input
                  type="number"
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={replayForm.seed}
                  onChange={(event) =>
                    onReplayChange('seed', event.target.value)
                  }
                />
              </label>
            </div>
            <label className="mt-3 inline-flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={replayForm.allow_out_of_order}
                onChange={(event) =>
                  onReplayChange('allow_out_of_order', event.target.checked)
                }
              />
              Allow out-of-order events
            </label>
            <div className="mt-3 flex items-center gap-3">
              <button
                className="rounded-md bg-cyan-500 px-3 py-1 text-sm font-medium text-slate-950 disabled:opacity-60"
                disabled={replayState.loading}
                onClick={runReplay}
              >
                {replayState.loading ? 'Running replay...' : 'Run replay'}
              </button>
              {replayState.error ? (
                <p className="text-sm text-rose-400">{replayState.error}</p>
              ) : null}
            </div>
            {replayState.result ? (
              <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Run ID</p>
                  <p className="truncate text-sm font-semibold">
                    {replayState.result.replay_run_id}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Ingested</p>
                  <p className="text-xl font-semibold">
                    {replayState.result.ingested}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Anomalies</p>
                  <p className="text-xl font-semibold">
                    {replayState.result.anomalous}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Duration (ms)</p>
                  <p className="text-xl font-semibold">
                    {replayState.result.duration_ms}
                  </p>
                </article>
              </div>
            ) : null}
          </section>
        )}

        {(page === 'Dashboard' || page === 'Metrics') && state.metrics ? (
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              [
                'Anomaly rate',
                `${(state.metrics.anomaly_rate * 100).toFixed(1)}%`,
              ],
              ['Alerts', state.metrics.alert_count],
              ['Throughput / min', state.metrics.throughput_per_minute],
              [
                'High severity anomalies',
                state.metrics.high_severity_anomalies,
              ],
            ].map(([label, value]) => (
              <article key={label} className="rounded-lg bg-slate-900 p-4">
                <p className="text-sm text-slate-400">{label}</p>
                <p className="text-2xl font-semibold">{value}</p>
              </article>
            ))}
          </section>
        ) : null}

        {(page === 'Dashboard' || page === 'Metrics') && state.bufferStats ? (
          <section className="grid gap-4 sm:grid-cols-3">
            <article className="rounded-lg bg-slate-900 p-4">
              <p className="text-sm text-slate-400">Buffer queued</p>
              <p className="text-2xl font-semibold">
                {state.bufferStats.queued}
              </p>
            </article>
            <article className="rounded-lg bg-slate-900 p-4">
              <p className="text-sm text-slate-400">Total enqueued</p>
              <p className="text-2xl font-semibold">
                {state.bufferStats.total_enqueued}
              </p>
            </article>
            <article className="rounded-lg bg-slate-900 p-4">
              <p className="text-sm text-slate-400">Total flushed</p>
              <p className="text-2xl font-semibold">
                {state.bufferStats.total_flushed}
              </p>
            </article>
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
              <h2 className="mb-3 text-lg font-semibold">Alerts by severity</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={alertsBySeverity}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="severity" stroke="#cbd5e1" />
                    <YAxis stroke="#cbd5e1" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#38bdf8" />
                  </BarChart>
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
                      <td className="px-2 py-1">{event.source}</td>
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

        {(page === 'Dashboard' || page === 'Alerts') && (
          <section className="rounded-lg bg-slate-900 p-4">
            <h2 className="mb-3 text-lg font-semibold">
              Anomaly scoring rationale
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="text-slate-400">
                    <th className="px-2 py-1">Event ID</th>
                    <th className="px-2 py-1">Entity</th>
                    <th className="px-2 py-1">Combined</th>
                    <th className="px-2 py-1">Threshold</th>
                    <th className="px-2 py-1">Detector</th>
                    <th className="px-2 py-1">Reasons</th>
                    <th className="px-2 py-1">Alert</th>
                  </tr>
                </thead>
                <tbody>
                  {topAnomalies.length === 0 ? (
                    <tr>
                      <td className="px-2 py-2 text-slate-400" colSpan={7}>
                        No anomalous scored events yet. Run a replay to generate
                        data.
                      </td>
                    </tr>
                  ) : (
                    topAnomalies.map((item) => (
                      <tr
                        key={item.event.id}
                        className="border-t border-slate-800 align-top"
                      >
                        <td className="px-2 py-1">{item.event.id}</td>
                        <td className="px-2 py-1">{item.event.entity_id}</td>
                        <td className="px-2 py-1">
                          {item.score?.combined_score}
                        </td>
                        <td className="px-2 py-1">
                          {item.score?.dynamic_threshold}
                        </td>
                        <td className="px-2 py-1">
                          {item.score?.selected_detector}
                        </td>
                        <td className="px-2 py-1">
                          {(item.score?.reason_codes ?? []).join(', ')}
                        </td>
                        <td className="px-2 py-1">{item.alert_id ?? '-'}</td>
                      </tr>
                    ))
                  )}
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
