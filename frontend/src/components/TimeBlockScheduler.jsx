import React, { useState, useEffect, useCallback } from 'react';
import {
    Card,
    Button,
    Form,
    DatePicker,
    Space,
    message,
    Typography,
    Row,
    Col,
    Empty,
    Spin,
    Badge,
    notification,
    Modal
} from 'antd';
import {
    PlusOutlined,
    ReloadOutlined,
    ScheduleOutlined,
    WarningOutlined,
    BarChartOutlined,
    SearchOutlined,
    AppstoreOutlined,
    DeleteOutlined
} from '@ant-design/icons';
import { timeBlockService, taskService } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import dayjs from 'dayjs';
import { DragDropContext } from 'react-beautiful-dnd';

// 导入拆分后的组件
import TimeBlockItem from './TimeBlockItem';
import TaskPool from './TaskPool';
import TimeBlockForm from './TimeBlockForm';
import ConflictDrawer from './ConflictDrawer';
import BlockTypeLegend from './BlockTypeLegend';
import TimeBlockBatchOperations from './TimeBlockBatchOperations';
import TimeBlockStatistics from './TimeBlockStatistics';
import TimeBlockSearch from './TimeBlockSearch';

const { Title } = Typography;

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
    const [autoFixes, setAutoFixes] = useState([]);
    const [severitySummary, setSeveritySummary] = useState({});
    const [form] = Form.useForm();

    // 新增状态
    const [batchModalVisible, setBatchModalVisible] = useState(false);
    const [statisticsVisible, setStatisticsVisible] = useState(false);
    const [searchVisible, setSearchVisible] = useState(false);

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
            const response = await timeBlockService.getTimeBlocks({ date: dateStr });
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
            const autoFixes = response.auto_fixes || [];
            const severitySummary = response.severity_summary || {};

            setConflicts(conflicts);
            setAutoFixes(autoFixes);
            setSeveritySummary(severitySummary);

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
                        message: `${blockTypeConfig[block1.block_type]?.label || block1.block_type} 时间块与 ${blockTypeConfig[block2.block_type]?.label || block2.block_type} 时间块时间重叠`,
                        severity: 'medium'
                    });
                }
            }
        }

        setConflicts(conflicts);
        setSeveritySummary({ medium: conflicts.length });

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

            if (editingBlock) {
                await timeBlockService.updateTimeBlock(editingBlock.id, blockData);
                message.success('时间块更新成功');
            } else {
                await timeBlockService.createTimeBlock(blockData);
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

    // 编辑时间块
    const handleEditBlock = (block) => {
        setEditingBlock(block);
        setModalVisible(true);
    };

    // 创建时间块
    const handleCreateBlock = () => {
        setEditingBlock(null);
        setModalVisible(true);
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

    // 自动修复所有冲突
    const handleAutoFixAll = async () => {
        try {
            // 这里可以调用自动修复API
            message.info('自动修复功能开发中...');
        } catch (error) {
            console.error('自动修复失败:', error);
            message.error('自动修复失败');
        }
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
                                icon={<SearchOutlined />}
                                onClick={() => setSearchVisible(true)}
                            >
                                搜索
                            </Button>
                            <Button
                                icon={<BarChartOutlined />}
                                onClick={() => setStatisticsVisible(true)}
                            >
                                统计
                            </Button>
                            <Button
                                icon={<AppstoreOutlined />}
                                onClick={() => setBatchModalVisible(true)}
                            >
                                批量操作
                            </Button>
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
                                    共 {timeBlocks.length} 个时间块
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
                                            <TimeBlockItem
                                                key={block.id}
                                                block={block}
                                                index={index}
                                                onEdit={handleEditBlock}
                                                onDelete={handleDeleteBlock}
                                                onUnscheduleTask={() => fetchTimeBlocks(selectedDate)}
                                                blockTypeConfig={blockTypeConfig}
                                            />
                                        ))}
                                </div>
                            )}
                        </Card>
                    </Col>

                    {/* 右侧面板 */}
                    <Col span={8}>
                        <TaskPool tasks={tasks} />
                        <BlockTypeLegend blockTypeConfig={blockTypeConfig} />
                    </Col>
                </Row>

                {/* 创建/编辑时间块表单 */}
                <TimeBlockForm
                    visible={modalVisible}
                    onCancel={() => setModalVisible(false)}
                    onSubmit={handleSubmit}
                    editingBlock={editingBlock}
                    selectedDate={selectedDate}
                    blockTypeConfig={blockTypeConfig}
                    form={form}
                />

                {/* 冲突详情抽屉 */}
                <ConflictDrawer
                    visible={conflictDrawerVisible}
                    onClose={() => setConflictDrawerVisible(false)}
                    conflicts={conflicts}
                    autoFixes={autoFixes}
                    onAutoFixAll={handleAutoFixAll}
                    severitySummary={severitySummary}
                />

                {/* 批量操作模态框 */}
                <TimeBlockBatchOperations
                    visible={batchModalVisible}
                    onClose={() => setBatchModalVisible(false)}
                    onSuccess={() => fetchTimeBlocks(selectedDate)}
                    selectedDate={selectedDate}
                />

                {/* 统计分析模态框 */}
                <Modal
                    title="时间块统计分析"
                    open={statisticsVisible}
                    onCancel={() => setStatisticsVisible(false)}
                    footer={null}
                    width={1200}
                    style={{ top: 20 }}
                >
                    <TimeBlockStatistics />
                </Modal>

                {/* 搜索模态框 */}
                <Modal
                    title="时间块搜索"
                    open={searchVisible}
                    onCancel={() => setSearchVisible(false)}
                    footer={null}
                    width={1000}
                    style={{ top: 20 }}
                >
                    <TimeBlockSearch
                        onTimeBlockSelect={(block) => {
                            // 可以在这里处理选中的时间块，比如跳转到对应日期
                            const blockDate = dayjs(block.date);
                            if (blockDate.isSame(selectedDate, 'day')) {
                                // 如果是同一天，高亮显示该时间块
                                message.info(`已选择时间块：${blockTypeConfig[block.block_type]?.label || block.block_type}`);
                            } else {
                                // 跳转到对应日期
                                setSelectedDate(blockDate);
                                message.info(`已跳转到 ${blockDate.format('YYYY-MM-DD')} 的时间块`);
                            }
                            setSearchVisible(false);
                        }}
                    />
                </Modal>
            </div>
        </DragDropContext>
    );
};

export default TimeBlockScheduler;