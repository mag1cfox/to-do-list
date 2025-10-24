import React, { useState, useEffect } from 'react'
import { Card, Typography, Row, Col, DatePicker, Button, Space, Spin, Empty } from 'antd'
import { ArrowLeftOutlined, BarChartOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import DataVisualizationReport from '../components/DataVisualizationReport'

const { Title } = Typography
const { RangePicker } = DatePicker

function Reports() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/')}
          >
            返回首页
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            <BarChartOutlined /> 数据报表
          </Title>
        </Space>
      </div>

      <DataVisualizationReport />
    </div>
  )
}

export default Reports