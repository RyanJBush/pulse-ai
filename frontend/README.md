# Pulse AI Frontend

React + Vite dashboard for Pulse AI anomaly monitoring.

## Development

```bash
npm install
npm run dev
```

By default the UI expects the backend at:

- `http://localhost:8000`

Override with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Build

```bash
npm run build
npm run preview -- --host 0.0.0.0 --port 4173
```
