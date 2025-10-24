import React from 'react';
import {
    Card,
    Button,
    Space,
    Typography,
    Badge,
    Popconfirm,
    Tooltip
} from 'antd';
import {
    EditOutlined,
    DeleteOutlined
} from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import dayjs from 'dayjs';
import { timeBlockService } from '../services/api';

const { Text } = Typography;

const TimeBlockItem = ({ block, index, onEdit, onDelete, onUnscheduleTask, blockTypeConfig }) => {
    const config = blockTypeConfig[block.block_type] || { label: block.block_type, color: '#1890ff' };

    const handleUnscheduleTask = async (taskId) => {
        try {
            await timeBlockService.unscheduleTask(block.id, taskId);
            onUnscheduleTask?.();
        } catch (error) {
            console.error('移除任务失败:', error);
        }
    };

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
                                                            onConfirm={() => handleUnscheduleTask(task.id)}
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
                            onClick={() => onEdit(block)}
                            style={{ color: '#fff' }}
                        />
                    </Tooltip>
                    <Tooltip title="删除">
                        <Popconfirm
                            title="确定删除？"
                            description="删除时间块将同时移除其中的任务安排"
                            onConfirm={() => onDelete(block.id)}
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

export default TimeBlockItem;