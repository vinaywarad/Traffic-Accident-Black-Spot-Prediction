import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppShell      from './components/layout/AppShell'
import ErrorBoundary from './components/ui/ErrorBoundary'
import DashboardPage   from './pages/DashboardPage'
import MapPage         from './pages/MapPage'
import AnalyticsPage   from './pages/AnalyticsPage'
import PredictionsPage from './pages/PredictionsPage'
import UploadPage      from './pages/UploadPage'
import SettingsPage    from './pages/SettingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/"            element={<ErrorBoundary><DashboardPage /></ErrorBoundary>} />
          <Route path="/map"         element={<ErrorBoundary><MapPage /></ErrorBoundary>} />
          <Route path="/analytics"   element={<ErrorBoundary><AnalyticsPage /></ErrorBoundary>} />
          <Route path="/predictions" element={<ErrorBoundary><PredictionsPage /></ErrorBoundary>} />
          <Route path="/upload"      element={<ErrorBoundary><UploadPage /></ErrorBoundary>} />
          <Route path="/settings"    element={<ErrorBoundary><SettingsPage /></ErrorBoundary>} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}
