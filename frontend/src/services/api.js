import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage')
    if (token) {
      try {
        const authData = JSON.parse(token)
        if (authData.state?.token) {
          config.headers.Authorization = `Bearer ${authData.state.token}`
        }
      } catch (error) {
        console.warn('Failed to parse auth token from localStorage')
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除认证信息
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error)
  }
)

// 认证相关API
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me')
}

// 用户相关API
export const userService = {
  getProfile: () => api.get('/users/profile'),
  getPreferences: () => api.get('/users/preferences')
}

// 任务相关API
export const taskService = {
  getTasks: (params) => api.get('/tasks', { params }),
  getTask: (id) => api.get(`/tasks/${id}`),
  createTask: (data) => api.post('/tasks', data),
  updateTask: (id, data) => api.put(`/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/tasks/${id}`)
}

// 任务类别相关API
export const taskCategoryService = {
  getCategories: () => api.get('/task-categories'),
  getCategory: (id) => api.get(`/task-categories/${id}`),
  createCategory: (data) => api.post('/task-categories', data),
  updateCategory: (id, data) => api.put(`/task-categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/task-categories/${id}`)
}

// 项目相关API
export const projectService = {
  getProjects: () => api.get('/projects'),
  getProject: (id) => api.get(`/projects/${id}`),
  createProject: (data) => api.post('/projects', data),
  updateProject: (id, data) => api.put(`/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/projects/${id}`)
}

// 标签相关API
export const tagService = {
  getTags: () => api.get('/tags'),
  getTag: (id) => api.get(`/tags/${id}`),
  createTag: (data) => api.post('/tags', data),
  updateTag: (id, data) => api.put(`/tags/${id}`, data),
  deleteTag: (id) => api.delete(`/tags/${id}`)
}

// 时间块相关API
export const timeBlockService = {
  getTimeBlocks: (params) => api.get('/time-blocks', { params }),
  getTimeBlock: (id) => api.get(`/time-blocks/${id}`),
  createTimeBlock: (data) => api.post('/time-blocks', data),
  updateTimeBlock: (id, data) => api.put(`/time-blocks/${id}`, data),
  deleteTimeBlock: (id) => api.delete(`/time-blocks/${id}`),
  scheduleTask: (timeBlockId, taskId) => api.post(`/time-blocks/${timeBlockId}/schedule-task`, { task_id: taskId }),
  unscheduleTask: (timeBlockId, taskId) => api.post(`/time-blocks/${timeBlockId}/unschedule-task`, { task_id: taskId }),
  checkConflicts: (date) => api.post('/time-blocks/check-conflicts', { date }),
  suggestTimeSlots: (taskId, date) => api.post('/time-blocks/suggest-time-slots', { task_id: taskId, date }),
  // 新增API
  getStatistics: (params) => api.get('/time-blocks/statistics', { params }),
  searchTimeBlocks: (params) => api.get('/time-blocks/search', { params }),
  batchCreateTimeBlocks: (data) => api.post('/time-blocks/batch', data),
  batchDeleteTimeBlocks: (data) => api.delete('/time-blocks/batch', { data })
}

// 时间块模板相关API
export const timeBlockTemplateService = {
  getTemplates: () => api.get('/time-block-templates'),
  getTemplate: (id) => api.get(`/time-block-templates/${id}`),
  createTemplate: (data) => api.post('/time-block-templates', data),
  updateTemplate: (id, data) => api.put(`/time-block-templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/time-block-templates/${id}`),
  applyTemplate: (id, data) => api.post(`/time-block-templates/${id}/apply`, data),
  cloneTemplate: (id) => api.post(`/time-block-templates/${id}/clone`)
}

// 番茄钟相关API
export const pomodoroService = {
  getSessions: (params) => api.get('/pomodoro-sessions', { params }),
  getSession: (id) => api.get(`/pomodoro-sessions/${id}`),
  createSession: (data) => api.post('/pomodoro-sessions', data),
  startSession: (id) => api.post(`/pomodoro-sessions/${id}/start`),
  completeSession: (id, summary) => api.post(`/pomodoro-sessions/${id}/complete`, { completion_summary: summary }),
  interruptSession: (id, reason) => api.post(`/pomodoro-sessions/${id}/interrupt`, { interruption_reason: reason }),
  getActiveSession: () => api.get('/pomodoro-sessions/active'),
  deleteSession: (id) => api.delete(`/pomodoro-sessions/${id}`)
}

// 推荐引擎相关API
export const recommendationService = {
  getCurrentRecommendation: (params) => api.get('/recommendations/current', { params }),
  getTaskRecommendations: (params) => api.get('/recommendations/tasks', { params }),
  getScheduleSuggestions: (params) => api.get('/recommendations/schedule', { params }),
  getRecommendationSummary: () => api.get('/recommendations/summary')
}

// 健康检查
export const healthService = {
  check: () => api.get('/health')
}

export default api