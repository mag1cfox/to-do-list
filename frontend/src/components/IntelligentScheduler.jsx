import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  List,
  Avatar,
  Tag,
  Typography,
  Space,
  Spin,
  Empty,
  Alert,
  Timeline,
  Badge,
  Tooltip,
  Row,
  Col,
  Statistic,
  Progress
} from 'antd'
import {
  BulbOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  StarOutlined,
  FireOutlined,
  RocketOutlined,
  ScheduleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { useAuthStore } from '../stores/authStore'
import { recommendationService, pomodoroService } from '../services/api'

const { Title, Text, Paragraph } = Typography

function IntelligentScheduler() {
  const { isAuthenticated } = useAuthStore()

  // 如果用户未登录，显示提示信息
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Empty
          description="请先登录以使用智能调度功能"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    )
  }

  const [loading, setLoading] = useState(false)
  const [currentRecommendation, setCurrentRecommendation] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [scheduleSuggestions, setScheduleSuggestions] = useState(null)
  const [summary, setSummary] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  // 获取推荐数据
  const fetchRecommendations = async () => {
    if (!isAuthenticated) return

    setLoading(true)
    try {
      // 获取当前推荐
      const currentResponse = await recommendationService.getCurrentRecommendation()

      // 获取推荐列表
      const listResponse = await recommendationService.getTaskRecommendations({ limit: 5 })

      // 获取推荐摘要
      const summaryResponse = await recommendationService.getRecommendationSummary()

      setCurrentRecommendation(currentResponse.recommendation || null)
      setRecommendations(listResponse.recommendations || [])
      setSummary(summaryResponse)
    } catch (error) {
      console.error('获取推荐失败:', error)
      // 如果API不存在，使用模拟数据
      setMockData()
    } finally {
      setLoading(false)
    }
  }

  // 获取时间安排建议
  const fetchScheduleSuggestions = async () => {
    if (!isAuthenticated) return

    try {
      const response = await recommendationService.getScheduleSuggestions()
      setScheduleSuggestions(response.schedule_suggestions)
    } catch (error) {
      console.error('获取时间安排建议失败:', error)
      setScheduleSuggestions(null)
    }
  }

  // 模拟数据（用于演示）
  const setMockData = () => {
    const mockRecommendation = {
      task: {
        id: 'mock-1',
        title: '完成项目文档编写',
        description: '编写项目技术文档和用户手册',
        priority: 'HIGH',
        task_type: 'RIGID',
        estimated_pomodoros: 2
      },
      score: 95,
      reason: '刚性任务已到计划时间、高优先级任务、需要准时完成',
      priority_level: '紧急'
    }

    const mockRecommendations = [
      mockRecommendation,
      {
        task: {
          id: 'mock-2',
          title: '代码审查',
          description: '审查团队成员提交的代码',
          priority: 'MEDIUM',
          task_type: 'FLEXIBLE',
          estimated_pomodoros: 1
        },
        score: 75,
        reason: '任务已到计划时间、中等优先级任务',
        priority_level: '高'
      },
      {
        task: {
          id: 'mock-3',
          title: '学习新技术',
          description: '学习React Hooks最佳实践',
          priority: 'LOW',
          task_type: 'FLEXIBLE',
          estimated_pomodoros: 3
        },
        score: 45,
        reason: '建议执行此任务',
        priority_level: '中'
      }
    ]

    setCurrentRecommendation(mockRecommendation)
    setRecommendations(mockRecommendations)
    setSummary({
      current_recommendation: mockRecommendation,
      top_recommendations_count: 3,
      priority_distribution: { '紧急': 1, '高': 1, '中': 1 },
      has_recommendations: true
    })
  }

  // 开始番茄钟
  const startPomodoro = async (task) => {
    try {
      // 创建番茄钟会话
      const response = await pomodoroService.createSession({
        task_id: task.id,
        planned_duration: 25,
        session_type: 'FOCUS'
      })

      const session = response.pomodoro_session

      // 开始会话
      await pomodoroService.startSession(session.id)

      // 跳转到番茄钟页面
      window.location.href = '/pomodoro'
    } catch (error) {
      console.error('启动番茄钟失败:', error)
      // 如果API失败，也跳转到番茄钟页面
      window.location.href = '/pomodoro'
    }
  }

  // 获取优先级颜色
  const getPriorityColor = (level) => {
    const colorMap = {
      '紧急': '#ff4d4f',
      '高': '#fa8c16',
      '中': '#1890ff',
      '低': '#52c41a'
    }
    return colorMap[level] || '#666'
  }

  // 获取优先级图标
  const getPriorityIcon = (level) => {
    const iconMap = {
      '紧急': <FireOutlined />,
      '高': <ThunderboltOutlined />,
      '中': <StarOutlined />,
      '低': <ClockCircleOutlined />
    }
    return iconMap[level] || <ClockCircleOutlined />
  }

  // 刷新数据
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1)
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchRecommendations()
      fetchScheduleSuggestions()
    }
  }, [isAuthenticated, refreshKey])

  useEffect(() => {
    // 每30秒自动刷新推荐
    const interval = setInterval(() => {
      fetchRecommendations()
    }, 30000)

    return () => clearInterval(interval)
  }, [isAuthenticated])

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <BulbOutlined /> 智能调度
          </Title>
          <Text type="secondary">基于AI的任务推荐，让您专注当下</Text>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ScheduleOutlined />}
              onClick={fetchScheduleSuggestions}
            >
              时间建议
            </Button>
            <Button
              type="primary"
              icon={<RocketOutlined />}
              onClick={handleRefresh}
            >
              刷新推荐
            </Button>
          </Space>
        </Col>
      </Row>

      {summary && (
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="待推荐任务"
                value={summary.top_recommendations_count}
                prefix={<BulbOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="紧急任务"
                value={summary.priority_distribution?.['紧急'] || 0}
                prefix={<FireOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="高优先级"
                value={summary.priority_distribution?.['高'] || 0}
                prefix={<ThunderboltOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="推荐质量"
                value={currentRecommendation ? "优秀" : "一般"}
                prefix={<StarOutlined />}
                valueStyle={{
                  color: currentRecommendation ? '#52c41a' : '#faad14'
                }}
              />
            </Card>
          </Col>
        </Row>
      )}

      <Row gutter={16}>
        <Col span={12}>
          {/* 当前推荐 */}
          <Card
            title={
              <Space>
                <BulbOutlined />
                现在该做什么？
              </Space>
            }
            extra={
              <Badge
                status={currentRecommendation ? 'processing' : 'default'}
                text={currentRecommendation ? '活跃' : '无任务'}
              />
            }
            style={{ marginBottom: '16px' }}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Spin size="large" />
                <div style={{ marginTop: '16px' }}>正在分析您的任务...</div>
              </div>
            ) : currentRecommendation ? (
              <div>
                <div style={{ marginBottom: '16px' }}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Tag
                        color={getPriorityColor(currentRecommendation.priority_level)}
                        icon={getPriorityIcon(currentRecommendation.priority_level)}
                        style={{ fontSize: '14px' }}
                      >
                        {currentRecommendation.priority_level}优先级
                      </Tag>
                      <Tag color="blue">
                        推荐分数: {currentRecommendation.score}
                      </Tag>
                    </div>
                    <Title level={4} style={{ margin: '8px 0' }}>
                      {currentRecommendation.task.title}
                    </Title>
                    {currentRecommendation.task.description && (
                      <Paragraph type="secondary" style={{ margin: '8px 0' }}>
                        {currentRecommendation.task.description}
                      </Paragraph>
                    )}
                    <div>
                      <Text strong>推荐原因：</Text>
                      <Text>{currentRecommendation.reason}</Text>
                    </div>
                    <div style={{ marginTop: '12px' }}>
                      <Space>
                        <Text type="secondary">
                          预估番茄钟: {currentRecommendation.task.estimated_pomodoros || 1}个
                        </Text>
                        <Text type="secondary">
                          类型: {currentRecommendation.task.task_type === 'RIGID' ? '刚性' : '柔性'}
                        </Text>
                      </Space>
                    </div>
                  </Space>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<RocketOutlined />}
                    onClick={() => startPomodoro(currentRecommendation.task)}
                    style={{ marginRight: '8px' }}
                  >
                    开始专注
                  </Button>
                  <Button
                    onClick={handleRefresh}
                  >
                    换一个
                  </Button>
                </div>
              </div>
            ) : (
              <Empty
                description="暂无推荐任务"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button type="primary" onClick={() => window.location.href = '/tasks'}>
                  创建任务
                </Button>
              </Empty>
            )}
          </Card>

          {/* 推荐列表 */}
          <Card
            title="更多推荐"
            extra={
              <Text type="secondary">
                按优先级排序
              </Text>
            }
          >
            {recommendations.length > 0 ? (
              <List
                dataSource={recommendations}
                renderItem={(item, index) => (
                  <List.Item
                    actions={[
                      <Button
                        type="link"
                        size="small"
                        onClick={() => startPomodoro(item.task)}
                      >
                        开始
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          style={{
                            backgroundColor: getPriorityColor(item.priority_level)
                          }}
                          icon={getPriorityIcon(item.priority_level)}
                        >
                          {index + 1}
                        </Avatar>
                      }
                      title={
                        <Space>
                          <Text>{item.task.title}</Text>
                          <Tag
                            color={getPriorityColor(item.priority_level)}
                            size="small"
                          >
                            {item.score}分
                          </Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {item.reason}
                          </Text>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty
                description="暂无更多推荐"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </Card>
        </Col>

        <Col span={12}>
          {/* 时间安排建议 */}
          {scheduleSuggestions ? (
            <Card
              title="今日时间安排"
              extra={
                <Text type="secondary">
                  共{scheduleSuggestions.total_tasks}个任务
                </Text>
              }
            >
              {scheduleSuggestions.time_slots.length > 0 ? (
                <Timeline>
                  {scheduleSuggestions.time_slots.map((slot, index) => (
                    <Timeline.Item
                      key={index}
                      color={slot.recommended_task ? 'blue' : 'gray'}
                      dot={slot.recommended_task ? <BulbOutlined /> : <ClockCircleOutlined />}
                    >
                      <div>
                        <Text strong>{slot.time_range}</Text>
                        <div style={{ marginTop: '4px' }}>
                          <Space direction="vertical" size="small">
                            <Text type="secondary">
                              {slot.count}个任务
                            </Text>
                            {slot.recommended_task && (
                              <div>
                                <Text strong>推荐: </Text>
                                <Text>{slot.recommended_task.title}</Text>
                              </div>
                            )}
                          </Space>
                        </div>
                      </div>
                    </Timeline.Item>
                  ))}
                </Timeline>
              ) : (
                <Empty
                  description="今日暂无时间安排"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              )}

              {scheduleSuggestions.recommendations.length > 0 && (
                <Alert
                  message="智能建议"
                  description={
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      {scheduleSuggestions.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  }
                  type="info"
                  style={{ marginTop: '16px' }}
                />
              )}
            </Card>
          ) : (
            <Card title="今日时间安排">
              <Empty
                description="时间安排功能加载中..."
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            </Card>
          )}

          {/* 推荐算法说明 */}
          <Card title="推荐算法说明" style={{ marginTop: '16px' }}>
            <Paragraph style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <Text strong>优先级规则：</Text>
              <br />
              1. <Text mark>刚性任务优先</Text> - 已到计划时间的刚性任务获得最高优先级
              <br />
              2. <Text mark>时间紧迫性</Text> - 距离计划时间越近，推荐分数越高
              <br />
              3. <Text mark>任务优先级</Text> - HIGH/MEDIUM/LOW分别获得不同加成
              <br />
              4. <Text mark>任务类型</Text> - 刚性任务比柔性任务权重更高
            </Paragraph>
            <Paragraph style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <Text strong>推荐分数范围：</Text> 0-120分，分数越高越推荐
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default IntelligentScheduler