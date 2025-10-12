# 时间管理系统 - 实体关系分析

## 实体关系概览

### 1. User（用户）与其他实体的关系

**一对多关系：**
- **User → Task**：一个用户可以创建多个任务
- **User → Project**：一个用户可以拥有多个项目
- **User → Tag**：一个用户可以创建多个标签
- **User → TimeBlock**：一个用户可以设置多个时间块
- **User → PomodoroSession**：一个用户可以有多个番茄钟会话
- **User → TimeLog**：一个用户会产生多个时间日志
- **User → Recommendation**：一个用户会收到多个推荐
- **User → DailyStats**：一个用户有多个日统计记录

### 2. Task（任务）与其他实体的关系

**多对一关系：**
- **Task → User**：多个任务属于一个用户
- **Task → Project**：多个任务可以属于一个项目（可选）

**一对多关系：**
- **Task → PomodoroSession**：一个任务可以有多个番茄钟会话
- **Task → TimeLog**：一个任务对应多个时间日志

**多对多关系：**
- **Task ↔ Tag**：一个任务可以有多个标签，一个标签可以标记多个任务

### 3. Project（项目）与其他实体的关系

**多对一关系：**
- **Project → User**：多个项目属于一个用户

**一对多关系：**
- **Project → Task**：一个项目包含多个任务

### 4. PomodoroSession（番茄钟会话）与其他实体的关系

**多对一关系：**
- **PomodoroSession → User**：多个番茄钟会话属于一个用户
- **PomodoroSession → Task**：多个番茄钟会话对应一个任务

**一对一关系：**
- **PomodoroSession ↔ TimeLog**：一个番茄钟会话产生一个时间日志

### 5. TimeLog（时间日志）与其他实体的关系

**多对一关系：**
- **TimeLog → User**：多个时间日志属于一个用户
- **TimeLog → Task**：多个时间日志对应一个任务

**一对一关系：**
- **TimeLog ↔ PomodoroSession**：一个时间日志对应一个番茄钟会话

### 6. Recommendation（推荐）与其他实体的关系

**多对一关系：**
- **Recommendation → User**：多个推荐针对一个用户
- **Recommendation → Task**：多个推荐可以指向同一个任务

### 7. DailyStats（日统计）与其他实体的关系

**多对一关系：**
- **DailyStats → User**：多个日统计记录属于一个用户

## 核心业务关系详解

### 1. 任务规划关系链

User → (创建) → Task → (关联) → Project
→ (标记) → Tag
→ (安排) → TimeBlock

**说明：** 用户创建任务，任务可以归类到项目中，用标签进行灵活分类，并在时间块中进行具体安排。

### 2. 任务执行关系链
User → (启动) → PomodoroSession → (对应) → Task
↓ (生成)
TimeLog → (记录) → Task

**说明：** 用户通过番茄钟会话执行任务，每个会话都会生成对应的时间日志记录。

### 3. 智能推荐关系链
User ← (接收) ← Recommendation → (建议) → Task
↑
RecommendationService → (分析) → User的Task和历史数据

**说明：** 推荐系统分析用户的任务和历史数据，生成个性化的任务推荐。

### 4. 统计分析关系链
User → (生成) → DailyStats
↓ (通过)
TimeLog → (聚合) → DailyStats
**说明：** 系统基于用户的时间日志记录聚合生成每日统计数据。

## 关键约束关系

### 1. 时间不重叠约束
- **TimeLog** 实体之间在时间轴上不能重叠
- **TimeBlock** 实体之间在时间轴上不能重叠（除非明确允许）
- **PomodoroSession** 在同一用户的同一时间段内只能有一个活跃会话

### 2. 完整性约束
- 每个 **PomodoroSession** 必须关联一个 **Task**
- 每个 **TimeLog** 必须关联一个 **PomodoroSession**
- 每个 **Recommendation** 必须关联一个 **Task**

### 3. 状态流转约束
- **Task** 的状态流转：PENDING → IN_PROGRESS → COMPLETED/CANCELLED
- **PomodoroSession** 的状态流转：PLANNED → IN_PROGRESS → COMPLETED/INTERRUPTED

## 数据库关系映射建议
用户表 (users)
└── 项目表 (projects)
└── 标签表 (tags)
└── 时间块表 (time_blocks)
└── 日统计表 (daily_stats)
└── 任务表 (tasks)
├── 任务标签关联表 (task_tags)
└── 番茄钟会话表 (pomodoro_sessions)
└── 时间日志表 (time_logs)
└── 推荐表 (recommendations)

text

这个关系分析清晰地展示了系统中各个实体之间的连接方式，为数据库设计和业务逻辑实现提供了重要参考。