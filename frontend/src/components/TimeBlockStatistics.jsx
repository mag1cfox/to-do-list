import React, { useState, useEffect } from 'react';
import {
    Card,
    Row,
    Col,
    Statistic,
    DatePicker,
    Select,
    Spin,
    Empty,
    Tabs,
    Table,
    Tag,
    Progress,
    Tooltip,
    Typography,
    Space
} from 'antd';
import {
    BarChartOutlined,
    ClockCircleOutlined,
    CalendarOutlined,
    FireOutlined,
    TrophyOutlined,
    LineChartOutlined
} from '@ant-design/icons';
import { timeBlockService } from '../services/api';
import { Pie, Column, Line } from '@ant-design/plots';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text } = Typography;

const TimeBlockStatistics = () => {
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dateRange, setDateRange] = useState([
        dayjs().subtract(30, 'day'),
        dayjs()
    ]);
    const [activeTab, setActiveTab] = useState('overview');

    // 获取统计数据
    const fetchStatistics = async (range = dateRange) => {
        setLoading(true);
        try {
            const params = {
                start_date: range[0].format('YYYY-MM-DD'),
                end_date: range[1].format('YYYY-MM-DD')
            };
            const data = await timeBlockService.getStatistics(params);
            setStatistics(data);
        } catch (error) {
            console.error('获取统计数据失败:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatistics();
    }, []);

    const handleDateRangeChange = (range) => {
        if (range && range.length === 2) {
            setDateRange(range);
            fetchStatistics(range);
        }
    };

    const getPieData = () => {
        if (!statistics?.by_type) return [];
        return Object.entries(statistics.by_type).map(([type, data]) => ({
            type: getTypeLabel(type),
            value: data.hours,
            percentage: data.percentage
        }));
    };

    const getDailyData = () => {
        if (!statistics?.by_date) return [];
        return Object.entries(statistics.by_date)
            .map(([date, data]) => ({
                date: dayjs(date).format('MM-DD'),
                hours: data.hours,
                blocks: data.count
            }))
            .sort((a, b) => dayjs(a.date).diff(dayjs(b.date)));
    };

    const getWeekdayData = () => {
        if (!statistics?.by_weekday) return [];
        const weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'];
        return Object.entries(statistics.by_weekday).map(([weekday, data]) => ({
            weekday,
            hours: data.hours,
            blocks: data.count
        }));
    };

    const getHourlyData = () => {
        if (!statistics?.by_hour) return [];
        return Object.entries(statistics.by_hour)
            .map(([hour, data]) => ({
                hour,
                minutes: data.minutes,
                blocks: data.count
            }))
            .sort((a, b) => parseInt(a.hour) - parseInt(b.hour));
    };

    const getTypeLabel = (type) => {
        const typeMap = {
            'RESEARCH': '科研',
            'GROWTH': '成长',
            'REST': '休息',
            'ENTERTAINMENT': '娱乐',
            'REVIEW': '复盘'
        };
        return typeMap[type] || type;
    };

    const getTypeColor = (type) => {
        const colorMap = {
            'RESEARCH': '#1890ff',
            'GROWTH': '#52c41a',
            'REST': '#fa8c16',
            'ENTERTAINMENT': '#eb2f96',
            'REVIEW': '#722ed1'
        };
        return colorMap[type] || '#d9d9d9';
    };

    const pieConfig = {
        data: getPieData(),
        angleField: 'value',
        colorField: 'type',
        radius: 0.8,
        label: {
            type: 'outer',
            content: '{name}: {value}h ({percentage}%)'
        },
        interactions: [{ type: 'pie-legend-active' }, { type: 'element-active' }]
    };

    const dailyConfig = {
        data: getDailyData(),
        xField: 'date',
        yField: 'hours',
        height: 300,
        point: {
            size: 5,
            shape: 'diamond'
        },
        tooltip: {
            formatter: (datum) => ({
                name: '时长',
                value: `${datum.hours}小时`
            })
        }
    };

    const hourlyConfig = {
        data: getHourlyData(),
        xField: 'hour',
        yField: 'minutes',
        height: 300,
        columnWidthRatio: 0.8,
        tooltip: {
            formatter: (datum) => ({
                name: '时长',
                value: `${datum.minutes}分钟`
            })
        }
    };

    const typeTableColumns = [
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
            render: (type) => (
                <Tag color={getTypeColor(type)}>
                    {getTypeLabel(type)}
                </Tag>
            )
        },
        {
            title: '时间块数量',
            dataIndex: 'count',
            key: 'count',
            sorter: (a, b) => a.count - b.count
        },
        {
            title: '总时长',
            dataIndex: 'hours',
            key: 'hours',
            render: (hours) => `${hours}小时`,
            sorter: (a, b) => a.hours - b.hours
        },
        {
            title: '占比',
            dataIndex: 'percentage',
            key: 'percentage',
            render: (percentage) => <Progress percent={percentage} size="small" />
        }
    ];

    const typeTableData = statistics?.by_type ?
        Object.entries(statistics.by_type).map(([type, data]) => ({
            key: type,
            type,
            ...data
        })) : [];

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '40px' }}>
                <Spin size="large" />
                <div style={{ marginTop: '16px' }}>加载统计数据中...</div>
            </div>
        );
    }

    if (!statistics) {
        return (
            <Empty
                description="暂无统计数据"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
        );
    }

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>
                <BarChartOutlined /> 时间块统计分析
            </Title>

            {/* 日期范围选择器 */}
            <Card style={{ marginBottom: '24px' }}>
                <Row justify="space-between" align="middle">
                    <Col>
                        <Text strong>统计时间范围：</Text>
                        <RangePicker
                            value={dateRange}
                            onChange={handleDateRangeChange}
                            format="YYYY-MM-DD"
                            style={{ marginLeft: '16px' }}
                        />
                    </Col>
                    <Col>
                        <Space>
                            <Text>统计天数：{statistics.period?.days || 0}天</Text>
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={() => fetchStatistics(dateRange)}
                            >
                                刷新
                            </Button>
                        </Space>
                    </Col>
                </Row>
            </Card>

            {/* 总览统计 */}
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
                <TabPane tab="总览" key="overview">
                    <Row gutter={16} style={{ marginBottom: '24px' }}>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="总时间块"
                                    value={statistics.summary?.total_blocks || 0}
                                    suffix="个"
                                    prefix={<CalendarOutlined />}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="总时长"
                                    value={statistics.summary?.total_hours || 0}
                                    suffix="小时"
                                    prefix={<ClockCircleOutlined />}
                                    precision={1}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="日均时间块"
                                    value={statistics.summary?.avg_blocks_per_day || 0}
                                    suffix="个"
                                    prefix={<BarChartOutlined />}
                                    precision={1}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="日均时长"
                                    value={statistics.summary?.avg_hours_per_day || 0}
                                    suffix="小时"
                                    prefix={<FireOutlined />}
                                    precision={1}
                                />
                            </Card>
                        </Col>
                    </Row>

                    <Row gutter={16} style={{ marginBottom: '24px' }}>
                        <Col span={8}>
                            <Card title="最常用类型" size="small">
                                <div style={{ textAlign: 'center' }}>
                                    <Tag
                                        color={getTypeColor(statistics.summary?.most_used_type)}
                                        style={{ fontSize: '16px', padding: '4px 12px' }}
                                    >
                                        {getTypeLabel(statistics.summary?.most_used_type || '无')}
                                    </Tag>
                                </div>
                            </Card>
                        </Col>
                        <Col span={8}>
                            <Card title="最忙碌一天" size="small">
                                <div style={{ textAlign: 'center' }}>
                                    <Text strong>
                                        {statistics.summary?.busiest_day || '无'}
                                    </Text>
                                </div>
                            </Card>
                        </Col>
                        <Col span={8}>
                            <Card title="最活跃时段" size="small">
                                <div style={{ textAlign: 'center' }}>
                                    <Text strong>
                                        {statistics.summary?.most_active_hour || '无'}
                                    </Text>
                                </div>
                            </Card>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Card title="类型分布" extra={<TrophyOutlined />}>
                                <Pie {...pieConfig} height={300} />
                            </Card>
                        </Col>
                        <Col span={12}>
                            <Card title="每日时长趋势" extra={<LineChartOutlined />}>
                                <Line {...dailyConfig} />
                            </Card>
                        </Col>
                    </Row>
                </TabPane>

                <TabPane tab="类型分析" key="types">
                    <Row gutter={16}>
                        <Col span={16}>
                            <Card title="类型详细统计">
                                <Table
                                    columns={typeTableColumns}
                                    dataSource={typeTableData}
                                    pagination={false}
                                    size="middle"
                                />
                            </Card>
                        </Col>
                        <Col span={8}>
                            <Card title="类型占比" extra={<TrophyOutlined />}>
                                <Pie {...pieConfig} height={250} />
                            </Card>
                        </Col>
                    </Row>
                </TabPane>

                <TabPane tab="时间分析" key="time">
                    <Row gutter={16}>
                        <Col span={12}>
                            <Card title="星期分布">
                                <Column
                                    data={getWeekdayData()}
                                    xField="weekday"
                                    yField="hours"
                                    height={300}
                                    columnWidthRatio={0.6}
                                    meta={{
                                        weekday: { alias: '星期' },
                                        hours: { alias: '时长(小时)' }
                                    }}
                                />
                            </Card>
                        </Col>
                        <Col span={12}>
                            <Card title="时段分布">
                                <Column {...hourlyConfig} />
                            </Card>
                        </Col>
                    </Row>
                </TabPane>

                <TabPane tab="每日详情" key="daily">
                    <Card title="每日时间块详情">
                        <Table
                            columns={[
                                {
                                    title: '日期',
                                    dataIndex: 'date',
                                    key: 'date',
                                    render: (date) => dayjs(date).format('YYYY-MM-DD')
                                },
                                {
                                    title: '时间块数量',
                                    dataIndex: 'count',
                                    key: 'count'
                                },
                                {
                                    title: '总时长',
                                    dataIndex: 'hours',
                                    key: 'hours',
                                    render: (hours) => `${hours}小时`
                                }
                            ]}
                            dataSource={Object.entries(statistics.by_date || {}).map(([date, data]) => ({
                                key: date,
                                date,
                                ...data
                            }))}
                            pagination={{ pageSize: 10 }}
                            size="middle"
                        />
                    </Card>
                </TabPane>
            </Tabs>
        </div>
    );
};

export default TimeBlockStatistics;