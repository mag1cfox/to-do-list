import React, { useState } from 'react';
import { Card, Typography, Button, Space } from 'antd';
import { ArrowLeftOutlined, BarChartOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import TimeBlockStatistics from '../components/TimeBlockStatistics';

const { Title } = Typography;

const TimeBlockAnalytics = () => {
    const navigate = useNavigate();

    return (
        <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '24px' }}>
                <Space>
                    <Button
                        icon={<ArrowLeftOutlined />}
                        onClick={() => navigate('/scheduler')}
                    >
                        返回时间块规划
                    </Button>
                    <Title level={2} style={{ margin: 0 }}>
                        <BarChartOutlined /> 时间块数据分析
                    </Title>
                </Space>
            </div>

            <TimeBlockStatistics />
        </div>
    );
};

export default TimeBlockAnalytics;