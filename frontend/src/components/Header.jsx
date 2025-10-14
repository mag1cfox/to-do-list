import { Layout, Menu, Button, Space } from 'antd'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { UserOutlined } from '@ant-design/icons'

const { Header: AntHeader } = Layout

function Header() {
  const location = useLocation()
  const { isAuthenticated, user, logout } = useAuthStore()

  const menuItems = [
    {
      key: '/',
      label: <Link to="/">首页</Link>
    },
    {
      key: '/tasks',
      label: <Link to="/tasks">任务管理</Link>
    },
    {
      key: '/projects',
      label: <Link to="/projects">项目管理</Link>
    },
    {
      key: '/calendar',
      label: <Link to="/calendar">日历视图</Link>
    },
    {
      key: '/scheduler',
      label: <Link to="/scheduler">时间块调度</Link>
    },
    {
      key: '/pomodoro',
      label: <Link to="/pomodoro">番茄钟</Link>
    },
    {
      key: '/analytics',
      label: <Link to="/analytics">数据分析</Link>
    },
    {
      key: '/settings',
      label: <Link to="/settings">系统设置</Link>
    }
  ]

  return (
    <AntHeader style={{ display: 'flex', alignItems: 'center' }}>
      <div style={{ color: 'white', fontSize: '18px', fontWeight: 'bold', marginRight: '24px' }}>
        时间管理系统
      </div>

      <Menu
        theme="dark"
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{ flex: 1 }}
      />

      <Space>
        {isAuthenticated ? (
          <>
            <Link to="/profile" style={{ color: 'white', display: 'flex', alignItems: 'center' }}>
              <UserOutlined style={{ marginRight: 4 }} />
              {user?.username}
            </Link>
            <Button type="primary" onClick={logout}>
              退出登录
            </Button>
          </>
        ) : (
          <Link to="/login">
            <Button type="primary">登录</Button>
          </Link>
        )}
      </Space>
    </AntHeader>
  )
}

export default Header