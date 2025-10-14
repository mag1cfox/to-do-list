import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Header from './components/Header'
import Home from './pages/Home'
import Login from './pages/Login'
import Tasks from './pages/Tasks'
import Projects from './pages/Projects'
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
        </Routes>
      </Content>
    </Layout>
  )
}

export default App