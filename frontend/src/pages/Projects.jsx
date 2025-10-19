import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  List,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Space,
  Tag,
  Row,
  Col,
  Statistic,
  Progress,
  Empty,
  Tooltip
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ProjectOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  FireOutlined,
  FolderOutlined
} from '@ant-design/icons'
import { projectService } from '../services/api'
import { useAuthStore } from '../stores/authStore'

const { TextArea } = Input

function Projects() {
  const { isAuthenticated } = useAuthStore()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [form] = Form.useForm()

  // 预设颜色选项
  const colorOptions = [
    { label: '蓝色', value: '#1890ff' },
    { label: '绿色', value: '#52c41a' },
    { label: '橙色', value: '#fa8c16' },
    { label: '红色', value: '#f5222d' },
    { label: '紫色', value: '#722ed1' },
    { label: '青色', value: '#13c2c2' },
    { label: '粉色', value: '#eb2f96' },
    { label: '灰色', value: '#8c8c8c' }
  ]

  // 获取项目列表
  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await projectService.getProjects()
      setProjects(response || [])
    } catch (error) {
      message.error('获取项目列表失败: ' + (error.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchProjects()
    }
  }, [isAuthenticated])

  // 创建/更新项目
  const handleSubmit = async (values) => {
    try {
      if (editingProject) {
        await projectService.updateProject(editingProject.id, values)
        message.success('项目更新成功')
      } else {
        await projectService.createProject(values)
        message.success('项目创建成功')
      }
      setModalVisible(false)
      setEditingProject(null)
      form.resetFields()
      fetchProjects()
    } catch (error) {
      message.error('操作失败: ' + (error.error || error.message))
    }
  }

  // 删除项目
  const handleDelete = async (projectId) => {
    try {
      await projectService.deleteProject(projectId)
      message.success('项目删除成功')
      fetchProjects()
    } catch (error) {
      message.error('删除失败: ' + (error.error || error.message))
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

  // 未登录状态
  if (!isAuthenticated) {
    return (
      <Card title="项目管理">
        <Empty
          description="请先登录以管理项目"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    )
  }

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
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
      {projects.length === 0 && !loading ? (
        <Card>
          <Empty
            description="暂无项目"
            image={<FolderOutlined style={{ fontSize: '64px', color: '#ccc' }} />}
          >
            <Button type="primary" icon={<PlusOutlined />} onClick={() => openEditModal()}>
              创建第一个项目
            </Button>
          </Empty>
        </Card>
      ) : (
        <List
          loading={loading}
          dataSource={projects}
          renderItem={(project) => (
            <Card
              key={project.id}
              style={{ marginBottom: 16 }}
              size="default"
              title={
                <Space>
                  <div
                    style={{
                      width: '16px',
                      height: '16px',
                      backgroundColor: project.color,
                      borderRadius: '4px',
                      border: '1px solid #f0f0f0'
                    }}
                  />
                  <span style={{ fontWeight: 600 }}>{project.name}</span>
                  <Tag color={project.color}>
                    {project.task_count || 0} 个任务
                  </Tag>
                </Space>
              }
              extra={
                <Space>
                  <Tooltip title="编辑项目">
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => openEditModal(project)}
                    />
                  </Tooltip>
                  <Popconfirm
                    title="确认删除"
                    description={`确定要删除项目"${project.name}"吗？此操作不可恢复。`}
                    onConfirm={() => handleDelete(project.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Tooltip title="删除项目">
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                      />
                    </Tooltip>
                  </Popconfirm>
                </Space>
              }
            >
              {project.description && (
                <p style={{ margin: '0 0 16px', color: '#666', fontSize: '14px' }}>
                  {project.description}
                </p>
              )}

              <Row gutter={24}>
                <Col span={8}>
                  <div style={{ textAlign: 'center', padding: '16px 0' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: project.color, marginBottom: '4px' }}>
                      {project.task_count || 0}
                    </div>
                    <div style={{ color: '#999', fontSize: '14px' }}>任务数量</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center', padding: '16px 0' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1890ff', marginBottom: '4px' }}>
                      {formatTime(project.total_estimated_time || 0)}
                    </div>
                    <div style={{ color: '#999', fontSize: '14px' }}>预估时间</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center', padding: '16px 0' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#52c41a', marginBottom: '4px' }}>
                      {Math.round((project.completion_progress || 0) * 100)}%
                    </div>
                    <div style={{ color: '#999', fontSize: '14px', marginBottom: '8px' }}>完成进度</div>
                    <Progress
                      percent={Math.round((project.completion_progress || 0) * 100)}
                      size="small"
                      strokeColor={project.color}
                    />
                  </div>
                </Col>
              </Row>
            </Card>
          )}
        />
      )}

      {/* 创建/编辑项目模态框 */}
      <Modal
        title={editingProject ? '编辑项目' : '创建项目'}
        open={modalVisible}
        onCancel={closeModal}
        footer={null}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            color: '#1890ff'
          }}
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
            <Select placeholder="请选择项目颜色">
              {colorOptions.map(color => (
                <Select.Option key={color.value} value={color.value}>
                  <Space>
                    <div
                      style={{
                        width: '16px',
                        height: '16px',
                        backgroundColor: color.value,
                        borderRadius: '4px',
                        border: '1px solid #f0f0f0'
                      }}
                    />
                    {color.label}
                  </Space>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="项目描述"
            name="description"
          >
            <TextArea
              rows={4}
              placeholder="请输入项目描述（可选）"
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingProject ? '更新项目' : '创建项目'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Projects