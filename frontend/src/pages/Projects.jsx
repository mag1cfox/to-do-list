import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  List,
  Modal,
  Form,
  Input,
  ColorPicker,
  message,
  Popconfirm,
  Space,
  Tag,
  Row,
  Col,
  Statistic
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ProjectOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  FireOutlined
} from '@ant-design/icons'
import api from '../services/api'

const { TextArea } = Input

function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [form] = Form.useForm()

  // 获取项目列表
  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await api.get('/projects')
      setProjects(response.data)
    } catch (error) {
      message.error('获取项目列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  // 创建/更新项目
  const handleSubmit = async (values) => {
    try {
      if (editingProject) {
        await api.put(`/projects/${editingProject.id}`, values)
        message.success('项目更新成功')
      } else {
        await api.post('/projects', values)
        message.success('项目创建成功')
      }
      setModalVisible(false)
      setEditingProject(null)
      form.resetFields()
      fetchProjects()
    } catch (error) {
      message.error(error.response?.data?.error || '操作失败')
    }
  }

  // 删除项目
  const handleDelete = async (projectId) => {
    try {
      await api.delete(`/projects/${projectId}`)
      message.success('项目删除成功')
      fetchProjects()
    } catch (error) {
      message.error(error.response?.data?.error || '删除失败')
    }
  }

  // 打开编辑模态框
  const openEditModal = (project = null) => {
    setEditingProject(project)
    if (project) {
      form.setFieldsValue({
        name: project.name,
        description: project.description,
        color: project.color
      })
    }
    setModalVisible(true)
  }

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false)
    setEditingProject(null)
    form.resetFields()
  }

  // 格式化时间显示
  const formatTime = (minutes) => {
    if (!minutes) return '0分钟'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) {
      return `${hours}小时${mins > 0 ? mins + '分钟' : ''}`
    }
    return `${mins}分钟`
  }

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
            项目管理
          </h1>
          <p style={{ margin: '8px 0 0', color: '#666' }}>
            管理您的项目，跟踪进度和任务
          </p>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openEditModal()}
            size="large"
          >
            创建项目
          </Button>
        </Col>
      </Row>

      {/* 项目统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={projects.length}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总预估时间"
              value={formatTime(projects.reduce((sum, project) => sum + project.total_estimated_time, 0))}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总实际时间"
              value={formatTime(projects.reduce((sum, project) => sum + project.total_actual_time, 0))}
              prefix={<FireOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均完成率"
              value={projects.length > 0 ?
                Math.round(projects.reduce((sum, project) => sum + project.completion_progress, 0) / projects.length * 100) : 0}
              suffix="%"
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 项目列表 */}
      <List
        loading={loading}
        dataSource={projects}
        renderItem={(project) => (
          <Card
            key={project.id}
            style={{ marginBottom: '16px' }}
            size="small"
            title={
              <Space>
                <div
                  style={{
                    width: '12px',
                    height: '12px',
                    backgroundColor: project.color,
                    borderRadius: '2px'
                  }}
                />
                {project.name}
                <Tag color={project.color}>
                  {project.task_count} 个任务
                </Tag>
              </Space>
            }
            extra={
              <Space>
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => openEditModal(project)}
                />
                <Popconfirm
                  title="确认删除"
                  description={`确定要删除项目"${project.name}"吗？此操作不可恢复。`}
                  onConfirm={() => handleDelete(project.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                  />
                </Popconfirm>
              </Space>
            }
          >
            {project.description && (
              <p style={{ margin: '0 0 8px', color: '#666' }}>
                {project.description}
              </p>
            )}
            <Row gutter={16}>
              <Col span={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: project.color }}>
                    {project.task_count}
                  </div>
                  <div style={{ color: '#999', fontSize: '12px' }}>任务数量</div>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                    {formatTime(project.total_estimated_time)}
                  </div>
                  <div style={{ color: '#999', fontSize: '12px' }}>预估时间</div>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                    {Math.round(project.completion_progress * 100)}%
                  </div>
                  <div style={{ color: '#999', fontSize: '12px' }}>完成进度</div>
                </div>
              </Col>
            </Row>
          </Card>
        )}
      />

      {/* 创建/编辑项目模态框 */}
      <Modal
        title={editingProject ? '编辑项目' : '创建项目'}
        open={modalVisible}
        onCancel={closeModal}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="项目名称"
            name="name"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>

          <Form.Item
            label="项目颜色"
            name="color"
            rules={[{ required: true, message: '请选择项目颜色' }]}
          >
            <ColorPicker
              showText
              format="hex"
              placeholder="选择项目颜色"
            />
          </Form.Item>

          <Form.Item
            label="项目描述"
            name="description"
          >
            <TextArea
              rows={4}
              placeholder="请输入项目描述（可选）"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingProject ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Projects