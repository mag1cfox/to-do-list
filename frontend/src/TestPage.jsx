import React from 'react'

const TestPage = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1>测试页面</h1>
      <p>如果你能看到这个页面，说明前端路由正常工作。</p>
      <p>时间：{new Date().toLocaleString()}</p>
    </div>
  )
}

export default TestPage