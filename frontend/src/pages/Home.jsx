import { Card, Row, Col, Statistic, Button, Space, message } from 'antd'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { taskService, pomodoroService } from '../services/api'

function Home() {
  const { isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    todayTasks: 0,
    totalTasks: 0,
    completedTasks: 0,
    completionRate: 0,
    focusTime: 0
  })

  // 获取统计数据
  const fetchStats = async () => {
    try {
      // 获取任务数据
      let tasks = []
      try {
        const taskResponse = await taskService.getTasks()
        tasks = taskResponse.tasks || []
      } catch (taskError) {
        console.warn('获取任务数据失败:', taskError)
      }

      // 获取番茄钟数据
      let pomodoroSessions = []
      try {
        const pomodoroResponse = await pomodoroService.getSessions()
        pomodoroSessions = pomodoroResponse.pomodoro_sessions || []
      } catch (pomodoroError) {
        console.warn('获取番茄钟数据失败:', pomodoroError)
      }

      // 计算统计数据
      const today = new Date().toDateString()
      const todayTasks = tasks.filter(task =>
        task.created_at && new Date(task.created_at).toDateString() === today
      ).length

      const completedTasks = tasks.filter(task => task.status === 'COMPLETED').length
      const totalTasks = tasks.length
      const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

      const totalFocusTime = pomodoroSessions
        .filter(session => session.status === 'COMPLETED')
        .reduce((total, session) => total + (session.actual_duration || session.planned_duration || 0), 0)

      setStats({
        todayTasks,
        totalTasks,
        completedTasks,
        completionRate,
        focusTime: totalFocusTime
      })
    } catch (error) {
      console.error('获取统计数据失败:', error)
      // 设置默认统计数据，防止页面崩溃
      setStats({
        todayTasks: 0,
        totalTasks: 0,
        completedTasks: 0,
        completionRate: 0,
        focusTime: 0
      })
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats()
    }
  }, [isAuthenticated])

  // 创建时间块
  const handleCreateTimeBlock = () => {
    navigate('/scheduler')
    setTimeout(() => {
      // 尝试触发时间块创建按钮
      const createButton = document.querySelector('[data-testid="create-time-block"]')
      if (createButton) {
        createButton.click()
      } else {
        message.info('请在调度页面点击"创建时间块"按钮')
      }
    }, 500)
  }

  // 添加任务
  const handleAddTask = () => {
    navigate('/tasks')
    setTimeout(() => {
      message.info('请在任务页面点击"创建任务"按钮')
    }, 500)
  }

  // 开始专注
  const handleStartFocus = async () => {
    try {
      // 检查是否有可用的任务
      const taskResponse = await taskService.getTasks()
      const tasks = taskResponse.tasks || []
      const availableTasks = tasks.filter(task =>
        task.status === 'PENDING' || task.status === 'IN_PROGRESS'
      )

      if (availableTasks.length === 0) {
        message.warning('请先创建任务才能开始专注')
        navigate('/tasks')
        return
      }

      // 导航到番茄钟页面
      navigate('/pomodoro')
      message.success('已切换到番茄钟页面，选择任务开始专注！')
    } catch (error) {
      console.error('开始专注失败:', error)
      message.error('开始专注失败，请稍后重试')
    }
  }

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1>欢迎使用时间管理系统</h1>
        <p style={{ fontSize: '16px', color: '#666' }}>
          智能推荐与自动化流程的个人时间管理工具
        </p>
      </div>

      {!isAuthenticated ? (
        <Card style={{ maxWidth: '400px', margin: '0 auto', textAlign: 'center' }}>
          <h3>开始使用</h3>
          <p style={{ marginBottom: '24px' }}>
            请先登录或注册账户来开始管理您的时间
          </p>
          <Space>
            <Link to="/login">
              <Button type="primary" size="large">
                立即登录
              </Button>
            </Link>
          </Space>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic title="今日任务" value={stats.todayTasks} suffix={`/ ${stats.totalTasks}`} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic title="完成率" value={stats.completionRate} suffix="%" />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic title="专注时间" value={stats.focusTime} suffix="分钟" />
            </Card>
          </Col>

          <Col span={24}>
            <Card
              title="快速开始"
              extra={
                <Link to="/tasks">
                  <Button type="primary">管理任务</Button>
                </Link>
              }
            >
              <p>开始规划您的时间，提高工作效率！</p>
              <Space size="large">
                <Button
                  type="default"
                  onClick={handleCreateTimeBlock}
                  icon={<span>📅</span>}
                >
                  创建时间块
                </Button>
                <Button
                  type="default"
                  onClick={handleAddTask}
                  icon={<span>📝</span>}
                >
                  添加任务
                </Button>
                <Button
                  type="primary"
                  onClick={handleStartFocus}
                  icon={<span>🎯</span>}
                >
                  开始专注
                </Button>
              </Space>
            </Card>
          </Col>

          <Col span={24}>
            <Card title="功能导航">
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={6}>
                  <Link to="/scheduler">
                    <Card
                      hoverable
                      style={{ textAlign: 'center' }}
                      bodyStyle={{ padding: '20px' }}
                    >
                      <div style={{ fontSize: '24px', marginBottom: '8px' }}>📅</div>
                      <div>时间块规划</div>
                    </Card>
                  </Link>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Link to="/tasks">
                    <Card
                      hoverable
                      style={{ textAlign: 'center' }}
                      bodyStyle={{ padding: '20px' }}
                    >
                      <div style={{ fontSize: '24px', marginBottom: '8px' }}>📋</div>
                      <div>任务管理</div>
                    </Card>
                  </Link>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Link to="/pomodoro">
                    <Card
                      hoverable
                      style={{ textAlign: 'center' }}
                      bodyStyle={{ padding: '20px' }}
                    >
                      <div style={{ fontSize: '24px', marginBottom: '8px' }}>🍅</div>
                      <div>番茄钟</div>
                    </Card>
                  </Link>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Link to="/analytics">
                    <Card
                      hoverable
                      style={{ textAlign: 'center' }}
                      bodyStyle={{ padding: '20px' }}
                    >
                      <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
                      <div>数据分析</div>
                    </Card>
                  </Link>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  )
}

export default Home