import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '概览', icon: 'DataLine' },
      },
      {
        path: 'learning-path',
        name: 'learning-path',
        component: () => import('@/views/LearningPath.vue'),
        meta: { title: '学习路线', icon: 'Reading' },
      },
      {
        path: 'generate',
        name: 'generate',
        component: () => import('@/views/Generate.vue'),
        meta: { title: '题目生成', icon: 'MagicStick' },
      },
      {
        path: 'exercises',
        name: 'exercises',
        component: () => import('@/views/Exercises.vue'),
        meta: { title: '题库管理', icon: 'Notebook' },
      },
      {
        path: 'practice',
        name: 'practice',
        component: () => import('@/views/Practice.vue'),
        meta: { title: '在线练习', icon: 'Aim' },
      },
      {
        path: 'llm-configs',
        name: 'llm-configs',
        component: () => import('@/views/LLMConfigs.vue'),
        meta: { title: '大模型配置', icon: 'Setting' },
      },
      {
        path: 'logs',
        name: 'logs',
        component: () => import('@/views/GenerationLogs.vue'),
        meta: { title: '生成日志', icon: 'Document' },
      },
      {
        path: 'export',
        name: 'export',
        component: () => import('@/views/Export.vue'),
        meta: { title: '导出题库', icon: 'Download' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  const title = to.meta?.title as string | undefined
  document.title = title ? `${title} · pyquiz-forge` : 'pyquiz-forge'
})

export default router
