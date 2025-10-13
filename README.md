# 时间管理系统

基于智能推荐与自动化流程的个人时间管理系统

## 项目概述

本项目旨在开发一款智能化的个人时间管理系统。通过**智能推荐**与**自动化流程**，将任务规划、专注执行与复盘记录无缝衔接，形成一个高效的闭环，帮助用户提升专注力与时间利用率。

## 技术栈

### 后端
- **框架**: Flask (Python)
- **包管理**: uv
- **数据库**: SQLite + SQLAlchemy
- **认证**: Flask-JWT-Extended
- **序列化**: Marshmallow

### 前端
- **框架**: React (JavaScript)
- **包管理**: pnpm
- **构建工具**: Vite
- **UI组件**: Ant Design
- **状态管理**: Zustand

## 核心功能

- 智能任务池管理
- 时间块规划系统
- 任务分类体系
- 番茄钟专注系统
- 智能推荐引擎
- 每日复盘系统

## 项目结构

```
time-management-system/
├── backend/                 # Flask后端
│   ├── app/                # 应用主模块
│   ├── models/             # 数据模型
│   ├── routes/             # API路由
│   ├── services/           # 业务逻辑服务
│   ├── utils/              # 工具函数
│   └── config/             # 配置文件
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── hooks/          # 自定义Hooks
│   │   └── utils/          # 工具函数
│   └── public/             # 静态资源
└── docs/                   # 项目文档
```

## 快速开始

### 后端启动
```bash
cd backend
uv run python app.py
```

### 前端启动
```bash
cd frontend
pnpm dev
```

## 开发规范

请参考项目中的开发规范文档：
- `Rule.md` - 开发规范
- `product_requirements.md` - 产品需求文档
- `model.md` - 领域模型设计
- `relations.md` - 实体关系分析