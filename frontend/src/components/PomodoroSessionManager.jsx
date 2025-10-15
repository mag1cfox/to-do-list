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
  Tooltip,
  Badge,
  Alert,
  Divider
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  StopOutlined,
  RotateRightOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
import api from '../services/api'

dayjs.extend(duration)

const { Title, Text } = Typography
const { Option } = Select
const { TextArea } = Input

/**
 * 番茄钟会话管理组件
 * 专门负责番茄钟会话的创建、启动、暂停、完成、中断和删除等核心管理功能
 */
const PomodoroSessionManager = ({ selectedTask = null, onSessionUpdate = null }) => {
  // 状态管理
  const [tasks, setTasks] = useState([])
  const [currentTask, setCurrentTask] = useState(selectedTask)
  const [activeSession, setActiveSession] = useState(null)
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [timeLeft, setTimeLeft] = useState(0)
  const [isRunning, setIsRunning] = useState(false)

  // 模态框状态
  const [interruptionModalVisible, setInterruptionModalVisible] = useState(false)
  const [completionModalVisible, setCompletionModalVisible] = useState(false)
  const [deleteModalVisible, setDeleteModalVisible] = useState(false)
  const [selectedSessionId, setSelectedSessionId] = useState(null)

  // 表单数据
  const [interruptionReason, setInterruptionReason] = useState('')
  const [completionSummary, setCompletionSummary] = useState('')

  // 配置
  const [sessionSettings, setSessionSettings] = useState({
    focusDuration: 25,      // 专注时长（分钟）
    breakDuration: 5,       // 休息时长（分钟）
    longBreakDuration: 15,  // 长休息时长（分钟）
    longBreakInterval: 4    // 长休息间隔（几个专注期后）
  })

  // 统计数据
  const [todayStats, setTodayStats] = useState({
    completedSessions: 0,
    interruptedSessions: 0,
    totalFocusTime: 0,
    currentStreak: 0
  })

  const timerRef = useRef(null)
  const intervalRef = useRef(null)

  // 获取任务列表
  const fetchTasks = async () => {
    try {
      const response = await api.get('/tasks')
      setTasks(response.data || [])
    } catch (error) {
      console.error('获取任务列表失败:', error)
      message.error('获取任务列表失败')
    }
  }

  // 获取会话列表
  const fetchSessions = async () => {
    try {
      const response = await api.get('/pomodoro-sessions')
      setSessions(response.data?.pomodoro_sessions || [])
      calculateTodayStats(response.data?.pomodoro_sessions || [])
    } catch (error) {
      console.error('获取会话列表失败:', error)
      message.error('获取会话列表失败')
    }
  }

  // 获取活跃会话
  const fetchActiveSession = async () => {
    try {
      const response = await api.get('/pomodoro-sessions/active')
      if (response.data?.active_session) {
        const session = response.data.active_session
        setActiveSession(session)
        setIsRunning(true)
        startTimer(session.remaining_time || session.planned_duration * 60)

        // 如果有指定任务且会话任务不匹配，更新当前任务
        if (selectedTask && session.task_id !== selectedTask.id) {
          setCurrentTask(null)
        }
      } else {
        setActiveSession(null)
        setIsRunning(false)
        stopTimer()
      }
    } catch (error) {
      console.error('获取活跃会话失败:', error)
    }
  }

  // 计算今日统计
  const calculateTodayStats = (sessionList) => {
    const today = dayjs().format('YYYY-MM-DD')
    const todaySessions = sessionList.filter(session =>
      dayjs(session.created_at).format('YYYY-MM-DD') === today
    )

    const completed = todaySessions.filter(s => s.status === 'COMPLETED').length
    const interrupted = todaySessions.filter(s => s.status === 'INTERRUPTED').length
    const totalMinutes = todaySessions.reduce((sum, s) => sum + (s.actual_duration || 0), 0)

    // 计算当前连续完成数
    let currentStreak = 0
    for (let i = todaySessions.length - 1; i >= 0; i--) {
      if (todaySessions[i].status === 'COMPLETED') {
        currentStreak++
      } else {
        break
      }
    }

    setTodayStats({
      completedSessions: completed,
      interruptedSessions: interrupted,
      totalFocusTime: totalMinutes,
      currentStreak: currentStreak
    })
  }

  useEffect(() => {
    fetchTasks()
    fetchSessions()
    fetchActiveSession()

    // 每10秒检查一次活跃会话状态
    intervalRef.current = setInterval(fetchActiveSession, 10000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (selectedTask) {
      setCurrentTask(selectedTask)
    }
  }, [selectedTask])

  // 启动计时器
  const startTimer = (initialTime = sessionSettings.focusDuration * 60) => {
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
          // 时间到，自动显示完成模态框
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

  // 创建并开始番茄钟会话
  const startSession = async () => {
    if (!currentTask) {
      message.warning('请先选择一个任务')
      return
    }

    setLoading(true)
    try {
      // 检查是否已有活跃会话
      if (activeSession) {
        message.warning('已有活跃的番茄钟会话')
        return
      }

      // 创建新会话
      const sessionData = {
        task_id: currentTask.id,
        planned_duration: sessionSettings.focusDuration,
        session_type: 'FOCUS'
      }

      const createResponse = await api.post('/pomodoro-sessions', sessionData)
      const newSession = createResponse.data.pomodoro_session

      // 立即开始会话
      await api.post(`/pomodoro-sessions/${newSession.id}/start`)

      setActiveSession(newSession)
      setIsRunning(true)
      startTimer(sessionSettings.focusDuration * 60)

      message.success('番茄钟会话已开始！')

      // 通知父组件
      if (onSessionUpdate) {
        onSessionUpdate(newSession)
      }

      // 刷新会话列表
      fetchSessions()
    } catch (error) {
      console.error('开始会话失败:', error)
      const errorMsg = error.response?.data?.error || '开始会话失败'
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // 暂停会话（仅本地暂停，不改变服务器状态）
  const pauseSession = () => {
    stopTimer()
    message.info('会话已暂停')
  }

  // 恢复会话
  const resumeSession = () => {
    if (activeSession && activeSession.remaining_time > 0) {
      startTimer(activeSession.remaining_time)
      setIsRunning(true)
      message.info('会话已恢复')
    }
  }

  // 完成会话
  const completeSession = async () => {
    if (!activeSession) return

    setLoading(true)
    try {
      await api.post(`/pomodoro-sessions/${activeSession.id}/complete`, {
        completion_summary: completionSummary.trim() || '番茄钟会话完成'
      })

      setActiveSession(null)
      stopTimer()
      setTimeLeft(0)
      setCompletionModalVisible(false)
      setCompletionSummary('')

      fetchSessions()
      fetchActiveSession()

      message.success('🎉 番茄钟会话已完成！')

      // 通知父组件
      if (onSessionUpdate) {
        onSessionUpdate(null)
      }
    } catch (error) {
      console.error('完成会话失败:', error)
      const errorMsg = error.response?.data?.error || '完成会话失败'
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // 中断会话
  const interruptSession = async () => {
    if (!activeSession) return

    setLoading(true)
    try {
      await api.post(`/pomodoro-sessions/${activeSession.id}/interrupt`, {
        interruption_reason: interruptionReason.trim() || '手动中断'
      })

      setActiveSession(null)
      stopTimer()
      setTimeLeft(0)
      setInterruptionModalVisible(false)
      setInterruptionReason('')

      fetchSessions()
      fetchActiveSession()

      message.warning('番茄钟会话已中断')

      // 通知父组件
      if (onSessionUpdate) {
        onSessionUpdate(null)
      }
    } catch (error) {
      console.error('中断会话失败:', error)
      const errorMsg = error.response?.data?.error || '中断会话失败'
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // 删除会话
  const deleteSession = async (sessionId) => {
    if (!sessionId) return

    setLoading(true)
    try {
      await api.delete(`/pomodoro-sessions/${sessionId}`)

      fetchSessions()
      setDeleteModalVisible(false)
      setSelectedSessionId(null)

      message.success('会话已删除')
    } catch (error) {
      console.error('删除会话失败:', error)
      const errorMsg = error.response?.data?.error || '删除会话失败'
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // 格式化时间显示
  const formatTime = (seconds) => {
    const duration = dayjs.duration(seconds, 'seconds')
    const minutes = duration.minutes()
    const secs = duration.seconds()
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // 获取会话状态标签
  const getSessionStatusTag = (status) => {
    const statusConfig = {
      'PLANNED': { color: 'default', text: '计划中' },
      'IN_PROGRESS': { color: 'processing', text: '进行中' },
      'COMPLETED': { color: 'success', text: '已完成' },
      'INTERRUPTED': { color: 'error', text: '已中断' }
    }
    const config = statusConfig[status] || statusConfig['PLANNED']
    return <Tag color={config.color}>{config.text}</Tag>
  }

  // 获取进度百分比
  const getProgressPercent = () => {
    if (!activeSession) return 0
    const total = sessionSettings.focusDuration * 60
    const elapsed = total - timeLeft
    return Math.max(0, Math.min(100, (elapsed / total) * 100))
  }

  return (
    <div style={{ padding: '16px' }}>
      {/* 标题和统计 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
        <Col>
          <Title level={3} style={{ margin: 0 }}>
            番茄钟会话管理
          </Title>
          <Text type="secondary">
            专注时间管理和会话控制
          </Text>
        </Col>
        <Col>
          <Space>
            <Badge count={todayStats.currentStreak} showZero>
              <Avatar style={{ backgroundColor: '#52c41a' }}>
                <FireOutlined />
              </Avatar>
            </Badge>
            <Text>连续完成</Text>
          </Space>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="今日完成"
              value={todayStats.completedSessions}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a', fontSize: '18px' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="今日中断"
              value={todayStats.interruptedSessions}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f', fontSize: '18px' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="专注时长"
              value={todayStats.totalFocusTime}
              suffix="分钟"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff', fontSize: '18px' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="连续完成"
              value={todayStats.currentStreak}
              suffix="次"
              prefix={<FireOutlined />}
              valueStyle={{ color: '#fa8c16', fontSize: '18px' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 左侧：任务选择和控制 */}
        <Col span={8}>
          <Card title="会话设置" size="small" style={{ marginBottom: '16px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>选择任务：</Text>
                <Select
                  style={{ width: '100%', marginTop: '8px' }}
                  placeholder="选择要专注的任务"
                  value={currentTask?.id}
                  onChange={(value) => {
                    const task = tasks.find(t => t.id === value)
                    setCurrentTask(task)
                  }}
                  disabled={isRunning}
                  size="small"
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
                              {task.description.length > 20 ? task.description.substring(0, 20) + '...' : task.description}
                            </Text>
                          )}
                        </div>
                      </div>
                    </Option>
                  ))}
                </Select>
              </div>

              <div>
                <Text strong>专注时长：</Text>
                <Input
                  type="number"
                  value={sessionSettings.focusDuration}
                  onChange={(e) => setSessionSettings({
                    ...sessionSettings,
                    focusDuration: Math.max(1, Math.min(60, parseInt(e.target.value) || 25))
                  })}
                  min={1}
                  max={60}
                  suffix="分钟"
                  size="small"
                  style={{ marginTop: '8px' }}
                  disabled={isRunning}
                />
              </div>

              {currentTask && (
                <Alert
                  message={`当前任务：${currentTask.title}`}
                  description={
                    currentTask.description
                      ? currentTask.description.length > 50
                        ? currentTask.description.substring(0, 50) + '...'
                        : currentTask.description
                      : '暂无描述'
                  }
                  type="info"
                  size="small"
                  style={{ marginTop: '8px' }}
                />
              )}
            </Space>
          </Card>

          {/* 会话历史记录 */}
          <Card title="最近会话" size="small">
            <List
              size="small"
              dataSource={sessions.slice(0, 5)}
              renderItem={(session) => (
                <List.Item
                  actions={[
                    session.status !== 'IN_PROGRESS' && (
                      <Tooltip title="删除会话">
                        <Button
                          type="text"
                          size="small"
                          icon={<DeleteOutlined />}
                          onClick={() => {
                            setSelectedSessionId(session.id)
                            setDeleteModalVisible(true)
                          }}
                          danger
                        />
                      </Tooltip>
                    )
                  ].filter(Boolean)}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        size="small"
                        style={{
                          backgroundColor: session.status === 'COMPLETED' ? '#52c41a' :
                                          session.status === 'INTERRUPTED' ? '#ff4d4f' :
                                          session.status === 'IN_PROGRESS' ? '#1890ff' : '#d9d9d9'
                        }}
                      >
                        {session.status === 'COMPLETED' ? '✓' :
                         session.status === 'INTERRUPTED' ? '✗' :
                         session.status === 'IN_PROGRESS' ? '●' : '○'}
                      </Avatar>
                    }
                    title={
                      <div style={{ fontSize: '12px' }}>
                        {dayjs(session.created_at).format('HH:mm')}
                        {getSessionStatusTag(session.status)}
                      </div>
                    }
                    description={
                      <Text style={{ fontSize: '11px' }} type="secondary">
                        {session.actual_duration || 0}分钟
                      </Text>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 右侧：计时器和控制 */}
        <Col span={16}>
          <Card>
            {!activeSession ? (
              // 无活跃会话时的界面
              <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                <ClockCircleOutlined style={{ fontSize: '48px', color: '#d9d9d9', marginBottom: '16px' }} />
                <Title level={4} type="secondary">
                  准备开始专注
                </Title>
                <Text type="secondary">
                  选择任务并设置专注时长，开始高效的工作时间
                </Text>
                <div style={{ marginTop: '24px' }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<PlayCircleOutlined />}
                    onClick={startSession}
                    disabled={!currentTask}
                    loading={loading}
                  >
                    开始番茄钟会话
                  </Button>
                </div>
              </div>
            ) : (
              // 有活跃会话时的界面
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{
                  fontSize: '64px',
                  fontWeight: 'bold',
                  color: '#1890ff',
                  marginBottom: '16px',
                  fontFamily: 'monospace'
                }}>
                  {formatTime(timeLeft)}
                </div>

                <Progress
                  percent={getProgressPercent()}
                  status={isRunning ? 'active' : 'normal'}
                  strokeColor={{
                    '0%': '#1890ff',
                    '100%': '#52c41a'
                  }}
                  strokeWidth={8}
                  style={{ marginBottom: '20px' }}
                />

                <div style={{ marginBottom: '20px' }}>
                  <Title level={5} style={{ margin: 0 }}>
                    {isRunning ? '🎯 专注中...' : '⏸️ 已暂停'}
                  </Title>
                  <Text type="secondary">
                    任务：{activeSession.task_id ? tasks.find(t => t.id === activeSession.task_id)?.title || '未知任务' : '未知任务'}
                  </Text>
                </div>

                <Space size="middle">
                  {!isRunning ? (
                    <Button
                      type="primary"
                      size="large"
                      icon={<PlayCircleOutlined />}
                      onClick={resumeSession}
                      disabled={loading}
                    >
                      恢复
                    </Button>
                  ) : (
                    <Button
                      size="large"
                      icon={<PauseCircleOutlined />}
                      onClick={pauseSession}
                    >
                      暂停
                    </Button>
                  )}

                  <Button
                    danger
                    size="large"
                    icon={<StopOutlined />}
                    onClick={() => setInterruptionModalVisible(true)}
                  >
                    中断
                  </Button>

                  <Button
                    type="primary"
                    size="large"
                    icon={<CheckCircleOutlined />}
                    onClick={() => setCompletionModalVisible(true)}
                    ghost
                  >
                    完成
                  </Button>
                </Space>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 中断原因模态框 */}
      <Modal
        title="中断会话"
        open={interruptionModalVisible}
        onCancel={() => {
          setInterruptionModalVisible(false)
          setInterruptionReason('')
        }}
        onOk={interruptSession}
        okText="确认中断"
        cancelText="取消"
        confirmLoading={loading}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="中断会话将记录为中断状态"
            description="请简要说明中断原因，这有助于后续分析和改进。"
            type="warning"
            showIcon
          />
          <Text>中断原因（可选）：</Text>
          <TextArea
            placeholder="请输入中断原因..."
            value={interruptionReason}
            onChange={(e) => setInterruptionReason(e.target.value)}
            rows={4}
            maxLength={200}
            showCount
          />
        </Space>
      </Modal>

      {/* 完成总结模态框 */}
      <Modal
        title="完成会话"
        open={completionModalVisible}
        onCancel={() => {
          setCompletionModalVisible(false)
          setCompletionSummary('')
        }}
        onOk={completeSession}
        okText="确认完成"
        cancelText="稍后总结"
        confirmLoading={loading}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="恭喜完成番茄钟会话！"
            description="简要记录本次专注的成果，有助于积累成就感。"
            type="success"
            showIcon
          />
          <Text>完成总结（可选）：</Text>
          <TextArea
            placeholder="本次专注完成了什么？有什么收获？"
            value={completionSummary}
            onChange={(e) => setCompletionSummary(e.target.value)}
            rows={4}
            maxLength={200}
            showCount
          />
        </Space>
      </Modal>

      {/* 删除确认模态框 */}
      <Modal
        title="删除会话"
        open={deleteModalVisible}
        onCancel={() => {
          setDeleteModalVisible(false)
          setSelectedSessionId(null)
        }}
        onOk={() => deleteSession(selectedSessionId)}
        okText="确认删除"
        cancelText="取消"
        confirmLoading={loading}
        okButtonProps={{ danger: true }}
      >
        <Alert
          message="确定要删除这个番茄钟会话吗？"
          description="删除后将无法恢复，请谨慎操作。"
          type="error"
          showIcon
        />
      </Modal>
    </div>
  )
}

export default PomodoroSessionManager