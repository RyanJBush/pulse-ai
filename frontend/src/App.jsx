import { useCallback, useEffect, useMemo, useState } from 'react'
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

const fetchJson = async (path, init = {}) => {
  const response = await fetch(`${apiBase}${path}`, init)
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
  const [selectedEntity, setSelectedEntity] = useState('')
  const [entityDrilldown, setEntityDrilldown] = useState({
    loading: false,
    data: null,
    error: '',
  })
  const [incidents, setIncidents] = useState([])
  const [selectedAlertId, setSelectedAlertId] = useState(null)
  const [selectedAlertStatus, setSelectedAlertStatus] = useState('acknowledged')
  const [alertNoteInput, setAlertNoteInput] = useState('')
  const [alertNotes, setAlertNotes] = useState([])
  const [alertWorkflowError, setAlertWorkflowError] = useState('')
  const [selectedIncidentId, setSelectedIncidentId] = useState(null)
  const [selectedIncidentStatus, setSelectedIncidentStatus] =
    useState('investigating')
  const [incidentNoteInput, setIncidentNoteInput] = useState('')
  const [incidentNotes, setIncidentNotes] = useState([])
  const [incidentWorkflowError, setIncidentWorkflowError] = useState('')
  const [evaluationForm, setEvaluationForm] = useState({
    workspace_id: 'default',
    source: 'benchmark',
    signal_type: 'latency',
    entity_id: 'svc-eval',
    replay_count: 60,
    replay_seed: 123,
    inject_spike_every: 10,
    thresholds_text: '0.6,0.7,0.8,0.9',
  })
  const [benchmarkState, setBenchmarkState] = useState({
    loading: false,
    data: null,
    error: '',
  })
  const [thresholdState, setThresholdState] = useState({
    loading: false,
    data: null,
    error: '',
  })
  const [detectorState, setDetectorState] = useState({
    loading: false,
    data: null,
    error: '',
  })

  const refreshData = useCallback(async () => {
    try {
      const [events, scoredEvents, alerts, metrics, bufferStats, incidentRows] =
        await Promise.all([
          fetchJson('/api/v1/events?limit=100'),
          fetchJson('/api/v1/events/scored?limit=100'),
          fetchJson('/api/v1/alerts'),
          fetchJson('/api/v1/metrics/summary'),
          fetchJson('/api/v1/events/buffer/stats'),
          fetchJson('/api/v1/incidents', {
            headers: { 'x-role': 'analyst' },
          }),
        ])
      setState({
        events,
        scoredEvents,
        alerts,
        metrics,
        bufferStats,
        error: '',
      })
      setIncidents(incidentRows)
    } catch (error) {
      setState((prev) => ({ ...prev, error: error.message }))
    }
  }, [])

  useEffect(() => {
    let alive = true

    const refresh = async () => {
      if (!alive) return
      await refreshData()
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
  }, [refreshData])

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

  const entityOptions = useMemo(() => {
    return [...new Set(state.events.map((event) => event.entity_id))]
  }, [state.events])

  const selectedAlert = useMemo(() => {
    return state.alerts.find((alert) => alert.id === selectedAlertId) ?? null
  }, [selectedAlertId, state.alerts])

  const selectedIncident = useMemo(() => {
    return (
      incidents.find((incident) => incident.id === selectedIncidentId) ?? null
    )
  }, [incidents, selectedIncidentId])

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
      await refreshData()
    } catch (error) {
      setReplayState({ loading: false, result: null, error: error.message })
    }
  }

  useEffect(() => {
    if (!selectedEntity) {
      setEntityDrilldown({ loading: false, data: null, error: '' })
      return
    }
    let alive = true
    const run = async () => {
      setEntityDrilldown({ loading: true, data: null, error: '' })
      try {
        const data = await fetchJson(
          `/api/v1/metrics/entities/${selectedEntity}`
        )
        if (alive) {
          setEntityDrilldown({ loading: false, data, error: '' })
        }
      } catch (error) {
        if (alive) {
          setEntityDrilldown({
            loading: false,
            data: null,
            error: error.message,
          })
        }
      }
    }
    run()
    return () => {
      alive = false
    }
  }, [selectedEntity])

  useEffect(() => {
    if (!selectedAlertId) {
      setAlertNotes([])
      return
    }
    let alive = true
    const loadNotes = async () => {
      try {
        const notes = await fetchJson(`/api/v1/alerts/${selectedAlertId}/notes`)
        if (alive) {
          setAlertNotes(notes)
        }
      } catch {
        if (alive) {
          setAlertNotes([])
        }
      }
    }
    loadNotes()
    return () => {
      alive = false
    }
  }, [selectedAlertId])

  useEffect(() => {
    if (!selectedIncidentId) {
      setIncidentNotes([])
      return
    }
    let alive = true
    const loadNotes = async () => {
      try {
        const notes = await fetchJson(
          `/api/v1/incidents/${selectedIncidentId}/notes`,
          {
            headers: { 'x-role': 'analyst' },
          }
        )
        if (alive) {
          setIncidentNotes(notes)
        }
      } catch {
        if (alive) {
          setIncidentNotes([])
        }
      }
    }
    loadNotes()
    return () => {
      alive = false
    }
  }, [selectedIncidentId])

  const updateSelectedAlertStatus = async () => {
    if (!selectedAlertId) return
    setAlertWorkflowError('')
    try {
      await fetchJson(`/api/v1/alerts/${selectedAlertId}/status`, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          status: selectedAlertStatus,
          author: 'operator-ui',
          note: alertNoteInput || null,
        }),
      })
      if (alertNoteInput.trim()) {
        setAlertNoteInput('')
      }
      await refreshData()
      const notes = await fetchJson(`/api/v1/alerts/${selectedAlertId}/notes`)
      setAlertNotes(notes)
    } catch (error) {
      setAlertWorkflowError(error.message)
    }
  }

  const addAlertNote = async () => {
    if (!selectedAlertId || !alertNoteInput.trim()) return
    setAlertWorkflowError('')
    try {
      await fetchJson(`/api/v1/alerts/${selectedAlertId}/notes`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          author: 'analyst-ui',
          note: alertNoteInput.trim(),
        }),
      })
      setAlertNoteInput('')
      const notes = await fetchJson(`/api/v1/alerts/${selectedAlertId}/notes`)
      setAlertNotes(notes)
    } catch (error) {
      setAlertWorkflowError(error.message)
    }
  }

  const updateSelectedIncident = async () => {
    if (!selectedIncidentId) return
    setIncidentWorkflowError('')
    try {
      await fetchJson(`/api/v1/incidents/${selectedIncidentId}`, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json', 'x-role': 'operator' },
        body: JSON.stringify({
          status: selectedIncidentStatus,
          actor: 'operator-ui',
          note: incidentNoteInput || null,
        }),
      })
      if (incidentNoteInput.trim()) {
        setIncidentNoteInput('')
      }
      await refreshData()
      const notes = await fetchJson(
        `/api/v1/incidents/${selectedIncidentId}/notes`,
        {
          headers: { 'x-role': 'analyst' },
        }
      )
      setIncidentNotes(notes)
    } catch (error) {
      setIncidentWorkflowError(error.message)
    }
  }

  const addIncidentNote = async () => {
    if (!selectedIncidentId || !incidentNoteInput.trim()) return
    setIncidentWorkflowError('')
    try {
      await fetchJson(`/api/v1/incidents/${selectedIncidentId}/notes`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-role': 'analyst' },
        body: JSON.stringify({
          author: 'analyst-ui',
          note: incidentNoteInput.trim(),
        }),
      })
      setIncidentNoteInput('')
      const notes = await fetchJson(
        `/api/v1/incidents/${selectedIncidentId}/notes`,
        {
          headers: { 'x-role': 'analyst' },
        }
      )
      setIncidentNotes(notes)
    } catch (error) {
      setIncidentWorkflowError(error.message)
    }
  }

  const setEvaluationField = (key, value) => {
    setEvaluationForm((prev) => ({ ...prev, [key]: value }))
  }

  const parseThresholds = () => {
    return evaluationForm.thresholds_text
      .split(',')
      .map((item) => Number(item.trim()))
      .filter((value) => Number.isFinite(value) && value > 0 && value <= 1)
  }

  const evaluationSlicePayload = () => ({
    workspace_id: evaluationForm.workspace_id,
    source: evaluationForm.source,
    signal_type: evaluationForm.signal_type,
    entity_id: evaluationForm.entity_id,
  })

  const runSeededBenchmark = async () => {
    setBenchmarkState({ loading: true, data: null, error: '' })
    try {
      const data = await fetchJson('/api/v1/evaluation/seeded-benchmark', {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-role': 'analyst' },
        body: JSON.stringify({
          benchmark_name: 'phase4-ui-benchmark',
          replay: {
            ...evaluationSlicePayload(),
            seed: Number(evaluationForm.replay_seed),
            count: Number(evaluationForm.replay_count),
            event_type: evaluationForm.signal_type,
            inject_spike_every: Number(evaluationForm.inject_spike_every),
          },
        }),
      })
      setBenchmarkState({ loading: false, data, error: '' })
      await refreshData()
    } catch (error) {
      setBenchmarkState({ loading: false, data: null, error: error.message })
    }
  }

  const runThresholdTuning = async () => {
    setThresholdState({ loading: true, data: null, error: '' })
    try {
      const data = await fetchJson('/api/v1/evaluation/threshold-tuning', {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-role': 'analyst' },
        body: JSON.stringify({
          ...evaluationSlicePayload(),
          thresholds: parseThresholds(),
        }),
      })
      setThresholdState({ loading: false, data, error: '' })
    } catch (error) {
      setThresholdState({ loading: false, data: null, error: error.message })
    }
  }

  const runDetectorComparison = async () => {
    setDetectorState({ loading: true, data: null, error: '' })
    try {
      const data = await fetchJson('/api/v1/evaluation/detector-comparison', {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-role': 'analyst' },
        body: JSON.stringify(evaluationSlicePayload()),
      })
      setDetectorState({ loading: false, data, error: '' })
    } catch (error) {
      setDetectorState({ loading: false, data: null, error: error.message })
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

        {(page === 'Dashboard' || page === 'Metrics') && (
          <section className="rounded-lg bg-slate-900 p-4">
            <h2 className="mb-3 text-lg font-semibold">Entity drill-down</h2>
            <div className="flex flex-wrap items-center gap-3">
              <select
                className="rounded-md bg-slate-800 px-2 py-1 text-sm"
                value={selectedEntity}
                onChange={(event) => setSelectedEntity(event.target.value)}
              >
                <option value="">Select entity…</option>
                {entityOptions.map((entityId) => (
                  <option key={entityId} value={entityId}>
                    {entityId}
                  </option>
                ))}
              </select>
              {entityDrilldown.loading ? (
                <p className="text-sm text-slate-400">
                  Loading entity metrics…
                </p>
              ) : null}
              {entityDrilldown.error ? (
                <p className="text-sm text-rose-400">{entityDrilldown.error}</p>
              ) : null}
            </div>
            {entityDrilldown.data ? (
              <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Total events</p>
                  <p className="text-xl font-semibold">
                    {entityDrilldown.data.total_events}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Anomalous events</p>
                  <p className="text-xl font-semibold">
                    {entityDrilldown.data.anomalous_events}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Active alerts</p>
                  <p className="text-xl font-semibold">
                    {entityDrilldown.data.active_alerts}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Avg score</p>
                  <p className="text-xl font-semibold">
                    {entityDrilldown.data.avg_combined_score}
                  </p>
                </article>
              </div>
            ) : null}
          </section>
        )}

        {page === 'Metrics' && (
          <section className="rounded-lg bg-slate-900 p-4">
            <h2 className="mb-3 text-lg font-semibold">
              Detector evaluation lab
            </h2>
            <div className="grid gap-3 md:grid-cols-4">
              <label className="text-sm text-slate-300">
                Workspace
                <input
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.workspace_id}
                  onChange={(event) =>
                    setEvaluationField('workspace_id', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Source
                <input
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.source}
                  onChange={(event) =>
                    setEvaluationField('source', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Signal type
                <input
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.signal_type}
                  onChange={(event) =>
                    setEvaluationField('signal_type', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Entity
                <input
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.entity_id}
                  onChange={(event) =>
                    setEvaluationField('entity_id', event.target.value)
                  }
                />
              </label>
            </div>
            <div className="mt-3 grid gap-3 md:grid-cols-4">
              <label className="text-sm text-slate-300">
                Replay count
                <input
                  type="number"
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.replay_count}
                  onChange={(event) =>
                    setEvaluationField('replay_count', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Replay seed
                <input
                  type="number"
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.replay_seed}
                  onChange={(event) =>
                    setEvaluationField('replay_seed', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Spike every N
                <input
                  type="number"
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.inject_spike_every}
                  onChange={(event) =>
                    setEvaluationField('inject_spike_every', event.target.value)
                  }
                />
              </label>
              <label className="text-sm text-slate-300">
                Thresholds (csv)
                <input
                  className="mt-1 w-full rounded-md bg-slate-800 px-2 py-1"
                  value={evaluationForm.thresholds_text}
                  onChange={(event) =>
                    setEvaluationField('thresholds_text', event.target.value)
                  }
                />
              </label>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                className="rounded-md bg-cyan-500 px-3 py-1 text-sm font-medium text-slate-950"
                onClick={runSeededBenchmark}
              >
                {benchmarkState.loading
                  ? 'Running benchmark…'
                  : 'Run benchmark'}
              </button>
              <button
                className="rounded-md bg-indigo-500 px-3 py-1 text-sm font-medium text-white"
                onClick={runThresholdTuning}
              >
                {thresholdState.loading ? 'Tuning…' : 'Tune thresholds'}
              </button>
              <button
                className="rounded-md bg-emerald-500 px-3 py-1 text-sm font-medium text-slate-950"
                onClick={runDetectorComparison}
              >
                {detectorState.loading ? 'Comparing…' : 'Compare detectors'}
              </button>
            </div>

            {benchmarkState.error ? (
              <p className="mt-2 text-sm text-rose-400">
                {benchmarkState.error}
              </p>
            ) : null}
            {benchmarkState.data ? (
              <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Precision</p>
                  <p className="text-xl font-semibold">
                    {benchmarkState.data.precision}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Recall</p>
                  <p className="text-xl font-semibold">
                    {benchmarkState.data.recall}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">False positive rate</p>
                  <p className="text-xl font-semibold">
                    {benchmarkState.data.false_positive_rate}
                  </p>
                </article>
                <article className="rounded-md bg-slate-800 p-3">
                  <p className="text-xs text-slate-400">Mean latency (s)</p>
                  <p className="text-xl font-semibold">
                    {benchmarkState.data.mean_alert_latency_seconds}
                  </p>
                </article>
              </div>
            ) : null}

            {(thresholdState.error || thresholdState.data) && (
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                <article className="rounded-md bg-slate-800 p-3">
                  <h3 className="mb-2 text-sm font-semibold">
                    Threshold tuning curve
                  </h3>
                  {thresholdState.error ? (
                    <p className="text-sm text-rose-400">
                      {thresholdState.error}
                    </p>
                  ) : (
                    <div className="h-56">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={thresholdState.data?.points ?? []}>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#334155"
                          />
                          <XAxis dataKey="threshold" stroke="#cbd5e1" />
                          <YAxis stroke="#cbd5e1" />
                          <Tooltip />
                          <Line
                            type="monotone"
                            dataKey="precision"
                            stroke="#22d3ee"
                          />
                          <Line
                            type="monotone"
                            dataKey="recall"
                            stroke="#f97316"
                          />
                          <Line
                            type="monotone"
                            dataKey="false_positive_rate"
                            stroke="#ef4444"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                  {thresholdState.data?.recommended_threshold != null ? (
                    <p className="mt-2 text-sm text-slate-300">
                      Recommended threshold:{' '}
                      <span className="font-semibold">
                        {thresholdState.data.recommended_threshold}
                      </span>
                    </p>
                  ) : null}
                </article>

                <article className="rounded-md bg-slate-800 p-3">
                  <h3 className="mb-2 text-sm font-semibold">
                    Detector comparison
                  </h3>
                  {detectorState.error ? (
                    <p className="text-sm text-rose-400">
                      {detectorState.error}
                    </p>
                  ) : (
                    <div className="h-56">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={detectorState.data?.detectors ?? []}>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#334155"
                          />
                          <XAxis dataKey="detector" stroke="#cbd5e1" />
                          <YAxis stroke="#cbd5e1" />
                          <Tooltip />
                          <Bar dataKey="true_positive_rate" fill="#22c55e" />
                          <Bar dataKey="false_positive_rate" fill="#ef4444" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </article>
              </div>
            )}
          </section>
        )}

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

        {page === 'Alerts' && (
          <section className="grid gap-4 lg:grid-cols-2">
            <article className="rounded-lg bg-slate-900 p-4">
              <h2 className="mb-3 text-lg font-semibold">Alert workflow</h2>
              <div className="space-y-3">
                <select
                  className="w-full rounded-md bg-slate-800 px-2 py-1 text-sm"
                  value={selectedAlertId ?? ''}
                  onChange={(event) =>
                    setSelectedAlertId(
                      event.target.value ? Number(event.target.value) : null
                    )
                  }
                >
                  <option value="">Select alert…</option>
                  {state.alerts.map((alert) => (
                    <option key={alert.id} value={alert.id}>
                      #{alert.id} {alert.severity} {alert.status}
                    </option>
                  ))}
                </select>
                {selectedAlert ? (
                  <div className="rounded-md bg-slate-800 p-3 text-sm">
                    <p>
                      <span className="text-slate-400">Message:</span>{' '}
                      {selectedAlert.message}
                    </p>
                    <p>
                      <span className="text-slate-400">Current status:</span>{' '}
                      {selectedAlert.status}
                    </p>
                  </div>
                ) : null}
                <div className="grid gap-2 sm:grid-cols-2">
                  <select
                    className="rounded-md bg-slate-800 px-2 py-1 text-sm"
                    value={selectedAlertStatus}
                    onChange={(event) =>
                      setSelectedAlertStatus(event.target.value)
                    }
                  >
                    <option value="acknowledged">acknowledged</option>
                    <option value="investigating">investigating</option>
                    <option value="resolved">resolved</option>
                    <option value="suppressed">suppressed</option>
                  </select>
                  <button
                    className="rounded-md bg-cyan-500 px-3 py-1 text-sm font-medium text-slate-950"
                    onClick={updateSelectedAlertStatus}
                  >
                    Update status
                  </button>
                </div>
                <textarea
                  rows={3}
                  className="w-full rounded-md bg-slate-800 px-2 py-1 text-sm"
                  placeholder="Add workflow note..."
                  value={alertNoteInput}
                  onChange={(event) => setAlertNoteInput(event.target.value)}
                />
                <button
                  className="rounded-md bg-slate-700 px-3 py-1 text-sm"
                  onClick={addAlertNote}
                >
                  Add note
                </button>
                {alertWorkflowError ? (
                  <p className="text-sm text-rose-400">{alertWorkflowError}</p>
                ) : null}
                <div className="max-h-40 space-y-2 overflow-auto rounded-md bg-slate-950/40 p-2">
                  {alertNotes.length === 0 ? (
                    <p className="text-sm text-slate-500">No notes yet.</p>
                  ) : (
                    alertNotes.map((note) => (
                      <p key={note.id} className="text-sm">
                        <span className="text-slate-400">{note.author}:</span>{' '}
                        {note.note}
                      </p>
                    ))
                  )}
                </div>
              </div>
            </article>

            <article className="rounded-lg bg-slate-900 p-4">
              <h2 className="mb-3 text-lg font-semibold">Incident workflow</h2>
              <div className="space-y-3">
                <select
                  className="w-full rounded-md bg-slate-800 px-2 py-1 text-sm"
                  value={selectedIncidentId ?? ''}
                  onChange={(event) =>
                    setSelectedIncidentId(
                      event.target.value ? Number(event.target.value) : null
                    )
                  }
                >
                  <option value="">Select incident…</option>
                  {incidents.map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      #{incident.id} {incident.group_key} ({incident.status})
                    </option>
                  ))}
                </select>
                {selectedIncident ? (
                  <div className="rounded-md bg-slate-800 p-3 text-sm">
                    <p>
                      <span className="text-slate-400">Title:</span>{' '}
                      {selectedIncident.title}
                    </p>
                    <p>
                      <span className="text-slate-400">Current status:</span>{' '}
                      {selectedIncident.status}
                    </p>
                  </div>
                ) : null}
                <div className="grid gap-2 sm:grid-cols-2">
                  <select
                    className="rounded-md bg-slate-800 px-2 py-1 text-sm"
                    value={selectedIncidentStatus}
                    onChange={(event) =>
                      setSelectedIncidentStatus(event.target.value)
                    }
                  >
                    <option value="investigating">investigating</option>
                    <option value="resolved">resolved</option>
                    <option value="suppressed">suppressed</option>
                  </select>
                  <button
                    className="rounded-md bg-cyan-500 px-3 py-1 text-sm font-medium text-slate-950"
                    onClick={updateSelectedIncident}
                  >
                    Update incident
                  </button>
                </div>
                <textarea
                  rows={3}
                  className="w-full rounded-md bg-slate-800 px-2 py-1 text-sm"
                  placeholder="Add incident note..."
                  value={incidentNoteInput}
                  onChange={(event) => setIncidentNoteInput(event.target.value)}
                />
                <button
                  className="rounded-md bg-slate-700 px-3 py-1 text-sm"
                  onClick={addIncidentNote}
                >
                  Add incident note
                </button>
                {incidentWorkflowError ? (
                  <p className="text-sm text-rose-400">
                    {incidentWorkflowError}
                  </p>
                ) : null}
                <div className="max-h-40 space-y-2 overflow-auto rounded-md bg-slate-950/40 p-2">
                  {incidentNotes.length === 0 ? (
                    <p className="text-sm text-slate-500">
                      No incident notes yet.
                    </p>
                  ) : (
                    incidentNotes.map((note) => (
                      <p key={note.id} className="text-sm">
                        <span className="text-slate-400">{note.author}:</span>{' '}
                        {note.note}
                      </p>
                    ))
                  )}
                </div>
              </div>
            </article>
          </section>
        )}
      </div>
    </div>
  )
}

export default App
