import React from 'react';
import {
    Card,
    Space,
    Typography
} from 'antd';

const { Text } = Typography;

const BlockTypeLegend = ({ blockTypeConfig }) => {
    return (
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
    );
};

export default BlockTypeLegend;