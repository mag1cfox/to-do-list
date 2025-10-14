import React, { useState, useEffect } from 'react';
import {
    Card,
    Form,
    Input,
    Button,
    Switch,
    Select,
    InputNumber,
    ColorPicker,
    Tabs,
    Space,
    message,
    Divider,
    Typography,
    Row,
    Col,
    Avatar,
    Upload,
    Modal
} from 'antd';
import {
    UserOutlined,
    SettingOutlined,
    BellOutlined,
    ThemeOutlined,
    ClockCircleOutlined,
    FileTextOutlined,
    UploadOutlined,
    SaveOutlined,
    ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { TextArea } = Input;

const Settings = () => {
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [activeTab, setActiveTab] = useState('profile');
    const [userProfile, setUserProfile] = useState({});
    const [preferences, setPreferences] = useState({
        // 番茄钟设置
        pomodoroDuration: 25,
        breakDuration: 5,
        longBreakDuration: 15,
        pomodorosUntilLongBreak: 4,
        autoStartBreaks: false,
        autoStartPomodoros: false,

        // 通知设置
        desktopNotifications: true,
        soundNotifications: true,
        notificationSound: 'default',
        flashTitle: true,
        showNotifications: true,

        // 主题设置
        theme: 'LIGHT',
        primaryColor: '#1890ff',
        fontSize: 'medium',
        compactMode: false,
        sidebarCollapsed: false,

        // 时间块设置
        defaultTimeBlockTemplate: '',
        autoApplyTimeBlocks: false,
        timeBlockColors: {
            RESEARCH: '#1890ff',
            GROWTH: '#52c41a',
            REST: '#fa8c16',
            ENTERTAINMENT: '#eb2f96',
            REVIEW: '#722ed1'
        },

        // 复盘设置
        defaultReviewTemplate: '',
        autoPromptReview: true,
        reviewTime: '22:00',
        reviewReminderEnabled: true,
        autoSaveReviews: true,

        // 通用设置
        language: 'zh-CN',
        timezone: 'Asia/Shanghai',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: 'HH:mm',
        weekStartsOn: 1
    });

    // 获取认证token
    const getToken = () => {
        return localStorage.getItem('access_token');
    };

    // API配置
    const api = axios.create({
        baseURL: 'http://localhost:5000/api',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        }
    });

    // 获取用户资料
    const fetchUserProfile = async () => {
        try {
            setLoading(true);
            const response = await api.get('/users/profile');
            setUserProfile(response.data.user || {});
        } catch (error) {
            console.error('获取用户资料失败:', error);
            message.error('获取用户资料失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取用户偏好设置
    const fetchUserPreferences = async () => {
        try {
            setLoading(true);
            const response = await api.get('/users/preferences');
            const userPrefs = response.data.preferences || {};
            // 合并默认设置和用户设置
            setPreferences({ ...preferences, ...userPrefs });
        } catch (error) {
            console.error('获取用户偏好设置失败:', error);
            message.error('获取用户偏好设置失败');
        } finally {
            setLoading(false);
        }
    };

    // 更新用户资料
    const updateProfile = async (values) => {
        try {
            setSaving(true);
            const response = await api.put('/users/profile', values);
            if (response.status === 200) {
                message.success('个人资料更新成功');
                setUserProfile({ ...userProfile, ...values });
            }
        } catch (error) {
            console.error('更新个人资料失败:', error);
            message.error('更新个人资料失败');
        } finally {
            setSaving(false);
        }
    };

    // 更新偏好设置
    const updatePreferences = async (newPreferences) => {
        try {
            setSaving(true);
            const response = await api.put('/users/preferences', { preferences: newPreferences });
            if (response.status === 200) {
                message.success('偏好设置保存成功');
                setPreferences(newPreferences);
            }
        } catch (error) {
            console.error('保存偏好设置失败:', error);
            message.error('保存偏好设置失败');
        } finally {
            setSaving(false);
        }
    };

    // 重置为默认设置
    const resetToDefaults = () => {
        Modal.confirm({
            title: '重置设置',
            content: '确定要重置所有设置为默认值吗？此操作不可撤销。',
            okText: '确定',
            cancelText: '取消',
            onOk: () => {
                const defaultPreferences = {
                    pomodoroDuration: 25,
                    breakDuration: 5,
                    longBreakDuration: 15,
                    pomodorosUntilLongBreak: 4,
                    autoStartBreaks: false,
                    autoStartPomodoros: false,
                    desktopNotifications: true,
                    soundNotifications: true,
                    notificationSound: 'default',
                    flashTitle: true,
                    showNotifications: true,
                    theme: 'LIGHT',
                    primaryColor: '#1890ff',
                    fontSize: 'medium',
                    compactMode: false,
                    sidebarCollapsed: false,
                    defaultTimeBlockTemplate: '',
                    autoApplyTimeBlocks: false,
                    timeBlockColors: {
                        RESEARCH: '#1890ff',
                        GROWTH: '#52c41a',
                        REST: '#fa8c16',
                        ENTERTAINMENT: '#eb2f96',
                        REVIEW: '#722ed1'
                    },
                    defaultReviewTemplate: '',
                    autoPromptReview: true,
                    reviewTime: '22:00',
                    reviewReminderEnabled: true,
                    autoSaveReviews: true,
                    language: 'zh-CN',
                    timezone: 'Asia/Shanghai',
                    dateFormat: 'YYYY-MM-DD',
                    timeFormat: 'HH:mm',
                    weekStartsOn: 1
                };
                updatePreferences(defaultPreferences);
            }
        });
    };

    useEffect(() => {
        fetchUserProfile();
        fetchUserPreferences();
    }, []);

    // 个人资料表单
    const ProfileForm = () => (
        <Card title="个人资料" extra={<UserOutlined />}>
            <Form
                layout="vertical"
                initialValues={userProfile}
                onFinish={updateProfile}
            >
                <Row gutter={16}>
                    <Col xs={24} md={8}>
                        <Form.Item label="头像">
                            <div style={{ textAlign: 'center' }}>
                                <Avatar
                                    size={100}
                                    icon={<UserOutlined />}
                                    src={userProfile.avatar}
                                    style={{ marginBottom: 16 }}
                                />
                                <Upload
                                    showUploadList={false}
                                    beforeUpload={() => false}
                                    onChange={(info) => {
                                        if (info.file.status === 'done') {
                                            message.success('头像上传成功');
                                        }
                                    }}
                                >
                                    <Button icon={<UploadOutlined />}>更换头像</Button>
                                </Upload>
                            </div>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={16}>
                        <Row gutter={16}>
                            <Col xs={24} md={12}>
                                <Form.Item
                                    label="用户名"
                                    name="username"
                                    rules={[{ required: true, message: '请输入用户名' }]}
                                >
                                    <Input placeholder="请输入用户名" />
                                </Form.Item>
                            </Col>
                            <Col xs={24} md={12}>
                                <Form.Item
                                    label="邮箱"
                                    name="email"
                                    rules={[
                                        { required: true, message: '请输入邮箱' },
                                        { type: 'email', message: '请输入有效的邮箱地址' }
                                    ]}
                                >
                                    <Input placeholder="请输入邮箱" />
                                </Form.Item>
                            </Col>
                        </Row>
                        <Form.Item
                            label="个人简介"
                            name="bio"
                        >
                            <TextArea
                                rows={3}
                                placeholder="介绍一下自己..."
                                maxLength={200}
                                showCount
                            />
                        </Form.Item>
                    </Col>
                </Row>
                <Form.Item>
                    <Space>
                        <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                            保存资料
                        </Button>
                        <Button onClick={fetchUserProfile} icon={<ReloadOutlined />}>
                            重置
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Card>
    );

    // 番茄钟设置表单
    const PomodoroSettings = () => (
        <Card title="番茄钟设置" extra={<ClockCircleOutlined />}>
            <Form
                layout="vertical"
                initialValues={preferences}
                onFinish={(values) => updatePreferences({ ...preferences, ...values })}
            >
                <Row gutter={16}>
                    <Col xs={24} md={12}>
                        <Form.Item label="专注时长（分钟）" name="pomodoroDuration">
                            <InputNumber min={1} max={60} style={{ width: '100%' }} />
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="短休息时长（分钟）" name="breakDuration">
                            <InputNumber min={1} max={30} style={{ width: '100%' }} />
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="长休息时长（分钟）" name="longBreakDuration">
                            <InputNumber min={1} max={60} style={{ width: '100%' }} />
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="长休息间隔数" name="pomodorosUntilLongBreak">
                            <InputNumber min={2} max={10} style={{ width: '100%' }} />
                        </Form.Item>
                    </Col>
                </Row>
                <Row gutter={16}>
                    <Col xs={24} md={12}>
                        <Form.Item name="autoStartPomodoros" valuePropName="checked">
                            <Switch /> 自动开始下一个番茄钟
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item name="autoStartBreaks" valuePropName="checked">
                            <Switch /> 自动开始休息
                        </Form.Item>
                    </Col>
                </Row>
                <Form.Item>
                    <Space>
                        <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                            保存番茄钟设置
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Card>
    );

    // 通知设置表单
    const NotificationSettings = () => (
        <Card title="通知设置" extra={<BellOutlined />}>
            <Form
                layout="vertical"
                initialValues={preferences}
                onFinish={(values) => updatePreferences({ ...preferences, ...values })}
            >
                <Row gutter={16}>
                    <Col xs={24} md={12}>
                        <Form.Item name="desktopNotifications" valuePropName="checked">
                            <Switch /> 桌面通知
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item name="soundNotifications" valuePropName="checked">
                            <Switch /> 声音提醒
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item name="flashTitle" valuePropName="checked">
                            <Switch /> 标题闪烁提醒
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item name="showNotifications" valuePropName="checked">
                            <Switch /> 显示通知内容
                        </Form.Item>
                    </Col>
                </Row>
                <Form.Item label="通知声音" name="notificationSound">
                    <Select style={{ width: '100%' }}>
                        <Option value="default">默认声音</Option>
                        <Option value="bell">铃声</Option>
                        <Option value="chime">钟声</Option>
                        <Option value="digital">数字声</Option>
                        <Option value="none">静音</Option>
                    </Select>
                </Form.Item>
                <Form.Item>
                    <Space>
                        <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                            保存通知设置
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Card>
    );

    // 主题设置表单
    const ThemeSettings = () => (
        <Card title="主题设置" extra={<ThemeOutlined />}>
            <Form
                layout="vertical"
                initialValues={preferences}
                onFinish={(values) => updatePreferences({ ...preferences, ...values })}
            >
                <Row gutter={16}>
                    <Col xs={24} md={12}>
                        <Form.Item label="界面主题" name="theme">
                            <Select style={{ width: '100%' }}>
                                <Option value="LIGHT">浅色主题</Option>
                                <Option value="DARK">深色主题</Option>
                                <Option value="AUTO">跟随系统</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="主色调" name="primaryColor">
                            <ColorPicker showText />
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="字体大小" name="fontSize">
                            <Select style={{ width: '100%' }}>
                                <Option value="small">小</Option>
                                <Option value="medium">中</Option>
                                <Option value="large">大</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item name="compactMode" valuePropName="checked">
                            <Switch /> 紧凑模式
                        </Form.Item>
                    </Col>
                </Row>
                <Form.Item>
                    <Space>
                        <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                            保存主题设置
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Card>
    );

    // 高级设置表单
    const AdvancedSettings = () => (
        <Card title="高级设置" extra={<SettingOutlined />}>
            <Form
                layout="vertical"
                initialValues={preferences}
                onFinish={(values) => updatePreferences({ ...preferences, ...values })}
            >
                <Row gutter={16}>
                    <Col xs={24} md={12}>
                        <Form.Item label="语言" name="language">
                            <Select style={{ width: '100%' }}>
                                <Option value="zh-CN">简体中文</Option>
                                <Option value="en-US">English</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="时区" name="timezone">
                            <Select style={{ width: '100%' }}>
                                <Option value="Asia/Shanghai">北京时间 (GMT+8)</Option>
                                <Option value="America/New_York">纽约时间 (GMT-5)</Option>
                                <Option value="Europe/London">伦敦时间 (GMT+0)</Option>
                                <Option value="Asia/Tokyo">东京时间 (GMT+9)</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="日期格式" name="dateFormat">
                            <Select style={{ width: '100%' }}>
                                <Option value="YYYY-MM-DD">YYYY-MM-DD</Option>
                                <Option value="MM/DD/YYYY">MM/DD/YYYY</Option>
                                <Option value="DD/MM/YYYY">DD/MM/YYYY</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                        <Form.Item label="时间格式" name="timeFormat">
                            <Select style={{ width: '100%' }}>
                                <Option value="HH:mm">24小时制</Option>
                                <Option value="hh:mm A">12小时制</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                </Row>
                <Form.Item>
                    <Space>
                        <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                            保存高级设置
                        </Button>
                        <Button onClick={resetToDefaults} icon={<ReloadOutlined />}>
                            重置为默认值
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Card>
    );

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '50px' }}>
                <SettingOutlined spin style={{ fontSize: 32 }} />
                <div style={{ marginTop: 16 }}>
                    <Text>加载设置中...</Text>
                </div>
            </div>
        );
    }

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>
                <SettingOutlined /> 系统设置
            </Title>

            <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                type="card"
                size="large"
            >
                <TabPane tab={<span><UserOutlined />个人资料</span>} key="profile">
                    <ProfileForm />
                </TabPane>
                <TabPane tab={<span><ClockCircleOutlined />番茄钟</span>} key="pomodoro">
                    <PomodoroSettings />
                </TabPane>
                <TabPane tab={<span><BellOutlined />通知</span>} key="notifications">
                    <NotificationSettings />
                </TabPane>
                <TabPane tab={<span><ThemeOutlined />主题</span>} key="theme">
                    <ThemeSettings />
                </TabPane>
                <TabPane tab={<span><SettingOutlined />高级</span>} key="advanced">
                    <AdvancedSettings />
                </TabPane>
            </Tabs>

            <Divider />

            <Card>
                <Row justify="center" align="middle">
                    <Col>
                        <Text type="secondary">
                            © 2025 时间管理系统 - 版本 1.0.0
                        </Text>
                    </Col>
                </Row>
            </Card>
        </div>
    );
};

export default Settings;