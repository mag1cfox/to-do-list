import { useState, useEffect } from 'react'
import { Card, Button, Table, Space, Tag, message, Modal, Form, Input, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { taskService } from '../services/api'
import { useAuthStore } from '../stores/authStore'
import dayjs from 'dayjs'

const { Option } = Select

function Tasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTask, setEditingTask] = useState(null)
  const [form] = Form.useForm()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      loadTasks()
    }
  }, [isAuthenticated])

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
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个任务吗？',
      onOk: async () => {
        try {
          await taskService.deleteTask(taskId)
          message.success('删除成功')
          loadTasks()
        } catch (error) {
          message.error('删除失败')
        }
      }
    })
  }

  const handleSubmit = async (values) => {
    try {
      const taskData = {
        ...values,
        planned_start_time: values.planned_start_time?.toISOString()
      }

      if (editingTask) {
        await taskService.updateTask(editingTask.id, taskData)
        message.success('更新成功')
      } else {
        await taskService.createTask(taskData)
        message.success('创建成功')
      }

      setModalVisible(false)
      loadTasks()
    } catch (error) {
      message.error(editingTask ? '更新失败' : '创建失败')
    }
  }

  const columns = [
    {
      title: '任务标题',
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          PENDING: { color: 'default', text: '待开始' },
          IN_PROGRESS: { color: 'processing', text: '进行中' },
          COMPLETED: { color: 'success', text: '已完成' },
          CANCELLED: { color: 'error', text: '已取消' }
        }
        const statusInfo = statusMap[status] || { color: 'default', text: status }
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
      }
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => {
        const priorityMap = {
          HIGH: { color: 'red', text: '高' },
          MEDIUM: { color: 'orange', text: '中' },
          LOW: { color: 'green', text: '低' }
        }
        const priorityInfo = priorityMap[priority] || { color: 'default', text: priority }
        return <Tag color={priorityInfo.color}>{priorityInfo.text}</Tag>
      }
    },
    {
      title: '计划开始时间',
      dataIndex: 'planned_start_time',
      key: 'planned_start_time',
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
    },
    {
      title: '预估番茄数',
      dataIndex: 'estimated_pomodoros',
      key: 'estimated_pomodoros'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ]

  if (!isAuthenticated) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <h3>请先登录以管理任务</h3>
        </div>
      </Card>
    )
  }

  return (
    <div>
      <Card
        title="任务管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建任务
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
            showTotal: (total) => `共 ${total} 条任务`
          }}
        />
      </Card>

      <Modal
        title={editingTask ? '编辑任务' : '新建任务'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="任务标题"
            name="title"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="请输入任务标题" />
          </Form.Item>

          <Form.Item
            label="任务描述"
            name="description"
          >
            <Input.TextArea rows={3} placeholder="请输入任务描述（可选）" />
          </Form.Item>

          <Form.Item
            label="计划开始时间"
            name="planned_start_time"
            rules={[{ required: true, message: '请选择计划开始时间' }]}
          >
            <DatePicker
              showTime
              style={{ width: '100%' }}
              placeholder="请选择计划开始时间"
            />
          </Form.Item>

          <Form.Item
            label="预估番茄数"
            name="estimated_pomodoros"
            initialValue={1}
          >
            <Select>
              <Option value={1}>1个番茄</Option>
              <Option value={2}>2个番茄</Option>
              <Option value={3}>3个番茄</Option>
              <Option value={4}>4个番茄</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="任务类型"
            name="task_type"
            initialValue="FLEXIBLE"
          >
            <Select>
              <Option value="FLEXIBLE">柔性任务</Option>
              <Option value="RIGID">刚性任务</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="优先级"
            name="priority"
            initialValue="MEDIUM"
          >
            <Select>
              <Option value="LOW">低</Option>
              <Option value="MEDIUM">中</Option>
              <Option value="HIGH">高</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingTask ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Tasks