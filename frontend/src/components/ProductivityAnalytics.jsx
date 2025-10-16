import React, { useState, useEffect, useMemo, useRef } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Spin,
  message,
  Progress,
  Typography,
  Divider,
  Alert,
  Switch,
  Space,
  Tag,
  Tooltip,
  Button,
  Tabs,
  Timeline,
  List,
  Avatar,
  Badge
} from 'antd'
import {
  LineChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  FireOutlined,
  ThunderboltOutlined,
  RiseOutlined,
  FallOutlined,
  EyeOutlined,
  ReloadOutlined,
  SettingOutlined,
  BulbOutlined,
  TargetOutlined,
  BarChartOutlined,
  CalendarOutlined
} from '@ant-design/icons'
import { Line, Area, Column, Heatmap } from '@ant-design/plots'
import dayjs from 'dayjs'
import weekday from 'dayjs/plugin/weekday'
import weekOfYear from 'dayjs/plugin/weekOfYear'
import isoWeek from 'dayjs/plugin/isoWeek'
import api from '../services/api'

dayjs.extend(weekday)
dayjs.extend(weekOfYear)
dayjs.extend(isoWeek)

const { Title, Text, Paragraph } = Typography
const { RangePicker } = DatePicker
const { Option } = Select
const { TabPane } = Tabs

/**
 * 生产力分析组件
 * 专门负责计算和展示用户的生产力指标和趋势分析
 */
