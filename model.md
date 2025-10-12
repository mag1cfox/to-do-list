# 时间管理系统 - 领域模型设计 v2.0

## 核心领域对象

### 1. User（用户）
```typescript
class User {
  id: string;
  username: string;
  email: string;
  preferences: UserPreferences;
  createdAt: Date;
  updatedAt: Date;

  // 关联
  timeBlockTemplates: TimeBlockTemplate[];
  taskCategories: TaskCategory[];

  // 方法
  updatePreferences(prefs: UserPreferences): void;
  getDailyStats(date: Date): DailyStats;
  getDefaultTimeBlockTemplate(): TimeBlockTemplate;
}
```
### 2. Task（任务）
```typescript
class Task {
  id: string;
  title: string;
  description?: string;
  userId: string;

  // 时间属性
  plannedStartTime: Date;
  estimatedPomodoros: number;
  taskType: TaskType; // 'RIGID' | 'FLEXIBLE'

  // 分类与排布
  categoryId: string; // 关联任务类别
  scheduledTimeBlockId?: string; // 排布到的时间块ID

  // 状态管理
  status: TaskStatus; // 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  priority: PriorityLevel; // 'HIGH' | 'MEDIUM' | 'LOW'

  // 关联
  projectId?: string;
  tags: Tag[];
  timeLogs: TimeLog[];

  // 方法
  calculateCompletionRate(): number;
  getActualTimeSpent(): number;
  canStart(): boolean;
  markComplete(): void;
  canMoveToTimeBlock(timeBlock: TimeBlock): boolean;
}
```
### 3. TaskCategory（任务类别）
```typescript
class TaskCategory {
  id: string;
  name: string;
  userId: string;
  color: string;
  icon?: string;
  description?: string;

  // 关联
  tasks: Task[];

  // 方法
  getTaskCount(): number;
  getTotalTimeSpent(): number;
}
```

### 4. Project（项目）
```typescript
class Project {
  id: string;
  name: string;
  description?: string;
  userId: string;
  color: string; // 项目颜色标识
  createdAt: Date;

  // 关联
  tasks: Task[];

  // 方法
  getTotalEstimatedTime(): number;
  getTotalActualTime(): number;
  getCompletionProgress(): number;
}
```
### 4. Tag（标签）
```typescript
class Tag {
  id: string;
  name: string;
  userId: string;
  color?: string;
  
  // 方法
  getUsageCount(): number;
}
```
### 5. TimeBlock（时间块）
```typescript
class TimeBlock {
  id: string;
  userId: string;
  date: Date; // 所属日期
  startTime: Date;
  endTime: Date;
  blockType: BlockType; // 'RESEARCH' | 'GROWTH' | 'REST' | 'ENTERTAINMENT' | 'REVIEW'
  color: string;
  isRecurring: boolean;
  recurrencePattern?: string;

  // 关联
  scheduledTasks: Task[];
  templateId?: string; // 如果来自模板

  // 方法
  isActive(): boolean;
  overlapsWith(other: TimeBlock): boolean;
  getDuration(): number;
  canAccommodateTask(task: Task): boolean;
}
```

### 6. TimeBlockTemplate（时间块模板）
```typescript
class TimeBlockTemplate {
  id: string;
  name: string;
  userId: string;
  description?: string;
  isDefault: boolean;

  // 模板配置
  timeBlocks: TimeBlock[];

  // 方法
  applyToDate(date: Date): TimeBlock[];
  clone(): TimeBlockTemplate;
}
```
### 7. PomodoroSession（番茄钟会话）
```typescript
class PomodoroSession {
  id: string;
  taskId: string;
  userId: string;
  
  // 时间追踪
  startTime: Date;
  endTime?: Date;
  plannedDuration: number; // 默认25分钟
  actualDuration?: number;
  
  // 状态
  status: SessionStatus; // 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'INTERRUPTED'
  sessionType: SessionType; // 'FOCUS' | 'BREAK'
  
  // 复盘数据
  completionSummary?: string;
  interruptionReason?: string;
  
  // 方法
  start(): void;
  complete(summary: string): void;
  interrupt(reason: string): void;
  getRemainingTime(): number;
}
```
### 8. TimeLog（时间日志）
```typescript
class TimeLog {
  id: string;
  userId: string;
  taskId: string;
  pomodoroSessionId: string;
  
  // 时间记录
  startTime: Date;
  endTime: Date;
  duration: number; // 分钟
  
  // 关联数据
  completionSummary: string;
  taskSnapshot: TaskSnapshot; // 记录任务创建时的状态
  
  // 方法
  isValid(): boolean; // 检查时间是否重叠
}
```
### 9. Recommendation（推荐）
```typescript
class Recommendation {
  id: string;
  userId: string;
  recommendedTaskId: string;
  recommendationTime: Date;
  priorityScore: number;
  reason: string; // 推荐原因
  
  // 状态
  status: RecommendationStatus; // 'ACTIVE' | 'ACCEPTED' | 'IGNORED'
  
  // 方法
  calculatePriorityScore(task: Task, currentTime: Date): number;
  accept(): void;
  ignore(): void;
}
```
### 10. DailyStats（每日统计）
```typescript
class DailyStats {
  id: string;
  userId: string;
  date: Date;

  // 统计数据
  totalPomodoros: number;
  completedTasks: number;
  totalFocusTime: number;
  plannedVsActual: number; // 计划与实际时间比例
  interruptionCount: number;

  // 分类时间统计
  timeByCategory: Map<string, number>; // 按任务类别统计时间
  estimatedVsActualByCategory: Map<string, { estimated: number, actual: number }>;

  // 效率指标
  focusScore: number;
  completionRate: number;
  accuracyRate: number; // 预估准确性

  // 关联
  dailyReview?: DailyReview;

  // 方法
  calculateFocusScore(): number;
  updateStats(): void;
  getTimeDistribution(): TimeDistribution;
  getCategoryCompletionRates(): Map<string, number>;
}
```

