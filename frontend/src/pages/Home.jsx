import { Card, Row, Col, Statistic, Button, Space } from 'antd'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

function Home() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1>欢迎使用时间管理系统</h1>
        <p style={{ fontSize: '16px', color: '#666' }}>
          智能推荐与自动化流程的个人时间管理工具
        </p>
      </div>

      {!isAuthenticated ? (
        <Card style={{ maxWidth: '400px', margin: '0 auto', textAlign: 'center' }}>
          <h3>开始使用</h3>
          <p style={{ marginBottom: '24px' }}>
            请先登录或注册账户来开始管理您的时间
          </p>
          <Space>
            <Link to="/login">
              <Button type="primary" size="large">
                立即登录
              </Button>
            </Link>
          </Space>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic title="今日任务" value={0} suffix="/ 0" />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic title="完成率" value={0} suffix="%" />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic title="专注时间" value={0} suffix="分钟" />
            </Card>
          </Col>

          <Col span={24}>
            <Card
              title="快速开始"
              extra={
                <Link to="/tasks">
                  <Button type="primary">管理任务</Button>
                </Link>
              }
            >
              <p>开始规划您的时间，提高工作效率！</p>
              <Space>
                <Button>创建时间块</Button>
                <Button>添加任务</Button>
                <Button>开始专注</Button>
              </Space>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  )
}

export default Home