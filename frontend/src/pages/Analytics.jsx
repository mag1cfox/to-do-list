import React, { useState, useEffect } from 'react';
import {
    Card,
    Row,
    Col,
    Statistic,
    Select,
    DatePicker,
    Spin,
    message,
    Progress,
    Table,
    Tag,
    Empty,
    Typography,
    Divider
} from 'antd';
import {
    BarChartOutlined,
    PieChartOutlined,
    TrophyOutlined,
    ClockCircleOutlined,
    CheckCircleOutlined,
    CalendarOutlined
} from '@ant-design/icons';
import { Line, Pie, Column } from '@ant-design/plots';
import axios from 'axios';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const Analytics = () => {
    const [loading, setLoading] = useState(false);
    const [tasks, setTasks] = useState([]);
    const [pomodoroSessions, setPomodoroSessions] = useState([]);
    const [dateRange, setDateRange] = useState([]);
    const [timeRange, setTimeRange] = useState('week');

    // 统计数据
    const [stats, setStats] = useState({
        totalTasks: 0,
        completedTasks: 0,
        totalPomodoros: 0,
        totalFocusTime: 0,
        completionRate: 0,
        averageTaskTime: 0
    });

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

    // 获取任务数据
    const fetchTasks = async () => {
        try {
            setLoading(true);
            const response = await api.get('/tasks/');
            setTasks(response.data.tasks || []);
        } catch (error) {
            console.error('获取任务数据失败:', error);
            message.error('获取任务数据失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取番茄钟会话数据
    const fetchPomodoroSessions = async () => {
        try {
            setLoading(true);
            const response = await api.get('/pomodoro-sessions/');
            setPomodoroSessions(response.data.pomodoro_sessions || []);
        } catch (error) {
            console.error('获取番茄钟数据失败:', error);
            // 如果API不存在，使用模拟数据
            setPomodoroSessions([]);
        } finally {
            setLoading(false);
        }
    };

    // 计算统计数据
    const calculateStats = () => {
        const totalTasks = tasks.length;
        const completedTasks = tasks.filter(task => task.status === 'COMPLETED').length;
        const totalPomodoros = pomodoroSessions.length;
        const completedPomodoros = pomodoroSessions.filter(session => session.status === 'COMPLETED').length;
        const totalFocusTime = pomodoroSessions.reduce((sum, session) => {
            return sum + (session.actual_duration || session.planned_duration || 0);
        }, 0);

        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
        const averageTaskTime = completedTasks > 0 ? Math.round(totalFocusTime / completedTasks) : 0;

        setStats({
            totalTasks,
            completedTasks,
            totalPomodoros: completedPomodoros,
            totalFocusTime,
            completionRate,
            averageTaskTime
        });
    };

    // 按类别统计任务
    const getTasksByCategory = () => {
        const categoryCount = {};
        tasks.forEach(task => {
            const category = task.category_id || '未分类';
            categoryCount[category] = (categoryCount[category] || 0) + 1;
        });

        return Object.entries(categoryCount).map(([category, count]) => ({
            category,
            count,
            type: '任务数量'
        }));
    };

    // 按状态统计任务
    const getTasksByStatus = () => {
        const statusCount = {};
        tasks.forEach(task => {
            const status = getStatusText(task.status);
            statusCount[status] = (statusCount[status] || 0) + 1;
        });

        return Object.entries(statusCount).map(([status, count]) => ({
            status,
            count,
            percentage: tasks.length > 0 ? Math.round((count / tasks.length) * 100) : 0
        }));
    };

    // 获取最近7天的任务完成趋势
    const getTaskCompletionTrend = () => {
        const today = new Date();
        const trendData = [];

        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];

            const completedCount = tasks.filter(task => {
                if (task.updated_at) {
                    const taskDate = new Date(task.updated_at).toISOString().split('T')[0];
                    return task.status === 'COMPLETED' && taskDate === dateStr;
                }
                return false;
            }).length;

            trendData.push({
                date: `${date.getMonth() + 1}/${date.getDate()}`,
                completed: completedCount,
                total: tasks.filter(task => {
                    if (task.created_at) {
                        const taskDate = new Date(task.created_at).toISOString().split('T')[0];
                        return taskDate <= dateStr;
                    }
                    return false;
                }).length
            });
        }

        return trendData;
    };

    // 获取专注时间分布
    const getFocusTimeDistribution = () => {
        const hourCount = {};
        pomodoroSessions.forEach(session => {
            if (session.start_time) {
                const hour = new Date(session.start_time).getHours();
                const timeSlot = `${hour}:00-${hour + 1}:00`;
                hourCount[timeSlot] = (hourCount[timeSlot] || 0) + (session.actual_duration || session.planned_duration || 0);
            }
        });

        return Object.entries(hourCount)
            .map(([timeSlot, minutes]) => ({
                timeSlot,
                minutes,
                hours: (minutes / 60).toFixed(1)
            }))
            .sort((a, b) => parseInt(a.timeSlot) - parseInt(b.timeSlot));
    };

    // 状态文本映射
    const getStatusText = (status) => {
        const statusMap = {
            'PENDING': '待处理',
            'IN_PROGRESS': '进行中',
            'COMPLETED': '已完成',
            'CANCELLED': '已取消'
        };
        return statusMap[status] || status;
    };

    // 优先级文本映射
    const getPriorityText = (priority) => {
        const priorityMap = {
            'HIGH': '高',
            'MEDIUM': '中',
            'LOW': '低'
        };
        return priorityMap[priority] || priority;
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

    // 任务表格列定义
    const taskColumns = [
        {
            title: '任务标题',
            dataIndex: 'title',
            key: 'title',
            render: (text) => <Text strong>{text}</Text>
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
                <Tag color={status === 'COMPLETED' ? 'green' : status === 'IN_PROGRESS' ? 'blue' : 'default'}>
                    {getStatusText(status)}
                </Tag>
            )
        },
        {
            title: '优先级',
            dataIndex: 'priority',
            key: 'priority',
            render: (priority) => (
                <Tag color={getPriorityColor(priority)}>
                    {getPriorityText(priority)}
                </Tag>
            )
        },
        {
            title: '预计番茄钟',
            dataIndex: 'estimated_pomodoros',
            key: 'estimated_pomodoros',
            render: (count) => `${count || 0}个`
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (time) => time ? new Date(time).toLocaleDateString() : '-'
        }
    ];

    // 饼图配置
    const pieConfig = {
        data: getTasksByCategory(),
        angleField: 'count',
        colorField: 'category',
        radius: 0.8,
        label: {
            type: 'inner',
            offset: '-30%',
            content: ({ percent }) => `${(percent * 100).toFixed(0)}%`,
            style: {
                fontSize: 14,
                textAlign: 'center',
            },
        },
        interactions: [{ type: 'pie-legend-active' }, { type: 'element-active' }],
    };

    // 折线图配置
    const lineConfig = {
        data: getTaskCompletionTrend(),
        xField: 'date',
        yField: 'completed',
        smooth: true,
        point: {
            size: 5,
            shape: 'diamond',
        },
        tooltip: {
            formatter: (data) => ({
                name: '完成任务数',
                value: data.completed,
            }),
        },
    };

    // 柱状图配置
    const columnConfig = {
        data: getFocusTimeDistribution(),
        xField: 'timeSlot',
        yField: 'minutes',
        columnWidthRatio: 0.8,
        meta: {
            minutes: {
                alias: '专注时间(分钟)',
            },
        },
        tooltip: {
            formatter: (data) => ({
                name: '专注时间',
                value: `${data.minutes}分钟 (${data.hours}小时)`,
            }),
        },
    };

    useEffect(() => {
        fetchTasks();
        fetchPomodoroSessions();
    }, []);

    useEffect(() => {
        calculateStats();
    }, [tasks, pomodoroSessions]);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                    <Text>加载分析数据中...</Text>
                </div>
            </div>
        );
    }

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>
                <BarChartOutlined /> 数据分析和报表
            </Title>

            {/* 时间范围选择 */}
            <Card style={{ marginBottom: 16 }}>
                <Row gutter={16} align="middle">
                    <Col>
                        <Text>时间范围：</Text>
                    </Col>
                    <Col>
                        <Select
                            value={timeRange}
                            onChange={setTimeRange}
                            style={{ width: 120 }}
                        >
                            <Option value="today">今天</Option>
                            <Option value="week">最近7天</Option>
                            <Option value="month">最近30天</Option>
                            <Option value="all">全部</Option>
                        </Select>
                    </Col>
                    <Col>
                        <RangePicker
                            onChange={(dates) => setDateRange(dates)}
                            style={{ width: 240 }}
                        />
                    </Col>
                </Row>
            </Card>

            {/* 核心统计指标 */}
            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                <Col xs={24} sm={12} md={8} lg={4}>
                    <Card>
                        <Statistic
                            title="总任务数"
                            value={stats.totalTasks}
                            prefix={<CalendarOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={4}>
                    <Card>
                        <Statistic
                            title="已完成任务"
                            value={stats.completedTasks}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={4}>
                    <Card>
                        <Statistic
                            title="完成率"
                            value={stats.completionRate}
                            suffix="%"
                            prefix={<TrophyOutlined />}
                            valueStyle={{ color: '#722ed1' }}
                        />
                        <Progress
                            percent={stats.completionRate}
                            size="small"
                            style={{ marginTop: 8 }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={4}>
                    <Card>
                        <Statistic
                            title="完成番茄钟"
                            value={stats.totalPomodoros}
                            prefix={<ClockCircleOutlined />}
                            valueStyle={{ color: '#fa8c16' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={4}>
                    <Card>
                        <Statistic
                            title="总专注时间"
                            value={stats.totalFocusTime}
                            suffix="分钟"
                            prefix={<ClockCircleOutlined />}
                            valueStyle={{ color: '#13c2c2' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={4}>
                    <Card>
                        <Statistic
                            title="平均任务时间"
                            value={stats.averageTaskTime}
                            suffix="分钟"
                            prefix={<ClockCircleOutlined />}
                            valueStyle={{ color: '#eb2f96' }}
                        />
                    </Card>
                </Col>
            </Row>

            {/* 图表区域 */}
            <Row gutter={[16, 16]}>
                {/* 任务分类分布 */}
                <Col xs={24} lg={12}>
                    <Card title="任务分类分布" extra={<PieChartOutlined />}>
                        {getTasksByCategory().length > 0 ? (
                            <Pie {...pieConfig} height={300} />
                        ) : (
                            <Empty description="暂无数据" />
                        )}
                    </Card>
                </Col>

                {/* 任务完成趋势 */}
                <Col xs={24} lg={12}>
                    <Card title="任务完成趋势" extra={<BarChartOutlined />}>
                        {getTaskCompletionTrend().length > 0 ? (
                            <Line {...lineConfig} height={300} />
                        ) : (
                            <Empty description="暂无数据" />
                        )}
                    </Card>
                </Col>

                {/* 专注时间分布 */}
                <Col xs={24} lg={12}>
                    <Card title="专注时间分布" extra={<ClockCircleOutlined />}>
                        {getFocusTimeDistribution().length > 0 ? (
                            <Column {...columnConfig} height={300} />
                        ) : (
                            <Empty description="暂无数据" />
                        )}
                    </Card>
                </Col>

                {/* 任务状态统计 */}
                <Col xs={24} lg={12}>
                    <Card title="任务状态统计" extra={<CheckCircleOutlined />}>
                        <div style={{ padding: '16px 0' }}>
                            {getTasksByStatus().map((item, index) => (
                                <div key={index} style={{ marginBottom: 16 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                                        <Text>{item.status}</Text>
                                        <Text strong>{item.count} ({item.percentage}%)</Text>
                                    </div>
                                    <Progress
                                        percent={item.percentage}
                                        showInfo={false}
                                        strokeColor={
                                            item.status === '已完成' ? '#52c41a' :
                                            item.status === '进行中' ? '#1890ff' :
                                            item.status === '待处理' ? '#fa8c16' : '#d9d9d9'
                                        }
                                    />
                                </div>
                            ))}
                        </div>
                    </Card>
                </Col>
            </Row>

            <Divider />

            {/* 任务详情表格 */}
            <Card title="任务详情" style={{ marginTop: 16 }}>
                <Table
                    columns={taskColumns}
                    dataSource={tasks}
                    rowKey="id"
                    pagination={{
                        pageSize: 10,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 个任务`,
                    }}
                    locale={{
                        emptyText: '暂无任务数据'
                    }}
                />
            </Card>
        </div>
    );
};

export default Analytics;