### 11. DailyReview（每日复盘）
```typescript
class DailyReview {
  id: string;
  userId: string;
  date: Date;

  // 复盘内容
  achievements: string[]; // 今日收获
  challenges: string[]; // 遇到的问题
  improvements: string[]; // 明日改进点
  overallSummary: string; // 总体总结

  // 复盘模板
  templateId?: string;
  completedAt: Date;

  // 关联
  dailyStatsId: string;

  // 方法
  isComplete(): boolean;
  getTemplate(): ReviewTemplate;
}
```

### 12. ReviewTemplate（复盘模板）
```typescript
class ReviewTemplate {
  id: string;
  name: string;
  userId: string;
  description?: string;

  // 模板结构
  sections: ReviewSection[];
  prompts: Map<string, string>; // 引导性问题

  // 方法
  applyToReview(review: DailyReview): void;
}
```

### 13. ReviewSection（复盘部分）
```typescript
class ReviewSection {
  id: string;
  templateId: string;
  title: string;
  description?: string;
  order: number;

  // 引导问题
  prompts: string[];

  // 方法
  getNextPrompt(currentIndex: number): string | null;
}
```
### 枚举类型定义
```typescript
enum TaskType {
  RIGID = 'RIGID',      // 刚性任务，不允许时间重叠
  FLEXIBLE = 'FLEXIBLE' // 柔性任务，允许时间重叠
}

enum TaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

enum PriorityLevel {
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW'
}

enum BlockType {
  RESEARCH = 'RESEARCH',     // 科研
  GROWTH = 'GROWTH',        // 成长
  REST = 'REST',            // 休息
  ENTERTAINMENT = 'ENTERTAINMENT', // 娱乐
  REVIEW = 'REVIEW'         // 复盘
}

enum SessionStatus {
  PLANNED = 'PLANNED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  INTERRUPTED = 'INTERRUPTED'
}

enum SessionType {
  FOCUS = 'FOCUS',
  BREAK = 'BREAK'
}

enum RecommendationStatus {
  ACTIVE = 'ACTIVE',
  ACCEPTED = 'ACCEPTED',
  IGNORED = 'IGNORED'
}

enum TimeBlockTemplateType {
  STANDARD_WORKDAY = 'STANDARD_WORKDAY',    // 标准工作日
  DEEP_WORK = 'DEEP_WORK',                  // 深度工作模式
  STUDY_DAY = 'STUDY_DAY',                  // 学习日
  CUSTOM = 'CUSTOM'                         // 自定义
}
```
### 值对象
```typescript
// 用户偏好设置
class UserPreferences {
  pomodoroDuration: number; // 默认25分钟
  breakDuration: number;    // 默认5分钟
  longBreakDuration: number; // 默认15分钟
  pomodorosUntilLongBreak: number; // 默认4个

  // 通知设置
  desktopNotifications: boolean;
  soundNotifications: boolean;

  // 主题
  theme: 'LIGHT' | 'DARK' | 'AUTO';
  timeBlockColors: Map<BlockType, string>;

  // 时间块设置
  defaultTimeBlockTemplate: string;
  autoApplyTimeBlocks: boolean;

  // 复盘设置
  defaultReviewTemplate: string;
  autoPromptReview: boolean;
}

// 任务快照（用于记录历史状态）
class TaskSnapshot {
  taskId: string;
  title: string;
  estimatedPomodoros: number;
  taskType: TaskType;
  categoryId: string;
  capturedAt: Date;
}

// 时间分布统计
class TimeDistribution {
  byCategory: Map<string, number>;
  byTimeBlock: Map<string, number>;
  totalTime: number;

  // 方法
  getPercentageByCategory(categoryId: string): number;
  getTopCategories(limit: number): Array<{ categoryId: string, time: number }>;
}
```
### 服务类
```typescript
// 推荐引擎服务
class RecommendationService {
  generateRecommendations(userId: string, currentTime: Date): Recommendation[];
  calculateTaskPriority(task: Task, currentTime: Date): number;
  getRigidTasksDue(userId: string, currentTime: Date): Task[];
  getFlexibleTasksAvailable(userId: string, currentTime: Date): Task[];
}

// 时间块规划服务
class TimeBlockService {
  createTimeBlocksFromTemplate(userId: string, date: Date, templateId: string): TimeBlock[];
  applyDefaultTimeBlocks(userId: string, date: Date): TimeBlock[];
  validateTimeBlockOverlap(timeBlocks: TimeBlock[]): ValidationResult;
  getTimeBlockSuggestions(userId: string, date: Date): TimeBlock[];
}

// 任务排布服务
class TaskSchedulingService {
  generateDailySchedule(userId: string, date: Date): ScheduledTask[];
  autoArrangeTasks(tasks: Task[], timeBlocks: TimeBlock[]): ArrangementResult;
  canScheduleTask(task: Task, timeBlock: TimeBlock): boolean;
  findOptimalTimeSlot(task: Task, timeBlocks: TimeBlock[]): TimeBlock | null;
  validateTaskArrangement(tasks: Task[]): ValidationResult;
}

// 番茄钟服务
class PomodoroService {
  startPomodoro(taskId: string, userId: string): PomodoroSession;
  completePomodoro(sessionId: string, summary: string): void;
  interruptPomodoro(sessionId: string, reason: string): void;
  getActiveSession(userId: string): PomodoroSession | null;
}

// 复盘服务
class ReviewService {
  generateDailyReview(userId: string, date: Date): DailyReview;
  applyReviewTemplate(review: DailyReview, templateId: string): void;
  getReviewStatistics(userId: string, startDate: Date, endDate: Date): ReviewStats;
  promptForReview(userId: string): boolean;
}

// 统计分析服务
class AnalyticsService {
  getUserStats(userId: string, startDate: Date, endDate: Date): UserStats;
  getTaskCompletionTrends(userId: string): CompletionTrend[];
  getFocusTimeDistribution(userId: string): TimeDistribution;
  generateProductivityReport(userId: string, period: string): ProductivityReport;
  getCategoryTimeAnalysis(userId: string, startDate: Date, endDate: Date): CategoryAnalysis[];
  getTimeBlockEfficiency(userId: string, date: Date): TimeBlockEfficiency[];
}
```
### 数据库关系设计

