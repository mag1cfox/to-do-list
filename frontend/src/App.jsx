import { Routes, Route } from 'react-router-dom'
import { Layout, Card } from 'antd'
import Header from './components/Header'
import Home from './pages/Home'
import Login from './pages/Login'
import './App.css'

const { Content } = Layout

// 临时占位组件，避免导入可能有问题的高级组件
const Tasks = () => (
  <Card title="任务管理" style={{ margin: '20px' }}>
    <p>任务管理功能正在开发中...</p>
  </Card>
)

const Projects = () => (
  <Card title="项目管理" style={{ margin: '20px' }}>
    <p>项目管理功能正在开发中...</p>
  </Card>
)

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
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/scheduler" element={
            <Card title="时间块调度" style={{ margin: '20px' }}>
              <p>智能时间块调度功能正在开发中...</p>
            </Card>
          } />
          <Route path="/pomodoro" element={
            <Card title="番茄钟计时器" style={{ margin: '20px' }}>
              <p>番茄钟计时器功能正在开发中...</p>
            </Card>
          } />
          <Route path="/analytics" element={
            <Card title="数据分析" style={{ margin: '20px' }}>
              <p>数据分析和报表功能正在开发中...</p>
            </Card>
          } />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App