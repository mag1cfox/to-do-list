import React, { useState, useEffect } from 'react';
import {
    Card,
    Form,
    Input,
    Button,
    Avatar,
    Upload,
    Row,
    Col,
    Statistic,
    Typography,
    Divider,
    Space,
    message,
    Descriptions,
    Tag,
    Spin,
    Empty,
    Tabs,
    DatePicker,
    Progress
} from 'antd';
import {
    UserOutlined,
    EditOutlined,
    SaveOutlined,
    UploadOutlined,
    CalendarOutlined,
    ClockCircleOutlined,
    CheckCircleOutlined,
    TrophyOutlined,
    MailOutlined,
    PhoneOutlined,
    GlobalOutlined,
    BookOutlined,
    LockOutlined,
    HistoryOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;

const Profile = () => {
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [editing, setEditing] = useState(false);
    const [activeTab, setActiveTab] = useState('info');
    const [userProfile, setUserProfile] = useState({});
    const [userStats, setUserStats] = useState({
        totalTasks: 0,
        completedTasks: 0,
        totalFocusTime: 0,
        joinDays: 0,
        completionRate: 0
    });
    const [form] = Form.useForm();

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
            if (response.status === 200) {
                const user = response.data.user;
                setUserProfile(user);
                form.setFieldsValue(user);

                // 计算用户统计数据
                calculateUserStats(user);
            }
        } catch (error) {
            console.error('获取用户资料失败:', error);
            message.error('获取用户资料失败');
        } finally {
            setLoading(false);
        }
    };

    // 计算用户统计数据
    const calculateUserStats = (user) => {
        // 计算加入天数
        const joinDate = new Date(user.created_at);
        const today = new Date();
        const joinDays = Math.floor((today - joinDate) / (1000 * 60 * 60 * 24));

        // 模拟数据（实际应该从API获取）
        const stats = {
            totalTasks: 0,
            completedTasks: 0,
            totalFocusTime: 0,
            joinDays: joinDays,
            completionRate: 0
        };

        setUserStats(stats);
    };

    // 获取任务统计数据
    const fetchTaskStats = async () => {
        try {
            const response = await api.get('/tasks/');
            if (response.status === 200) {
                const tasks = response.data.tasks || [];
                const totalTasks = tasks.length;
                const completedTasks = tasks.filter(task => task.status === 'COMPLETED').length;
                const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

                setUserStats(prev => ({
                    ...prev,
                    totalTasks,
                    completedTasks,
                    completionRate
                }));
            }
        } catch (error) {
            console.error('获取任务统计失败:', error);
        }
    };

    // 获取番茄钟统计数据
    const fetchPomodoroStats = async () => {
        try {
            const response = await api.get('/pomodoro-sessions/');
            if (response.status === 200) {
                const sessions = response.data.pomodoro_sessions || [];
                const completedSessions = sessions.filter(session => session.status === 'COMPLETED');
                const totalFocusTime = completedSessions.reduce((sum, session) => {
                    return sum + (session.actual_duration || session.planned_duration || 0);
                }, 0);

                setUserStats(prev => ({
                    ...prev,
                    totalFocusTime
                }));
            }
        } catch (error) {
            console.error('获取番茄钟统计失败:', error);
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
                setEditing(false);
            }
        } catch (error) {
            console.error('更新个人资料失败:', error);
            message.error('更新个人资料失败');
        } finally {
            setSaving(false);
        }
    };

    // 头像上传处理
    const handleAvatarUpload = (info) => {
        if (info.file.status === 'done') {
            message.success('头像上传成功');
            fetchUserProfile(); // 重新获取用户资料
        } else if (info.file.status === 'error') {
            message.error('头像上传失败');
        }
    };

    // 切换编辑模式
    const toggleEdit = () => {
        if (editing) {
            form.setFieldsValue(userProfile); // 重置表单
        }
        setEditing(!editing);
    };

    useEffect(() => {
        fetchUserProfile();
        fetchTaskStats();
        fetchPomodoroStats();
    }, []);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                    <Text>加载个人资料中...</Text>
                </div>
            </div>
        );
    }

    // 基本信息卡片
    const BasicInfoCard = () => (
        <Card
            title="基本信息"
            extra={
                <Button
                    type={editing ? "default" : "primary"}
                    icon={editing ? <SaveOutlined /> : <EditOutlined />}
                    onClick={editing ? () => form.submit() : toggleEdit}
                    loading={saving}
                >
                    {editing ? '保存' : '编辑'}
                </Button>
            }
        >
            <Row gutter={24}>
                <Col xs={24} md={8}>
                    <div style={{ textAlign: 'center', marginBottom: 16 }}>
                        <Avatar
                            size={120}
                            icon={<UserOutlined />}
                            src={userProfile.avatar}
                            style={{ marginBottom: 16 }}
                        />
                        <div>
                            <Upload
                                showUploadList={false}
                                beforeUpload={() => false}
                                onChange={handleAvatarUpload}
                                disabled={!editing}
                            >
                                <Button
                                    icon={<UploadOutlined />}
                                    disabled={!editing}
                                    size="small"
                                >
                                    更换头像
                                </Button>
                            </Upload>
                        </div>
                    </div>
                </Col>
                <Col xs={24} md={16}>
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={updateProfile}
                    >
                        <Row gutter={16}>
                            <Col xs={24} md={12}>
                                <Form.Item
                                    label="用户名"
                                    name="username"
                                    rules={[{ required: true, message: '请输入用户名' }]}
                                >
                                    <Input
                                        disabled={!editing}
                                        placeholder="请输入用户名"
                                    />
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
                                    <Input
                                        disabled={!editing}
                                        placeholder="请输入邮箱"
                                        prefix={<MailOutlined />}
                                    />
                                </Form.Item>
                            </Col>
                        </Row>
                        <Row gutter={16}>
                            <Col xs={24} md={12}>
                                <Form.Item
                                    label="手机号"
                                    name="phone"
                                >
                                    <Input
                                        disabled={!editing}
                                        placeholder="请输入手机号"
                                        prefix={<PhoneOutlined />}
                                    />
                                </Form.Item>
                            </Col>
                            <Col xs={24} md={12}>
                                <Form.Item
                                    label="所在地"
                                    name="location"
                                >
                                    <Input
                                        disabled={!editing}
                                        placeholder="请输入所在地"
                                        prefix={<GlobalOutlined />}
                                    />
                                </Form.Item>
                            </Col>
                        </Row>
                        <Form.Item
                            label="个人简介"
                            name="bio"
                        >
                            <TextArea
                                rows={4}
                                disabled={!editing}
                                placeholder="介绍一下自己..."
                                maxLength={500}
                                showCount
                            />
                        </Form.Item>
                    </Form>
                </Col>
            </Row>
        </Card>
    );

    // 统计数据卡片
    const StatsCard = () => (
        <Card title="我的统计">
            <Row gutter={[16, 16]}>
                <Col xs={12} sm={6}>
                    <Statistic
                        title="总任务数"
                        value={userStats.totalTasks}
                        prefix={<CalendarOutlined />}
                        valueStyle={{ color: '#1890ff' }}
                    />
                </Col>
                <Col xs={12} sm={6}>
                    <Statistic
                        title="已完成任务"
                        value={userStats.completedTasks}
                        prefix={<CheckCircleOutlined />}
                        valueStyle={{ color: '#52c41a' }}
                    />
                </Col>
                <Col xs={12} sm={6}>
                    <Statistic
                        title="专注时长"
                        value={userStats.totalFocusTime}
                        suffix="分钟"
                        prefix={<ClockCircleOutlined />}
                        valueStyle={{ color: '#fa8c16' }}
                    />
                </Col>
                <Col xs={12} sm={6}>
                    <Statistic
                        title="加入天数"
                        value={userStats.joinDays}
                        suffix="天"
                        prefix={<TrophyOutlined />}
                        valueStyle={{ color: '#722ed1' }}
                    />
                </Col>
            </Row>
            <Divider />
            <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text>任务完成率</Text>
                    <Text strong>{userStats.completionRate}%</Text>
                </div>
                <Progress
                    percent={userStats.completionRate}
                    strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                    }}
                />
            </div>
        </Card>
    );

    // 账户信息卡片
    const AccountInfoCard = () => (
        <Card title="账户信息">
            <Descriptions column={1}>
                <Descriptions.Item label="用户ID">
                    <Text code>{userProfile.id}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="用户名">
                    <Text strong>{userProfile.username}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="邮箱地址">
                    <Text>{userProfile.email}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="手机号">
                    <Text>{userProfile.phone || '未设置'}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="所在地">
                    <Text>{userProfile.location || '未设置'}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="注册时间">
                    <Text>
                        {userProfile.created_at ?
                            new Date(userProfile.created_at).toLocaleString() :
                            '未知'
                        }
                    </Text>
                </Descriptions.Item>
                <Descriptions.Item label="最后更新">
                    <Text>
                        {userProfile.updated_at ?
                            new Date(userProfile.updated_at).toLocaleString() :
                            '未知'
                        }
                    </Text>
                </Descriptions.Item>
            </Descriptions>
        </Card>
    );

    // 安全设置卡片
    const SecurityCard = () => (
        <Card title="安全设置" extra={<LockOutlined />}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <Text strong>登录密码</Text>
                        <br />
                        <Text type="secondary">上次修改：未知</Text>
                    </div>
                    <Button type="primary">修改密码</Button>
                </div>
                <Divider />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <Text strong>两步验证</Text>
                        <br />
                        <Text type="secondary">增强账户安全性</Text>
                    </div>
                    <Button>设置</Button>
                </div>
                <Divider />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <Text strong>登录历史</Text>
                        <br />
                        <Text type="secondary">查看最近登录记录</Text>
                    </div>
                    <Button icon={<HistoryOutlined />}>查看</Button>
                </div>
            </Space>
        </Card>
    );

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>
                <UserOutlined /> 个人资料管理
            </Title>

            <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                type="card"
                size="large"
            >
                <TabPane tab={<span><UserOutlined />基本信息</span>} key="info">
                    <BasicInfoCard />
                    <Divider />
                    <StatsCard />
                </TabPane>
                <TabPane tab={<span><BookOutlined />账户详情</span>} key="account">
                    <AccountInfoCard />
                </TabPane>
                <TabPane tab={<span><LockOutlined />安全设置</span>} key="security">
                    <SecurityCard />
                </TabPane>
            </Tabs>

            <Divider />

            <Card>
                <Row justify="center" align="middle">
                    <Col>
                        <Text type="secondary">
                            © 2025 时间管理系统 - 个人资料管理
                        </Text>
                    </Col>
                </Row>
            </Card>
        </div>
    );
};

export default Profile;