```
User (1) ──────── (n) Task
User (1) ──────── (n) TaskCategory
User (1) ──────── (n) Project
User (1) ──────── (n) TimeBlock
User (1) ──────── (n) TimeBlockTemplate
User (1) ──────── (n) TimeLog
User (1) ──────── (n) DailyStats
User (1) ──────── (n) DailyReview
User (1) ──────── (n) ReviewTemplate

Task (1) ──────── (n) TimeLog
Task (1) ──────── (n) PomodoroSession
Task (n) ──────── (1) TaskCategory
Task (n) ──────── (1) TimeBlock (scheduledTimeBlockId)

Project (1) ───── (n) Task
TimeBlockTemplate (1) ─ (n) TimeBlock
ReviewTemplate (1) ─ (n) ReviewSection
DailyStats (1) ─ (1) DailyReview

PomodoroSession (1) ─ (1) TimeLog
```

### 对象关系说明

**一对一关系：**
- PomodoroSession 与 TimeLog 是一对一关系
- DailyStats 与 DailyReview 是一对一关系

**一对多关系：**
- User 与 Task、TaskCategory、Project、TimeBlock、TimeBlockTemplate、TimeLog、DailyStats、DailyReview、ReviewTemplate 是一对多关系
- Project 与 Task 是一对多关系
- Task 与 TimeLog、PomodoroSession 是一对多关系
- TimeBlockTemplate 与 TimeBlock 是一对多关系
- ReviewTemplate 与 ReviewSection 是一对多关系

**多对一关系：**
- Task 与 TaskCategory 是多对一关系
- Task 与 TimeBlock 是多对一关系（通过 scheduledTimeBlockId）

**多对多关系：**
- Task 与 Tag 是多对多关系（通过中间表实现）

### 新增关系说明
1. **TaskCategory 分类体系**：Task 通过 categoryId 关联到 TaskCategory，实现任务分类管理
2. **TimeBlock 排布系统**：Task 通过 scheduledTimeBlockId 关联到 TimeBlock，实现任务在时间块中的排布
3. **TimeBlockTemplate 模板系统**：TimeBlock 通过 templateId 关联到 TimeBlockTemplate，支持时间块模板化
4. **Review 复盘系统**：DailyReview 与 DailyStats 一对一关联，ReviewTemplate 与 ReviewSection 一对多关联

这个领域模型设计 v2.0 完全支持新版需求文档的功能，包括时间块规划、任务分类、手动排布和完整复盘系统，每个对象都有明确的职责，服务类封装了核心业务逻辑，适合前后端分离的架构。