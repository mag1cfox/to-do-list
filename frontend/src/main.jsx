import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App.jsx'
import { useAuthStore } from './stores/authStore'
import './index.css'

// 认证初始化组件
const AuthInitializer = ({ children }) => {
  const { checkAuth } = useAuthStore()

  useEffect(() => {
    // 应用启动时检查认证状态
    checkAuth()
  }, [checkAuth])

  return children
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider locale={zhCN}>
        <AuthInitializer>
          <App />
        </AuthInitializer>
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>,
)