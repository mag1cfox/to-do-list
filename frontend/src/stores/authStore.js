import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authService } from '../services/api'

const useAuthStore = create(
  persist(
    (set, get) => ({
      // 状态
      isAuthenticated: false,
      user: null,
      token: null,

      // 操作
      login: async (credentials) => {
        try {
          const response = await authService.login(credentials)
          console.log('AuthStore - 登录响应:', response)
          set({
            isAuthenticated: true,
            user: response.user,
            token: response.access_token
          })
          console.log('AuthStore - 状态已更新:', {
            isAuthenticated: true,
            user: response.user,
            token: response.access_token ? '已设置' : '未设置'
          })
          return response
        } catch (error) {
          console.error('AuthStore - 登录失败:', error)
          throw error
        }
      },

      register: async (userData) => {
        try {
          const response = await authService.register(userData)
          return response
        } catch (error) {
          throw error
        }
      },

      logout: () => {
        set({
          isAuthenticated: false,
          user: null,
          token: null
        })
      },

      checkAuth: async () => {
        const { token } = get()
        if (!token) {
          set({ isAuthenticated: false, user: null })
          return false
        }

        try {
          const response = await authService.getCurrentUser()
          set({
            isAuthenticated: true,
            user: response.user
          })
          return true
        } catch (error) {
          set({ isAuthenticated: false, user: null, token: null })
          return false
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token
      })
    }
  )
)

export { useAuthStore }