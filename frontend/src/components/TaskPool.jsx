import React from 'react';
import {
    Card,
    Space,
    Typography,
    Tag,
    Empty
} from 'antd';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { DragOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const TaskPool = ({ tasks }) => {
    return (
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

            <div style={{ margin: '12px 0' }} />

            <Text type="secondary" style={{ fontSize: '12px' }}>
                💡 拖拽任务到左侧时间块进行调度
            </Text>
        </Card>
    );
};

export default TaskPool;