# 时间管理系统 - 实体关系分析

## 实体关系概览

### 1. User（用户）与其他实体的关系

**一对多关系：**
- **User → Task**：一个用户可以创建多个任务
- **User → Project**：一个用户可以拥有多个项目
- **User → Tag**：一个用户可以创建多个标签
- **User → TaskCategory**：一个用户可以创建多个任务类别
- **User → TimeBlock**：一个用户可以设置多个时间块
- **User → TimeBlockTemplate**：一个用户可以创建多个时间块模板
- **User → PomodoroSession**：一个用户可以有多个番茄钟会话
- **User → TimeLog**：一个用户会产生多个时间日志
- **User → Recommendation**：一个用户会收到多个推荐
- **User → DailyStats**：一个用户有多个日统计记录
- **User → DailyReview**：一个用户有多个每日复盘记录
- **User → ReviewTemplate**：一个用户可以创建多个复盘模板

### 2. Task（任务）与其他实体的关系

**多对一关系：**
- **Task → User**：多个任务属于一个用户
- **Task → Project**：多个任务可以属于一个项目（可选）
- **Task → TaskCategory**：多个任务属于一个任务类别
- **Task → TimeBlock**：多个任务可以排布到同一个时间块（通过 scheduledTimeBlockId）

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

### 4. TaskCategory（任务类别）与其他实体的关系

**多对一关系：**
- **TaskCategory → User**：多个任务类别属于一个用户

**一对多关系：**
- **TaskCategory → Task**：一个任务类别包含多个任务

### 5. TimeBlock（时间块）与其他实体的关系

**多对一关系：**
- **TimeBlock → User**：多个时间块属于一个用户
- **TimeBlock → TimeBlockTemplate**：多个时间块可以来自同一个模板（可选）

**一对多关系：**
- **TimeBlock → Task**：一个时间块可以排布多个任务

### 6. TimeBlockTemplate（时间块模板）与其他实体的关系

**多对一关系：**
- **TimeBlockTemplate → User**：多个时间块模板属于一个用户

**一对多关系：**
- **TimeBlockTemplate → TimeBlock**：一个时间块模板包含多个时间块

### 7. PomodoroSession（番茄钟会话）与其他实体的关系

**多对一关系：**
- **PomodoroSession → User**：多个番茄钟会话属于一个用户
- **PomodoroSession → Task**：多个番茄钟会话对应一个任务

**一对一关系：**
- **PomodoroSession ↔ TimeLog**：一个番茄钟会话产生一个时间日志

### 8. TimeLog（时间日志）与其他实体的关系

**多对一关系：**
- **TimeLog → User**：多个时间日志属于一个用户
- **TimeLog → Task**：多个时间日志对应一个任务

**一对一关系：**
- **TimeLog ↔ PomodoroSession**：一个时间日志对应一个番茄钟会话

### 9. Recommendation（推荐）与其他实体的关系

**多对一关系：**
- **Recommendation → User**：多个推荐针对一个用户
- **Recommendation → Task**：多个推荐可以指向同一个任务

### 10. DailyStats（日统计）与其他实体的关系

**多对一关系：**
- **DailyStats → User**：多个日统计记录属于一个用户

**一对一关系：**
- **DailyStats ↔ DailyReview**：一个日统计记录对应一个每日复盘记录

### 11. DailyReview（每日复盘）与其他实体的关系

**多对一关系：**
- **DailyReview → User**：多个每日复盘记录属于一个用户
- **DailyReview → ReviewTemplate**：多个每日复盘记录可以使用同一个复盘模板（可选）

**一对一关系：**
- **DailyReview ↔ DailyStats**：一个每日复盘记录对应一个日统计记录

### 12. ReviewTemplate（复盘模板）与其他实体的关系

**多对一关系：**
- **ReviewTemplate → User**：多个复盘模板属于一个用户

**一对多关系：**
- **ReviewTemplate → ReviewSection**：一个复盘模板包含多个复盘部分
- **ReviewTemplate → DailyReview**：一个复盘模板可以被多个每日复盘记录使用

### 13. ReviewSection（复盘部分）与其他实体的关系

**多对一关系：**
- **ReviewSection → ReviewTemplate**：多个复盘部分属于一个复盘模板

## 核心业务关系详解

### 1. 时间块规划关系链

User → (创建) → TimeBlockTemplate → (应用) → TimeBlock
→ (关联) → TaskCategory

**说明：** 用户创建时间块模板，模板应用到具体日期生成时间块，时间块与任务类别关联。

### 2. 任务规划关系链

User → (创建) → Task → (分类) → TaskCategory
→ (关联) → Project
→ (标记) → Tag
→ (排布) → TimeBlock

