import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Header from './components/Header'
import Home from './pages/Home'
import Login from './pages/Login'
import Tasks from './pages/Tasks'
import Projects from './pages/Projects'
import Calendar from './pages/Calendar'
import Scheduler from './pages/Scheduler'
import Pomodoro from './pages/Pomodoro'
import './App.css'

const { Content } = Layout

function App() {
  return (
    <Layout className="app-layout">
      <Header />
      <Content className="app-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/scheduler" element={<Scheduler />} />
          <Route path="/pomodoro" element={<Pomodoro />} />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App