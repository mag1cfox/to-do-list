import React, { useEffect } from 'react';
import {
    Modal,
    Form,
    Select,
    TimePicker,
    ColorPicker,
    Switch,
    Button,
    Space,
    Row,
    Col,
    message
} from 'antd';
import dayjs from 'dayjs';
import { timeBlockService } from '../services/api';

const { Option } = Select;

const TimeBlockForm = ({
    visible,
    onCancel,
    onSubmit,
    editingBlock,
    selectedDate,
    blockTypeConfig,
    form
}) => {
    useEffect(() => {
        if (editingBlock) {
            form.setFieldsValue({
                block_type: editingBlock.block_type,
                start_time: dayjs(editingBlock.start_time),
                end_time: dayjs(editingBlock.end_time),
                color: editingBlock.color,
                is_recurring: editingBlock.is_recurring,
                recurrence_pattern: editingBlock.recurrence_pattern
            });
        } else {
            form.resetFields();
            form.setFieldsValue({
                block_type: 'GROWTH',
                is_recurring: false,
                color: blockTypeConfig['GROWTH'].color
            });
        }
    }, [editingBlock, form, blockTypeConfig]);

    const handleSubmit = async (values) => {
        try {
            const blockData = {
                date: selectedDate.format('YYYY-MM-DD'),
                start_time: selectedDate.format(`YYYY-MM-DD ${values.start_time.format('HH:mm')}`),
                end_time: selectedDate.format(`YYYY-MM-DD ${values.end_time.format('HH:mm')}`),
                block_type: values.block_type,
                color: values.color?.toHexString?.() || values.color?.toString() || blockTypeConfig[values.block_type]?.color || '#1890ff',
                is_recurring: values.is_recurring || false,
                recurrence_pattern: values.recurrence_pattern
            };

            await onSubmit(blockData);
        } catch (error) {
            console.error(`${editingBlock ? '更新' : '创建'}时间块失败:`, error);
            const errorMessage = error.error || `${editingBlock ? '更新' : '创建'}时间块失败`;
            message.error(errorMessage);
        }
    };

    return (
        <Modal
            title={editingBlock ? '编辑时间块' : '创建时间块'}
            open={visible}
            onCancel={onCancel}
            footer={null}
            width={500}
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
            >
                <Form.Item
                    label="时间块类型"
                    name="block_type"
                    rules={[{ required: true, message: '请选择时间块类型' }]}
                >
                    <Select placeholder="选择时间块类型">
                        {Object.entries(blockTypeConfig).map(([type, config]) => (
                            <Option key={type} value={type}>
                                {config.icon} {config.label}
                            </Option>
                        ))}
                    </Select>
                </Form.Item>

                <Row gutter={16}>
                    <Col span={12}>
                        <Form.Item
                            label="开始时间"
                            name="start_time"
                            rules={[{ required: true, message: '请选择开始时间' }]}
                        >
                            <TimePicker
                                format="HH:mm"
                                placeholder="选择开始时间"
                                style={{ width: '100%' }}
                            />
                        </Form.Item>
                    </Col>
                    <Col span={12}>
                        <Form.Item
                            label="结束时间"
                            name="end_time"
                            rules={[{ required: true, message: '请选择结束时间' }]}
                        >
                            <TimePicker
                                format="HH:mm"
                                placeholder="选择结束时间"
                                style={{ width: '100%' }}
                            />
                        </Form.Item>
                    </Col>
                </Row>

                <Form.Item
                    label="颜色"
                    name="color"
                    rules={[{ required: true, message: '请选择颜色' }]}
                >
                    <ColorPicker
                        showText
                        size="large"
                        style={{ width: '100%' }}
                    />
                </Form.Item>

                <Form.Item
                    label="重复"
                    name="is_recurring"
                    valuePropName="checked"
                >
                    <Switch />
                </Form.Item>

                <Form.Item
                    label="重复模式"
                    name="recurrence_pattern"
                >
                    <Select placeholder="选择重复模式" allowClear>
                        <Option value="daily">每天</Option>
                        <Option value="weekly">每周</Option>
                        <Option value="monthly">每月</Option>
                        <Option value="workdays">工作日</Option>
                    </Select>
                </Form.Item>

                <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                    <Space>
                        <Button onClick={onCancel}>
                            取消
                        </Button>
                        <Button type="primary" htmlType="submit">
                            {editingBlock ? '更新' : '创建'}
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Modal>
    );
};

export default TimeBlockForm;