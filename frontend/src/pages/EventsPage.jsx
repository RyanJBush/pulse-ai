import { useEffect, useMemo, useState } from 'react';
import DataTable from '../components/DataTable';
import FilterBar from '../components/FilterBar';
import { fetchEvents } from '../services/api';

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [sourceFilter, setSourceFilter] = useState('all');
  const [typeQuery, setTypeQuery] = useState('');

  useEffect(() => {
    fetchEvents().then(setEvents).catch(() => setEvents([]));
  }, []);

  const sources = useMemo(
    () => ['all', ...new Set(events.map((event) => event.source))],
    [events]
  );

  const filtered = useMemo(() => {
    return events.filter((event) => {
      const sourceMatch = sourceFilter === 'all' || event.source === sourceFilter;
      const typeMatch = event.event_type.toLowerCase().includes(typeQuery.toLowerCase());
      return sourceMatch && typeMatch;
    });
  }, [events, sourceFilter, typeQuery]);

  return (
    <section className="page">
      <header className="page-header">
        <h2>Events</h2>
        <p>Event ingestion stream with filtering for source and type.</p>
      </header>

      <FilterBar>
        <label>
          Source
          <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
            {sources.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label>
          Event Type
          <input
            value={typeQuery}
            onChange={(event) => setTypeQuery(event.target.value)}
            placeholder="cpu, latency, error..."
          />
        </label>
      </FilterBar>

      <DataTable
        columns={[
          { key: 'id', label: 'ID' },
          { key: 'source', label: 'Source' },
          { key: 'event_type', label: 'Type' },
          { key: 'value', label: 'Value' },
          { key: 'created_at', label: 'Timestamp' }
        ]}
        rows={filtered}
      />
    </section>
  );
}
