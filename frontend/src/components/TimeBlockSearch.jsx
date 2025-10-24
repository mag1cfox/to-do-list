import React, { useState, useEffect } from 'react';
import {
    Card,
    Input,
    Select,
    DatePicker,
    Button,
    Table,
    Tag,
    Space,
    Row,
    Col,
    Switch,
    InputNumber,
    Tooltip,
    Typography,
    Alert,
    Empty,
    Spin,
    message
} from 'antd';
import {
    SearchOutlined,
    ClearOutlined,
    FilterOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    FileTextOutlined
} from '@ant-design/icons';
import { timeBlockService } from '../services/api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

const TimeBlockSearch = ({ onSearchResult, onTimeBlockSelect }) => {
    const [searchParams, setSearchParams] = useState({
        keyword: '',
        type: undefined,
        start_date: null,
        end_date: null,
        has_tasks: undefined,
        min_duration: null,
        max_duration: null,
        sort_by: 'date',
        sort_order: 'desc',
        limit: 50
    });
    const [searchResults, setSearchResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [totalCount, setTotalCount] = useState(0);

    // 时间块类型选项
    const typeOptions = [
        { value: 'RESEARCH', label: '科研', color: '#1890ff' },
        { value: 'GROWTH', label: '成长', color: '#52c41a' },
        { value: 'REST', label: '休息', color: '#fa8c16' },
        { value: 'ENTERTAINMENT', label: '娱乐', color: '#eb2f96' },
        { value: 'REVIEW', label: '复盘', color: '#722ed1' }
    ];

    // 执行搜索
    const handleSearch = async () => {
        setLoading(true);
        try {
            const params = { ...searchParams };

            // 转换日期格式
            if (params.start_date) {
                params.start_date = params.start_date.format('YYYY-MM-DD');
            }
            if (params.end_date) {
                params.end_date = params.end_date.format('YYYY-MM-DD');
            }

            // 移除空值
            Object.keys(params).forEach(key => {
                if (params[key] === null || params[key] === '' || params[key] === undefined) {
                    delete params[key];
                }
            });

            const response = await timeBlockService.searchTimeBlocks(params);
            setSearchResults(response.results || []);
            setTotalCount(response.count || 0);

            if (onSearchResult) {
                onSearchResult(response);
            }

            message.success(`找到 ${response.count} 个时间块`);
        } catch (error) {
            console.error('搜索失败:', error);
            message.error('搜索失败：' + (error.error || '未知错误'));
        } finally {
            setLoading(false);
        }
    };

    // 重置搜索条件
    const handleReset = () => {
        setSearchParams({
            keyword: '',
            type: undefined,
            start_date: null,
            end_date: null,
            has_tasks: undefined,
            min_duration: null,
            max_duration: null,
            sort_by: 'date',
            sort_order: 'desc',
            limit: 50
        });
        setSearchResults([]);
        setTotalCount(0);
    };

    // 更新搜索参数
    const updateSearchParams = (key, value) => {
        setSearchParams(prev => ({
            ...prev,
            [key]: value
        }));
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

    // 格式化时间
    const formatTime = (timeStr) => {
        return dayjs(timeStr).format('HH:mm');
    };

    // 计算时长
    const getDuration = (startTime, endTime) => {
        const start = dayjs(startTime);
        const end = dayjs(endTime);
        return end.diff(start, 'minute');
    };

    // 表格列配置
    const columns = [
        {
            title: '日期',
            dataIndex: 'date',
            key: 'date',
            width: 120,
            sorter: (a, b) => dayjs(a.date).diff(dayjs(b.date)),
            render: (date) => dayjs(date).format('MM-DD')
        },
        {
            title: '时间',
            key: 'time',
            width: 140,
            render: (_, record) => (
                <Text>
                    {formatTime(record.start_time)} - {formatTime(record.end_time)}
                </Text>
            )
        },
        {
            title: '类型',
            dataIndex: 'block_type',
            key: 'block_type',
            width: 100,
            render: (type) => (
                <Tag color={getTypeColor(type)}>
                    {getTypeLabel(type)}
                </Tag>
            )
        },
        {
            title: '时长',
            key: 'duration',
            width: 80,
            render: (_, record) => (
                <Text>{getDuration(record.start_time, record.end_time)}分钟</Text>
            )
        },
        {
            title: '任务',
            key: 'tasks',
            width: 200,
            render: (_, record) => {
                const tasks = record.scheduled_tasks || [];
                if (tasks.length === 0) {
                    return <Text type="secondary">无任务</Text>;
                }
                return (
                    <Space direction="vertical" size="small">
                        {tasks.slice(0, 2).map(task => (
                            <Tooltip key={task.id} title={task.description}>
                                <Text ellipsis style={{ maxWidth: '180px' }}>
                                    {task.title}
                                </Text>
                            </Tooltip>
                        ))}
                        {tasks.length > 2 && (
                            <Text type="secondary">+{tasks.length - 2} 更多</Text>
                        )}
                    </Space>
                );
            }
        },
        {
            title: '操作',
            key: 'actions',
            width: 100,
            render: (_, record) => (
                <Space>
                    <Button
                        type="link"
                        size="small"
                        onClick={() => onTimeBlockSelect && onTimeBlockSelect(record)}
                    >
                        查看
                    </Button>
                </Space>
            )
        }
    ];

    // 快速搜索预设
    const quickSearches = [
        {
            name: '最近7天',
            params: {
                start_date: dayjs().subtract(7, 'day'),
                end_date: dayjs()
            }
        },
        {
            name: '本周',
            params: {
                start_date: dayjs().startOf('week'),
                end_date: dayjs().endOf('week')
            }
        },
        {
            name: '本月',
            params: {
                start_date: dayjs().startOf('month'),
                end_date: dayjs().endOf('month')
            }
        },
        {
            name: '无任务时间块',
            params: {
                has_tasks: 'false'
            }
        }
    ];

    const applyQuickSearch = (quickSearch) => {
        setSearchParams(prev => ({
            ...prev,
            ...quickSearch.params
        }));
        setTimeout(handleSearch, 100);
    };

    return (
        <div style={{ padding: '24px' }}>
            <Title level={3}>
                <SearchOutlined /> 时间块搜索
            </Title>

            {/* 基础搜索 */}
            <Card style={{ marginBottom: '16px' }}>
                <Row gutter={16} align="middle">
                    <Col span={8}>
                        <Input
                            placeholder="搜索关键词..."
                            value={searchParams.keyword}
                            onChange={(e) => updateSearchParams('keyword', e.target.value)}
                            prefix={<SearchOutlined />}
                            allowClear
                        />
                    </Col>
                    <Col span={4}>
                        <Select
                            placeholder="时间块类型"
                            value={searchParams.type}
                            onChange={(value) => updateSearchParams('type', value)}
                            allowClear
                            style={{ width: '100%' }}
                        >
                            {typeOptions.map(type => (
                                <Option key={type.value} value={type.value}>
                                    <Tag color={type.color}>{type.label}</Tag>
                                </Option>
                            ))}
                        </Select>
                    </Col>
                    <Col span={8}>
                        <RangePicker
                            value={[searchParams.start_date, searchParams.end_date]}
                            onChange={(dates) => {
                                updateSearchParams('start_date', dates ? dates[0] : null);
                                updateSearchParams('end_date', dates ? dates[1] : null);
                            }}
                            style={{ width: '100%' }}
                        />
                    </Col>
                    <Col span={4}>
                        <Space>
                            <Button
                                type="primary"
                                icon={<SearchOutlined />}
                                onClick={handleSearch}
                                loading={loading}
                            >
                                搜索
                            </Button>
                            <Button
                                icon={<ClearOutlined />}
                                onClick={handleReset}
                            >
                                重置
                            </Button>
                        </Space>
                    </Col>
                </Row>
            </Card>

            {/* 快速搜索 */}
            <Card style={{ marginBottom: '16px' }}>
                <Space wrap>
                    <Text strong>快速搜索：</Text>
                    {quickSearches.map((quickSearch, index) => (
                        <Button
                            key={index}
                            size="small"
                            onClick={() => applyQuickSearch(quickSearch)}
                        >
                            {quickSearch.name}
                        </Button>
                    ))}
                    <Button
                        size="small"
                        icon={<FilterOutlined />}
                        onClick={() => setShowAdvanced(!showAdvanced)}
                    >
                        {showAdvanced ? '隐藏高级搜索' : '显示高级搜索'}
                    </Button>
                </Space>
            </Card>

            {/* 高级搜索 */}
            {showAdvanced && (
                <Card style={{ marginBottom: '16px', backgroundColor: '#fafafa' }}>
                    <Title level={5}>高级搜索选项</Title>
                    <Row gutter={16}>
                        <Col span={6}>
                            <div style={{ marginBottom: '16px' }}>
                                <Text>是否包含任务：</Text>
                                <Select
                                    value={searchParams.has_tasks}
                                    onChange={(value) => updateSearchParams('has_tasks', value)}
                                    allowClear
                                    style={{ width: '100%', marginTop: '8px' }}
                                >
                                    <Option value="true">包含任务</Option>
                                    <Option value="false">不包含任务</Option>
                                </Select>
                            </div>
                        </Col>
                        <Col span={6}>
                            <div style={{ marginBottom: '16px' }}>
                                <Text>最小时长（分钟）：</Text>
                                <InputNumber
                                    value={searchParams.min_duration}
                                    onChange={(value) => updateSearchParams('min_duration', value)}
                                    min={1}
                                    style={{ width: '100%', marginTop: '8px' }}
                                />
                            </div>
                        </Col>
                        <Col span={6}>
                            <div style={{ marginBottom: '16px' }}>
                                <Text>最大时长（分钟）：</Text>
                                <InputNumber
                                    value={searchParams.max_duration}
                                    onChange={(value) => updateSearchParams('max_duration', value)}
                                    min={1}
                                    style={{ width: '100%', marginTop: '8px' }}
                                />
                            </div>
                        </Col>
                        <Col span={6}>
                            <div style={{ marginBottom: '16px' }}>
                                <Text>排序方式：</Text>
                                <Select
                                    value={searchParams.sort_by}
                                    onChange={(value) => updateSearchParams('sort_by', value)}
                                    style={{ width: '100%', marginTop: '8px' }}
                                >
                                    <Option value="date">按日期</Option>
                                    <Option value="duration">按时长</Option>
                                </Select>
                            </div>
                        </Col>
                        <Col span={6}>
                            <div style={{ marginBottom: '16px' }}>
                                <Text>排序顺序：</Text>
                                <Select
                                    value={searchParams.sort_order}
                                    onChange={(value) => updateSearchParams('sort_order', value)}
                                    style={{ width: '100%', marginTop: '8px' }}
                                >
                                    <Option value="desc">降序</Option>
                                    <Option value="asc">升序</Option>
                                </Select>
                            </div>
                        </Col>
                        <Col span={6}>
                            <div style={{ marginBottom: '16px' }}>
                                <Text>结果数量限制：</Text>
                                <InputNumber
                                    value={searchParams.limit}
                                    onChange={(value) => updateSearchParams('limit', value)}
                                    min={1}
                                    max={200}
                                    style={{ width: '100%', marginTop: '8px' }}
                                />
                            </div>
                        </Col>
                    </Row>
                </Card>
            )}

            {/* 搜索结果 */}
            <Card>
                <div style={{ marginBottom: '16px' }}>
                    <Space>
                        <Text strong>搜索结果：</Text>
                        <Text>共找到 {totalCount} 个时间块</Text>
                        {loading && <Spin size="small" />}
                    </Space>
                </div>

                {searchResults.length === 0 && !loading ? (
                    <Empty
                        description="暂无搜索结果"
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                    />
                ) : (
                    <Table
                        columns={columns}
                        dataSource={searchResults}
                        rowKey="id"
                        pagination={{
                            total: totalCount,
                            pageSize: 20,
                            showSizeChanger: true,
                            showQuickJumper: true,
                            showTotal: (total, range) =>
                                `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
                        }}
                        loading={loading}
                        size="middle"
                        scroll={{ x: 800 }}
                    />
                )}
            </Card>
        </div>
    );
};

export default TimeBlockSearch;