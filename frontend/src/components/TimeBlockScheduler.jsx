import React, { useState, useEffect, useRef } from 'react';
import {
    Card,
    Calendar,
    Button,
    Modal,
    Form,
    Input,
    Select,
    DatePicker,
    TimePicker,
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
    Divider,
    List,
    Avatar,
    Badge,
    Switch
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    DragOutlined,
    SaveOutlined,
    CancelOutlined,
    ReloadOutlined,
    BlockOutlined,
    ScheduleOutlined,
    CheckCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const TimeBlockScheduler = ({ selectedDate, onDateChange, onTaskSchedule }) => {
    const [timeBlocks, setTimeBlocks] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingBlock, setEditingBlock] = useState(null);
    const [draggedTask, setDraggedTask] = useState(null);
    const [currentDate, setCurrentDate] = useState(selectedDate || moment());
    const [form] = Form.useForm();
    const calendarRef = useRef(null);

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

    // 获取时间块数据
    const fetchTimeBlocks = async (date) => {
        try {
            setLoading(true);
            const dateStr = date.format('YYYY-MM-DD');
            const response = await api.get(`/time-blocks/?date=${dateStr}`);
            if (response.status === 200) {
                setTimeBlocks(response.data || []);
            }
        } catch (error) {
            console.error('获取时间块失败:', error);
            message.error('获取时间块失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取任务数据
    const fetchTasks = async () => {
        try {
            const response = await api.get('/tasks/');
            if (response.status === 200) {
                const tasksData = response.data.tasks || [];
                // 过滤出待处理和进行中的任务
                const activeTasks = tasksData.filter(task =>
                    task.status === 'PENDING' || task.status === 'IN_PROGRESS'
                );
                setTasks(activeTasks);
            }
        } catch (error) {
            console.error('获取任务失败:', error);
            message.error('获取任务失败');
        }
    };

    // 创建或更新时间块
    const handleSubmit = async (values) => {
        try {
            const blockData = {
                date: currentDate.format('YYYY-MM-DD'),
                start_time: currentDate.format(`YYYY-MM-DD ${values.start_time.format('HH:mm')}`),
                end_time: currentDate.format(`YYYY-MM-DD ${values.end_time.format('HH:mm')}`),
                block_type: values.block_type,
                color: values.color?.toHexString() || '#1890ff',
                is_recurring: values.is_recurring || false,
                recurrence_pattern: values.recurrence_pattern
            };

            let response;
            if (editingBlock) {
                response = await api.put(`/time-blocks/${editingBlock.id}`, blockData);
            } else {
                response = await api.post('/time-blocks/', blockData);
            }

            if (response.status === (editingBlock ? 200 : 201)) {
                message.success(editingBlock ? '时间块更新成功' : '时间块创建成功');
                setModalVisible(false);
                setEditingBlock(null);
                form.resetFields();
                fetchTimeBlocks(currentDate);
            }
        } catch (error) {
            console.error(`${editingBlock ? '更新' : '创建'}时间块失败:`, error);
            const errorMessage = error.response?.data?.error ||
                `${editingBlock ? '更新' : '创建'}时间块失败`;
            message.error(errorMessage);
        }
    };

    // 删除时间块
    const handleDeleteBlock = async (blockId) => {
        try {
            const response = await api.delete(`/time-blocks/${blockId}`);
            if (response.status === 200) {
                message.success('时间块删除成功');
                fetchTimeBlocks(currentDate);
            }
        } catch (error) {
            console.error('删除时间块失败:', error);
            const errorMessage = error.response?.data?.error || '删除时间块失败';
            message.error(errorMessage);
        }
    };

    // 打开编辑模态框
    const handleEditBlock = (block) => {
        setEditingBlock(block);
        form.setFieldsValue({
            block_type: block.block_type,
            start_time: moment(block.start_time),
            end_time: moment(block.end_time),
            color: block.color,
            is_recurring: block.is_recurring,
            recurrence_pattern: block.recurrence_pattern
        });
        setModalVisible(true);
    };

    // 打开创建模态框
    const handleCreateBlock = () => {
        setEditingBlock(null);
        form.resetFields();
        form.setFieldsValue({
            block_type: 'GROWTH',
            is_recurring: false,
            color: '#1890ff'
        });
        setModalVisible(true);
    };

    // 关闭模态框
    const handleModalCancel = () => {
        setModalVisible(false);
        setEditingBlock(null);
        form.resetFields();
    };

    // 处理任务拖拽
    const handleTaskDragStart = (task) => {
        setDraggedTask(task);
    };

    // 处理任务拖拽到时间块
    const handleTaskDrop = (block, task) => {
        console.log('调度任务到时间块:', task, block);
        // 这里可以添加任务调度逻辑
        message.success(`任务"${task.title}"已调度到时间块`);
        setDraggedTask(null);

        if (onTaskSchedule) {
            onTaskSchedule(task, block);
        }
    };

    // 拖拽任务组件
    const DraggableTask = ({ task }) => {
        const [{ isDragging }, drag] = useDrag(() => ({
            type: 'task',
            item: task,
            collect: (monitor) => ({
                isDragging: monitor.isDragging(),
            }),
        }), [task]);

        return (
            <div
                ref={drag}
                style={{
                    opacity: isDragging ? 0.5 : 1,
                    cursor: 'move',
                    marginBottom: 8
                }}
            >
                <Card
                    size="small"
                    style={{
                        border: isDragging ? '2px dashed #1890ff' : '1px solid #d9d9d9'
                    }}
                >
                    <Space>
                        <Text strong>{task.title}</Text>
                        <Tag color={task.status === 'PENDING' ? 'orange' : 'blue'}>
                            {task.status === 'PENDING' ? '待处理' : '进行中'}
                        </Tag>
                    </Space>
                </Card>
            </div>
        );
    };

    // 时间块组件
    const DroppableTimeBlock = ({ block, index }) => {
        const [{ isOver }, drop] = useDrop(() => ({
            accept: 'task',
            drop: (item) => handleTaskDrop(block, item),
            collect: (monitor) => ({
                isOver: monitor.isOver(),
            }),
        }), [block]);

        const blockColors = {
            'RESEARCH': '#1890ff',
            'GROWTH': '#52c41a',
            'REST': '#fa8c16',
            'ENTERTAINMENT': '#eb2f96',
            'REVIEW': '#722ed1'
        };

        const blockLabels = {
            'RESEARCH': '科研',
            'GROWTH': '成长',
            'REST': '休息',
            'ENTERTAINMENT': '娱乐',
            'REVIEW': '复盘'
        };

        return (
            <div
                ref={drop}
                style={{
                    backgroundColor: isOver ? '#f0f8ff' : blockColors[block.block_type] || '#1890ff',
                    padding: '8px',
                    borderRadius: '4px',
                    marginBottom: '4px',
                    border: isOver ? '2px dashed #1890ff' : '1px solid transparent',
                    minHeight: '60px',
                    position: 'relative'
                }}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <Text style={{ color: '#fff', fontWeight: 'bold' }}>
                            {blockLabels[block.block_type]}
                        </Text>
                        <Text style={{ color: '#fff', fontSize: '12px' }}>
                            {moment(block.start_time).format('HH:mm')} - {moment(block.end_time).format('HH:mm')}
                        </Text>
                    </div>
                    <Space size="small">
                        <Tooltip title="编辑时间块">
                            <Button
                                type="text"
                                size="small"
                                icon={<EditOutlined />}
                                onClick={() => handleEditBlock(block)}
                                style={{ color: '#fff' }}
                            />
                        </Tooltip>
                        <Tooltip title="删除时间块">
                            <Popconfirm
                                title="确定要删除这个时间块吗？"
                                description="删除后将无法恢复，请确认操作。"
                                onConfirm={() => handleDeleteBlock(block.id)}
                                okText="确定"
                                cancelText="取消"
                            >
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<DeleteOutlined />}
                                    danger
                                    style={{ color: '#fff' }}
                                />
                            </Popconfirm>
                        </Tooltip>
                    </Space>
                </div>

                {/* 显示已调度的任务 */}
                {block.scheduled_tasks && block.scheduled_tasks.length > 0 && (
                    <div style={{ marginTop: '8px' }}>
                        <Text style={{ color: '#fff', fontSize: '12px' }}>已调度任务:</Text>
                        <div style={{ marginTop: '4px' }}>
                            {block.scheduled_tasks.slice(0, 2).map(task => (
                                <Tag
                                    key={task.id}
                                    style={{ marginBottom: '2px', fontSize: '10px', color: '#fff', backgroundColor: 'rgba(255,255,255,0.2)' }}
                                >
                                    {task.title}
                                </Tag>
                            ))}
                            {block.scheduled_tasks.length > 2 && (
                                <Tag style={{ fontSize: '10px', color: '#fff', backgroundColor: 'rgba(255,255,255,0.2)' }}>
                                    +{block.scheduled_tasks.length - 2} 更多
                                </Tag>
                            )}
                        </div>
                    </div>
                )}

                {isOver && (
                    <div
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backgroundColor: 'rgba(24, 144, 255, 0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '2px dashed #1890ff',
                            borderRadius: '4px'
                        }}
                    >
                        <Text style={{ color: '#1890ff', fontWeight: 'bold' }}>
                            <DragOutlined /> 放置任务到这里
                        </Text>
                    </div>
                )}
            </div>
        );
    };

    // 日期选择器配置
    const dateCellRender = (value) => {
        const dateStr = value.format('YYYY-MM-DD');
        const dayBlocks = timeBlocks.filter(block => block.date === dateStr);

        return (
            <div style={{ position: 'relative' }}>
                <div style={{ textAlign: 'center' }}>
                    {value.date()}
                </div>
                {dayBlocks.length > 0 && (
                    <div style={{ marginTop: '4px' }}>
                        {dayBlocks.map((block, index) => (
                            <DroppableTimeBlock key={block.id} block={block} index={index} />
                        ))}
                    </div>
                )}
            </div>
        );
    };

    useEffect(() => {
        if (selectedDate) {
            setCurrentDate(moment(selectedDate));
        }
    }, [selectedDate]);

    useEffect(() => {
        fetchTimeBlocks(currentDate);
        fetchTasks();
    }, [currentDate]);

    return (
        <DndProvider backend={HTML5Backend}>
            <div>
                <div style={{ marginBottom: 16 }}>
                    <Row justify="space-between" align="middle">
                        <Col>
                            <Title level={4} style={{ margin: 0 }}>
                                <ScheduleOutlined /> 时间块调度
                            </Title>
                        </Col>
                        <Col>
                            <Space>
                                <Button
                                    icon={<ReloadOutlined />}
                                    onClick={() => fetchTimeBlocks(currentDate)}
                                    loading={loading}
                                >
                                    刷新
                                </Button>
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    onClick={handleCreateBlock}
                                >
                                    创建时间块
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </div>

                <Row gutter={16}>
                    <Col span={18}>
                        <Card title="日历视图 - 时间块拖拽调度">
                            <Calendar
                                ref={calendarRef}
                                value={currentDate}
                                onChange={(date) => {
                                    setCurrentDate(date);
                                    if (onDateChange) {
                                        onDateChange(date);
                                    }
                                }}
                                dateCellRender={dateCellRender}
                                fullscreen={false}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card
                            title={
                                <Space>
                                    <ClockCircleOutlined />
                                    可调度任务
                                </Space>
                            }
                            size="small"
                        >
                            {tasks.length === 0 ? (
                                <Empty
                                    description="暂无可调度任务"
                                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                                />
                            ) : (
                                <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                                    {tasks.map(task => (
                                        <DraggableTask key={task.id} task={task} />
                                    ))}
                                </div>
                            )}

                            <Divider />

                            <div style={{ marginBottom: 8 }}>
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                    拖拽任务到时间块进行调度
                                </Text>
                            </div>

                            <div>
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                    时间块类型：
                                </Text>
                                <div style={{ marginTop: 4 }}>
                                    <Tag color="#1890ff">科研</Tag>
                                    <Tag color="#52c41a">成长</Tag>
                                    <Tag color="#fa8c16">休息</Tag>
                                    <Tag color="#eb2f96">娱乐</Tag>
                                    <Tag color="#722ed1">复盘</Tag>
                                </div>
                            </div>
                        </Card>
                    </Col>
                </Row>

                {/* 创建/编辑时间块模态框 */}
                <Modal
                    title={
                        <Space>
                            <BlockOutlined />
                            {editingBlock ? '编辑时间块' : '创建时间块'}
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
                        initialValues={{
                            block_type: 'GROWTH',
                            is_recurring: false
                        }}
                    >
                        <Form.Item
                            label="时间块类型"
                            name="block_type"
                            rules={[{ required: true, message: '请选择时间块类型' }]}
                        >
                            <Select placeholder="选择时间块类型">
                                <Option value="RESEARCH">科研</Option>
                                <Option value="GROWTH">成长</Option>
                                <Option value="REST">休息</Option>
                                <Option value="ENTERTAINMENT">娱乐</Option>
                                <Option value="REVIEW">复盘</Option>
                            </Select>
                        </Form.Item>

                        <Row gutter={16}>
                            <Col span={12}>
                                <Form.Item
                                    label="开始时间"
                                    name="start_time"
                                    rules={[{ required: true, message: '请选择开始时间' }]}
                                >
                                    <TimePicker
                                        format="HH:mm"
                                        placeholder="选择开始时间"
                                        style={{ width: '100%' }}
                                    />
                                </Form.Item>
                            </Col>
                            <Col span={12}>
                                <Form.Item
                                    label="结束时间"
                                    name="end_time"
                                    rules={[{ required: true, message: '请选择结束时间' }]}
                                >
                                    <TimePicker
                                        format="HH:mm"
                                        placeholder="选择结束时间"
                                        style={{ width: '100%' }}
                                    />
                                </Form.Item>
                            </Col>
                        </Row>

                        <Form.Item
                            label="时间块颜色"
                            name="color"
                            rules={[{ required: true, message: '请选择时间块颜色' }]}
                        >
                            <ColorPicker
                                showText
                                size="large"
                                style={{ width: '100%' }}
                            />
                        </Form.Item>

                        <Form.Item
                            label="重复设置"
                            name="is_recurring"
                            valuePropName="checked"
                        >
                            <Switch />
                        </Form.Item>

                        <Form.Item
                            label="重复模式"
                            name="recurrence_pattern"
                        >
                            <Select placeholder="选择重复模式" allowClear>
                                <Option value="daily">每天</Option>
                                <Option value="weekly">每周</Option>
                                <Option value="monthly">每月</Option>
                                <Option value="workdays">工作日</Option>
                            </Select>
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
                                    icon={<SaveOutlined />}
                                >
                                    {editingBlock ? '更新时间块' : '创建时间块'}
                                </Button>
                            </Space>
                        </Form.Item>
                    </Form>
                </Modal>

                <div style={{ marginTop: 16, padding: '16px', background: '#f5f5f5', borderRadius: '4px' }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                        💡 使用提示：从右侧任务列表拖拽任务到日历中的时间块进行调度。时间块会自动检测时间冲突，确保不会重叠。
                    </Text>
                </div>
            </div>
        </DndProvider>
    );
};

export default TimeBlockScheduler;