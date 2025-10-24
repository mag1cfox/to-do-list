import React, { useState } from 'react';
import {
    Modal,
    Form,
    Input,
    Select,
    TimePicker,
    Button,
    Space,
    Table,
    message,
    Typography,
    Divider,
    Alert,
    Card,
    Row,
    Col,
    Tag,
    InputNumber,
    ColorPicker
} from 'antd';
import {
    PlusOutlined,
    DeleteOutlined,
    CopyOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    FileTextOutlined
} from '@ant-design/icons';
import { timeBlockService } from '../services/api';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

const TimeBlockBatchOperations = ({ visible, onClose, onSuccess, selectedDate }) => {
    const [activeTab, setActiveTab] = useState('create');
    const [loading, setLoading] = useState(false);
    const [form] = Form.useForm();
    const [timeBlocksList, setTimeBlocksList] = useState([]);
    const [selectedBlockIds, setSelectedBlockIds] = useState([]);
    const [deleteLoading, setDeleteLoading] = useState(false);

    // 时间块类型选项
    const typeOptions = [
        { value: 'RESEARCH', label: '科研', color: '#1890ff' },
        { value: 'GROWTH', label: '成长', color: '#52c41a' },
        { value: 'REST', label: '休息', color: '#fa8c16' },
        { value: 'ENTERTAINMENT', label: '娱乐', color: '#eb2f96' },
        { value: 'REVIEW', label: '复盘', color: '#722ed1' }
    ];

    // 预设时间块模板
    const timeBlockTemplates = [
        {
            name: '标准工作时间段',
            blocks: [
                { start_time: '09:00', end_time: '12:00', block_type: 'RESEARCH', color: '#1890ff' },
                { start_time: '14:00', end_time: '17:00', block_type: 'GROWTH', color: '#52c41a' }
            ]
        },
        {
            name: '深度工作模式',
            blocks: [
                { start_time: '09:00', end_time: '11:30', block_type: 'RESEARCH', color: '#1890ff' },
                { start_time: '13:30', end_time: '16:00', block_type: 'RESEARCH', color: '#1890ff' },
                { start_time: '16:30', end_time: '17:00', block_type: 'REVIEW', color: '#722ed1' }
            ]
        },
        {
            name: '学习时间段',
            blocks: [
                { start_time: '08:00', end_time: '10:00', block_type: 'GROWTH', color: '#52c41a' },
                { start_time: '14:00', end_time: '16:00', block_type: 'GROWTH', color: '#52c41a' },
                { start_time: '19:00', end_time: '21:00', block_type: 'GROWTH', color: '#52c41a' }
            ]
        }
    ];

    // 添加时间块到列表
    const addTimeBlock = () => {
        const newBlock = {
            id: Date.now().toString(),
            date: selectedDate.format('YYYY-MM-DD'),
            start_time: null,
            end_time: null,
            block_type: 'GROWTH',
            color: '#52c41a',
            is_recurring: false,
            recurrence_pattern: ''
        };
        setTimeBlocksList([...timeBlocksList, newBlock]);
    };

    // 更新时间块
    const updateTimeBlock = (id, field, value) => {
        setTimeBlocksList(prev => prev.map(block =>
            block.id === id ? { ...block, [field]: value } : block
        ));
    };

    // 删除时间块
    const removeTimeBlock = (id) => {
        setTimeBlocksList(prev => prev.filter(block => block.id !== id));
    };

    // 应用模板
    const applyTemplate = (template) => {
        const blocks = template.blocks.map(block => ({
            ...block,
            id: Date.now().toString() + Math.random(),
            date: selectedDate.format('YYYY-MM-DD'),
            is_recurring: false,
            recurrence_pattern: ''
        }));
        setTimeBlocksList(blocks);
        message.success(`已应用模板"${template.name}"`);
    };

    // 批量创建时间块
    const handleBatchCreate = async () => {
        if (timeBlocksList.length === 0) {
            message.warning('请至少添加一个时间块');
            return;
        }

        setLoading(true);
        try {
            // 验证时间块数据
            const validBlocks = timeBlocksList.filter(block =>
                block.start_time && block.end_time &&
                dayjs(block.start_time).isBefore(dayjs(block.end_time))
            );

            if (validBlocks.length === 0) {
                message.error('没有有效的时间块数据');
                return;
            }

            if (validBlocks.length < timeBlocksList.length) {
                message.warning(`${timeBlocksList.length - validBlocks.length} 个时间块数据无效，将被跳过`);
            }

            // 格式化数据
            const formattedBlocks = validBlocks.map(block => ({
                date: block.date,
                start_time: block.start_time,
                end_time: block.end_time,
                block_type: block.block_type,
                color: block.color,
                is_recurring: block.is_recurring,
                recurrence_pattern: block.recurrence_pattern
            }));

            await timeBlockService.batchCreateTimeBlocks({
                time_blocks: formattedBlocks
            });

            message.success(`成功创建 ${validBlocks.length} 个时间块`);
            setTimeBlocksList([]);
            onSuccess && onSuccess();
            onClose();
        } catch (error) {
            console.error('批量创建失败:', error);
            message.error('批量创建失败：' + (error.error || '未知错误'));
        } finally {
            setLoading(false);
        }
    };

    // 批量删除时间块
    const handleBatchDelete = async () => {
        if (selectedBlockIds.length === 0) {
            message.warning('请选择要删除的时间块');
            return;
        }

        setDeleteLoading(true);
        try {
            await timeBlockService.batchDeleteTimeBlocks({
                time_block_ids: selectedBlockIds
            });

            message.success(`成功删除 ${selectedBlockIds.length} 个时间块`);
            setSelectedBlockIds([]);
            onSuccess && onSuccess();
            onClose();
        } catch (error) {
            console.error('批量删除失败:', error);
            message.error('批量删除失败：' + (error.error || '未知错误'));
        } finally {
            setDeleteLoading(false);
        }
    };

    // 获取类型标签
    const getTypeLabel = (type) => {
        const option = typeOptions.find(opt => opt.value === type);
        return option ? option.label : type;
    };

    // 获取类型颜色
    const getTypeColor = (type) => {
        const option = typeOptions.find(opt => opt.value === type);
        return option ? option.color : '#d9d9d9';
    };

    // 批量创建表格列
    const createColumns = [
        {
            title: '开始时间',
            dataIndex: 'start_time',
            key: 'start_time',
            width: 140,
            render: (time, record) => (
                <TimePicker
                    value={time ? dayjs(time, 'HH:mm') : null}
                    onChange={(time, timeString) => updateTimeBlock(record.id, 'start_time', timeString)}
                    format="HH:mm"
                    placeholder="选择开始时间"
                    style={{ width: '100%' }}
                />
            )
        },
        {
            title: '结束时间',
            dataIndex: 'end_time',
            key: 'end_time',
            width: 140,
            render: (time, record) => (
                <TimePicker
                    value={time ? dayjs(time, 'HH:mm') : null}
                    onChange={(time, timeString) => updateTimeBlock(record.id, 'end_time', timeString)}
                    format="HH:mm"
                    placeholder="选择结束时间"
                    style={{ width: '100%' }}
                />
            )
        },
        {
            title: '类型',
            dataIndex: 'block_type',
            key: 'block_type',
            width: 120,
            render: (type, record) => (
                <Select
                    value={type}
                    onChange={(value) => updateTimeBlock(record.id, 'block_type', value)}
                    style={{ width: '100%' }}
                >
                    {typeOptions.map(option => (
                        <Option key={option.value} value={option.value}>
                            <Tag color={option.color}>{option.label}</Tag>
                        </Option>
                    ))}
                </Select>
            )
        },
        {
            title: '颜色',
            dataIndex: 'color',
            key: 'color',
            width: 80,
            render: (color, record) => (
                <ColorPicker
                    value={color}
                    onChange={(color) => updateTimeBlock(record.id, 'color', color.toHexString())}
                    showText
                    style={{ width: '100%' }}
                />
            )
        },
        {
            title: '操作',
            key: 'actions',
            width: 80,
            render: (_, record) => (
                <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => removeTimeBlock(record.id)}
                />
            )
        }
    ];

    return (
        <Modal
            title="时间块批量操作"
            open={visible}
            onCancel={onClose}
            width={1000}
            footer={[
                <Button key="cancel" onClick={onClose}>
                    取消
                </Button>,
                <Button
                    key="create"
                    type="primary"
                    loading={loading}
                    onClick={handleBatchCreate}
                    disabled={activeTab !== 'create' || timeBlocksList.length === 0}
                >
                    批量创建 ({timeBlocksList.length})
                </Button>,
                <Button
                    key="delete"
                    danger
                    loading={deleteLoading}
                    onClick={handleBatchDelete}
                    disabled={activeTab !== 'delete' || selectedBlockIds.length === 0}
                >
                    批量删除 ({selectedBlockIds.length})
                </Button>
            ]}
        >
            <div>
                <Space style={{ marginBottom: '16px' }}>
                    <Button
                        type={activeTab === 'create' ? 'primary' : 'default'}
                        onClick={() => setActiveTab('create')}
                    >
                        <PlusOutlined /> 批量创建
                    </Button>
                    <Button
                        type={activeTab === 'delete' ? 'primary' : 'default'}
                        onClick={() => setActiveTab('delete')}
                    >
                        <DeleteOutlined /> 批量删除
                    </Button>
                </Space>

                {activeTab === 'create' && (
                    <div>
                        {/* 预设模板 */}
                        <Card style={{ marginBottom: '16px' }}>
                            <Title level={5}>快速模板</Title>
                            <Space wrap>
                                {timeBlockTemplates.map((template, index) => (
                                    <Button
                                        key={index}
                                        onClick={() => applyTemplate(template)}
                                    >
                                        {template.name}
                                    </Button>
                                ))}
                                <Button
                                    icon={<PlusOutlined />}
                                    onClick={addTimeBlock}
                                    type="dashed"
                                >
                                    添加空白时间块
                                </Button>
                            </Space>
                        </Card>

                        {/* 时间块列表 */}
                        {timeBlocksList.length > 0 && (
                            <Card>
                                <div style={{ marginBottom: '16px' }}>
                                    <Space>
                                        <Text strong>时间块列表 ({timeBlocksList.length})</Text>
                                        <Text type="secondary">目标日期：{selectedDate.format('YYYY-MM-DD')}</Text>
                                    </Space>
                                </div>
                                <Table
                                    columns={createColumns}
                                    dataSource={timeBlocksList}
                                    rowKey="id"
                                    pagination={false}
                                    size="small"
                                    scroll={{ x: 600 }}
                                />
                            </Card>
                        )}

                        {timeBlocksList.length === 0 && (
                            <Empty
                                description="暂无时间块，请选择模板或手动添加"
                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                            />
                        )}
                    </div>
                )}

                {activeTab === 'delete' && (
                    <div>
                        <Alert
                            message="批量删除操作不可撤销"
                            description="请谨慎选择要删除的时间块。删除包含任务的时间块会失败。"
                            type="warning"
                            style={{ marginBottom: '16px' }}
                        />

                        <Card>
                            <Text>请先在时间块规划页面选择要删除的时间块，然后在此页面进行批量删除操作。</Text>
                            <div style={{ marginTop: '16px' }}>
                                <Text type="secondary">
                                    当前已选择 {selectedBlockIds.length} 个时间块
                                </Text>
                            </div>
                        </Card>
                    </div>
                )}
            </div>
        </Modal>
    );
};

export default TimeBlockBatchOperations;