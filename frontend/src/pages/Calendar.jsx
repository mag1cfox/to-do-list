import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  TimePicker,
  Select,
  ColorPicker,
  message,
  Popconfirm,
  Space,
  Badge,
  Row,
  Col,
  Statistic,
  Tag
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  FireOutlined,
  CheckCircleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../services/api'

const { Option } = Select
const { TextArea } = Input

// 时间块类型选项
const BLOCK_TYPES = [
  { value: 'RESEARCH', label: '科研', color: '#1890ff' },
  { value: 'GROWTH', label: '成长', color: '#52c41a' },
  { value: 'REST', label: '休息', color: '#f5222d' },
  { value: 'ENTERTAINMENT', label: '娱乐', color: '#fa8c16' },
  { value: 'REVIEW', label: '复盘', color: '#722ed1' }
]

function Calendar() {
  const [timeBlocks, setTimeBlocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedDate, setSelectedDate] = useState(dayjs())
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTimeBlock, setEditingTimeBlock] = useState(null)
  const [form] = Form.useForm()

  // 获取时间块列表
  const fetchTimeBlocks = async (date = null) => {
    setLoading(true)
    try {
      const params = date ? `?date=${date.format('YYYY-MM-DD')}` : ''
      const response = await api.get(`/time-blocks${params}`)
      setTimeBlocks(response.data)
    } catch (error) {
      message.error('获取时间块列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTimeBlocks(selectedDate)
  }, [selectedDate])

  // 创建/更新时间块
  const handleSubmit = async (values) => {
    try {
      // 转换时间格式
      const submitData = {
        date: selectedDate.format('YYYY-MM-DD'),
        start_time: dayjs(selectedDate.format('YYYY-MM-DD') + ' ' + values.start_time.format('HH:mm')).toISOString(),
        end_time: dayjs(selectedDate.format('YYYY-MM-DD') + ' ' + values.end_time.format('HH:mm')).toISOString(),
        block_type: values.block_type,
        color: values.color,
        description: values.description
      }

      if (editingTimeBlock) {
        await api.put(`/time-blocks/${editingTimeBlock.id}`, submitData)
        message.success('时间块更新成功')
      } else {
        await api.post('/time-blocks', submitData)
        message.success('时间块创建成功')
      }

      setModalVisible(false)
      setEditingTimeBlock(null)
      form.resetFields()
      fetchTimeBlocks(selectedDate)
    } catch (error) {
      message.error(error.response?.data?.error || '操作失败')
    }
  }

  // 删除时间块
  const handleDelete = async (timeBlockId) => {
    try {
      await api.delete(`/time-blocks/${timeBlockId}`)
      message.success('时间块删除成功')
      fetchTimeBlocks(selectedDate)
    } catch (error) {
      message.error(error.response?.data?.error || '删除失败')
    }
  }

  // 打开编辑模态框
  const openEditModal = (timeBlock = null) => {
    setEditingTimeBlock(timeBlock)
    if (timeBlock) {
      form.setFieldsValue({
        start_time: dayjs(timeBlock.start_time),
        end_time: dayjs(timeBlock.end_time),
        block_type: timeBlock.block_type,
        color: timeBlock.color,
        description: timeBlock.description
      })
    } else {
      form.setFieldsValue({
        start_time: dayjs().hour(9).minute(0),
        end_time: dayjs().hour(10).minute(0),
        block_type: 'RESEARCH',
        color: '#1890ff'
      })
    }
    setModalVisible(true)
  }

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false)
    setEditingTimeBlock(null)
    form.resetFields()
  }

  // 生成时间轴
  const generateTimeAxis = () => {
    const hours = []
    for (let i = 0; i < 24; i++) {
      hours.push(
        <div key={i} className="time-slot">
          <div className="time-label">
            {i.toString().padStart(2, '0')}:00
          </div>
          <div className="time-content">
            {getTimeBlocksForHour(i)}
          </div>
        </div>
      )
    }
    return hours
  }

  // 获取指定小时的时间块
  const getTimeBlocksForHour = (hour) => {
    return timeBlocks
      .filter(tb => {
        const startHour = dayjs(tb.start_time).hour()
        const endHour = dayjs(tb.end_time).hour()
        return hour >= startHour && hour < endHour
      })
      .map(timeBlock => {
        const blockType = BLOCK_TYPES.find(type => type.value === timeBlock.block_type)
        return (
          <Card
            key={timeBlock.id}
            size="small"
            style={{
              backgroundColor: timeBlock.color,
              marginBottom: '4px',
              border: 'none',
              cursor: 'pointer'
            }}
            bodyStyle={{ padding: '8px' }}
            onClick={() => openEditModal(timeBlock)}
          >
            <div style={{ color: 'white' }}>
              <div style={{ fontWeight: 'bold', fontSize: '12px' }}>
                {blockType?.label}
              </div>
              <div style={{ fontSize: '10px', opacity: 0.9 }}>
                {dayjs(timeBlock.start_time).format('HH:mm')} - {dayjs(timeBlock.end_time).format('HH:mm')}
              </div>
              {timeBlock.description && (
                <div style={{ fontSize: '10px', opacity: 0.8 }}>
                  {timeBlock.description}
                </div>
              )}
            </div>
          </Card>
        )
      })
  }

  // 日期选择器
  const dateSelector = (
    <div style={{ marginBottom: '24px', textAlign: 'center' }}>
      <Space>
        <Button
          onClick={() => setSelectedDate(selectedDate.subtract(1, 'day'))}
          disabled={selectedDate.isSame(dayjs(), 'day')}
        >
          上一天
        </Button>
        <Button
          onClick={() => setSelectedDate(dayjs())}
          type={selectedDate.isSame(dayjs(), 'day') ? 'primary' : 'default'}
        >
          今天
        </Button>
        <Button
          onClick={() => setSelectedDate(selectedDate.add(1, 'day'))}
        >
          下一天
        </Button>
      </Space>
      <div style={{ marginTop: '8px', fontSize: '18px', fontWeight: 'bold' }}>
        {selectedDate.format('YYYY年MM月DD日 dddd')}
      </div>
    </div>
  )

  // 统计信息
  const statistics = (
    <Row gutter={16} style={{ marginBottom: '24px' }}>
      <Col span={6}>
        <Card>
          <Statistic
            title="时间块数量"
            value={timeBlocks.length}
            prefix={<CalendarOutlined />}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="总计划时间"
            value={timeBlocks.reduce((sum, tb) => sum + tb.duration, 0)}
            suffix="分钟"
            prefix={<ClockCircleOutlined />}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="活跃时间块"
            value={timeBlocks.filter(tb => tb.is_active).length}
            prefix={<FireOutlined />}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="时间利用率"
            value={timeBlocks.length > 0 ?
              Math.round(timeBlocks.reduce((sum, tb) => sum + tb.duration, 0) / (24 * 60) * 100) : 0}
            suffix="%"
            prefix={<CheckCircleOutlined />}
          />
        </Card>
      </Col>
    </Row>
  )

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
            日历视图
          </h1>
          <p style={{ margin: '8px 0 0', color: '#666' }}>
            查看和管理您的每日时间安排
          </p>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openEditModal()}
            size="large"
          >
            创建时间块
          </Button>
        </Col>
      </Row>

      {dateSelector}
      {statistics}

      <Card title="时间轴" style={{ marginBottom: '24px' }}>
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          {generateTimeAxis()}
        </div>
      </Card>

      {/* 时间块类型图例 */}
      <Card title="时间块类型">
        <Row gutter={16}>
          {BLOCK_TYPES.map(type => (
            <Col span={4} key={type.value}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <div
                  style={{
                    width: '16px',
                    height: '16px',
                    backgroundColor: type.color,
                    marginRight: '8px',
                    borderRadius: '2px'
                  }}
                />
                <span>{type.label}</span>
              </div>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 创建/编辑时间块模态框 */}
      <Modal
        title={editingTimeBlock ? '编辑时间块' : '创建时间块'}
        open={modalVisible}
        onCancel={closeModal}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="开始时间"
            name="start_time"
            rules={[{ required: true, message: '请选择开始时间' }]}
          >
            <TimePicker format="HH:mm" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="结束时间"
            name="end_time"
            rules={[{ required: true, message: '请选择结束时间' }]}
          >
            <TimePicker format="HH:mm" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="时间块类型"
            name="block_type"
            rules={[{ required: true, message: '请选择时间块类型' }]}
          >
            <Select>
              {BLOCK_TYPES.map(type => (
                <Option key={type.value} value={type.value}>
                  {type.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="颜色"
            name="color"
            rules={[{ required: true, message: '请选择颜色' }]}
          >
            <ColorPicker
              showText
              format="hex"
              placeholder="选择颜色"
            />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea
              rows={3}
              placeholder="请输入时间块描述（可选）"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingTimeBlock ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <style jsx>{`
        .time-slot {
          display: flex;
          border-bottom: 1px solid #f0f0f0;
          min-height: 60px;
        }
        .time-slot:hover {
          background-color: #fafafa;
        }
        .time-label {
          width: 80px;
          padding: 8px;
          border-right: 1px solid #f0f0f0;
          font-size: 12px;
          color: #666;
          text-align: right;
        }
        .time-content {
          flex: 1;
          padding: 4px 8px;
        }
      `}</style>
    </div>
  )
}

export default Calendar