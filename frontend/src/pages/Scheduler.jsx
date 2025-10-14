import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  DatePicker,
  Select,
  Switch,
  message,
  Popconfirm,
  Space,
  Row,
  Col,
  Statistic,
  Tag,
  Table,
  Tooltip,
  Alert
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  PlayCircleOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../services/api'

const { Option } = Select
const { TextArea } = Input

function Scheduler() {
  const [templates, setTemplates] = useState([])
  const [timeBlocks, setTimeBlocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedDate, setSelectedDate] = useState(dayjs())
  const [templateModalVisible, setTemplateModalVisible] = useState(false)
  const [applyModalVisible, setApplyModalVisible] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [form] = Form.useForm()
  const [applyForm] = Form.useForm()

  // 获取模板列表
  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const response = await api.get('/time-block-templates')
      setTemplates(response.data)
    } catch (error) {
      message.error('获取模板列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取指定日期的时间块
  const fetchTimeBlocks = async (date) => {
    try {
      const params = `?date=${date.format('YYYY-MM-DD')}`
      const response = await api.get(`/time-blocks${params}`)
      setTimeBlocks(response.data)
    } catch (error) {
      message.error('获取时间块列表失败')
    }
  }

  useEffect(() => {
    fetchTemplates()
    fetchTimeBlocks(selectedDate)
  }, [selectedDate])

  // 创建/更新模板
  const handleTemplateSubmit = async (values) => {
    try {
      if (editingTemplate) {
        await api.put(`/time-block-templates/${editingTemplate.id}`, values)
        message.success('模板更新成功')
      } else {
        await api.post('/time-block-templates', values)
        message.success('模板创建成功')
      }

      setTemplateModalVisible(false)
      setEditingTemplate(null)
      form.resetFields()
      fetchTemplates()
    } catch (error) {
      message.error(error.response?.data?.error || '操作失败')
    }
  }

  // 应用模板到日期
  const handleApplyTemplate = async (values) => {
    try {
      const response = await api.post(`/time-block-templates/${selectedTemplate.id}/apply`, {
        date: values.date.format('YYYY-MM-DD')
      })

      const generatedBlocks = response.data.generated_time_blocks
      message.success(`模板应用成功，生成了 ${generatedBlocks.length} 个时间块`)

      setApplyModalVisible(false)
      setSelectedTemplate(null)
      applyForm.resetFields()

      // 刷新时间块列表
      const targetDate = dayjs(values.date)
      if (targetDate.isSame(selectedDate, 'day')) {
        fetchTimeBlocks(selectedDate)
      }
    } catch (error) {
      message.error(error.response?.data?.error || '应用模板失败')
    }
  }

  // 删除模板
  const handleDeleteTemplate = async (templateId) => {
    try {
      await api.delete(`/time-block-templates/${templateId}`)
      message.success('模板删除成功')
      fetchTemplates()
    } catch (error) {
      message.error(error.response?.data?.error || '删除失败')
    }
  }

  // 克隆模板
  const handleCloneTemplate = async (templateId) => {
    try {
      await api.post(`/time-block-templates/${templateId}/clone`)
      message.success('模板克隆成功')
      fetchTemplates()
    } catch (error) {
      message.error(error.response?.data?.error || '克隆失败')
    }
  }

  // 打开编辑模态框
  const openEditModal = (template = null) => {
    setEditingTemplate(template)
    if (template) {
      form.setFieldsValue({
        name: template.name,
        description: template.description,
        is_default: template.is_default
      })
    }
    setTemplateModalVisible(true)
  }

  // 关闭模态框
  const closeTemplateModal = () => {
    setTemplateModalVisible(false)
    setEditingTemplate(null)
    form.resetFields()
  }

  // 打开应用模态框
  const openApplyModal = (template) => {
    setSelectedTemplate(template)
    setApplyModalVisible(true)
  }

  // 关闭应用模态框
  const closeApplyModal = () => {
    setApplyModalVisible(false)
    setSelectedTemplate(null)
    applyForm.resetFields()
  }

  // 日期选择器
  const dateSelector = (
    <div style={{ marginBottom: '24px', textAlign: 'center' }}>
      <Space>
        <Button
          onClick={() => setSelectedDate(selectedDate.subtract(1, 'day'))}
          disabled={selectedDate.isSame(dayjs(), 'day')}
        >
          上一天
        </Button>
        <Button
          onClick={() => setSelectedDate(dayjs())}
          type={selectedDate.isSame(dayjs(), 'day') ? 'primary' : 'default'}
        >
          今天
        </Button>
        <Button
          onClick={() => setSelectedDate(selectedDate.add(1, 'day'))}
        >
          下一天
        </Button>
      </Space>
      <div style={{ marginTop: '8px', fontSize: '18px', fontWeight: 'bold' }}>
        {selectedDate.format('YYYY年MM月DD日 dddd')}
      </div>
    </div>
  )

  // 模板表格列定义
  const templateColumns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          {text}
          {record.is_default && <Tag color="blue">默认</Tag>}
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '关联时间块',
      dataIndex: 'time_block_count',
      key: 'time_block_count',
      render: (count) => `${count} 个`
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="应用到日期">
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => openApplyModal(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="克隆">
            <Button
              type="text"
              icon={<CopyOutlined />}
              onClick={() => handleCloneTemplate(record.id)}
            />
          </Tooltip>
          {!record.is_default && (
            <Tooltip title="删除">
              <Popconfirm
                title="确认删除"
                description={`确定要删除模板"${record.name}"吗？`}
                onConfirm={() => handleDeleteTemplate(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                />
              </Popconfirm>
            </Tooltip>
          )}
        </Space>
      )
    }
  ]

  // 时间块表格列定义
  const timeBlockColumns = [
    {
      title: '时间',
      key: 'time',
      render: (_, record) => (
        <span>
          {dayjs(record.start_time).format('HH:mm')} - {dayjs(record.end_time).format('HH:mm')}
        </span>
      )
    },
    {
      title: '类型',
      dataIndex: 'block_type',
      key: 'block_type',
      render: (type) => {
        const typeMap = {
          'RESEARCH': { text: '科研', color: 'blue' },
          'GROWTH': { text: '成长', color: 'green' },
          'REST': { text: '休息', color: 'red' },
          'ENTERTAINMENT': { text: '娱乐', color: 'orange' },
          'REVIEW': { text: '复盘', color: 'purple' }
        }
        const config = typeMap[type] || { text: type, color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      }
    },
    {
      title: '持续时间',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration) => `${duration} 分钟`
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? '活跃' : '未开始'}
        </Tag>
      )
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
            时间块调度
          </h1>
          <p style={{ margin: '8px 0 0', color: '#666' }}>
            管理时间块模板，快速应用到日期
          </p>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openEditModal()}
            size="large"
          >
            创建模板
          </Button>
        </Col>
      </Row>

      {dateSelector}

      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="模板总数"
              value={templates.length}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="今日时间块"
              value={timeBlocks.length}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="活跃时间块"
              value={timeBlocks.filter(tb => tb.is_active).length}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 模板管理区域 */}
      <Card title="时间块模板" style={{ marginBottom: '24px' }}>
        <Table
          columns={templateColumns}
          dataSource={templates}
          rowKey="id"
          loading={loading}
          pagination={false}
          locale={{
            emptyText: '暂无模板，点击"创建模板"开始'
          }}
        />
      </Card>

      {/* 今日时间块展示 */}
      <Card title={`${selectedDate.format('MM月DD日')} 时间块安排`}>
        {timeBlocks.length > 0 ? (
          <Table
            columns={timeBlockColumns}
            dataSource={timeBlocks}
            rowKey="id"
            pagination={false}
            size="small"
          />
        ) : (
          <Alert
            message="暂无时间块安排"
            description="请选择一个模板应用到当前日期，或手动创建时间块"
            type="info"
            showIcon
            icon={<ExclamationCircleOutlined />}
          />
        )}
      </Card>

      {/* 创建/编辑模板模态框 */}
      <Modal
        title={editingTemplate ? '编辑模板' : '创建模板'}
        open={templateModalVisible}
        onCancel={closeTemplateModal}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleTemplateSubmit}
        >
          <Form.Item
            label="模板名称"
            name="name"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="请输入模板名称" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea
              rows={4}
              placeholder="请输入模板描述（可选）"
            />
          </Form.Item>

          <Form.Item
            label="设为默认模板"
            name="is_default"
            valuePropName="checked"
          >
            <Switch checkedChildren="是" unCheckedChildren="否" />
          </Form.Item>

          <Alert
            message="预设模板"
            description="系统会根据模板名称自动生成对应的时间块安排：标准工作日、深度工作模式、学习日模式"
            type="info"
            showIcon
            style={{ marginBottom: '16px' }}
          />

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeTemplateModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingTemplate ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 应用模板模态框 */}
      <Modal
        title={`应用模板: ${selectedTemplate?.name}`}
        open={applyModalVisible}
        onCancel={closeApplyModal}
        footer={null}
        width={400}
      >
        <Form
          form={applyForm}
          layout="vertical"
          onFinish={handleApplyTemplate}
        >
          <Form.Item
            label="选择日期"
            name="date"
            rules={[{ required: true, message: '请选择日期' }]}
            initialValue={dayjs()}
          >
            <DatePicker
              style={{ width: '100%' }}
              placeholder="请选择要应用模板的日期"
              disabledDate={(current) => current && current < dayjs().startOf('day')}
            />
          </Form.Item>

          <Alert
            message="提示"
            description="应用模板将会在选定日期生成对应的时间块，如果该日期已有时间块，可能会产生时间冲突。"
            type="warning"
            showIcon
            style={{ marginBottom: '16px' }}
          />

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeApplyModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                应用模板
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Scheduler