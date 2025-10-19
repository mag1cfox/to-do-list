import { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Table,
  Space,
  Tag,
  message,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Row,
  Col,
  Statistic,
  Badge,
  Tooltip,
  Popconfirm
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { taskService, taskCategoryService, projectService } from '../services/api'
import { useAuthStore } from '../stores/authStore'
import dayjs from 'dayjs'

const { Option } = Select
const { TextArea } = Input

function Tasks() {
  const [tasks, setTasks] = useState([])
  const [categories, setCategories] = useState([])
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTask, setEditingTask] = useState(null)
  const [form] = Form.useForm()
  const { isAuthenticated } = useAuthStore()

  // 统计数据
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    inProgress: 0,
    completed: 0
  })

  useEffect(() => {
    if (isAuthenticated) {
      loadData()
    }
  }, [isAuthenticated])

  const loadData = async () => {
    setLoading(true)
    try {
      const [tasksRes, categoriesRes, projectsRes] = await Promise.all([
        taskService.getTasks(),
        taskCategoryService.getCategories(),
        projectService.getProjects()
      ])

      setTasks(tasksRes.tasks || [])
      setCategories(categoriesRes || [])
      setProjects(projectsRes || [])

      // 计算统计数据
      const taskStats = {
        total: tasksRes.tasks?.length || 0,
        pending: tasksRes.tasks?.filter(t => t.status === 'PENDING').length || 0,
        inProgress: tasksRes.tasks?.filter(t => t.status === 'IN_PROGRESS').length || 0,
        completed: tasksRes.tasks?.filter(t => t.status === 'COMPLETED').length || 0
      }
      setStats(taskStats)
    } catch (error) {
      message.error('加载数据失败: ' + (error.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  const loadTasks = async () => {
    setLoading(true)
    try {
      const response = await taskService.getTasks()
      setTasks(response.tasks || [])
    } catch (error) {
      message.error('获取任务列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingTask(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (task) => {
    setEditingTask(task)
    form.setFieldsValue({
      ...task,
      planned_start_time: task.planned_start_time ? dayjs(task.planned_start_time) : null
    })
    setModalVisible(true)
  }

  const handleDelete = async (taskId) => {
    try {
      await taskService.deleteTask(taskId)
      message.success('任务删除成功')
      loadData()
    } catch (error) {
      message.error('删除失败: ' + (error.error || error.message))
    }
  }

  const handleStartTask = async (task) => {
    try {
      await taskService.updateTask(task.id, { status: 'IN_PROGRESS' })
      message.success('任务已开始')
      loadData()
    } catch (error) {
      message.error('操作失败: ' + (error.error || error.message))
    }
  }

  const handleCompleteTask = async (task) => {
    try {
      await taskService.updateTask(task.id, { status: 'COMPLETED' })
      message.success('任务已完成')
      loadData()
    } catch (error) {
      message.error('操作失败: ' + (error.error || error.message))
    }
  }

  const handleSubmit = async (values) => {
    try {
      const taskData = {
        ...values,
        planned_start_time: values.planned_start_time ? values.planned_start_time.toISOString() : null
      }

      if (editingTask) {
        await taskService.updateTask(editingTask.id, taskData)
        message.success('任务更新成功')
      } else {
        await taskService.createTask(taskData)
        message.success('任务创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error) {
      message.error('操作失败: ' + (error.error || error.message))
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'default',
      'IN_PROGRESS': 'processing',
      'COMPLETED': 'success',
      'CANCELLED': 'error'
    }
    return colors[status] || 'default'
  }

  const getStatusText = (status) => {
    const texts = {
      'PENDING': '待开始',
      'IN_PROGRESS': '进行中',
      'COMPLETED': '已完成',
      'CANCELLED': '已取消'
    }
    return texts[status] || status
  }

  const getPriorityColor = (priority) => {
    const colors = {
      'HIGH': 'red',
      'MEDIUM': 'orange',
      'LOW': 'green'
    }
    return colors[priority] || 'default'
  }

  const getPriorityText = (priority) => {
    const texts = {
      'HIGH': '高',
      'MEDIUM': '中',
      'LOW': '低'
    }
    return texts[priority] || priority
  }

  const getTaskTypeText = (type) => {
    const texts = {
      'RIGID': '刚性',
      'FLEXIBLE': '柔性'
    }
    return texts[type] || type
  }

  const columns = [
    {
      title: '任务标题',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <Space>
          <span style={{ fontWeight: record.priority === 'HIGH' ? 'bold' : 'normal' }}>
            {text}
          </span>
          {record.priority === 'HIGH' && <ExclamationCircleOutlined style={{ color: 'red' }} />}
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => text || '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Badge status={getStatusColor(status)} text={getStatusText(status)} />
      )
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => (
        <Tag color={getPriorityColor(priority)}>
          {getPriorityText(priority)}
        </Tag>
      )
    },
    {
      title: '类型',
      dataIndex: 'task_type',
      key: 'task_type',
      render: (type) => (
        <Tag>{getTaskTypeText(type)}</Tag>
      )
    },
    {
      title: '预估番茄数',
      dataIndex: 'estimated_pomodoros',
      key: 'estimated_pomodoros',
      render: (num) => `${num} 🍅`
    },
    {
      title: '计划开始时间',
      dataIndex: 'planned_start_time',
      key: 'planned_start_time',
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          {record.status === 'PENDING' && (
            <Tooltip title="开始任务">
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                size="small"
                onClick={() => handleStartTask(record)}
              />
            </Tooltip>
          )}
          {record.status === 'IN_PROGRESS' && (
            <Tooltip title="完成任务">
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                size="small"
                onClick={() => handleCompleteTask(record)}
              />
            </Tooltip>
          )}
          <Tooltip title="编辑">
            <Button
              icon={<EditOutlined />}
              size="small"
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除这个任务吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                danger
                icon={<DeleteOutlined />}
                size="small"
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ]

  if (!isAuthenticated) {
    return (
      <Card title="任务管理">
        <p>请先登录以查看任务</p>
      </Card>
    )
  }

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.total}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待开始"
              value={stats.pending}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="进行中"
              value={stats.inProgress}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completed}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="任务管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            创建任务
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个任务`
          }}
        />
      </Card>

      <Modal
        title={editingTask ? '编辑任务' : '创建任务'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            estimated_pomodoros: 1,
            task_type: 'FLEXIBLE',
            priority: 'MEDIUM'
          }}
        >
          <Form.Item
            name="title"
            label="任务标题"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="请输入任务标题" />
          </Form.Item>

          <Form.Item
            name="description"
            label="任务描述"
          >
            <TextArea
              rows={3}
              placeholder="请输入任务描述（可选）"
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="category_id"
                label="任务类别"
                rules={[{ required: true, message: '请选择任务类别' }]}
              >
                <Select placeholder="请选择任务类别">
                  {categories.map(category => (
                    <Option key={category.id} value={category.id}>
                      <Tag color={category.color}>{category.name}</Tag>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="project_id"
                label="所属项目"
              >
                <Select placeholder="请选择所属项目（可选）" allowClear>
                  {projects.map(project => (
                    <Option key={project.id} value={project.id}>
                      <Tag color={project.color}>{project.name}</Tag>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="task_type"
                label="任务类型"
                rules={[{ required: true, message: '请选择任务类型' }]}
              >
                <Select>
                  <Option value="FLEXIBLE">柔性任务</Option>
                  <Option value="RIGID">刚性任务</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="priority"
                label="优先级"
                rules={[{ required: true, message: '请选择优先级' }]}
              >
                <Select>
                  <Option value="LOW">低</Option>
                  <Option value="MEDIUM">中</Option>
                  <Option value="HIGH">高</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="estimated_pomodoros"
                label="预估番茄数"
                rules={[{ required: true, message: '请输入预估番茄数' }]}
              >
                <Select>
                  <Option value={1}>1个番茄</Option>
                  <Option value={2}>2个番茄</Option>
                  <Option value={3}>3个番茄</Option>
                  <Option value={4}>4个番茄</Option>
                  <Option value={5}>5个番茄</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="planned_start_time"
            label="计划开始时间"
            rules={[{ required: true, message: '请选择计划开始时间' }]}
          >
            <DatePicker
              showTime
              style={{ width: '100%' }}
              placeholder="请选择计划开始时间"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Tasks