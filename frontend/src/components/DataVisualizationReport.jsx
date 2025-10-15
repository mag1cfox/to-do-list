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
  Table,
  Tag,
  Empty,
  Typography,
  Divider,
  Button,
  Tooltip,
  Switch,
  Space,
  Alert
} from 'antd'
import {
  BarChartOutlined,
  PieChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CalendarOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  FireOutlined,
  ThunderboltOutlined,
  EyeOutlined,
  DownloadOutlined,
  ReloadOutlined
} from '@ant-design/icons'
import { Line, Pie, Column, Area, DualAxes } from '@ant-design/plots'
import dayjs from 'dayjs'
import quarterOfYear from 'dayjs/plugin/quarterOfYear'
import weekOfYear from 'dayjs/plugin/weekOfYear'
import api from '../services/api'

dayjs.extend(quarterOfYear)
dayjs.extend(weekOfYear)

const { Title, Text } = Typography
const { RangePicker } = DatePicker
const { Option } = Select

/**
 * 数据可视化报表组件
 * 专门负责各种数据统计、分析和可视化展示
 */
const DataVisualizationReport = () => {
  // 状态管理
  const [loading, setLoading] = useState(false)
  const [tasks, setTasks] = useState([])
  const [pomodoroSessions, setPomodoroSessions] = useState([])
  const [timeBlocks, setTimeBlocks] = useState([])
  const [projects, setProjects] = useState([])
  const [categories, setCategories] = useState([])

  // 过滤和配置
  const [dateRange, setDateRange] = useState([])
  const [timeRange, setTimeRange] = useState('week')
  const [chartType, setChartType] = useState('overview')
  const [showComparison, setShowComparison] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(false)

  // 自动刷新定时器
  const refreshTimerRef = useRef(null)

  // 获取数据
  const fetchData = async () => {
    setLoading(true)
    try {
      const [tasksRes, pomodoroRes, timeBlocksRes, projectsRes, categoriesRes] = await Promise.allSettled([
        api.get('/tasks'),
        api.get('/pomodoro-sessions'),
        api.get('/time-blocks'),
        api.get('/projects'),
        api.get('/task-categories')
      ])

      if (tasksRes.status === 'fulfilled') {
        setTasks(tasksRes.value.data || [])
      }
      if (pomodoroRes.status === 'fulfilled') {
        setPomodoroSessions(pomodoroRes.value.data?.pomodoro_sessions || [])
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
      console.error('获取数据失败:', error)
      message.error('获取报表数据失败')
    } finally {
      setLoading(false)
    }
  }

  // 初始化数据
  useEffect(() => {
    fetchData()
  }, [])

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      refreshTimerRef.current = setInterval(fetchData, 30000) // 每30秒刷新
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

  // 数据过滤
  const filteredData = useMemo(() => {
    let filteredTasks = [...tasks]
    let filteredSessions = [...pomodoroSessions]
    let filteredTimeBlocks = [...timeBlocks]

    // 按时间范围过滤
    if (dateRange && dateRange.length === 2) {
      const [start, end] = dateRange
      filteredTasks = filteredTasks.filter(task => {
        if (!task.created_at) return false
        const taskDate = dayjs(task.created_at)
        return taskDate.isAfter(start) && taskDate.isBefore(end.endOf('day'))
      })

      filteredSessions = filteredSessions.filter(session => {
        if (!session.created_at) return false
        const sessionDate = dayjs(session.created_at)
        return sessionDate.isAfter(start) && sessionDate.isBefore(end.endOf('day'))
      })

      filteredTimeBlocks = filteredTimeBlocks.filter(block => {
        if (!block.date) return false
        const blockDate = dayjs(block.date)
        return blockDate.isAfter(start) && blockDate.isBefore(end.endOf('day'))
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
  }, [tasks, pomodoroSessions, timeBlocks, dateRange, timeRange])

  // 核心统计数据
  const coreStats = useMemo(() => {
    const { tasks, sessions } = filteredData
    const totalTasks = tasks.length
    const completedTasks = tasks.filter(task => task.status === 'COMPLETED').length
    const inProgressTasks = tasks.filter(task => task.status === 'IN_PROGRESS').length
    const totalSessions = sessions.length
    const completedSessions = sessions.filter(session => session.status === 'COMPLETED').length
    const totalFocusTime = sessions.reduce((sum, session) =>
      sum + (session.actual_duration || session.planned_duration || 0), 0
    )

    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
    const sessionCompletionRate = totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0
    const averageTaskTime = completedTasks > 0 ? Math.round(totalFocusTime / completedTasks) : 0

    // 计算趋势数据
    const todayTasks = tasks.filter(task => dayjs(task.created_at).isSame(dayjs(), 'day')).length
    const yesterdayTasks = tasks.filter(task => {
      return dayjs(task.created_at).isSame(dayjs().subtract(1, 'day'), 'day')
    }).length
    const taskTrend = todayTasks - yesterdayTasks

    const todayFocusTime = sessions
      .filter(session => dayjs(session.created_at).isSame(dayjs(), 'day'))
      .reduce((sum, session) => sum + (session.actual_duration || session.planned_duration || 0), 0)
    const yesterdayFocusTime = sessions
      .filter(session => dayjs(session.created_at).isSame(dayjs().subtract(1, 'day'), 'day'))
      .reduce((sum, session) => sum + (session.actual_duration || session.planned_duration || 0), 0)
    const focusTimeTrend = todayFocusTime - yesterdayFocusTime

    return {
      totalTasks,
      completedTasks,
      inProgressTasks,
      totalSessions,
      completedSessions,
      totalFocusTime,
      completionRate,
      sessionCompletionRate,
      averageTaskTime,
      taskTrend,
      focusTimeTrend,
      todayFocusTime
    }
  }, [filteredData])

  // 任务分类统计
  const taskCategoryStats = useMemo(() => {
    const { tasks } = filteredData
    const categoryCount = {}
    const categoryCompletion = {}

    tasks.forEach(task => {
      const categoryName = categories.find(cat => cat.id === task.category_id)?.name || '未分类'
      categoryCount[categoryName] = (categoryCount[categoryName] || 0) + 1

      if (!categoryCompletion[categoryName]) {
        categoryCompletion[categoryName] = { total: 0, completed: 0 }
      }
      categoryCompletion[categoryName].total += 1
      if (task.status === 'COMPLETED') {
        categoryCompletion[categoryName].completed += 1
      }
    })

    return Object.entries(categoryCount).map(([category, count]) => ({
      category,
      count,
      completionRate: categoryCompletion[category] ?
        Math.round((categoryCompletion[category].completed / categoryCompletion[category].total) * 100) : 0
    }))
  }, [filteredData, categories])

  // 项目任务分布
  const projectTaskStats = useMemo(() => {
    const { tasks } = filteredData
    const projectCount = {}

    tasks.forEach(task => {
      const projectName = projects.find(proj => proj.id === task.project_id)?.name || '个人任务'
      projectCount[projectName] = (projectCount[projectName] || 0) + 1
    })

    return Object.entries(projectCount).map(([project, count]) => ({
      project,
      count
    }))
  }, [filteredData, projects])

  // 每日任务完成趋势
  const dailyTaskTrend = useMemo(() => {
    const { tasks } = filteredData
    const today = dayjs()
    const trendData = []

    for (let i = 29; i >= 0; i--) { // 最近30天
      const date = today.subtract(i, 'day')
      const dateStr = date.format('YYYY-MM-DD')

      const createdCount = tasks.filter(task =>
        dayjs(task.created_at).format('YYYY-MM-DD') === dateStr
      ).length

      const completedCount = tasks.filter(task =>
        task.status === 'COMPLETED' &&
        dayjs(task.updated_at).format('YYYY-MM-DD') === dateStr
      ).length

      trendData.push({
        date: date.format('MM/DD'),
        created: createdCount,
        completed: completedCount,
        total: createdCount + completedCount
      })
    }

    return trendData
  }, [filteredData])

  // 专注时间分布
  const focusTimeDistribution = useMemo(() => {
    const { sessions } = filteredData
    const hourCount = {}

    sessions.forEach(session => {
      if (session.start_time) {
        const hour = dayjs(session.start_time).hour()
        const timeSlot = `${hour.toString().padStart(2, '0')}:00`
        hourCount[timeSlot] = (hourCount[timeSlot] || 0) + (session.actual_duration || session.planned_duration || 0)
      }
    })

    return Object.entries(hourCount)
      .map(([timeSlot, minutes]) => ({
        timeSlot,
        minutes,
        hours: (minutes / 60).toFixed(1)
      }))
      .sort((a, b) => parseInt(a.timeSlot) - parseInt(b.timeSlot))
  }, [filteredData])

  // 番茄钟完成率统计
  const pomodoroStats = useMemo(() => {
    const { sessions } = filteredData
    const statusCount = {
      COMPLETED: 0,
      INTERRUPTED: 0,
      IN_PROGRESS: 0,
      PLANNED: 0
    }

    sessions.forEach(session => {
      if (statusCount[session.status] !== undefined) {
        statusCount[session.status] += 1
      }
    })

    return Object.entries(statusCount).map(([status, count]) => ({
      status: getStatusText(status),
      count,
      percentage: sessions.length > 0 ? Math.round((count / sessions.length) * 100) : 0
    }))
  }, [filteredData])

  // 状态文本映射
  const getStatusText = (status) => {
    const statusMap = {
      'PENDING': '待处理',
      'IN_PROGRESS': '进行中',
      'COMPLETED': '已完成',
      'CANCELLED': '已取消',
      'PLANNED': '计划中',
      'INTERRUPTED': '已中断'
    }
    return statusMap[status] || status
  }

  // 图表配置
  const pieConfig = {
    data: taskCategoryStats,
    angleField: 'count',
    colorField: 'category',
    radius: 0.8,
    label: {
      type: 'inner',
      offset: '-30%',
      content: ({ percent }) => `${(percent * 100).toFixed(0)}%`,
      style: {
        fontSize: 14,
        textAlign: 'center',
      },
    },
    interactions: [{ type: 'pie-legend-active' }, { type: 'element-active' }],
  }

  const lineConfig = {
    data: dailyTaskTrend,
    xField: 'date',
    yField: 'created',
    seriesField: 'type',
    smooth: true,
    color: ['#1890ff', '#52c41a'],
    tooltip: {
      formatter: (data) => ({
        name: data.type === 'created' ? '创建任务' : '完成任务',
        value: data.value,
      }),
    },
  }

  const dualAxesConfig = {
    data: [dailyTaskTrend, dailyTaskTrend.map(item => ({ ...item, value: item.completed }))],
    xField: 'date',
    yField: ['created', 'value'],
    geometryOptions: [
      {
        geometry: 'column',
        color: '#1890ff',
      },
      {
        geometry: 'line',
        color: '#52c41a',
        smooth: true,
      },
    ],
  }

  const columnConfig = {
    data: focusTimeDistribution,
    xField: 'timeSlot',
    yField: 'minutes',
    columnWidthRatio: 0.8,
    meta: {
      minutes: {
        alias: '专注时间(分钟)',
      },
    },
    tooltip: {
      formatter: (data) => ({
        name: '专注时间',
        value: `${data.minutes}分钟 (${data.hours}小时)`,
      }),
    },
  }

  // 表格列定义
  const taskColumns = [
    {
      title: '任务标题',
      dataIndex: 'title',
      key: 'title',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'COMPLETED' ? 'green' : status === 'IN_PROGRESS' ? 'blue' : 'default'}>
          {getStatusText(status)}
        </Tag>
      )
    },
    {
      title: '项目',
      dataIndex: 'project_id',
      key: 'project_id',
      render: (projectId) => {
        const project = projects.find(p => p.id === projectId)
        return project ? project.name : '个人任务'
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    }
  ]

  const getTrendIcon = (trend) => {
    if (trend > 0) return <TrendingUpOutlined style={{ color: '#52c41a' }} />
    if (trend < 0) return <TrendingDownOutlined style={{ color: '#ff4d4f' }} />
    return <span style={{ color: '#d9d9d9' }}>—</span>
  }

  const getTrendText = (trend, suffix = '') => {
    if (trend > 0) return `+${trend}${suffix}`
    if (trend < 0) return `${trend}${suffix}`
    return `0${suffix}`
  }

  if (loading && tasks.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>加载报表数据中...</Text>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 标题和控制栏 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <BarChartOutlined /> 数据可视化报表
          </Title>
          <Text type="secondary">
            全面的时间管理和 productivity 数据分析
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

      {/* 时间范围和显示控制 */}
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
            <Text>图表类型：</Text>
          </Col>
          <Col>
            <Select
              value={chartType}
              onChange={setChartType}
              style={{ width: 150 }}
            >
              <Option value="overview">总览</Option>
              <Option value="tasks">任务分析</Option>
              <Option value="focus">专注分析</Option>
              <Option value="trends">趋势分析</Option>
            </Select>
          </Col>
          <Col>
            <Tooltip title="显示对比数据">
              <Switch
                checked={showComparison}
                onChange={setShowComparison}
                checkedChildren="对比"
                unCheckedChildren="单期"
              />
            </Tooltip>
          </Col>
        </Row>
      </Card>

      {/* 核心统计指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={8} lg={6} xl={4}>
          <Card>
            <Statistic
              title="总任务数"
              value={coreStats.totalTasks}
              prefix={<CalendarOutlined />}
              suffix={getTrendIcon(coreStats.taskTrend)}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                较昨日 {getTrendText(coreStats.taskTrend)}
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6} xl={4}>
          <Card>
            <Statistic
              title="已完成任务"
              value={coreStats.completedTasks}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress
              percent={coreStats.completionRate}
              size="small"
              style={{ marginTop: 8 }}
              format={() => `${coreStats.completionRate}%`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6} xl={4}>
          <Card>
            <Statistic
              title="专注时间"
              value={coreStats.totalFocusTime}
              suffix="分钟"
              prefix={<ClockCircleOutlined />}
              suffix={getTrendIcon(coreStats.focusTimeTrend)}
              valueStyle={{ color: '#13c2c2' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                较昨日 {getTrendText(coreStats.focusTimeTrend, '分钟')}
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6} xl={4}>
          <Card>
            <Statistic
              title="番茄钟会话"
              value={coreStats.completedSessions}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                完成率 {coreStats.sessionCompletionRate}%
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6} xl={4}>
          <Card>
            <Statistic
              title="进行中任务"
              value={coreStats.inProgressTasks}
              prefix={<FireOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6} xl={4}>
          <Card>
            <Statistic
              title="平均任务时间"
              value={coreStats.averageTaskTime}
              suffix="分钟"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 数据总览提示 */}
      {filteredData.tasks.length === 0 && (
        <Alert
          message="当前时间范围内暂无数据"
          description="请尝试调整时间范围或创建一些任务和番茄钟会话。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 图表展示区域 */}
      {chartType === 'overview' && (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="任务分类分布" extra={<PieChartOutlined />}>
              {taskCategoryStats.length > 0 ? (
                <Pie {...pieConfig} height={300} />
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="项目任务分布" extra={<BarChartOutlined />}>
              {projectTaskStats.length > 0 ? (
                <Column
                  data={projectTaskStats}
                  xField="project"
                  yField="count"
                  columnWidthRatio={0.6}
                  height={300}
                />
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="专注时间分布" extra={<ClockCircleOutlined />}>
              {focusTimeDistribution.length > 0 ? (
                <Column {...columnConfig} height={300} />
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="番茄钟状态统计" extra={<ThunderboltOutlined />}>
              <div style={{ padding: '16px 0' }}>
                {pomodoroStats.map((item, index) => (
                  <div key={index} style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <Text>{item.status}</Text>
                      <Text strong>{item.count} ({item.percentage}%)</Text>
                    </div>
                    <Progress
                      percent={item.percentage}
                      showInfo={false}
                      strokeColor={
                        item.status === '已完成' ? '#52c41a' :
                        item.status === '已中断' ? '#ff4d4f' :
                        item.status === '进行中' ? '#1890ff' : '#d9d9d9'
                      }
                    />
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {chartType === 'trends' && (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <Card title="任务完成趋势（最近30天）" extra={<TrendingUpOutlined />}>
              {dailyTaskTrend.length > 0 ? (
                <DualAxes {...dualAxesConfig} height={400} />
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>
          </Col>
        </Row>
      )}

      <Divider />

      {/* 任务详情表格 */}
      <Card title="任务详情" extra={<EyeOutlined />}>
        <Table
          columns={taskColumns}
          dataSource={filteredData.tasks}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个任务`,
          }}
          locale={{
            emptyText: '暂无任务数据'
          }}
        />
      </Card>
    </div>
  )
}

export default DataVisualizationReport