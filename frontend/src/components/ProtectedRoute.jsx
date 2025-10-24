import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Card } from 'antd'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated || !user) {
    return (
      <Card title="需要登录" style={{ margin: '20px', textAlign: 'center' }}>
        <p>请先登录以访问此页面</p>
        <p>正在跳转到登录页面...</p>
        <Navigate to="/login" replace />
      </Card>
    )
  }

  return children
}

export default ProtectedRoute