const ProductivityAnalytics = () => {
  // 状态管理
  const [loading, setLoading] = useState(false)
  const [tasks, setTasks] = useState([])
  const [pomodoroSessions, setPomodoroSessions] = useState([])
  const [timeBlocks, setTimeBlocks] = useState([])
  const [projects, setProjects] = useState([])
  const [categories, setCategories] = useState([])

  // 分析配置
  const [dateRange, setDateRange] = useState([])
  const [timeRange, setTimeRange] = useState('month')
  const [analysisMode, setAnalysisMode] = useState('comprehensive')
  const [compareMode, setCompareMode] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [showTrends, setShowTrends] = useState(true)

  const refreshTimerRef = useRef(null)

  // 生产力指标
  const [productivityMetrics, setProductivityMetrics] = useState({
    overallScore: 0,
    taskCompletionRate: 0,
    focusEfficiency: 0,
    timeUtilization: 0,
    streakDays: 0,
    averageDailyFocus: 0,
    productivityTrend: 'stable', // 'improving', 'declining', 'stable'
  })

  // 获取数据
  const fetchData = async () => {
    setLoading(true)
    try {
      const [tasksRes, sessionsRes, timeBlocksRes, projectsRes, categoriesRes] = await Promise.allSettled([
        api.get('/tasks'),
        api.get('/pomodoro-sessions'),
        api.get('/time-blocks'),
        api.get('/projects'),
        api.get('/task-categories')
      ])

      if (tasksRes.status === 'fulfilled') {
        setTasks(tasksRes.value.data || [])
      }
      if (sessionsRes.status === 'fulfilled') {
        setPomodoroSessions(sessionsRes.value.data?.pomodoro_sessions || [])
      }
      if (timeBlocksRes.status === 'fulfilled') {
        setTimeBlocks(timeBlocksRes.value.data?.time_blocks || [])
      }
      if (projectsRes.status === 'fulfilled') {
        setProjects(projectsRes.value.data || [])
      }
      if (categoriesRes.status === 'fulfilled') {
        setCategories(categoriesRes.value.data || [])
      }
    } catch (error) {
      console.error('获取生产力数据失败:', error)
      message.error('获取生产力数据失败')
    } finally {
      setLoading(false)
    }
  }

  // 计算生产力指标
  const calculateProductivityMetrics = () => {
    const { tasks, pomodoroSessions, timeBlocks } = { tasks, pomodoroSessions, timeBlocks }

    // 过滤数据
    const filteredData = filterDataByDateRange(tasks, pomodoroSessions, timeBlocks)

    // 计算核心指标
    const metrics = {
      overallScore: calculateOverallProductivityScore(filteredData),
      taskCompletionRate: calculateTaskCompletionRate(filteredData.tasks),
      focusEfficiency: calculateFocusEfficiency(filteredData.sessions, filteredData.timeBlocks),
      timeUtilization: calculateTimeUtilization(filteredData.timeBlocks),
      streakDays: calculateCurrentStreak(filteredData.tasks),
      averageDailyFocus: calculateAverageDailyFocus(filteredData.sessions),
      productivityTrend: calculateProductivityTrend(filteredData.tasks, filteredData.sessions)
    }

    setProductivityMetrics(metrics)
  }

  // 按日期范围过滤数据
  const filterDataByDateRange = (tasksData, sessionsData, timeBlocksData) => {
    let filteredTasks = [...tasksData]
    let filteredSessions = [...sessionsData]
    let filteredTimeBlocks = [...timeBlocksData]

    if (dateRange && dateRange.length === 2) {
      const [start, end] = dateRange
      const startDate = start.startOf('day')
      const endDate = end.endOf('day')

      filteredTasks = filteredTasks.filter(task => {
        if (!task.created_at) return false
        return dayjs(task.created_at).isBetween(startDate, endDate, 'day')
      })

      filteredSessions = filteredSessions.filter(session => {
        if (!session.created_at) return false
        return dayjs(session.created_at).isBetween(startDate, endDate, 'day')
      })

      filteredTimeBlocks = filteredTimeBlocks.filter(block => {
        if (!block.date) return false
        return dayjs(block.date).isBetween(startDate, endDate, 'day')
      })
    } else {
      // 按预设时间范围过滤
      const now = dayjs()
      let startDate

      switch (timeRange) {
        case 'today':
          startDate = now.startOf('day')
          break
        case 'week':
          startDate = now.subtract(7, 'day').startOf('day')
          break
        case 'month':
          startDate = now.subtract(30, 'day').startOf('day')
          break
        case 'quarter':
          startDate = now.subtract(3, 'month').startOf('day')
          break
        default:
          startDate = null
      }

      if (startDate) {
        filteredTasks = filteredTasks.filter(task => {
          if (!task.created_at) return false
          return dayjs(task.created_at).isAfter(startDate)
        })

        filteredSessions = filteredSessions.filter(session => {
          if (!session.created_at) return false
          return dayjs(session.created_at).isAfter(startDate)
        })

        filteredTimeBlocks = filteredTimeBlocks.filter(block => {
          if (!block.date) return false
          return dayjs(block.date).isAfter(startDate)
        })
      }
    }

    return {
      tasks: filteredTasks,
      sessions: filteredSessions,
      timeBlocks: filteredTimeBlocks
    }
  }

  // 计算总体生产力分数 (0-100)
  const calculateOverallProductivityScore = (data) => {
    const { tasks, sessions, timeBlocks } = data

    if (tasks.length === 0) return 0

    // 任务完成率权重 30%
    const completionRate = calculateTaskCompletionRate(tasks)
    const completionScore = completionRate * 0.3

    // 专注效率权重 25%
    const focusEfficiency = calculateFocusEfficiency(sessions, timeBlocks)
    const focusScore = focusEfficiency * 0.25

    // 时间利用率权重 20%
    const timeUtilization = calculateTimeUtilization(timeBlocks)
    const timeScore = timeUtilization * 0.2

    // 任务多样性权重 15%
    const diversityScore = calculateTaskDiversity(tasks) * 0.15

    // 连续性权重 10%
    const consistencyScore = calculateConsistencyScore(sessions) * 0.1

    const totalScore = completionScore + focusScore + timeScore + diversityScore + consistencyScore
    return Math.round(totalScore)
  }

  // 计算任务完成率
  const calculateTaskCompletionRate = (tasks) => {
    if (tasks.length === 0) return 0
    const completedTasks = tasks.filter(task => task.status === 'COMPLETED').length
    return Math.round((completedTasks / tasks.length) * 100)
  }

  // 计算专注效率 (实际专注时间/计划时间)
  const calculateFocusEfficiency = (sessions, timeBlocks) => {
    if (sessions.length === 0) return 0

    const totalActualTime = sessions.reduce((sum, session) => {
      return sum + (session.actual_duration || session.planned_duration || 0)
    }, 0)

    const totalPlannedTime = sessions.reduce((sum, session) => {
      return sum + (session.planned_duration || 25)
    }, 0)

    if (totalPlannedTime === 0) return 100
    return Math.round((totalActualTime / totalPlannedTime) * 100)
  }

  // 计算时间利用率
  const calculateTimeUtilization = (timeBlocks) => {
    if (timeBlocks.length === 0) return 0

    const totalPlannedTime = timeBlocks.reduce((sum, block) => {
      const start = dayjs(block.start_time)
      const end = dayjs(block.end_time)
      return sum + end.diff(start, 'minute')
    }, 0)

    // 假设目标是每天8小时 = 480分钟
    const dailyTarget = 480
    const days = timeBlocks.length > 0 ?
      [...new Set(timeBlocks.map(block => block.date))].length : 1

    const totalTargetTime = dailyTarget * days
    if (totalTargetTime === 0) return 0

    return Math.round((totalPlannedTime / totalTargetTime) * 100)
  }

  // 计算任务多样性
  const calculateTaskDiversity = (tasks) => {
    if (tasks.length === 0) return 0

    // 基于类别的多样性
    const categories = [...new Set(tasks.map(task => task.category_id).filter(Boolean))]
    const categoryScore = Math.min((categories.length / 3) * 100, 100)

    // 基于项目的多样性
    const projects = [...new Set(tasks.map(task => task.project_id).filter(Boolean))]
    const projectScore = Math.min((projects.length / 2) * 100, 100)

    return Math.round((categoryScore + projectScore) / 2)
  }

  // 计算连续性分数
  const calculateConsistencyScore = (sessions) => {
    if (sessions.length === 0) return 0

    // 按日期分组
    const dailySessions = {}
    sessions.forEach(session => {
      if (session.created_at) {
        const date = dayjs(session.created_at).format('YYYY-MM-DD')
        if (!dailySessions[date]) {
          dailySessions[date] = []
        }
        dailySessions[date].push(session)
      }
    })

    // 计算活跃天数
    const activeDays = Object.keys(dailySessions).length
    if (activeDays === 0) return 0

    // 计算平均每天会话数
    const avgSessionsPerDay = sessions.length / activeDays

    // 连续性评分 (理想是每天2-4个会话)
    if (avgSessionsPerDay >= 2 && avgSessionsPerDay <= 4) {
      return 100
    } else if (avgSessionsPerDay < 2) {
      return Math.round((avgSessionsPerDay / 2) * 100)
    } else {
      return Math.max(0, 100 - ((avgSessionsPerDay - 4) * 20))
    }
  }

  // 计算当前连续天数
  const calculateCurrentStreak = (tasks) => {
    if (tasks.length === 0) return 0

    // 获取最近30天的日期
    const dates = []
    for (let i = 0; i < 30; i++) {
      dates.push(dayjs().subtract(i, 'day').format('YYYY-MM-DD'))
    }

    let streak = 0
    for (const date of dates) {
      const hasCompletedTask = tasks.some(task =>
        task.status === 'COMPLETED' &&
        task.updated_at &&
        dayjs(task.updated_at).format('YYYY-MM-DD') === date
      )

      if (hasCompletedTask) {
        streak++
      } else {
        break
      }
    }

    return streak
  }

  // 计算平均每日专注时间
  const calculateAverageDailyFocus = (sessions) => {
    if (sessions.length === 0) return 0

    const totalFocusTime = sessions.reduce((sum, session) => {
      return sum + (session.actual_duration || session.planned_duration || 0)
    }, 0)

    const days = [...new Set(sessions.map(session =>
      session.created_at ? dayjs(session.created_at).format('YYYY-MM-DD') : null
    )).filter(Boolean)].length

    return days > 0 ? Math.round(totalFocusTime / days) : 0
  }

  // 计算生产力趋势
  const calculateProductivityTrend = (tasks, sessions) => {
    if (tasks.length < 7 || sessions.length < 7) return 'stable'

    // 简化的趋势计算
    const recentTasks = tasks.slice(-7)
    const earlierTasks = tasks.slice(-14, -7)

    const recentCompletion = recentTasks.filter(t => t.status === 'COMPLETED').length
    const earlierCompletion = earlierTasks.filter(t => t.status === 'COMPLETED').length

    if (recentCompletion > earlierCompletion * 1.2) {
      return 'improving'
    } else if (recentCompletion < earlierCompletion * 0.8) {
      return 'declining'
    } else {
      return 'stable'
    }
  }

  // 获取每日生产力数据
  const getDailyProductivityData = () => {
    const { tasks, sessions } = filterDataByDateRange(tasks, pomodoroSessions, timeBlocks)
    const dailyData = {}

    // 按日期分组
    tasks.forEach(task => {
      const date = dayjs(task.created_at).format('YYYY-MM-DD')
      if (!dailyData[date]) {
        dailyData[date] = {
          date,
          completedTasks: 0,
          totalTasks: 0,
          focusTime: 0,
          sessions: 0
        }
      }
      dailyData[date].totalTasks++
      if (task.status === 'COMPLETED') {
        dailyData[date].completedTasks++
      }
    })

    sessions.forEach(session => {
      const date = dayjs(session.created_at).format('YYYY-MM-DD')
      if (!dailyData[date]) {
        dailyData[date] = {
          date,
          completedTasks: 0,
          totalTasks: 0,
          focusTime: 0,
          sessions: 0
        }
      }
      dailyData[date].sessions++
      dailyData[date].focusTime += session.actual_duration || session.planned_duration || 0
    })

    return Object.values(dailyData).sort((a, b) => a.date.localeCompare(b.date))
  }

  // 获取热力图数据
  const getHeatmapData = () => {
    const { sessions } = filterDataByDateRange(tasks, pomodoroSessions, timeBlocks)
    const heatmapData = []

    // 按小时和星期几生成数据
    const hours = Array.from({ length: 24 }, (_, i) => i)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

    weekdays.forEach((weekday, weekIndex) => {
      hours.forEach(hour => {
        const sessionsInSlot = sessions.filter(session => {
          if (!session.start_time) return false
          const sessionHour = dayjs(session.start_time).hour()
          const sessionWeekday = dayjs(session.start_time).day()
          return sessionHour === hour && sessionWeekday === weekIndex
        })

        const focusTime = sessionsInSlot.reduce((sum, session) =>
          sum + (session.actual_duration || session.planned_duration || 0), 0
        )

        heatmapData.push({
          weekday,
          hour,
          value: Math.round(focusTime),
          sessions: sessionsInSlot.length
        })
      })
    })

    return heatmapData
  }

  // 获取生产力洞察
  const getProductivityInsights = () => {
    const insights = []

    // 基于指标生成洞察
    if (productivityMetrics.taskCompletionRate < 50) {
      insights.push({
        type: 'warning',
        title: '任务完成率偏低',
        description: `当前任务完成率为 ${productivityMetrics.taskCompletionRate}%，建议分析任务难度和时间安排`,
        suggestion: '考虑分解大任务或调整时间规划'
      })
    }

    if (productivityMetrics.focusEfficiency > 110) {
      insights.push({
        type: 'success',
        title: '专注效率优秀',
        description: `您的专注效率达到 ${productivityMetrics.focusEfficiency}%，超过了计划时间利用率`,
        suggestion: '保持当前的专注习惯，可以考虑增加挑战性任务'
      })
    } else if (productivityMetrics.focusEfficiency < 80) {
      insights.push({
        type: 'warning',
        title: '专注效率有待提升',
        description: `当前专注效率为 ${productivityMetrics.focusEfficiency}%，建议减少干扰因素`,
        suggestion: '创造更好的专注环境，避免多任务处理'
      })
    }

    if (productivityMetrics.streakDays >= 7) {
      insights.push({
        type: 'success',
        title: '连续生产力出色',
        description: `您已经连续 ${productivityMetrics.streakDays} 天完成任务，展现了良好的习惯坚持`,
        suggestion: '继续保持，可以考虑设定更高的目标'
      })
    }

    if (productivityMetrics.averageDailyFocus < 120) {
      insights.push({
        type: 'info',
        title: '专注时间有提升空间',
        description: `当前平均每日专注时间为 ${productivityMetrics.averageDailyFocus} 分钟`,
        suggestion: '建议逐步增加每日专注时间，提升整体生产力'
      })
    }

    return insights
  }

  // 获取趋势图标
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving':
        return <RiseOutlined style={{ color: '#52c41a' }} />
      case 'declining':
        return <FallOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <BarChartOutlined style={{ color: '#1890ff' }} />
    }
  }

  // 获取趋势颜色
  const getTrendColor = (trend) => {
    switch (trend) {
      case 'improving': return '#52c41a'
      case 'declining': return '#ff4d4f'
      default: return '#1890ff'
    }
  }

  // 初始化数据
  useEffect(() => {
    fetchData()
  }, [])

  // 计算指标
  useEffect(() => {
    calculateProductivityMetrics()
  }, [tasks, pomodoroSessions, timeBlocks, dateRange, timeRange])

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      refreshTimerRef.current = setInterval(() => {
        fetchData()
      }, 60000) // 每分钟刷新
    } else {
      if (refreshTimerRef.current) {
        clearInterval(refreshTimerRef.current)
      }
    }

    return () => {
      if (refreshTimerRef.current) {
        clearInterval(refreshTimerRef.current)
      }
    }
  }, [autoRefresh])

  // 图表配置
  const dailyLineConfig = {
    data: getDailyProductivityData(),
    xField: 'date',
    yField: 'focusTime',
    smooth: true,
    point: {
      size: 4,
      shape: 'circle',
    },
    tooltip: {
      formatter: (data) => ({
        name: '专注时间',
        value: `${data.focusTime}分钟`,
      }),
    },
  }

  const completionAreaConfig = {
    data: getDailyProductivityData(),
    xField: 'date',
    yField: ['completedTasks', 'totalTasks'],
    smooth: true,
    areaStyle: {
      fill: 'origin',
    },
  }

  const heatmapConfig = {
    data: getHeatmapData(),
    xField: 'hour',
    yField: 'weekday',
    colorField: 'value',
    color: ['#ebedff', '#c6e7ff', '#91caff', '#69c0ff', '#40a9ff', '#1890ff', '#096dd9', '#0050b3', '#003a8c', '#002766'],
    meta: {
      hour: {
        type: 'cat',
        values: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      },
      weekday: {
        type: 'cat',
        values: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
      },
    },
    tooltip: {
      showTitle: true,
      customContent: (title, items) => {
        const data = items[0]?.data || {}
        return (
          <div>
            <div>{title}</div>
            <div>时间: {data.hour}:00</div>
            <div>专注时间: {data.value}分钟</div>
            <div>会话数: {data.sessions}</div>
          </div>
        )
      },
    },
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 标题和控制栏 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <ThunderboltOutlined /> 生产力分析
          </Title>
          <Text type="secondary">
            基于数据驱动的生产力指标分析和趋势洞察
          </Text>
        </Col>
        <Col>
          <Space>
            <Tooltip title="刷新数据">
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchData}
                loading={loading}
              >
                刷新
              </Button>
            </Tooltip>
            <Tooltip title="自动刷新">
              <Switch
                checked={autoRefresh}
                onChange={setAutoRefresh}
                checkedChildren="自动"
                unCheckedChildren="手动"
              />
            </Tooltip>
          </Space>
        </Col>
      </Row>

      {/* 配置选项 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={16} align="middle">
          <Col>
            <Text>时间范围：</Text>
          </Col>
          <Col>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: 120 }}
            >
              <Option value="today">今天</Option>
              <Option value="week">最近7天</Option>
              <Option value="month">最近30天</Option>
              <Option value="quarter">最近3个月</Option>
              <Option value="all">全部</Option>
            </Select>
          </Col>
          <Col>
            <RangePicker
              onChange={(dates) => setDateRange(dates)}
              style={{ width: 240 }}
            />
          </Col>
          <Col>
            <Text>分析模式：</Text>
          </Col>
          <Col>
            <Select
              value={analysisMode}
              onChange={setAnalysisMode}
              style={{ width: 150 }}
            >
              <Option value="comprehensive">综合分析</Option>
              <Option value="focus">专注分析</Option>
              <Option value="trend">趋势分析</Option>
            </Select>
          </Col>
          <Col>
            <Text>显示趋势：</Text>
          </Col>
          <Col>
            <Switch
              checked={showTrends}
              onChange={setShowTrends}
              checkedChildren="显示"
              unCheckedChildren="隐藏"
            />
          </Col>
        </Row>
      </Card>

      {/* 生产力概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="生产力指数"
              value={productivityMetrics.overallScore}
              suffix="分"
              prefix={<TrophyOutlined />}
              valueStyle={{
                color: productivityMetrics.overallScore >= 80 ? '#52c41a' :
                       productivityMetrics.overallScore >= 60 ? '#fa8c16' : '#ff4d4f'
              }}
            />
            <Progress
              percent={productivityMetrics.overallScore}
              size="small"
              strokeColor={productivityMetrics.overallScore >= 80 ? '#52c41a' :
                         productivityMetrics.overallScore >= 60 ? '#fa8c16' : '#ff4d4f'}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="任务完成率"
              value={productivityMetrics.taskCompletionRate}
              suffix="%"
              prefix={<TargetOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                趋势: {getTrendIcon(productivityMetrics.productivityTrend)}
                <Text style={{ color: getTrendColor(productivityMetrics.productivityTrend), marginLeft: 4 }}>
                  {productivityMetrics.productivityTrend === 'improving' ? '提升' :
                   productivityMetrics.productivityTrend === 'declining' ? '下降' : '稳定'}
                </Text>
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="专注效率"
              value={productivityMetrics.focusEfficiency}
              suffix="%"
              prefix={<FireOutlined />}
              valueStyle={{
                color: productivityMetrics.focusEfficiency >= 100 ? '#52c41a' :
                       productivityMetrics.focusEfficiency >= 80 ? '#1890ff' : '#fa8c16'
              }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                {productivityMetrics.focusEfficiency >= 100 ? '效率超预期' :
                 productivityMetrics.focusEfficiency >= 80 ? '效率良好' : '有提升空间'}
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="连续天数"
              value={productivityMetrics.streakDays}
              suffix="天"
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                {productivityMetrics.streakDays >= 7 ? '习惯养成' :
                 productivityMetrics.streakDays >= 3 ? '保持良好' : '需要坚持'}
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 详细统计 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="日均专注"
              value={productivityMetrics.averageDailyFocus}
              suffix="分钟"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="时间利用率"
              value={productivityMetrics.timeUtilization}
              suffix="%"
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="生产力等级"
              value={
                productivityMetrics.overallScore >= 90 ? '优秀' :
                productMetrics.overallScore >= 70 ? '良好' :
                productivityMetrics.overallScore >= 50 ? '一般' : '需要提升'
              }
              prefix={<EyeOutlined />}
              valueStyle={{
                color: productivityMetrics.overallScore >= 70 ? '#52c41a' : '#fa8c16'
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="每日专注时间趋势">
            {getDailyProductivityData().length > 0 ? (
              <Line {...dailyLineConfig} height={300} />
            ) : (
              <Empty description="暂无数据" />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="任务完成趋势">
            {getDailyProductivityData().length > 0 ? (
              <Area {...completionAreaConfig} height={300} />
            ) : (
              <Empty description="暂无数据" />
            )}
          </Card>
        </Col>
      </Row>

      {/* 热力图 */}
      {showTrends && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={24}>
            <Card title="专注时间热力图 (小时 x 星期)">
              {getHeatmapData().length > 0 ? (
                <Heatmap {...heatmapConfig} height={400} />
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>
          </Col>
        </Row>
      )}

      {/* 生产力洞察 */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="生产力洞察">
            <Timeline>
              {getProductivityInsights().map((insight, index) => (
                <Timeline.Item
                  key={index}
                  color={
                    insight.type === 'success' ? 'green' :
                    insight.type === 'warning' ? 'orange' :
                    insight.type === 'info' ? 'blue' : 'gray'
                  }
                  dot={
                    <BulbOutlined
                      style={{
                        color: insight.type === 'success' ? '#52c41a' :
                               insight.type === 'warning' ? '#fa8c16' :
                               insight.type === 'info' ? '#1890ff' : '#d9d9d9'
                      }}
                    />
                  }
                >
                  <div>
                    <Text strong>{insight.title}</Text>
                    <div style={{ marginTop: 4 }}>
                      <Text>{insight.description}</Text>
                    </div>
                    <div style={{ marginTop: 8 }}>
                      <Tag color={insight.type === 'success' ? 'green' :
                                   insight.type === 'warning' ? 'orange' :
                                   insight.type === 'info' ? 'blue' : 'default'}>
                        {insight.suggestion}
                      </Tag>
                    </div>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
            </Card>
        </Col>
      </Row>
    </div>
  )
}

export default ProductivityAnalytics