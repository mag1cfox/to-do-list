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
    Divider,
    Badge
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    TagsOutlined,
    CalendarOutlined,
    CheckCircleOutlined,
    ReloadOutlined,
    ExclamationCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { TextArea } = Input;

const TagManager = ({ onTagSelect, multiSelect = false, selectedTags = [] }) => {
    const [tags, setTags] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingTag, setEditingTag] = useState(null);
    const [tagStats, setTagStats] = useState({});
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

    // 获取标签列表
    const fetchTags = async () => {
        try {
            setLoading(true);
            const response = await api.get('/tags/');
            if (response.status === 200) {
                const tagsList = response.data || [];
                setTags(tagsList);

                // 获取每个标签的统计数据
                await fetchTagStats(tagsList);
            }
        } catch (error) {
            console.error('获取标签列表失败:', error);
            message.error('获取标签列表失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取标签统计数据
    const fetchTagStats = async (tagsList) => {
        try {
            // 获取任务数据用于统计
            const tasksResponse = await api.get('/tasks/');
            if (tasksResponse.status === 200) {
                const tasks = tasksResponse.data.tasks || [];
                const stats = {};

                // 统计每个标签的使用次数
                tagsList.forEach(tag => {
                    const tagTasks = tasks.filter(task =>
                        task.tags && task.tags.some(t => t.id === tag.id)
                    );
                    const completedTasks = tagTasks.filter(task => task.status === 'COMPLETED');

                    stats[tag.id] = {
                        totalTasks: tagTasks.length,
                        completedTasks: completedTasks.length,
                        usageCount: tagTasks.length,
                        completionRate: tagTasks.length > 0
                            ? Math.round((completedTasks.length / tagTasks.length) * 100)
                            : 0
                    };
                });

                setTagStats(stats);
            }
        } catch (error) {
            console.error('获取标签统计数据失败:', error);
        }
    };

    // 创建或更新标签
    const handleSubmit = async (values) => {
        try {
            const tagData = {
                name: values.name,
                color: values.color?.toHexString() || '#1890ff'
            };

            let response;
            if (editingTag) {
                response = await api.put(`/tags/${editingTag.id}`, tagData);
            } else {
                response = await api.post('/tags/', tagData);
            }

            if (response.status === (editingTag ? 200 : 201)) {
                message.success(editingTag ? '标签更新成功' : '标签创建成功');
                setModalVisible(false);
                setEditingTag(null);
                form.resetFields();
                fetchTags();
            }
        } catch (error) {
            console.error(`${editingTag ? '更新' : '创建'}标签失败:`, error);
            const errorMessage = error.response?.data?.error ||
                `${editingTag ? '更新' : '创建'}标签失败`;
            message.error(errorMessage);
        }
    };

    // 删除标签
    const handleDeleteTag = async (tagId) => {
        try {
            const response = await api.delete(`/tags/${tagId}`);
            if (response.status === 200) {
                message.success('标签删除成功');
                fetchTags();
            }
        } catch (error) {
            console.error('删除标签失败:', error);
            const errorMessage = error.response?.data?.error || '删除标签失败';
            message.error(errorMessage);
        }
    };

    // 打开编辑模态框
    const handleEditTag = (tag) => {
        setEditingTag(tag);
        form.setFieldsValue({
            name: tag.name,
            color: tag.color
        });
        setModalVisible(true);
    };

    // 打开创建模态框
    const handleCreateTag = () => {
        setEditingTag(null);
        form.resetFields();
        form.setFieldsValue({
            color: '#1890ff'
        });
        setModalVisible(true);
    };

    // 关闭模态框
    const handleModalCancel = () => {
        setModalVisible(false);
        setEditingTag(null);
        form.resetFields();
    };

    // 标签选择处理
    const handleTagSelect = (tag) => {
        if (onTagSelect) {
            if (multiSelect) {
                const isSelected = selectedTags.find(t => t.id === tag.id);
                if (isSelected) {
                    onTagSelect(selectedTags.filter(t => t.id !== tag.id));
                } else {
                    onTagSelect([...selectedTags, tag]);
                }
            } else {
                onTagSelect(tag);
            }
        }
    };

    // 获取使用状态颜色
    const getUsageColor = (usageCount) => {
        if (usageCount === 0) return 'default';
        if (usageCount <= 3) return 'blue';
        if (usageCount <= 6) return 'orange';
        return 'green';
    };

    useEffect(() => {
        fetchTags();
    }, []);

    // 标签卡片组件
    const TagCard = ({ tag }) => {
        const stats = tagStats[tag.id] || {};
        const isSelected = multiSelect ?
            selectedTags.find(t => t.id === tag.id) :
            selectedTags && selectedTags.id === tag.id;

        return (
            <Card
                key={tag.id}
                size="small"
                style={{ marginBottom: 12 }}
                hoverable
                onClick={() => handleTagSelect(tag)}
                className={isSelected ? 'selected-tag-card' : ''}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                        <div
                            style={{
                                width: 16,
                                height: 16,
                                borderRadius: '50%',
                                backgroundColor: tag.color,
                                marginRight: 8,
                                border: isSelected ? '2px solid #1890ff' : 'none'
                            }}
                        />
                        <div style={{ flex: 1 }}>
                            <Text strong style={{ color: isSelected ? '#1890ff' : 'inherit' }}>
                                {tag.name}
                            </Text>
                            <div style={{ marginTop: 4 }}>
                                <Space size="small">
                                    <Tag color={getUsageColor(stats.usageCount)} size="small">
                                        使用 {stats.usageCount || 0} 次
                                    </Tag>
                                    {stats.completedTasks > 0 && (
                                        <Tag color="success" size="small">
                                            完成 {stats.completedTasks} 个任务
                                        </Tag>
                                    )}
                                </Space>
                            </div>
                        </div>
                    </div>
                    <Space size="small">
                        <Tooltip title="编辑标签">
                            <Button
                                type="text"
                                size="small"
                                icon={<EditOutlined />}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleEditTag(tag);
                                }}
                            />
                        </Tooltip>
                        <Tooltip title="删除标签">
                            <Popconfirm
                                title="确定要删除这个标签吗？"
                                description={stats.usageCount > 0 ?
                                    `这个标签被使用了 ${stats.usageCount} 次，删除后将从所有任务中移除。` :
                                    '删除后将无法恢复，请确认操作。'
                                }
                                onConfirm={(e) => {
                                    e.stopPropagation();
                                    handleDeleteTag(tag.id);
                                }}
                                okText="确定"
                                cancelText="取消"
                            >
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<DeleteOutlined />}
                                    danger
                                    onClick={(e) => e.stopPropagation()}
                                />
                            </Popconfirm>
                        </Tooltip>
                    </Space>
                </div>
            </Card>
        );
    };

    return (
        <div>
            <div style={{ marginBottom: 16 }}>
                <Row justify="space-between" align="middle">
                    <Col>
                        <Title level={4} style={{ margin: 0 }}>
                            <TagsOutlined /> 标签管理
                        </Title>
                    </Col>
                    <Col>
                        <Space>
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={fetchTags}
                                loading={loading}
                            >
                                刷新
                            </Button>
                            <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                onClick={handleCreateTag}
                            >
                                新建标签
                            </Button>
                        </Space>
                    </Col>
                </Row>
            </div>

            {/* 标签统计信息 */}
            <Card size="small" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                    <Col span={6}>
                        <Statistic
                            title="总标签数"
                            value={tags.length}
                            prefix={<TagsOutlined />}
                            valueStyle={{ fontSize: 16 }}
                        />
                    </Col>
                    <Col span={6}>
                        <Statistic
                            title="活跃标签"
                            value={Object.values(tagStats).filter(stat => stat.usageCount > 0).length}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{ fontSize: 16, color: '#52c41a' }}
                        />
                    </Col>
                    <Col span={6}>
                        <Statistic
                            title="未使用标签"
                            value={Object.values(tagStats).filter(stat => stat.usageCount === 0).length}
                            prefix={<ExclamationCircleOutlined />}
                            valueStyle={{ fontSize: 16, color: '#fa8c16' }}
                        />
                    </Col>
                    <Col span={6}>
                        <Statistic
                            title="总使用次数"
                            value={Object.values(tagStats).reduce((sum, stat) => sum + stat.usageCount, 0)}
                            prefix={<CalendarOutlined />}
                            valueStyle={{ fontSize: 16 }}
                        />
                    </Col>
                </Row>
            </Card>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: 16 }}>
                        <Text>加载标签数据中...</Text>
                    </div>
                </div>
            ) : tags.length === 0 ? (
                <Empty
                    description="暂无标签"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={handleCreateTag}
                    >
                        创建第一个标签
                    </Button>
                </Empty>
            ) : (
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                            {tags.map(tag => (
                                <TagCard key={tag.id} tag={tag} />
                            ))}
                        </div>
                    </Col>
                </Row>
            )}

            {/* 创建/编辑标签模态框 */}
            <Modal
                title={
                    <Space>
                        <TagsOutlined />
                        {editingTag ? '编辑标签' : '创建标签'}
                    </Space>
                }
                open={modalVisible}
                onCancel={handleModalCancel}
                footer={null}
                width={400}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                >
                    <Form.Item
                        label="标签名称"
                        name="name"
                        rules={[{ required: true, message: '请输入标签名称' }]}
                    >
                        <Input
                            placeholder="请输入标签名称"
                            prefix={<TagsOutlined />}
                        />
                    </Form.Item>

                    <Form.Item
                        label="标签颜色"
                        name="color"
                        rules={[{ required: true, message: '请选择标签颜色' }]}
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
                                {editingTag ? '更新标签' : '创建标签'}
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            <style jsx>{`
                .selected-tag-card {
                    border-color: #1890ff;
                    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
                }
            `}</style>
        </div>
    );
};

export default TagManager;