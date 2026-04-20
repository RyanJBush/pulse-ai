import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import DashboardPage from './pages/DashboardPage';
import EventsPage from './pages/EventsPage';
import AlertsPage from './pages/AlertsPage';
import MetricsPage from './pages/MetricsPage';

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/events" element={<EventsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
      </Routes>
    </AppLayout>
  );
}
