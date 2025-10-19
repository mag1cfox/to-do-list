import React, { useState, useEffect, useRef, useCallback } from 'react';
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
    Switch,
    Alert,
    notification,
    Drawer
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    DragOutlined,
    ReloadOutlined,
    BlockOutlined,
    ScheduleOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    WarningOutlined,
    EyeOutlined,
    SettingOutlined
} from '@ant-design/icons';
import { timeBlockService, taskService } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import dayjs from 'dayjs';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const TimeBlockScheduler = () => {
    const { isAuthenticated } = useAuthStore();
    const [timeBlocks, setTimeBlocks] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingBlock, setEditingBlock] = useState(null);
    const [selectedDate, setSelectedDate] = useState(dayjs());
    const [conflictDrawerVisible, setConflictDrawerVisible] = useState(false);
    const [conflicts, setConflicts] = useState([]);
    const [viewMode, setViewMode] = useState('day'); // 'day' | 'week' | 'month'
    const [form] = Form.useForm();

    // 时间块类型配置
    const blockTypeConfig = {
        'RESEARCH': { label: '科研', color: '#1890ff', icon: '🔬' },
        'GROWTH': { label: '成长', color: '#52c41a', icon: '📈' },
        'REST': { label: '休息', color: '#fa8c16', icon: '☕' },
        'ENTERTAINMENT': { label: '娱乐', color: '#eb2f96', icon: '🎮' },
        'REVIEW': { label: '复盘', color: '#722ed1', icon: '📝' }
    };

    // 获取时间块数据
    const fetchTimeBlocks = useCallback(async (date) => {
        if (!isAuthenticated) return;

        setLoading(true);
        try {
            const dateStr = date.format('YYYY-MM-DD');
            const response = await timeBlockService.getTimeBlocks({
                date: dateStr
            });
            setTimeBlocks(response || []);
            // 检查时间冲突
            checkConflicts(response || []);
        } catch (error) {
            console.error('获取时间块失败:', error);
            message.error('获取时间块失败');
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated]);

    // 获取任务数据
    const fetchTasks = useCallback(async () => {
        if (!isAuthenticated) return;

        try {
            const response = await taskService.getTasks();
            if (response.tasks) {
                const activeTasks = response.tasks.filter(task =>
                    task.status === 'PENDING' || task.status === 'IN_PROGRESS'
                );
                setTasks(activeTasks);
            }
        } catch (error) {
            console.error('获取任务失败:', error);
            message.error('获取任务失败');
        }
    }, [isAuthenticated]);

    // 检查时间冲突
    const checkConflicts = async (blocks) => {
        try {
            const response = await timeBlockService.checkConflicts(selectedDate.format('YYYY-MM-DD'));
            const conflicts = response.conflicts || [];
            setConflicts(conflicts);

            // 如果有冲突，显示通知
            if (conflicts.length > 0) {
                notification.warning({
                    message: '检测到时间冲突',
                    description: `发现 ${conflicts.length} 个时间冲突，点击查看详情`,
                    icon: <WarningOutlined style={{ color: '#fa8c16' }} />,
                    duration: 4,
                    onClick: () => setConflictDrawerVisible(true)
                });
            }
        } catch (error) {
            console.error('检查时间冲突失败:', error);
            // 降级到前端检查
            checkConflictsLocally(blocks);
        }
    };

    // 本地冲突检查（降级方案）
    const checkConflictsLocally = (blocks) => {
        const conflicts = [];

        for (let i = 0; i < blocks.length; i++) {
            for (let j = i + 1; j < blocks.length; j++) {
                const block1 = blocks[i];
                const block2 = blocks[j];

                const start1 = dayjs(block1.start_time);
                const end1 = dayjs(block1.end_time);
                const start2 = dayjs(block2.start_time);
                const end2 = dayjs(block2.end_time);

                // 检查时间重叠
                if (start1.isBefore(end2) && start2.isBefore(end1)) {
                    conflicts.push({
                        type: 'time_overlap',
                        block1: block1,
                        block2: block2,
                        duration: Math.min(end1.valueOf(), end2.valueOf()) - Math.max(start1.valueOf(), start2.valueOf()),
                        message: `${blockTypeConfig[block1.block_type]?.label || block1.block_type} 时间块与 ${blockTypeConfig[block2.block_type]?.label || block2.block_type} 时间块时间重叠`
                    });
                }
            }
        }

        // 检查任务与时间块的时间匹配
        blocks.forEach(block => {
            if (block.scheduled_tasks && block.scheduled_tasks.length > 0) {
                block.scheduled_tasks.forEach(task => {
                    const taskDuration = (task.estimated_pomodoros || 1) * 25; // 25分钟每个番茄钟
                    const blockDuration = dayjs(block.end_time).diff(dayjs(block.start_time), 'minute');

                    if (taskDuration > blockDuration) {
                        conflicts.push({
                            type: 'task_duration',
                            block: block,
                            task: task,
                            message: `任务"${task.title}"的预估时间(${taskDuration}分钟)超过时间块时长(${blockDuration}分钟)`
                        });
                    }
                });
            }
        });

        setConflicts(conflicts);

        // 如果有冲突，显示通知
        if (conflicts.length > 0) {
            notification.warning({
                message: '检测到时间冲突',
                description: `发现 ${conflicts.length} 个时间冲突，点击查看详情`,
                icon: <WarningOutlined style={{ color: '#fa8c16' }} />,
                duration: 4,
                onClick: () => setConflictDrawerVisible(true)
            });
        }
    };

    // 创建或更新时间块
    const handleSubmit = async (values) => {
        try {
            const blockData = {
                date: selectedDate.format('YYYY-MM-DD'),
                start_time: selectedDate.format(`YYYY-MM-DD ${values.start_time.format('HH:mm')}`),
                end_time: selectedDate.format(`YYYY-MM-DD ${values.end_time.format('HH:mm')}`),
                block_type: values.block_type,
                color: values.color?.toHexString?.() || values.color?.toString() || blockTypeConfig[values.block_type]?.color || '#1890ff',
                is_recurring: values.is_recurring || false,
                recurrence_pattern: values.recurrence_pattern
            };

            let response;
            if (editingBlock) {
                response = await timeBlockService.updateTimeBlock(editingBlock.id, blockData);
                message.success('时间块更新成功');
            } else {
                response = await timeBlockService.createTimeBlock(blockData);
                message.success('时间块创建成功');
            }

            setModalVisible(false);
            setEditingBlock(null);
            form.resetFields();
            fetchTimeBlocks(selectedDate);
        } catch (error) {
            console.error(`${editingBlock ? '更新' : '创建'}时间块失败:`, error);
            const errorMessage = error.error || `${editingBlock ? '更新' : '创建'}时间块失败`;
            message.error(errorMessage);
        }
    };

    // 删除时间块
    const handleDeleteBlock = async (blockId) => {
        try {
            await timeBlockService.deleteTimeBlock(blockId);
            message.success('时间块删除成功');
            fetchTimeBlocks(selectedDate);
        } catch (error) {
            console.error('删除时间块失败:', error);
            const errorMessage = error.error || '删除时间块失败';
            message.error(errorMessage);
        }
    };

    // 拖拽结束处理
    const handleDragEnd = async (result) => {
        if (!result.destination) return;

        const { source, destination, draggableId } = result;

        // 如果是任务拖拽到时间块
        if (source.droppableId.startsWith('task-list') && destination.droppableId.startsWith('time-block-')) {
            const task = tasks.find(t => t.id === draggableId);
            const timeBlockId = destination.droppableId.replace('time-block-', '');
            const timeBlock = timeBlocks.find(tb => tb.id === timeBlockId);

            if (task && timeBlock) {
                try {
                    await timeBlockService.scheduleTask(timeBlockId, task.id);
                    message.success(`任务"${task.title}"已调度到${blockTypeConfig[timeBlock.block_type]?.label}时间块`);
                    fetchTimeBlocks(selectedDate);
                } catch (error) {
                    console.error('任务调度失败:', error);
                    const errorMessage = error.error || '任务调度失败';
                    message.error(errorMessage);
                }
            }
        }

        // 如果是时间块重新排序
        else if (source.droppableId.startsWith('time-block-') && destination.droppableId.startsWith('time-block-')) {
            const sourceBlockId = source.droppableId.replace('time-block-', '');
            const destBlockId = destination.droppableId.replace('time-block-', '');
            const taskId = draggableId;

            if (sourceBlockId !== destBlockId) {
                const task = tasks.find(t => t.id === taskId);
                const destBlock = timeBlocks.find(tb => tb.id === destBlockId);

                if (task && destBlock) {
                    try {
                        // 先从原时间块移除任务
                        await timeBlockService.unscheduleTask(sourceBlockId, taskId);
                        // 再调度到新时间块
                        await timeBlockService.scheduleTask(destBlockId, taskId);
                        message.success(`任务"${task.title}"已移动到新的时间块`);
                        fetchTimeBlocks(selectedDate);
                    } catch (error) {
                        console.error('任务移动失败:', error);
                        const errorMessage = error.error || '任务移动失败';
                        message.error(errorMessage);
                    }
                }
            }
        }
    };

    // 打开编辑模态框
    const handleEditBlock = (block) => {
        setEditingBlock(block);
        form.setFieldsValue({
            block_type: block.block_type,
            start_time: dayjs(block.start_time),
            end_time: dayjs(block.end_time),
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
            color: blockTypeConfig['GROWTH'].color
        });
        setModalVisible(true);
    };

    // 时间块组件
    const TimeBlockItem = ({ block, index }) => {
        const config = blockTypeConfig[block.block_type] || { label: block.block_type, color: '#1890ff' };

        return (
            <Card
                size="small"
                style={{
                    backgroundColor: config.color,
                    border: 'none',
                    borderRadius: '8px',
                    marginBottom: '8px',
                    position: 'relative'
                }}
                bodyStyle={{ padding: '12px' }}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                            <Text style={{ color: '#fff', fontSize: '14px', fontWeight: 'bold' }}>
                                {config.icon} {config.label}
                            </Text>
                            <Badge
                                count={block.scheduled_tasks?.length || 0}
                                style={{
                                    backgroundColor: 'rgba(255,255,255,0.3)',
                                    marginLeft: '8px',
                                    color: '#fff'
                                }}
                            />
                        </div>
                        <Text style={{ color: '#fff', fontSize: '12px' }}>
                            {dayjs(block.start_time).format('HH:mm')} - {dayjs(block.end_time).format('HH:mm')}
                            {' '}({block.duration || dayjs(block.end_time).diff(dayjs(block.start_time), 'minute')}分钟)
                        </Text>

                        {/* 已调度的任务 */}
                        {block.scheduled_tasks && block.scheduled_tasks.length > 0 && (
                            <div style={{ marginTop: '6px' }}>
                                <Droppable droppableId={`time-block-${block.id}`} direction="vertical">
                                    {(provided, snapshot) => (
                                        <div
                                            {...provided.droppableProps}
                                            ref={provided.innerRef}
                                            style={{
                                                backgroundColor: snapshot.isDraggingOver ? 'rgba(255,255,255,0.2)' : 'transparent',
                                                borderRadius: '4px',
                                                padding: '4px',
                                                minHeight: '20px'
                                            }}
                                        >
                                            {block.scheduled_tasks.slice(0, 2).map((task, taskIndex) => (
                                                <Draggable key={task.id} draggableId={task.id} index={taskIndex}>
                                                    {(provided, snapshot) => (
                                                        <div
                                                            ref={provided.innerRef}
                                                            {...provided.draggableProps}
                                                            {...provided.dragHandleProps}
                                                            style={{
                                                                ...provided.draggableProps.style,
                                                                backgroundColor: 'rgba(255,255,255,0.9)',
                                                                borderRadius: '3px',
                                                                padding: '2px 6px',
                                                                marginBottom: '2px',
                                                                fontSize: '11px',
                                                                boxShadow: snapshot.isDragging ? '0 2px 8px rgba(0,0,0,0.2)' : 'none',
                                                                display: 'flex',
                                                                justifyContent: 'space-between',
                                                                alignItems: 'center'
                                                            }}
                                                        >
                                                            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                                {task.title}
                                                            </span>
                                                            <Popconfirm
                                                                title="移除任务"
                                                                description={`确定要将任务"${task.title}"从时间块中移除吗？`}
                                                                onConfirm={async () => {
                                                                    try {
                                                                        await timeBlockService.unscheduleTask(block.id, task.id);
                                                                        message.success('任务已移除');
                                                                        fetchTimeBlocks(selectedDate);
                                                                    } catch (error) {
                                                                        console.error('移除任务失败:', error);
                                                                        message.error('移除任务失败');
                                                                    }
                                                                }}
                                                                okText="确定"
                                                                cancelText="取消"
                                                            >
                                                                <Button
                                                                    type="text"
                                                                    size="small"
                                                                    icon={<DeleteOutlined />}
                                                                    style={{
                                                                        color: '#666',
                                                                        fontSize: '10px',
                                                                        height: '16px',
                                                                        lineHeight: '16px',
                                                                        padding: '0 2px',
                                                                        minWidth: '16px'
                                                                    }}
                                                                />
                                                            </Popconfirm>
                                                        </div>
                                                    )}
                                                </Draggable>
                                            ))}
                                            {block.scheduled_tasks.length > 2 && (
                                                <Text style={{ color: '#fff', fontSize: '10px' }}>
                                                    +{block.scheduled_tasks.length - 2} 更多任务
                                                </Text>
                                            )}
                                            {provided.placeholder}
                                        </div>
                                    )}
                                </Droppable>
                            </div>
                        )}
                    </div>

                    <Space size="small" style={{ flexShrink: 0 }}>
                        <Tooltip title="编辑">
                            <Button
                                type="text"
                                size="small"
                                icon={<EditOutlined />}
                                onClick={() => handleEditBlock(block)}
                                style={{ color: '#fff' }}
                            />
                        </Tooltip>
                        <Tooltip title="删除">
                            <Popconfirm
                                title="确定删除？"
                                description="删除时间块将同时移除其中的任务安排"
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
            </Card>
        );
    };

    // 日历单元格渲染
    const dateCellRender = (value) => {
        const dateStr = value.format('YYYY-MM-DD');
        const dayBlocks = timeBlocks.filter(block =>
            dayjs(block.date).format('YYYY-MM-DD') === dateStr
        );

        if (dayBlocks.length === 0) return null;

        return (
            <div style={{ padding: '4px' }}>
                {dayBlocks.slice(0, 3).map((block, index) => {
                    const config = blockTypeConfig[block.block_type] || { color: '#1890ff' };
                    return (
                        <div
                            key={block.id}
                            style={{
                                backgroundColor: config.color,
                                height: '4px',
                                borderRadius: '2px',
                                marginBottom: '2px'
                            }}
                        />
                    );
                })}
                {dayBlocks.length > 3 && (
                    <Text style={{ fontSize: '10px', color: '#666' }}>
                        +{dayBlocks.length - 3}
                    </Text>
                )}
            </div>
        );
    };

    useEffect(() => {
        if (isAuthenticated) {
            fetchTimeBlocks(selectedDate);
            fetchTasks();
        }
    }, [isAuthenticated, selectedDate, fetchTimeBlocks, fetchTasks]);

    if (!isAuthenticated) {
        return (
            <div style={{ padding: '24px', textAlign: 'center' }}>
                <Empty
                    description="请先登录以使用时间块规划功能"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
            </div>
        );
    }

    return (
        <DragDropContext onDragEnd={handleDragEnd}>
            <div style={{ padding: '24px' }}>
                {/* 页面头部 */}
                <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
                    <Col>
                        <Title level={2} style={{ margin: 0 }}>
                            <ScheduleOutlined /> 时间块规划
                        </Title>
                        <Text type="secondary">
                            智能时间块管理，支持拖拽排布和冲突检测
                        </Text>
                    </Col>
                    <Col>
                        <Space>
                            {conflicts.length > 0 && (
                                <Button
                                    icon={<WarningOutlined />}
                                    onClick={() => setConflictDrawerVisible(true)}
                                    danger
                                >
                                    查看冲突 ({conflicts.length})
                                </Button>
                            )}
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={() => fetchTimeBlocks(selectedDate)}
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

                {/* 日期选择器 */}
                <Row justify="center" style={{ marginBottom: '24px' }}>
                    <Space>
                        <Button
                            onClick={() => setSelectedDate(selectedDate.subtract(1, 'day'))}
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
                        <DatePicker
                            value={selectedDate}
                            onChange={setSelectedDate}
                            format="YYYY-MM-DD"
                        />
                    </Space>
                </Row>

                <Row gutter={16}>
                    {/* 时间块列表 */}
                    <Col span={16}>
                        <Card
                            title={`${selectedDate.format('YYYY年MM月DD日 dddd')} 时间块`}
                            extra={
                                <Space>
                                    <Text type="secondary">
                                        共 {timeBlocks.length} 个时间块
                                    </Text>
                                    {conflicts.length > 0 && (
                                        <Badge count={conflicts.length} style={{ backgroundColor: '#ff4d4f' }}>
                                            <WarningOutlined style={{ color: '#ff4d4f' }} />
                                        </Badge>
                                    )}
                                </Space>
                            }
                        >
                            {loading ? (
                                <div style={{ textAlign: 'center', padding: '40px' }}>
                                    <Spin size="large" />
                                    <div style={{ marginTop: '16px' }}>加载时间块中...</div>
                                </div>
                            ) : timeBlocks.length === 0 ? (
                                <Empty
                                    description="暂无时间块"
                                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                                >
                                    <Button type="primary" onClick={handleCreateBlock}>
                                        创建第一个时间块
                                    </Button>
                                </Empty>
                            ) : (
                                <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                                    {timeBlocks
                                        .sort((a, b) => dayjs(a.start_time).diff(dayjs(b.start_time)))
                                        .map((block, index) => (
                                            <TimeBlockItem key={block.id} block={block} index={index} />
                                        ))}
                                </div>
                            )}
                        </Card>
                    </Col>

                    {/* 任务列表和日历 */}
                    <Col span={8}>
                        {/* 可调度任务 */}
                        <Card
                            title="可调度任务"
                            size="small"
                            style={{ marginBottom: '16px' }}
                        >
                            <Droppable droppableId="task-list" direction="vertical">
                                {(provided, snapshot) => (
                                    <div
                                        {...provided.droppableProps}
                                        ref={provided.innerRef}
                                        style={{
                                            backgroundColor: snapshot.isDraggingOver ? '#f0f8ff' : 'transparent',
                                            borderRadius: '4px',
                                            padding: '8px',
                                            minHeight: '100px',
                                            maxHeight: '200px',
                                            overflowY: 'auto'
                                        }}
                                    >
                                        {tasks.length === 0 ? (
                                            <Empty
                                                description="暂无任务"
                                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                                            />
                                        ) : (
                                            tasks.map((task, index) => (
                                                <Draggable key={task.id} draggableId={task.id} index={index}>
                                                    {(provided, snapshot) => (
                                                        <div
                                                            ref={provided.innerRef}
                                                            {...provided.draggableProps}
                                                            {...provided.dragHandleProps}
                                                            style={{
                                                                ...provided.draggableProps.style,
                                                                backgroundColor: snapshot.isDragging ? '#e6f7ff' : '#fff',
                                                                border: '1px solid #d9d9d9',
                                                                borderRadius: '6px',
                                                                padding: '8px',
                                                                marginBottom: '8px',
                                                                cursor: 'move',
                                                                boxShadow: snapshot.isDragging ? '0 4px 12px rgba(0,0,0,0.15)' : '0 1px 3px rgba(0,0,0,0.1)'
                                                            }}
                                                        >
                                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                                <Text strong style={{ fontSize: '13px' }}>
                                                                    {task.title}
                                                                </Text>
                                                                <DragOutlined style={{ color: '#999' }} />
                                                            </div>
                                                            <div style={{ marginTop: '4px' }}>
                                                                <Tag size="small" color="blue">
                                                                    {task.estimated_pomodoros || 1} 番茄钟
                                                                </Tag>
                                                                <Tag size="small" color={task.priority === 'HIGH' ? 'red' : task.priority === 'MEDIUM' ? 'orange' : 'green'}>
                                                                    {task.priority}
                                                                </Tag>
                                                            </div>
                                                        </div>
                                                    )}
                                                </Draggable>
                                            ))
                                        )}
                                        {provided.placeholder}
                                    </div>
                                )}
                            </Droppable>

                            <Divider style={{ margin: '12px 0' }} />

                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                💡 拖拽任务到左侧时间块进行调度
                            </Text>
                        </Card>

                        {/* 时间块类型说明 */}
                        <Card title="时间块类型" size="small">
                            <Space direction="vertical" style={{ width: '100%' }}>
                                {Object.entries(blockTypeConfig).map(([type, config]) => (
                                    <div key={type} style={{ display: 'flex', alignItems: 'center' }}>
                                        <div
                                            style={{
                                                width: '16px',
                                                height: '16px',
                                                backgroundColor: config.color,
                                                borderRadius: '3px',
                                                marginRight: '8px'
                                            }}
                                        />
                                        <Text style={{ fontSize: '13px' }}>
                                            {config.icon} {config.label}
                                        </Text>
                                    </div>
                                ))}
                            </Space>
                        </Card>
                    </Col>
                </Row>

                {/* 创建/编辑时间块模态框 */}
                <Modal
                    title={editingBlock ? '编辑时间块' : '创建时间块'}
                    open={modalVisible}
                    onCancel={() => setModalVisible(false)}
                    footer={null}
                    width={500}
                >
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={handleSubmit}
                    >
                        <Form.Item
                            label="时间块类型"
                            name="block_type"
                            rules={[{ required: true, message: '请选择时间块类型' }]}
                        >
                            <Select placeholder="选择时间块类型">
                                {Object.entries(blockTypeConfig).map(([type, config]) => (
                                    <Option key={type} value={type}>
                                        {config.icon} {config.label}
                                    </Option>
                                ))}
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
                            label="颜色"
                            name="color"
                            rules={[{ required: true, message: '请选择颜色' }]}
                        >
                            <ColorPicker
                                showText
                                size="large"
                                style={{ width: '100%' }}
                            />
                        </Form.Item>

                        <Form.Item
                            label="重复"
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

                        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                            <Space>
                                <Button onClick={() => setModalVisible(false)}>
                                    取消
                                </Button>
                                <Button type="primary" htmlType="submit">
                                    {editingBlock ? '更新' : '创建'}
                                </Button>
                            </Space>
                        </Form.Item>
                    </Form>
                </Modal>

                {/* 冲突详情抽屉 */}
                <Drawer
                    title={
                        <Space>
                            <WarningOutlined style={{ color: '#ff4d4f' }} />
                            时间冲突详情
                        </Space>
                    }
                    placement="right"
                    onClose={() => setConflictDrawerVisible(false)}
                    open={conflictDrawerVisible}
                    width={400}
                >
                    {conflicts.length === 0 ? (
                        <Empty description="无冲突" />
                    ) : (
                        <List
                            dataSource={conflicts}
                            renderItem={(conflict, index) => (
                                <List.Item key={index}>
                                    <Alert
                                        message={conflict.message}
                                        type="warning"
                                        showIcon
                                        style={{ width: '100%' }}
                                    />
                                </List.Item>
                            )}
                        />
                    )}

                    <Divider />

                    <div>
                        <Text strong>解决方案建议：</Text>
                        <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                            <li>调整时间块的时间范围</li>
                            <li>将任务移动到其他合适的时间块</li>
                            <li>拆分长时间的任务到多个时间块</li>
                            <li>删除不必要的时间块</li>
                        </ul>
                    </div>
                </Drawer>
            </div>
        </DragDropContext>
    );
};

export default TimeBlockScheduler;