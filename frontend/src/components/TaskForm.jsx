import React, { useState, useEffect } from 'react';
import {
    Form,
    Input,
    Button,
    Select,
    DatePicker,
    InputNumber,
    Radio,
    Tag,
    Space,
    message,
    Row,
    Col,
    Card,
    Divider,
    Typography,
    TimePicker,
    Modal
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    SaveOutlined,
    CancelOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    FlagOutlined,
    FolderOutlined,
    TagsOutlined
} from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { Group: RadioGroup } = Radio;

const TaskForm = ({
    visible,
    onCancel,
    onSuccess,
    taskId = null,
    initialValues = null
}) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [categories, setCategories] = useState([]);
    const [projects, setProjects] = useState([]);
    const [tags, setTags] = useState([]);
    const [selectedTags, setSelectedTags] = useState([]);
    const [newTagInput, setNewTagInput] = useState('');
    const [isEditMode, setIsEditMode] = useState(!!taskId);

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

    // 获取任务类别
    const fetchCategories = async () => {
        try {
            const response = await api.get('/task-categories/');
            if (response.status === 200) {
                setCategories(response.data.task_categories || []);
            }
        } catch (error) {
            console.error('获取任务类别失败:', error);
        }
    };

    // 获取项目列表
    const fetchProjects = async () => {
        try {
            const response = await api.get('/projects/');
            if (response.status === 200) {
                setProjects(response.data.projects || []);
            }
        } catch (error) {
            console.error('获取项目列表失败:', error);
        }
    };

    // 获取标签列表
    const fetchTags = async () => {
        try {
            const response = await api.get('/tags/');
            if (response.status === 200) {
                setTags(response.data.tags || []);
            }
        } catch (error) {
            console.error('获取标签列表失败:', error);
        }
    };

    // 获取任务详情（编辑模式）
    const fetchTaskDetails = async (id) => {
        try {
            setLoading(true);
            const response = await api.get(`/tasks/${id}`);
            if (response.status === 200) {
                const task = response.data.task;

                // 设置表单初始值
                const formValues = {
                    title: task.title,
                    description: task.description,
                    category_id: task.category_id,
                    project_id: task.project_id,
                    priority: task.priority,
                    task_type: task.task_type,
                    estimated_pomodoros: task.estimated_pomodoros,
                    status: task.status,
                    planned_start_time: task.planned_start_time ? moment(task.planned_start_time) : null
                };

                form.setFieldsValue(formValues);

                // 设置标签
                if (task.tags) {
                    setSelectedTags(task.tags);
                }
            }
        } catch (error) {
            console.error('获取任务详情失败:', error);
            message.error('获取任务详情失败');
        } finally {
            setLoading(false);
        }
    };

    // 创建新标签
    const createTag = async (tagName) => {
        try {
            const response = await api.post('/tags/', {
                name: tagName,
                color: '#1890ff'
            });

            if (response.status === 201) {
                const newTag = response.data.tag;
                setTags([...tags, newTag]);
                setSelectedTags([...selectedTags, newTag]);
                return newTag;
            }
        } catch (error) {
            console.error('创建标签失败:', error);
            message.error('创建标签失败');
        }
        return null;
    };

    // 添加标签
    const handleAddTag = () => {
        if (newTagInput.trim()) {
            // 检查标签是否已存在
            const existingTag = tags.find(tag =>
                tag.name.toLowerCase() === newTagInput.trim().toLowerCase()
            );

            if (existingTag) {
                if (!selectedTags.find(tag => tag.id === existingTag.id)) {
                    setSelectedTags([...selectedTags, existingTag]);
                } else {
                    message.warning('标签已添加');
                }
            } else {
                createTag(newTagInput.trim());
            }

            setNewTagInput('');
        }
    };

    // 移除标签
    const handleRemoveTag = (tagToRemove) => {
        setSelectedTags(selectedTags.filter(tag => tag.id !== tagToRemove.id));
    };

    // 提交表单
    const handleSubmit = async (values) => {
        try {
            setLoading(true);

            // 处理时间格式
            if (values.planned_start_time) {
                values.planned_start_time = values.planned_start_time.toISOString();
            }

            // 添加标签ID
            values.tag_ids = selectedTags.map(tag => tag.id);

            let response;
            if (isEditMode) {
                // 更新任务
                response = await api.put(`/tasks/${taskId}`, values);
            } else {
                // 创建任务
                response = await api.post('/tasks/', values);
            }

            if (response.status === (isEditMode ? 200 : 201)) {
                message.success(isEditMode ? '任务更新成功' : '任务创建成功');
                form.resetFields();
                setSelectedTags([]);
                setNewTagInput('');
                onSuccess && onSuccess(response.data.task);
            }
        } catch (error) {
            console.error(`${isEditMode ? '更新' : '创建'}任务失败:`, error);
            const errorMessage = error.response?.data?.error || `${isEditMode ? '更新' : '创建'}任务失败`;
            message.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // 取消操作
    const handleCancel = () => {
        form.resetFields();
        setSelectedTags([]);
        setNewTagInput('');
        onCancel && onCancel();
    };

    // 获取优先级颜色
    const getPriorityColor = (priority) => {
        const colorMap = {
            'HIGH': 'red',
            'MEDIUM': 'orange',
            'LOW': 'green'
        };
        return colorMap[priority] || 'default';
    };

    // 获取任务类型标签
    const getTaskTypeLabel = (type) => {
        const labelMap = {
            'RIGID': '刚性任务',
            'FLEXIBLE': '柔性任务'
        };
        return labelMap[type] || type;
    };

    useEffect(() => {
        if (visible) {
            fetchCategories();
            fetchProjects();
            fetchTags();

            if (isEditMode && taskId) {
                fetchTaskDetails(taskId);
            } else if (initialValues) {
                form.setFieldsValue(initialValues);
                if (initialValues.tags) {
                    setSelectedTags(initialValues.tags);
                }
            }
        }
    }, [visible, taskId, isEditMode, initialValues]);

    return (
        <Modal
            title={
                <Space>
                    {isEditMode ? <EditOutlined /> : <PlusOutlined />}
                    {isEditMode ? '编辑任务' : '创建任务'}
                </Space>
            }
            open={visible}
            onCancel={handleCancel}
            footer={null}
            width={720}
            destroyOnClose
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                    priority: 'MEDIUM',
                    task_type: 'FLEXIBLE',
                    estimated_pomodoros: 1,
                    status: 'PENDING'
                }}
            >
                {/* 基本信息 */}
                <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={24}>
                            <Form.Item
                                label="任务标题"
                                name="title"
                                rules={[{ required: true, message: '请输入任务标题' }]}
                            >
                                <Input
                                    placeholder="请输入任务标题"
                                    prefix={<EditOutlined />}
                                />
                            </Form.Item>
                        </Col>
                        <Col span={24}>
                            <Form.Item
                                label="任务描述"
                                name="description"
                            >
                                <TextArea
                                    rows={3}
                                    placeholder="请输入任务描述（可选）"
                                    maxLength={500}
                                    showCount
                                />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* 分类和项目 */}
                <Card title="分类和项目" size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label={<><FolderOutlined /> 任务类别</>}
                                name="category_id"
                                rules={[{ required: true, message: '请选择任务类别' }]}
                            >
                                <Select placeholder="请选择任务类别">
                                    {categories.map(category => (
                                        <Option key={category.id} value={category.id}>
                                            <Tag color={category.color} style={{ marginRight: 4 }}>
                                                {category.name}
                                            </Tag>
                                        </Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label={<><FolderOutlined /> 关联项目</>}
                                name="project_id"
                            >
                                <Select placeholder="请选择项目（可选）" allowClear>
                                    {projects.map(project => (
                                        <Option key={project.id} value={project.id}>
                                            <Tag color={project.color} style={{ marginRight: 4 }}>
                                                {project.name}
                                            </Tag>
                                        </Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* 时间规划 */}
                <Card title="时间规划" size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label={<><CalendarOutlined /> 计划开始时间</>}
                                name="planned_start_time"
                                rules={[{ required: true, message: '请选择计划开始时间' }]}
                            >
                                <DatePicker
                                    showTime
                                    placeholder="请选择计划开始时间"
                                    style={{ width: '100%' }}
                                    format="YYYY-MM-DD HH:mm"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label={<><ClockCircleOutlined /> 预计番茄钟数</>}
                                name="estimated_pomodoros"
                                rules={[{ required: true, message: '请输入预计番茄钟数' }]}
                            >
                                <InputNumber
                                    min={1}
                                    max={20}
                                    placeholder="预计需要多少个番茄钟"
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* 属性设置 */}
                <Card title="属性设置" size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                label={<><FlagOutlined /> 优先级</>}
                                name="priority"
                            >
                                <Select placeholder="选择优先级">
                                    <Option value="HIGH">
                                        <Tag color="red">高优先级</Tag>
                                    </Option>
                                    <Option value="MEDIUM">
                                        <Tag color="orange">中优先级</Tag>
                                    </Option>
                                    <Option value="LOW">
                                        <Tag color="green">低优先级</Tag>
                                    </Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                label="任务类型"
                                name="task_type"
                            >
                                <RadioGroup>
                                    <Radio value="RIGID">刚性任务</Radio>
                                    <Radio value="FLEXIBLE">柔性任务</Radio>
                                </RadioGroup>
                            </Form.Item>
                        </Col>
                        {isEditMode && (
                            <Col span={8}>
                                <Form.Item
                                    label="任务状态"
                                    name="status"
                                >
                                    <Select placeholder="选择状态">
                                        <Option value="PENDING">待处理</Option>
                                        <Option value="IN_PROGRESS">进行中</Option>
                                        <Option value="COMPLETED">已完成</Option>
                                        <Option value="CANCELLED">已取消</Option>
                                    </Select>
                                </Form.Item>
                            </Col>
                        )}
                    </Row>
                </Card>

                {/* 标签管理 */}
                <Card title={<><TagsOutlined /> 标签管理</>} size="small" style={{ marginBottom: 16 }}>
                    <Space wrap style={{ marginBottom: 12 }}>
                        {selectedTags.map(tag => (
                            <Tag
                                key={tag.id}
                                color={tag.color}
                                closable
                                onClose={() => handleRemoveTag(tag)}
                            >
                                {tag.name}
                            </Tag>
                        ))}
                    </Space>

                    <Space.Compact style={{ width: '100%' }}>
                        <Input
                            placeholder="输入标签名称，按回车或点击添加"
                            value={newTagInput}
                            onChange={(e) => setNewTagInput(e.target.value)}
                            onPressEnter={handleAddTag}
                        />
                        <Button type="primary" icon={<PlusOutlined />} onClick={handleAddTag}>
                            添加
                        </Button>
                    </Space>

                    {/* 现有标签快速选择 */}
                    <div style={{ marginTop: 12 }}>
                        <Text type="secondary">快速选择现有标签：</Text>
                        <div style={{ marginTop: 8 }}>
                            <Space wrap>
                                {tags
                                    .filter(tag => !selectedTags.find(t => t.id === tag.id))
                                    .map(tag => (
                                        <Tag
                                            key={tag.id}
                                            color={tag.color}
                                            style={{ cursor: 'pointer' }}
                                            onClick={() => setSelectedTags([...selectedTags, tag])}
                                        >
                                            {tag.name}
                                        </Tag>
                                    ))}
                            </Space>
                        </div>
                    </div>
                </Card>

                {/* 操作按钮 */}
                <Divider />
                <Row justify="end">
                    <Space>
                        <Button onClick={handleCancel} icon={<CancelOutlined />}>
                            取消
                        </Button>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={loading}
                            icon={<SaveOutlined />}
                        >
                            {isEditMode ? '更新任务' : '创建任务'}
                        </Button>
                    </Space>
                </Row>
            </Form>
        </Modal>
    );
};

export default TaskForm;