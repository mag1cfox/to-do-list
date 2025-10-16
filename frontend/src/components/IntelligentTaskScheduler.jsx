import React, { useState, useEffect, useMemo, useRef } from 'react'
import {
  Card,
  List,
  Button,
  Tag,
  Space,
  Tooltip,
  Alert,
  Empty,
  Spin,
  Typography,
  Row,
  Col,
  Statistic,
  Progress,
  Timeline,
  Modal,
  Select,
  Switch,
  Badge,
  Divider,
  message
} from 'antd'
import {
  RobotOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  BulbOutlined,
  CalendarOutlined,
  StarOutlined,
  ReloadOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../services/api'

const { Title, Text, Paragraph } = Typography
const { Option } = Select

/**
 * 智能任务调度建议组件
 * 专门负责基于用户数据和AI算法生成智能的任务调度建议
 */
const IntelligentTaskScheduler = () => {
  // 状态管理
  const [loading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [tasks, setTasks] = useState([])
  const [timeBlocks, setTimeBlocks] = useState([])
  const [categories, setCategories] = useState([])
  const [projects, setProjects] = useState([])
  const [selectedDate, setSelectedDate] = useState(dayjs())

  // 配置选项
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [showAccepted, setShowAccepted] = useState(false)
  const [priorityMode, setPriorityMode] = useState('BALANCED')
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedRecommendation, setSelectedRecommendation] = useState(null)

  // 统计数据
  const [stats, setStats] = useState({
    totalRecommendations: 0,
    acceptedCount: 0,
    pendingCount: 0,
    highPriorityCount: 0
  })

  const refreshTimerRef = useRef(null)

  // 智能推荐算法配置
  const algorithmConfig = {
    priorityMode, // 'DEADLINE', 'IMPORTANCE', 'BALANCED', 'ENERGY'
    maxRecommendations: 10,
    minPriorityScore: 0.3,
    timeSlotBuffer: 15, // 分钟
    considerEnergy: true,
    considerDependencies: true,
    avoidOverload: true
  }

  // 获取数据
  const fetchData = async () => {
    setLoading(true)
    try {
      const [tasksRes, timeBlocksRes, categoriesRes, projectsRes] = await Promise.allSettled([
        api.get('/tasks'),
        api.get('/time-blocks'),
        api.get('/task-categories'),
        api.get('/projects')
      ])

      if (tasksRes.status === 'fulfilled') {
        setTasks(tasksRes.value.data || [])
      }
      if (timeBlocksRes.status === 'fulfilled') {
        setTimeBlocks(timeBlocksRes.value.data?.time_blocks || [])
      }
      if (categoriesRes.status === 'fulfilled') {
        setCategories(categoriesRes.value.data || [])
      }
      if (projectsRes.status === 'fulfilled') {
        setProjects(projectsRes.value.data || [])
      }
    } catch (error) {
      console.error('获取数据失败:', error)
      message.error('获取基础数据失败')
    } finally {
      setLoading(false)
    }
  }

  // 生成智能推荐
  const generateRecommendations = async () => {
    setLoading(true)
    try {
      // 这里是核心的智能推荐算法
      const smartRecommendations = calculateSmartRecommendations()
      setRecommendations(smartRecommendations)

      // 更新统计数据
      updateStats(smartRecommendations)

      message.success(`生成了 ${smartRecommendations.length} 条智能建议`)
    } catch (error) {
      console.error('生成推荐失败:', error)
      message.error('生成智能推荐失败')
    } finally {
      setLoading(false)
    }
  }

  // 核心智能推荐算法
  const calculateSmartRecommendations = () => {
    const pendingTasks = tasks.filter(task => task.status === 'PENDING')
    const todayTimeBlocks = timeBlocks.filter(block =>
      dayjs(block.date).isSame(selectedDate, 'day')
    )

    const recommendations = []

    // 1. 紧急任务推荐（基于截止时间和优先级）
    pendingTasks.forEach(task => {
      let priorityScore = 0
      let reasons = []

      // 优先级评分
      if (task.priority === 'HIGH') {
        priorityScore += 0.4
        reasons.push('高优先级任务')
      } else if (task.priority === 'MEDIUM') {
        priorityScore += 0.2
      }

      // 计划开始时间评分
      if (task.planned_start_time) {
        const taskDate = dayjs(task.planned_start_time)
        const daysUntil = taskDate.diff(selectedDate, 'day')

        if (daysUntil <= 1) {
          priorityScore += 0.3
          reasons.push('即将到期')
        } else if (daysUntil <= 3) {
          priorityScore += 0.2
          reasons.push('临近截止日期')
        }
      }

      // 任务复杂度评分（基于预估番茄钟数）
      if (task.estimated_pomodoros >= 3) {
        priorityScore += 0.1
        reasons.push('复杂任务，建议尽早开始')
      }

      // 项目重要性评分
      if (task.project_id) {
        const project = projects.find(p => p.id === task.project_id)
        if (project && project.priority === 'HIGH') {
          priorityScore += 0.1
          reasons.push('重要项目任务')
        }
      }

      // 类别重要性评分
      if (task.category_id) {
        const category = categories.find(c => c.id === task.category_id)
        if (category && category.name) {
          if (category.name.includes('学习') || category.name.includes('工作')) {
            priorityScore += 0.1
            reasons.push('重要类别任务')
          }
        }
      }

      // 只推荐优先级分数足够高的任务
      if (priorityScore >= algorithmConfig.minPriorityScore) {
        // 寻找合适的时间块
        const suitableTimeBlock = findSuitableTimeBlock(task, todayTimeBlocks)

        recommendations.push({
          id: `task_${task.id}`,
          type: 'TASK_RECOMMENDATION',
          priority: priorityScore,
          task: task,
          suggestedTime: suitableTimeBlock,
          suggestedAction: getSuggestedAction(task, suitableTimeBlock),
          reasons: reasons,
          estimatedDuration: task.estimated_pomodoros * 25, // 分钟
          energyLevel: calculateOptimalEnergyLevel(task),
          status: 'PENDING',
          generatedAt: dayjs()
        })
      }
    })

    // 2. 时间块优化建议
    const optimizationSuggestions = generateTimeBlockOptimizations(todayTimeBlocks, pendingTasks)
    recommendations.push(...optimizationSuggestions)

    // 3. 工作效率建议
    const efficiencySuggestions = generateEfficiencySuggestions(pendingTasks, todayTimeBlocks)
    recommendations.push(...efficiencySuggestions)

    // 按优先级排序并限制数量
    return recommendations
      .sort((a, b) => b.priority - a.priority)
      .slice(0, algorithmConfig.maxRecommendations)
  }

  // 寻找合适的时间块
  const findSuitableTimeBlock = (task, timeBlocks) => {
    const taskDuration = task.estimated_pomodoros * 25 // 分钟
    const preferredTime = task.planned_start_time ? dayjs(task.planned_start_time) : selectedDate

    // 按优先级寻找合适的时间块
    const suitableBlocks = timeBlocks
      .filter(block => {
        const blockDuration = dayjs(block.end_time).diff(dayjs(block.start_time), 'minute')
        return blockDuration >= taskDuration
      })
      .map(block => ({
        ...block,
        suitability: calculateTimeBlockSuitability(block, task, preferredTime)
      }))
      .sort((a, b) => b.suitability - a.suitability)

    return suitableBlocks[0] || null
  }

  // 计算时间块适合度
  const calculateTimeBlockSuitability = (timeBlock, task, preferredTime) => {
    let suitability = 0.5 // 基础分数

    // 时间匹配度
    const blockStart = dayjs(timeBlock.start_time)
    const timeDiff = Math.abs(blockStart.diff(preferredTime, 'hour'))
    suitability += Math.max(0, 0.3 - timeDiff * 0.05)

    // 类别匹配度
    if (task.category_id) {
      const category = categories.find(c => c.id === task.category_id)
      if (category && timeBlock.block_type) {
        const categoryTypeMatch = getCategoryBlockTypeMatch(category.name, timeBlock.block_type)
        suitability += categoryTypeMatch * 0.2
      }
    }

    return Math.min(1, suitability)
  }

  // 类别与时间块类型匹配
  const getCategoryBlockTypeMatch = (categoryName, blockType) => {
    const matches = {
      '工作': { 'RESEARCH': 0.9, 'GROWTH': 0.7, 'REVIEW': 0.8 },
      '学习': { 'RESEARCH': 0.9, 'GROWTH': 0.9, 'REVIEW': 0.7 },
      '生活': { 'REST': 0.9, 'ENTERTAINMENT': 0.8 },
      '休息': { 'REST': 0.9, 'ENTERTAINMENT': 0.7 },
      '复盘': { 'REVIEW': 0.9, 'GROWTH': 0.6 }
    }

    for (const [key, typeMatches] of Object.entries(matches)) {
      if (categoryName.includes(key)) {
        return typeMatches[blockType] || 0.5
      }
    }

    return 0.5
  }

  // 获取建议的行动
  const getSuggestedAction = (task, timeBlock) => {
    if (!timeBlock) {
      return {
        type: 'CREATE_TIME_BLOCK',
        text: '创建新的时间块',
        description: `为任务"${task.title}"创建一个${task.estimated_pomodoros * 25}分钟的时间块`
      }
    }

    return {
      type: 'SCHEDULE_TO_BLOCK',
      text: `安排到 ${dayjs(timeBlock.start_time).format('HH:mm')} 的时间块`,
      description: `将任务安排到${timeBlock.block_type}类型的时间块中`
    }
  }

  // 计算最优精力水平
  const calculateOptimalEnergyLevel = (task) => {
    // 根据任务类型和复杂度计算最优精力水平
    let energyLevel = 'MEDIUM' // LOW, MEDIUM, HIGH

    if (task.estimated_pomodoros >= 3) {
      energyLevel = 'HIGH'
    } else if (task.priority === 'HIGH') {
      energyLevel = 'HIGH'
    } else if (task.estimated_pomodoros === 1) {
      energyLevel = 'LOW'
    }

    return energyLevel
  }

  // 生成时间块优化建议
  const generateTimeBlockOptimizations = (timeBlocks, pendingTasks) => {
    const suggestions = []

    // 检查时间利用率
    const totalAvailableTime = timeBlocks.reduce((sum, block) => {
      return sum + dayjs(block.end_time).diff(dayjs(block.start_time), 'minute')
    }, 0)

    const totalTaskTime = pendingTasks.reduce((sum, task) => {
      return sum + (task.estimated_pomodoros * 25)
    }, 0)

    if (totalTaskTime > totalAvailableTime * 0.8) {
      suggestions.push({
        id: 'time_utilization_warning',
        type: 'TIME_OPTIMIZATION',
        priority: 0.7,
        title: '时间利用率过高',
        description: `当前待办任务需要${totalTaskTime}分钟，而可用时间只有${totalAvailableTime}分钟`,
        suggestedAction: {
          type: 'OPTIMIZE_SCHEDULE',
          text: '优化任务安排',
          description: '建议调整任务优先级或增加时间块'
        },
        reasons: ['任务过多', '时间不足'],
        status: 'PENDING'
      })
    }

    // 检查时间块间隙
    const sortedBlocks = timeBlocks.sort((a, b) =>
      dayjs(a.start_time).diff(dayjs(b.start_time))
    )

    for (let i = 0; i < sortedBlocks.length - 1; i++) {
      const currentEnd = dayjs(sortedBlocks[i].end_time)
      const nextStart = dayjs(sortedBlocks[i + 1].start_time)
      const gap = nextStart.diff(currentEnd, 'minute')

      if (gap >= 30 && gap <= 90) {
        suggestions.push({
          id: `gap_opportunity_${i}`,
          type: 'TIME_OPTIMIZATION',
          priority: 0.4,
          title: '发现可用时间间隙',
          description: `${currentEnd.format('HH:mm')} - ${nextStart.format('HH:mm')} 有${gap}分钟空闲时间`,
          suggestedAction: {
            type: 'FILL_GAP',
            text: '安排小型任务',
            description: `可以安排一个${Math.floor(gap / 25)}个番茄钟的小任务`
          },
          reasons: ['时间间隙利用', '提高效率'],
          status: 'PENDING'
        })
      }
    }

    return suggestions
  }

  // 生成效率建议
  const generateEfficiencySuggestions = (pendingTasks, timeBlocks) => {
    const suggestions = []

    // 批量处理建议
    const similarTasks = groupSimilarTasks(pendingTasks)
    Object.entries(similarTasks).forEach(([category, tasks]) => {
      if (tasks.length >= 2) {
        suggestions.push({
          id: `batch_${category}`,
          type: 'EFFICIENCY_IMPROVEMENT',
          priority: 0.5,
          title: `批量处理${category}类任务`,
          description: `发现${tasks.length}个${category}类任务可以批量处理`,
          suggestedAction: {
            type: 'BATCH_PROCESS',
            text: '批量安排',
            description: `将这些任务安排在连续的时间块中处理`
          },
          reasons: ['批量处理效率高', '减少上下文切换'],
          status: 'PENDING'
        })
      }
    })

    // 休息建议
    const focusBlocks = timeBlocks.filter(block =>
      block.block_type === 'RESEARCH' || block.block_type === 'GROWTH'
    )

    if (focusBlocks.length >= 3) {
      suggestions.push({
        id: 'rest_recommendation',
        type: 'EFFICIENCY_IMPROVEMENT',
        priority: 0.6,
        title: '建议安排休息时间',
        description: `连续${focusBlocks.length}个专注时间块，建议插入休息`,
        suggestedAction: {
          type: 'SCHEDULE_REST',
          text: '安排休息',
          description: '在专注时间块之间安排5-15分钟的休息'
        },
        reasons: ['避免过度疲劳', '保持专注效率'],
        status: 'PENDING'
      })
    }

    return suggestions
  }

  // 按类别分组相似任务
  const groupSimilarTasks = (tasks) => {
    const groups = {}

    tasks.forEach(task => {
      const category = categories.find(c => c.id === task.category_id)
      const categoryName = category ? category.name : '未分类'

      if (!groups[categoryName]) {
        groups[categoryName] = []
      }
      groups[categoryName].push(task)
    })

    return groups
  }

  // 更新统计数据
  const updateStats = (recommendations) => {
    setStats({
      totalRecommendations: recommendations.length,
      acceptedCount: recommendations.filter(r => r.status === 'ACCEPTED').length,
      pendingCount: recommendations.filter(r => r.status === 'PENDING').length,
      highPriorityCount: recommendations.filter(r => r.priority >= 0.7).length
    })
  }

  // 接受推荐
  const acceptRecommendation = async (recommendation) => {
    try {
      if (recommendation.type === 'TASK_RECOMMENDATION') {
        // 执行任务调度建议
        await executeTaskRecommendation(recommendation)
      } else if (recommendation.type === 'TIME_OPTIMIZATION') {
        // 执行时间优化建议
        await executeTimeOptimization(recommendation)
      } else if (recommendation.type === 'EFFICIENCY_IMPROVEMENT') {
        // 执行效率改进建议
        await executeEfficiencyImprovement(recommendation)
      }

      // 更新推荐状态
      setRecommendations(prev =>
        prev.map(r =>
          r.id === recommendation.id
            ? { ...r, status: 'ACCEPTED', acceptedAt: dayjs() }
            : r
        )
      )

      updateStats(recommendations.map(r =>
        r.id === recommendation.id
          ? { ...r, status: 'ACCEPTED' }
          : r
      ))

      message.success('已接受智能建议')
    } catch (error) {
      console.error('执行建议失败:', error)
      message.error('执行建议失败')
    }
  }

  // 执行任务推荐
  const executeTaskRecommendation = async (recommendation) => {
    const { task, suggestedAction, suggestedTime } = recommendation

    if (suggestedAction.type === 'CREATE_TIME_BLOCK') {
      // 创建新的时间块
      const newTimeBlock = {
        date: selectedDate.format('YYYY-MM-DD'),
        start_time: selectedDate.set('hour', 9).set('minute', 0).toISOString(),
        end_time: selectedDate.set('hour', 9).set('minute', 0).add(recommendation.estimatedDuration, 'minute').toISOString(),
        block_type: 'RESEARCH',
        color: '#1890ff',
        description: `为任务"${task.title}"安排的时间块`
      }

      await api.post('/time-blocks', newTimeBlock)
    } else if (suggestedAction.type === 'SCHEDULE_TO_BLOCK' && suggestedTime) {
      // 将任务关联到现有时间块
      await api.put(`/tasks/${task.id}`, {
        scheduled_time_block_id: suggestedTime.id
      })
    }
  }

  // 执行时间优化
  const executeTimeOptimization = async (recommendation) => {
    // 这里可以实现具体的时间优化逻辑
    message.info('时间优化功能正在开发中')
  }

  // 执行效率改进
  const executeEfficiencyImprovement = async (recommendation) => {
    // 这里可以实现具体的效率改进逻辑
    message.info('效率改进功能正在开发中')
  }

  // 忽略推荐
  const ignoreRecommendation = (recommendation) => {
    setRecommendations(prev =>
      prev.map(r =>
        r.id === recommendation.id
          ? { ...r, status: 'IGNORED', ignoredAt: dayjs() }
          : r
      )
    )
    message.info('已忽略此建议')
  }

  // 查看推荐详情
  const viewRecommendationDetail = (recommendation) => {
    setSelectedRecommendation(recommendation)
    setDetailModalVisible(true)
  }

  // 获取优先级颜色
  const getPriorityColor = (priority) => {
    if (priority >= 0.8) return '#ff4d4f'
    if (priority >= 0.6) return '#fa8c16'
    if (priority >= 0.4) return '#1890ff'
    return '#52c41a'
  }

  // 获取优先级标签
  const getPriorityTag = (priority) => {
    if (priority >= 0.8) return '紧急'
    if (priority >= 0.6) return '高'
    if (priority >= 0.4) return '中'
    return '低'
  }

  // 获取推荐类型图标
  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'TASK_RECOMMENDATION':
        return <ThunderboltOutlined style={{ color: '#1890ff' }} />
      case 'TIME_OPTIMIZATION':
        return <ClockCircleOutlined style={{ color: '#fa8c16' }} />
      case 'EFFICIENCY_IMPROVEMENT':
        return <BulbOutlined style={{ color: '#52c41a' }} />
      default:
        return <InfoCircleOutlined style={{ color: '#d9d9d9' }} />
    }
  }

  // 获取推荐类型名称
  const getRecommendationTypeName = (type) => {
    switch (type) {
      case 'TASK_RECOMMENDATION':
        return '任务调度'
      case 'TIME_OPTIMIZATION':
        return '时间优化'
      case 'EFFICIENCY_IMPROVEMENT':
        return '效率提升'
      default:
        return '其他建议'
    }
  }

  // 过滤推荐
  const filteredRecommendations = useMemo(() => {
    let filtered = recommendations

    if (!showAccepted) {
      filtered = filtered.filter(r => r.status === 'PENDING')
    }

    return filtered
  }, [recommendations, showAccepted])

  // 初始化数据
  useEffect(() => {
    fetchData()
  }, [])

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      refreshTimerRef.current = setInterval(() => {
        fetchData()
        generateRecommendations()
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

  return (
    <div style={{ padding: '24px' }}>
      {/* 标题和控制栏 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <RobotOutlined /> 智能任务调度建议
          </Title>
          <Text type="secondary">
            基于AI算法的个性化任务调度和时间优化建议
          </Text>
        </Col>
        <Col>
          <Space>
            <Tooltip title="刷新推荐">
              <Button
                icon={<ReloadOutlined />}
                onClick={generateRecommendations}
                loading={loading}
              >
                重新分析
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
            <Text>优先级模式：</Text>
          </Col>
          <Col>
            <Select
              value={priorityMode}
              onChange={setPriorityMode}
              style={{ width: 150 }}
            >
              <Option value="DEADLINE">截止时间优先</Option>
              <Option value="IMPORTANCE">重要性优先</Option>
              <Option value="BALANCED">平衡模式</Option>
              <Option value="ENERGY">精力导向</Option>
            </Select>
          </Col>
          <Col>
            <Text>显示已接受：</Text>
          </Col>
          <Col>
            <Switch
              checked={showAccepted}
              onChange={setShowAccepted}
              checkedChildren="显示"
              unCheckedChildren="隐藏"
            />
          </Col>
          <Col>
            <Text>目标日期：</Text>
          </Col>
          <Col>
            <Select
              value={selectedDate.format('YYYY-MM-DD')}
              onChange={(date) => setSelectedDate(dayjs(date))}
              style={{ width: 150 }}
            >
              <Option value={dayjs().format('YYYY-MM-DD')}>今天</Option>
              <Option value={dayjs().add(1, 'day').format('YYYY-MM-DD')}>明天</Option>
              <Option value={dayjs().add(7, 'day').format('YYYY-MM-DD')}>下周</Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总建议数"
              value={stats.totalRecommendations}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="高优先级"
              value={stats.highPriorityCount}
              prefix={<StarOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理"
              value={stats.pendingCount}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已接受"
              value={stats.acceptedCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 智能建议列表 */}
      <Card title={`智能建议 (${filteredRecommendations.length})`}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>AI正在分析您的时间和任务数据...</Text>
            </div>
          </div>
        ) : filteredRecommendations.length > 0 ? (
          <List
            dataSource={filteredRecommendations}
            renderItem={(recommendation) => (
              <List.Item
                actions={[
                  <Tooltip title="查看详情">
                    <Button
                      type="text"
                      icon={<InfoCircleOutlined />}
                      onClick={() => viewRecommendationDetail(recommendation)}
                    />
                  </Tooltip>,
                  recommendation.status === 'PENDING' && (
                    <Tooltip title="接受建议">
                      <Button
                        type="text"
                        icon={<CheckCircleOutlined />}
                        onClick={() => acceptRecommendation(recommendation)}
                        style={{ color: '#52c41a' }}
                      />
                    </Tooltip>
                  ),
                  recommendation.status === 'PENDING' && (
                    <Tooltip title="忽略建议">
                      <Button
                        type="text"
                        icon={<PauseCircleOutlined />}
                        onClick={() => ignoreRecommendation(recommendation)}
                        style={{ color: '#d9d9d9' }}
                      />
                    </Tooltip>
                  )
                ].filter(Boolean)}
              >
                <List.Item.Meta
                  avatar={getRecommendationIcon(recommendation.type)}
                  title={
                    <Space>
                      <span>{recommendation.title || recommendation.task?.title}</span>
                      <Tag color={getPriorityColor(recommendation.priority)}>
                        {getPriorityTag(recommendation.priority)}
                      </Tag>
                      <Badge
                        color={recommendation.status === 'ACCEPTED' ? 'green' :
                               recommendation.status === 'IGNORED' ? 'red' : 'blue'}
                        text={getRecommendationTypeName(recommendation.type)}
                      />
                    </Space>
                  }
                  description={
                    <div>
                      <Paragraph style={{ marginBottom: 8 }}>
                        {recommendation.description}
                      </Paragraph>
                      {recommendation.suggestedAction && (
                        <div>
                          <Text strong>建议操作：</Text>
                          <Text style={{ marginLeft: 8 }}>
                            {recommendation.suggestedAction.text}
                          </Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {recommendation.suggestedAction.description}
                          </Text>
                        </div>
                      )}
                      {recommendation.reasons && recommendation.reasons.length > 0 && (
                        <div style={{ marginTop: 8 }}>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            推荐原因：{recommendation.reasons.join('、')}
                          </Text>
                        </div>
                      )}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty
            description="暂无智能建议"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={generateRecommendations}>
              生成智能建议
            </Button>
          </Empty>
        )}
      </Card>

      {/* 推荐详情模态框 */}
      <Modal
        title="推荐详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          selectedRecommendation?.status === 'PENDING' && (
            <Button key="accept" type="primary" onClick={() => {
              acceptRecommendation(selectedRecommendation)
              setDetailModalVisible(false)
            }}>
              接受建议
            </Button>
          )
        ]}
        width={600}
      >
        {selectedRecommendation && (
          <div>
            <Timeline>
              <Timeline.Item>
                <Text strong>推荐类型：</Text>
                <Space>
                  {getRecommendationIcon(selectedRecommendation.type)}
                  <Text>{getRecommendationTypeName(selectedRecommendation.type)}</Text>
                </Space>
              </Timeline.Item>

              <Timeline.Item>
                <Text strong>优先级：</Text>
                <Tag color={getPriorityColor(selectedRecommendation.priority)}>
                  {getPriorityTag(selectedRecommendation.priority)} ({(selectedRecommendation.priority * 100).toFixed(0)}%)
                </Tag>
              </Timeline.Item>

              {selectedRecommendation.reasons && (
                <Timeline.Item>
                  <Text strong>推荐原因：</Text>
                  <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                    {selectedRecommendation.reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </Timeline.Item>
              )}

              {selectedRecommendation.task && (
                <Timeline.Item>
                  <Text strong>关联任务：</Text>
                  <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                    <div><Text strong>{selectedRecommendation.task.title}</Text></div>
                    {selectedRecommendation.task.description && (
                      <Text type="secondary">{selectedRecommendation.task.description}</Text>
                    )}
                    <div style={{ marginTop: 4 }}>
                      <Tag>预估时间：{selectedRecommendation.estimatedDuration}分钟</Tag>
                      <Tag>精力要求：{selectedRecommendation.energyLevel}</Tag>
                    </div>
                  </div>
                </Timeline.Item>
              )}

              <Timeline.Item>
                <Text strong>生成时间：</Text>
                <Text>{selectedRecommendation.generatedAt.format('YYYY-MM-DD HH:mm:ss')}</Text>
              </Timeline.Item>
            </Timeline>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default IntelligentTaskScheduler