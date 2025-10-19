import React from 'react'

const DebugPage = () => {
  React.useEffect(() => {
    console.log('DebugPage组件已加载')
    console.log('React版本:', React.version)
    console.log('当前时间:', new Date().toLocaleString())
  }, [])

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', color: 'black' }}>
      <h1 style={{ color: 'blue' }}>调试页面</h1>
      <p>如果你能看到这个页面，说明React正常工作。</p>
      <p>当前时间: {new Date().toLocaleString()}</p>
      <div style={{
        padding: '10px',
        backgroundColor: '#f0f0f0',
        border: '1px solid #ccc',
        margin: '10px 0'
      }}>
        <p>检查项目:</p>
        <ul>
          <li>✅ React组件渲染正常</li>
          <li>✅ 样式应用正常</li>
          <li>✅ JavaScript执行正常</li>
        </ul>
      </div>
    </div>
  )
}

export default DebugPage