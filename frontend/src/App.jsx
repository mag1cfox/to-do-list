import { Routes, Route } from 'react-router-dom'
import { Layout, Card } from 'antd'
import Header from './components/Header'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Tasks from './pages/Tasks'
import Projects from './pages/Projects'
import Scheduler from './pages/Scheduler'
import TimeBlockScheduler from './components/TimeBlockScheduler'
import Pomodoro from './pages/Pomodoro'
import Analytics from './pages/Analytics'
import IntelligentScheduling from './pages/IntelligentScheduling'
import TimeBlockAnalytics from './pages/TimeBlockAnalytics'
import DebugPage from './DebugPage'
import './App.css'

const { Content } = Layout

const Calendar = () => (
  <Card title="日历视图" style={{ margin: '20px' }}>
    <p>日历视图功能正在开发中...</p>
  </Card>
)

const Settings = () => (
  <Card title="系统设置" style={{ margin: '20px' }}>
    <p>系统设置功能正在开发中...</p>
  </Card>
)

const Profile = () => (
  <Card title="个人资料" style={{ margin: '20px' }}>
    <p>个人资料管理功能正在开发中...</p>
  </Card>
)

function App() {
  return (
    <Layout className="app-layout">
      <Header />
      <Content className="app-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/test" element={<DebugPage />} />
          <Route path="/tasks" element={
            <ProtectedRoute>
              <Tasks />
            </ProtectedRoute>
          } />
          <Route path="/projects" element={
            <ProtectedRoute>
              <Projects />
            </ProtectedRoute>
          } />
          <Route path="/calendar" element={
            <ProtectedRoute>
              <Calendar />
            </ProtectedRoute>
          } />
          <Route path="/scheduler" element={
            <ProtectedRoute>
              <TimeBlockScheduler />
            </ProtectedRoute>
          } />
          <Route path="/scheduler-templates" element={
            <ProtectedRoute>
              <Scheduler />
            </ProtectedRoute>
          } />
          <Route path="/pomodoro" element={
            <ProtectedRoute>
              <Pomodoro />
            </ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          } />
          <Route path="/timeblock-analytics" element={
            <ProtectedRoute>
              <TimeBlockAnalytics />
            </ProtectedRoute>
          } />
          <Route path="/intelligent-scheduling" element={
            <ProtectedRoute>
              <IntelligentScheduling />
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App