**说明：** 用户创建任务，任务按类别分类，可以关联到项目，用标签标记，并排布到时间块中。

### 3. 任务执行关系链
User → (启动) → PomodoroSession → (对应) → Task
↓ (生成)
TimeLog → (记录) → Task

**说明：** 用户通过番茄钟会话执行任务，每个会话都会生成对应的时间日志记录。

### 4. 智能推荐关系链
User ← (接收) ← Recommendation → (建议) → Task
↑
RecommendationService → (分析) → User的Task、TimeBlock和历史数据

**说明：** 推荐系统分析用户的任务、时间块安排和历史数据，生成个性化的任务推荐。

### 5. 统计分析关系链
User → (生成) → DailyStats
↓ (通过)
TimeLog → (聚合) → DailyStats
**说明：** 系统基于用户的时间日志记录聚合生成每日统计数据。

### 6. 复盘系统关系链
User → (创建) → ReviewTemplate → (包含) → ReviewSection
→ (生成) → DailyReview → (关联) → DailyStats

**说明：** 用户创建复盘模板，模板包含多个复盘部分，系统生成每日复盘记录，复盘记录关联到日统计数据。

## 关键约束关系

### 1. 时间不重叠约束
- **TimeLog** 实体之间在时间轴上不能重叠
- **TimeBlock** 实体之间在时间轴上不能重叠（除非明确允许）
- **PomodoroSession** 在同一用户的同一时间段内只能有一个活跃会话
- **Task** 中的刚性任务在时间轴上不能重叠

### 2. 完整性约束
- 每个 **PomodoroSession** 必须关联一个 **Task**
- 每个 **TimeLog** 必须关联一个 **PomodoroSession**
- 每个 **Recommendation** 必须关联一个 **Task**
- 每个 **Task** 必须关联一个 **TaskCategory**
- 每个 **DailyReview** 必须关联一个 **DailyStats**
- 每个 **ReviewSection** 必须关联一个 **ReviewTemplate**

### 3. 状态流转约束
- **Task** 的状态流转：PENDING → IN_PROGRESS → COMPLETED/CANCELLED
- **PomodoroSession** 的状态流转：PLANNED → IN_PROGRESS → COMPLETED/INTERRUPTED

### 4. 排布约束
- **Task** 只能排布到与其类别匹配的 **TimeBlock** 中
- **Task** 的排布必须在其 **plannedStartTime** 之后
- **Task** 的排布不能超出其所属 **TimeBlock** 的时间范围

## 数据库关系映射建议

```
用户表 (users)
├── 项目表 (projects)
├── 标签表 (tags)
├── 任务类别表 (task_categories)
├── 时间块模板表 (time_block_templates)
├── 复盘模板表 (review_templates)
├── 日统计表 (daily_stats)
├── 时间块表 (time_blocks)
│   └── 时间块模板外键 (template_id)
├── 任务表 (tasks)
│   ├── 项目外键 (project_id)
│   ├── 任务类别外键 (category_id)
│   └── 时间块外键 (scheduled_time_block_id)
├── 任务标签关联表 (task_tags)
├── 番茄钟会话表 (pomodoro_sessions)
│   └── 任务外键 (task_id)
├── 时间日志表 (time_logs)
│   ├── 任务外键 (task_id)
│   └── 番茄钟会话外键 (pomodoro_session_id)
├── 推荐表 (recommendations)
│   └── 任务外键 (task_id)
├── 每日复盘表 (daily_reviews)
│   ├── 日统计外键 (daily_stats_id)
│   └── 复盘模板外键 (template_id)
└── 复盘部分表 (review_sections)
    └── 复盘模板外键 (template_id)
```

### 数据库关系说明

**主外键关系：**
- 所有子表都包含 `user_id` 外键引用 `users.id`
- `tasks` 表包含多个外键：`project_id`, `category_id`, `scheduled_time_block_id`
- `time_blocks` 表包含 `template_id` 外键引用 `time_block_templates.id`
- `daily_reviews` 表包含 `daily_stats_id` 外键引用 `daily_stats.id` 和 `template_id` 外键引用 `review_templates.id`
- `review_sections` 表包含 `template_id` 外键引用 `review_templates.id`
- `pomodoro_sessions` 表包含 `task_id` 外键引用 `tasks.id`
- `time_logs` 表包含 `task_id` 和 `pomodoro_session_id` 外键
- `recommendations` 表包含 `task_id` 外键

**多对多关系：**
- `task_tags` 表作为中间表，包含 `task_id` 和 `tag_id` 字段

这个关系分析清晰地展示了系统中各个实体之间的连接方式，为数据库设计和业务逻辑实现提供了重要参考。