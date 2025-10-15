import React, { useState, useEffect } from 'react';
import {
    Card,
    List,
    Button,
    Modal,
    Form,
    Input,
    ColorPicker,
    Space,
    message,
    Typography,
    Row,
    Col,
    Tag,
    Tooltip,
    Popconfirm,
    Empty,
    Spin,
    Statistic,
    Progress,
    Divider,
    Badge
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    ProjectOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    CheckCircleOutlined,
    FolderOpenOutlined,
    EyeOutlined,
    ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const ProjectManager = ({ onProjectSelect, showProjectTasks = false }) => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingProject, setEditingProject] = useState(null);
    const [projectStats, setProjectStats] = useState({});
    const [form] = Form.useForm();

    // 获取认证token
    const getToken = () => {
        return localStorage.getItem('access_token');
    };

    // API配置
    const api = axios.create({
        baseURL: 'http://localhost:5000/api',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        }
    });

    // 获取项目列表
    const fetchProjects = async () => {
        try {
            setLoading(true);
            const response = await api.get('/projects/');
            if (response.status === 200) {
                const projectsList = response.data || [];
                setProjects(projectsList);

                // 获取每个项目的统计数据
                await fetchProjectStats(projectsList);
            }
        } catch (error) {
            console.error('获取项目列表失败:', error);
            message.error('获取项目列表失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取项目统计数据
    const fetchProjectStats = async (projectsList) => {
        try {
            // 获取任务数据用于统计
            const tasksResponse = await api.get('/tasks/');
            if (tasksResponse.status === 200) {
                const tasks = tasksResponse.data.tasks || [];
                const stats = {};

                projectsList.forEach(project => {
                    const projectTasks = tasks.filter(task => task.project_id === project.id);
                    const completedTasks = projectTasks.filter(task => task.status === 'COMPLETED');
                    const totalEstimatedTime = projectTasks.reduce((sum, task) =>
                        sum + (task.estimated_pomodoros || 0), 0);

                    stats[project.id] = {
                        totalTasks: projectTasks.length,
                        completedTasks: completedTasks.length,
                        completionRate: projectTasks.length > 0
                            ? Math.round((completedTasks.length / projectTasks.length) * 100)
                            : 0,
                        totalEstimatedTime: totalEstimatedTime,
                        tasks: projectTasks
                    };
                });

                setProjectStats(stats);
            }
        } catch (error) {
            console.error('获取项目统计数据失败:', error);
        }
    };

    // 创建或更新项目
    const handleSubmit = async (values) => {
        try {
            const projectData = {
                name: values.name,
                color: values.color?.toHexString() || '#1890ff',
                description: values.description
            };

            let response;
            if (editingProject) {
                response = await api.put(`/projects/${editingProject.id}`, projectData);
            } else {
                response = await api.post('/projects/', projectData);
            }

            if (response.status === (editingProject ? 200 : 201)) {
                message.success(editingProject ? '项目更新成功' : '项目创建成功');
                setModalVisible(false);
                setEditingProject(null);
                form.resetFields();
                fetchProjects();
            }
        } catch (error) {
            console.error(`${editingProject ? '更新' : '创建'}项目失败:`, error);
            const errorMessage = error.response?.data?.error ||
                `${editingProject ? '更新' : '创建'}项目失败`;
            message.error(errorMessage);
        }
    };

    // 删除项目
    const handleDeleteProject = async (projectId) => {
        try {
            const response = await api.delete(`/projects/${projectId}`);
            if (response.status === 200) {
                message.success('项目删除成功');
                fetchProjects();
            }
        } catch (error) {
            console.error('删除项目失败:', error);
            const errorMessage = error.response?.data?.error || '删除项目失败';
            message.error(errorMessage);
        }
    };

    // 打开编辑模态框
    const handleEditProject = (project) => {
        setEditingProject(project);
        form.setFieldsValue({
            name: project.name,
            description: project.description,
            color: project.color
        });
        setModalVisible(true);
    };

    // 打开创建模态框
    const handleCreateProject = () => {
        setEditingProject(null);
        form.resetFields();
        form.setFieldsValue({
            color: '#1890ff'
        });
        setModalVisible(true);
    };

    // 关闭模态框
    const handleModalCancel = () => {
        setModalVisible(false);
        setEditingProject(null);
        form.resetFields();
    };

    // 查看项目任务
    const handleViewProjectTasks = (project) => {
        if (onProjectSelect) {
            onProjectSelect(project);
        }
    };

    // 获取优先级颜色
    const getStatusColor = (completionRate) => {
        if (completionRate === 100) return 'success';
        if (completionRate >= 50) return 'processing';
        if (completionRate > 0) return 'warning';
        return 'default';
    };

    // 格式化时间
    const formatTime = (pomodoros) => {
        if (!pomodoros) return '0分钟';
        return `${pomodoros * 25}分钟`;
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    // 项目卡片组件
    const ProjectCard = ({ project }) => {
        const stats = projectStats[project.id] || {};

        return (
            <Card
                key={project.id}
                size="small"
                title={
                    <Space>
                        <div
                            style={{
                                width: 12,
                                height: 12,
                                borderRadius: '50%',
                                backgroundColor: project.color,
                                display: 'inline-block'
                            }}
                        />
                        <Text strong>{project.name}</Text>
                    </Space>
                }
                extra={
                    <Space>
                        <Tooltip title="查看任务">
                            <Button
                                type="text"
                                size="small"
                                icon={<EyeOutlined />}
                                onClick={() => handleViewProjectTasks(project)}
                            />
                        </Tooltip>
                        <Tooltip title="编辑项目">
                            <Button
                                type="text"
                                size="small"
                                icon={<EditOutlined />}
                                onClick={() => handleEditProject(project)}
                            />
                        </Tooltip>
                        <Tooltip title="删除项目">
                            <Popconfirm
                                title="确定要删除这个项目吗？"
                                description="删除后将无法恢复，请确认操作。"
                                onConfirm={() => handleDeleteProject(project.id)}
                                okText="确定"
                                cancelText="取消"
                            >
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<DeleteOutlined />}
                                    danger
                                />
                            </Popconfirm>
                        </Tooltip>
                    </Space>
                }
                style={{ marginBottom: 16 }}
                hoverable
            >
                {project.description && (
                    <Paragraph
                        ellipsis={{ rows: 2, expandable: true }}
                        style={{ marginBottom: 12 }}
                    >
                        {project.description}
                    </Paragraph>
                )}

                <Row gutter={16} style={{ marginBottom: 12 }}>
                    <Col span={8}>
                        <Statistic
                            title="总任务"
                            value={stats.totalTasks || 0}
                            prefix={<CalendarOutlined />}
                            valueStyle={{ fontSize: 16 }}
                        />
                    </Col>
                    <Col span={8}>
                        <Statistic
                            title="已完成"
                            value={stats.completedTasks || 0}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{ fontSize: 16, color: '#52c41a' }}
                        />
                    </Col>
                    <Col span={8}>
                        <Statistic
                            title="预计时间"
                            value={stats.totalEstimatedTime || 0}
                            suffix="个番茄钟"
                            prefix={<ClockCircleOutlined />}
                            valueStyle={{ fontSize: 16 }}
                        />
                    </Col>
                </Row>

                <div style={{ marginBottom: 8 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <Text type="secondary">完成进度</Text>
                        <Text strong>{stats.completionRate || 0}%</Text>
                    </div>
                    <Progress
                        percent={stats.completionRate || 0}
                        size="small"
                        status={getStatusColor(stats.completionRate)}
                        strokeColor={{
                            '0%': project.color,
                            '100%': '#52c41a',
                        }}
                    />
                </div>

                {stats.tasks && stats.tasks.length > 0 && (
                    <div>
                        <Text type="secondary" style={{ fontSize: 12 }}>最近任务：</Text>
                        <div style={{ marginTop: 4 }}>
                            {stats.tasks.slice(0, 3).map(task => (
                                <Tag
                                    key={task.id}
                                    color={task.status === 'COMPLETED' ? 'green' :
                                           task.status === 'IN_PROGRESS' ? 'blue' : 'default'}
                                    style={{ marginBottom: 4 }}
                                >
                                    {task.title}
                                </Tag>
                            ))}
                            {stats.tasks.length > 3 && (
                                <Tag color="default">+{stats.tasks.length - 3} 更多</Tag>
                            )}
                        </div>
                    </div>
                )}
            </Card>
        );
    };

    return (
        <div>
            <div style={{ marginBottom: 16 }}>
                <Row justify="space-between" align="middle">
                    <Col>
                        <Title level={4} style={{ margin: 0 }}>
                            <ProjectOutlined /> 项目管理
                        </Title>
                    </Col>
                    <Col>
                        <Space>
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={fetchProjects}
                                loading={loading}
                            >
                                刷新
                            </Button>
                            <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                onClick={handleCreateProject}
                            >
                                新建项目
                            </Button>
                        </Space>
                    </Col>
                </Row>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: 16 }}>
                        <Text>加载项目数据中...</Text>
                    </div>
                </div>
            ) : projects.length === 0 ? (
                <Empty
                    description="暂无项目"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={handleCreateProject}
                    >
                        创建第一个项目
                    </Button>
                </Empty>
            ) : (
                <Row gutter={[16, 16]}>
                    {projects.map(project => (
                        <Col xs={24} sm={12} lg={8} key={project.id}>
                            <ProjectCard project={project} />
                        </Col>
                    ))}
                </Row>
            )}

            {/* 创建/编辑项目模态框 */}
            <Modal
                title={
                    <Space>
                        <ProjectOutlined />
                        {editingProject ? '编辑项目' : '创建项目'}
                    </Space>
                }
                open={modalVisible}
                onCancel={handleModalCancel}
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
                        <Input
                            placeholder="请输入项目名称"
                            prefix={<FolderOpenOutlined />}
                        />
                    </Form.Item>

                    <Form.Item
                        label="项目描述"
                        name="description"
                    >
                        <TextArea
                            rows={3}
                            placeholder="请输入项目描述（可选）"
                            maxLength={500}
                            showCount
                        />
                    </Form.Item>

                    <Form.Item
                        label="项目颜色"
                        name="color"
                        rules={[{ required: true, message: '请选择项目颜色' }]}
                    >
                        <ColorPicker
                            showText
                            size="large"
                            style={{ width: '100%' }}
                        />
                    </Form.Item>

                    <Divider />

                    <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                        <Space>
                            <Button onClick={handleModalCancel}>
                                取消
                            </Button>
                            <Button
                                type="primary"
                                htmlType="submit"
                                icon={<PlusOutlined />}
                            >
                                {editingProject ? '更新项目' : '创建项目'}
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default ProjectManager;