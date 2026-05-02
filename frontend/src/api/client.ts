import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

const client: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 120_000,
  headers: { 'Content-Type': 'application/json' },
})

// Centralized error handling — extract FastAPI's `detail` and toast it.
client.interceptors.response.use(
  (resp) => resp,
  (error: AxiosError<any>) => {
    let msg = error.message || '请求失败'
    if (error.response?.data) {
      const data = error.response.data as any
      if (typeof data.detail === 'string') {
        msg = data.detail
      } else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
        msg = data.detail[0].msg
      }
    }
    if (!error.config?.headers?.['X-Silent']) {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

export default client
