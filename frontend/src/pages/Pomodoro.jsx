import React, { useState, useEffect, useRef } from 'react'
import {
  Card,
  Button,
  Select,
  Progress,
  Typography,
  Space,
  Modal,
  Form,
  Input,
  message,
  Row,
  Col,
  Statistic,
  Tag,
  List,
  Avatar,
  Timeline,
  Switch,
  Empty
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  FireOutlined,
  SettingOutlined,
  HistoryOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { pomodoroService, taskService } from '../services/api'
import { useAuthStore } from '../stores/authStore'

const { Title, Text } = Typography
const { Option } = Select

function Pomodoro() {
  const { isAuthenticated } = useAuthStore()

  // 如果用户未登录，显示提示信息
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Empty
          description="请先登录以使用番茄钟功能"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    )
  }

  const [tasks, setTasks] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)
  const [activeSession, setActiveSession] = useState(null)
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [timeLeft, setTimeLeft] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [settingsModalVisible, setSettingsModalVisible] = useState(false)
  const [historyModalVisible, setHistoryModalVisible] = useState(false)
  const [interruptionModalVisible, setInterruptionModalVisible] = useState(false)
  const [completionModalVisible, setCompletionModalVisible] = useState(false)
  const [interruptionReason, setInterruptionReason] = useState('')
  const [completionSummary, setCompletionSummary] = useState('')

  const [settings, setSettings] = useState({
    duration: 25,
    shortBreak: 5,
    longBreak: 15,
    autoStartBreak: false,
    autoStartPomodoro: false,
    soundEnabled: true
  })

  const timerRef = useRef(null)

  // 获取任务列表
  const fetchTasks = async () => {
    try {
      const response = await taskService.getTasks({ status: 'PENDING,IN_PROGRESS' })
      setTasks(response.tasks || [])
    } catch (error) {
      message.error('获取任务列表失败: ' + (error.error || error.message))
    }
  }

  // 获取会话列表
  const fetchSessions = async () => {
    try {
      const response = await pomodoroService.getSessions()
      setSessions(response.pomodoro_sessions || [])
    } catch (error) {
      message.error('获取会话列表失败: ' + (error.error || error.message))
    }
  }

  // 获取活跃会话
  const fetchActiveSession = async () => {
    try {
      const response = await pomodoroService.getActiveSession()
      if (response.active_session) {
        setActiveSession(response.active_session)
        setIsRunning(true)
        startTimer(response.active_session.remaining_time || settings.duration * 60)
        // 查找对应的任务
        const task = tasks.find(t => t.id === response.active_session.task_id)
        setSelectedTask(task)
      } else {
        setActiveSession(null)
        setIsRunning(false)
      }
    } catch (error) {
      // 没有活跃会话是正常情况
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks()
      fetchSessions()
      fetchActiveSession()

      // 每隔5秒检查一次活跃会话状态
      const interval = setInterval(fetchActiveSession, 5000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // 启动计时器
  const startTimer = (initialTime = settings.duration * 60) => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }

    setTimeLeft(initialTime)
    setIsRunning(true)

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current)
          setIsRunning(false)
          // 自动显示完成模态框
          setCompletionModalVisible(true)
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }

  // 停止计时器
  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }
    setIsRunning(false)
  }

  // 开始番茄钟
  const startPomodoro = async () => {
    if (!selectedTask) {
      message.warning('请先选择一个任务')
      return
    }

    setLoading(true)
    try {
      // 创建会话
      const response = await pomodoroService.createSession({
        task_id: selectedTask.id,
        planned_duration: settings.duration,
        session_type: 'FOCUS'
      })

      const session = response.pomodoro_session

      // 开始会话
      await pomodoroService.startSession(session.id)

      setActiveSession(session)
      setIsRunning(true)
      startTimer(settings.duration * 60)

      message.success('番茄钟已开始！')
    } catch (error) {
      message.error('开始番茄钟失败: ' + (error.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 暂停番茄钟
  const pausePomodoro = async () => {
    stopTimer()
    message.info('番茄钟已暂停')
  }

  // 继续番茄钟
  const resumePomodoro = () => {
    if (activeSession) {
      startTimer(timeLeft)
      setIsRunning(true)
      message.info('番茄钟已继续')
    }
  }

  // 完成番茄钟
  const completePomodoro = async () => {
    if (!activeSession) return

    setLoading(true)
    try {
      await pomodoroService.completeSession(activeSession.id, completionSummary || '番茄钟完成')

      setActiveSession(null)
      stopTimer()
      setTimeLeft(0)
      setCompletionModalVisible(false)
      setCompletionSummary('')

      fetchSessions()
      message.success('番茄钟已完成！')

      // 自动开始休息时间
      if (settings.autoStartBreak) {
        startBreak()
      }
    } catch (error) {
      message.error('完成番茄钟失败: ' + (error.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 中断番茄钟
  const interruptPomodoro = async () => {
    if (!activeSession) return

    setLoading(true)
    try {
      await pomodoroService.interruptSession(activeSession.id, interruptionReason || '手动中断')

      setActiveSession(null)
      stopTimer()
      setTimeLeft(0)
      setInterruptionModalVisible(false)
      setInterruptionReason('')

      fetchSessions()
      message.warning('番茄钟已中断')
    } catch (error) {
      message.error('中断番茄钟失败: ' + (error.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 开始休息
  const startBreak = () => {
    // 这里可以实现休息时间逻辑
    message.info('休息时间功能待实现')
  }

  // 格式化时间显示
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // 计算进度百分比
  const getProgressPercent = () => {
    if (!activeSession) return 0
    const total = settings.duration * 60
    return Math.max(0, Math.min(100, ((total - timeLeft) / total) * 100))
  }

  // 今日统计
  const getTodayStats = () => {
    const today = dayjs().format('YYYY-MM-DD')
    const todaySessions = sessions.filter(session =>
      dayjs(session.created_at).format('YYYY-MM-DD') === today
    )

    const completed = todaySessions.filter(s => s.status === 'COMPLETED').length
    const interrupted = todaySessions.filter(s => s.status === 'INTERRUPTED').length
    const totalMinutes = todaySessions.reduce((sum, s) => sum + (s.actual_duration || 0), 0)

    return { completed, interrupted, totalMinutes }
  }

  const stats = getTodayStats()

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            番茄钟计时器
          </Title>
          <Text type="secondary">
            专注工作，提高效率
          </Text>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<HistoryOutlined />}
              onClick={() => setHistoryModalVisible(true)}
            >
              历史记录
            </Button>
            <Button
              icon={<SettingOutlined />}
              onClick={() => setSettingsModalVisible(true)}
            >
              设置
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日完成"
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日中断"
              value={stats.interrupted}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="专注时长"
              value={stats.totalMinutes}
              suffix="分钟"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        </Row>

      {/* 主要内容区域 */}
      <Row gutter={16}>
        {/* 左侧：任务选择和设置 */}
        <Col span={8}>
          <Card title="选择任务" style={{ marginBottom: '16px' }}>
            <Select
              style={{ width: '100%', marginBottom: '16px' }}
              placeholder="选择要专注的任务"
              value={selectedTask?.id}
              onChange={(value) => {
                const task = tasks.find(t => t.id === value)
                setSelectedTask(task)
              }}
              disabled={isRunning}
            >
              {tasks.map(task => (
                <Option key={task.id} value={task.id}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar size="small" style={{ backgroundColor: '#1890ff', marginRight: '8px' }}>
                      {task.title.charAt(0).toUpperCase()}
                    </Avatar>
                    <div>
                      <div>{task.title}</div>
                      {task.description && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {task.description}
                        </Text>
                      )}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>

            {selectedTask && (
              <div style={{ padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
                <Title level={5}>{selectedTask.title}</Title>
                {selectedTask.description && (
                  <Text>{selectedTask.description}</Text>
                )}
                <div style={{ marginTop: '8px' }}>
                  <Tag color="blue">
                    预估: {selectedTask.estimated_pomodoros || 1} 个番茄钟
                  </Tag>
                </div>
              </div>
            )}
          </Card>

          <Card title="计时器设置">
            <Form layout="vertical">
              <Form.Item label="番茄钟时长">
                <Input
                  type="number"
                  value={settings.duration}
                  onChange={(e) => setSettings({...settings, duration: parseInt(e.target.value) || 25})}
                  min={1}
                  max={60}
                  suffix="分钟"
                  disabled={isRunning}
                />
              </Form.Item>
              <Form.Item label="短暂休息">
                <Input
                  type="number"
                  value={settings.shortBreak}
                  onChange={(e) => setSettings({...settings, shortBreak: parseInt(e.target.value) || 5})}
                  min={1}
                  max={15}
                  suffix="分钟"
                  disabled={isRunning}
                />
              </Form.Item>
              <Form.Item label="长时间休息">
                <Input
                  type="number"
                  value={settings.longBreak}
                  onChange={(e) => setSettings({...settings, longBreak: parseInt(e.target.value) || 15})}
                  min={10}
                  max={30}
                  suffix="分钟"
                  disabled={isRunning}
                />
              </Form.Item>
            </Form>
          </Card>
        </Col>

        {/* 右侧：计时器显示 */}
        <Col span={16}>
          <Card style={{ textAlign: 'center' }}>
            {!activeSession ? (
              <div style={{ padding: '40px' }}>
                <Title level={3} style={{ color: '#666' }}>
                  准备开始专注
                </Title>
                <Text type="secondary">
                  选择一个任务，然后点击开始按钮
                </Text>
                <div style={{ marginTop: '24px' }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<PlayCircleOutlined />}
                    onClick={startPomodoro}
                    disabled={!selectedTask}
                    loading={loading}
                  >
                    开始番茄钟
                  </Button>
                </div>
              </div>
            ) : (
              <div style={{ padding: '40px' }}>
                <div style={{ fontSize: '72px', fontWeight: 'bold', color: '#1890ff', marginBottom: '16px' }}>
                  {formatTime(timeLeft)}
                </div>
                <Progress
                  percent={getProgressPercent()}
                  status={isRunning ? 'active' : 'normal'}
                  strokeColor={{
                    '0%': '#1890ff',
                    '100%': '#52c41a'
                  }}
                  style={{ marginBottom: '24px' }}
                />
                <Title level={4} style={{ marginBottom: '24px' }}>
                  {activeSession.status === 'IN_PROGRESS' ? '专注中...' : '已暂停'}
                </Title>

                <Space size="large">
                  {!isRunning ? (
                    <Button
                      type="primary"
                      size="large"
                      icon={<PlayCircleOutlined />}
                      onClick={resumePomodoro}
                      disabled={loading}
                    >
                      继续
                    </Button>
                  ) : (
                    <Button
                      size="large"
                      icon={<PauseCircleOutlined />}
                      onClick={pausePomododoro}
                    >
                      暂停
                    </Button>
                  )}

                  <Button
                    danger
                    size="large"
                    icon={<CloseCircleOutlined />}
                    onClick={() => setInterruptionModalVisible(true)}
                  >
                    中断
                  </Button>

                  {timeLeft === 0 && (
                    <Button
                      type="primary"
                      size="large"
                      icon={<CheckCircleOutlined />}
                      onClick={() => setCompletionModalVisible(true)}
                    >
                      完成
                    </Button>
                  )}
                </Space>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 设置模态框 */}
      <Modal
        title="番茄钟设置"
        open={settingsModalVisible}
        onCancel={() => setSettingsModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical">
          <Form.Item label="自动开始休息">
            <Switch
              checked={settings.autoStartBreak}
              onChange={(checked) => setSettings({...settings, autoStartBreak: checked})}
            />
          </Form.Item>
          <Form.Item label="自动开始下一个番茄钟">
            <Switch
              checked={settings.autoStartPomodoro}
              onChange={(checked) => setSettings({...settings, autoStartPomodoro: checked})}
            />
          </Form.Item>
          <Form.Item label="启用声音提醒">
            <Switch
              checked={settings.soundEnabled}
              onChange={(checked) => setSettings({...settings, soundEnabled: checked})}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 中断原因模态框 */}
      <Modal
        title="中断原因"
        open={interruptionModalVisible}
        onCancel={() => setInterruptionModalVisible(false)}
        onOk={interruptPomodoro}
        okText="确认中断"
        cancelText="取消"
      >
        <Input.TextArea
          placeholder="请输入中断原因（可选）"
          value={interruptionReason}
          onChange={(e) => setInterruptionReason(e.target.value)}
          rows={4}
        />
      </Modal>

      {/* 完成总结模态框 */}
      <Modal
        title="完成总结"
        open={completionModalVisible}
        onCancel={() => setCompletionModalVisible(false)}
        onOk={completePomodoro}
        okText="确认完成"
        cancelText="稍后总结"
      >
        <Input.TextArea
          placeholder="请输入本次番茄钟的完成总结（可选）"
          value={completionSummary}
          onChange={(e) => setCompletionSummary(e.target.value)}
          rows={4}
        />
      </Modal>

      {/* 历史记录模态框 */}
      <Modal
        title="历史记录"
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={null}
        width={800}
      >
        <List
          dataSource={sessions}
          renderItem={(session) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <Avatar
                    style={{
                      backgroundColor: session.status === 'COMPLETED' ? '#52c41a' :
                                      session.status === 'INTERRUPTED' ? '#ff4d4f' : '#1890ff'
                    }}
                  >
                    {session.status === 'COMPLETED' ? '✓' :
                     session.status === 'INTERRUPTED' ? '✗' : '○'}
                  </Avatar>
                }
                title={
                  <div>
                    <div>番茄钟会话 #{session.id}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {dayjs(session.created_at).format('YYYY-MM-DD HH:mm')}
                    </div>
                  </div>
                }
                description={
                  <div>
                    <div>时长: {session.actual_duration || 0} 分钟</div>
                    <div>状态: {
                      session.status === 'COMPLETED' ? '已完成' :
                      session.status === 'INTERRUPTED' ? '已中断' : '计划中'
                    }</div>
                    {session.completion_summary && (
                      <div style={{ fontStyle: 'italic', marginTop: '4px' }}>
                        总结: {session.completion_summary}
                      </div>
                    )}
                    {session.interruption_reason && (
                      <div style={{ fontStyle: 'italic', marginTop: '4px', color: '#ff4d4f' }}>
                        中断原因: {session.interruption_reason}
                      </div>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  )
}

export default Pomodoro