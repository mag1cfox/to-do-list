import React from 'react';
import {
    Drawer,
    Space,
    Typography,
    Alert,
    List,
    Badge,
    Divider,
    Button,
    Tag
} from 'antd';
import {
    WarningOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined,
    ToolOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const ConflictDrawer = ({
    visible,
    onClose,
    conflicts,
    autoFixes,
    onAutoFixAll,
    severitySummary
}) => {
    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'critical':
                return <WarningOutlined style={{ color: '#ff4d4f' }} />;
            case 'high':
                return <ExclamationCircleOutlined style={{ color: '#fa8c16' }} />;
            case 'medium':
                return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
            case 'low':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
            default:
                return <InfoCircleOutlined />;
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical': return 'red';
            case 'high': return 'orange';
            case 'medium': return 'blue';
            case 'low': return 'green';
            default: return 'default';
        }
    };

    const renderConflict = (conflict, index) => (
        <List.Item key={index}>
            <Alert
                message={
                    <Space>
                        {getSeverityIcon(conflict.severity)}
                        <Tag color={getSeverityColor(conflict.severity)}>
                            {conflict.severity.toUpperCase()}
                        </Tag>
                        {conflict.message}
                    </Space>
                }
                description={
                    conflict.suggestions && conflict.suggestions.length > 0 && (
                        <div style={{ marginTop: '8px' }}>
                            <Text strong>解决建议：</Text>
                            <ul style={{ marginTop: '4px', paddingLeft: '20px', marginBottom: 0 }}>
                                {conflict.suggestions.map((suggestion, idx) => (
                                    <li key={idx}>{suggestion}</li>
                                ))}
                            </ul>
                        </div>
                    )
                }
                type={conflict.severity === 'critical' || conflict.severity === 'high' ? 'error' : 'warning'}
                showIcon={false}
                style={{ width: '100%' }}
            />
        </List.Item>
    );

    const renderAutoFix = (fix, index) => (
        <List.Item key={index}>
            <Alert
                message={
                    <Space>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        <Text>{fix.message}</Text>
                    </Space>
                }
                type="success"
                showIcon={false}
                style={{ width: '100%' }}
            />
        </List.Item>
    );

    return (
        <Drawer
            title={
                <Space>
                    <WarningOutlined style={{ color: '#ff4d4f' }} />
                    时间冲突详情
                    {conflicts.length > 0 && (
                        <Badge count={conflicts.length} style={{ backgroundColor: '#ff4d4f' }} />
                    )}
                </Space>
            }
            placement="right"
            onClose={onClose}
            open={visible}
            width={500}
        >
            {/* 严重程度统计 */}
            {severitySummary && (
                <div style={{ marginBottom: '16px' }}>
                    <Title level={5}>冲突统计</Title>
                    <Space wrap>
                        {Object.entries(severitySummary).map(([severity, count]) => (
                            count > 0 && (
                                <Tag key={severity} color={getSeverityColor(severity)}>
                                    {severity.toUpperCase()}: {count}
                                </Tag>
                            )
                        ))}
                    </Space>
                </div>
            )}

            {/* 自动修复结果 */}
            {autoFixes && autoFixes.length > 0 && (
                <>
                    <div style={{ marginBottom: '16px' }}>
                        <Title level={5}>
                            <CheckCircleOutlined style={{ color: '#52c41a', marginRight: '8px' }} />
                            自动修复结果
                        </Title>
                        <List
                            dataSource={autoFixes}
                            renderItem={renderAutoFix}
                            size="small"
                        />
                    </div>
                    <Divider />
                </>
            )}

            {/* 冲突详情 */}
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <Title level={5}>冲突列表</Title>
                    {conflicts.some(c => c.auto_fixable) && (
                        <Button
                            type="primary"
                            size="small"
                            icon={<ToolOutlined />}
                            onClick={onAutoFixAll}
                        >
                            自动修复所有
                        </Button>
                    )}
                </div>

                {conflicts.length === 0 ? (
                    <Alert
                        message="无冲突"
                        description="时间安排没有发现冲突"
                        type="success"
                        showIcon
                    />
                ) : (
                    <List
                        dataSource={conflicts}
                        renderItem={renderConflict}
                        size="small"
                    />
                )}
            </div>

            <Divider />

            {/* 解决方案建议 */}
            <div>
                <Title level={5}>通用解决方案建议：</Title>
                <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                    <li>调整时间块的时间范围，避免重叠</li>
                    <li>将任务移动到其他合适的时间块</li>
                    <li>拆分长时间的任务到多个时间块</li>
                    <li>删除不必要的时间块</li>
                    <li>调整任务类别以匹配时间块类型</li>
                </ul>
            </div>
        </Drawer>
    );
};

export default ConflictDrawer;