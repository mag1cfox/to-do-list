import { useState, useEffect } from 'react'
import { Form, Input, Button, Card, Tabs, message, Space } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

function Login() {
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('login')
  const navigate = useNavigate()
  const { login, register, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])

  const onLogin = async (values) => {
    setLoading(true)
    try {
      const response = await login(values)
      console.log('登录响应:', response)
      message.success('登录成功！')
      navigate('/')
    } catch (error) {
      console.error('登录失败:', error)
      // 显示更详细的错误信息
      if (error.error) {
        message.error(`登录失败: ${error.error}`)
      } else if (error.message) {
        message.error(`登录失败: ${error.message}`)
      } else {
        message.error('登录失败: 用户名或密码错误')
      }
    } finally {
      setLoading(false)
    }
  }

  const onRegister = async (values) => {
    setLoading(true)
    try {
      const response = await register(values)
      console.log('注册响应:', response)
      message.success('注册成功！请登录')
      setActiveTab('login')
    } catch (error) {
      console.error('注册失败:', error)
      // 显示更详细的错误信息
      if (error.error) {
        message.error(`注册失败: ${error.error}`)
      } else if (error.message) {
        message.error(`注册失败: ${error.message}`)
      } else {
        message.error('注册失败: 请检查输入信息')
      }
    } finally {
      setLoading(false)
    }
  }

  const tabItems = [
    {
      key: 'login',
      label: '登录',
      children: (
        <Form
          name="login"
          onFinish={onLogin}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
      )
    },
    {
      key: 'register',
      label: '注册',
      children: (
        <Form
          name="register"
          onFinish={onRegister}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注册
            </Button>
          </Form.Item>
        </Form>
      )
    }
  ]

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', paddingTop: '50px' }}>
      <Card title="时间管理系统">
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
        />
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <Space>
            <Link to="/">返回首页</Link>
          </Space>
        </div>
      </Card>
    </div>
  )
}

export default Login