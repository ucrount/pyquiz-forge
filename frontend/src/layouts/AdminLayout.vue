<template>
  <el-container class="layout-root">
    <el-aside width="220px" class="layout-aside">
      <div class="brand">
        <span class="brand-logo">⬡</span>
        <span class="brand-text">PYQUIZ <span class="brand-accent">FORGE</span></span>
      </div>

      <el-menu
        :default-active="activeRoute"
        :router="true"
        class="layout-menu"
      >
        <el-menu-item
          v-for="item in mainMenu"
          :key="item.path"
          :index="item.path"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>

      <!-- 左下角：设置按钮 + 系统状态 -->
      <div class="aside-footer">
        <router-link to="/settings" class="settings-btn" :class="{ 'is-active': activeRoute === '/settings' }">
          <el-icon><Tools /></el-icon>
          <span>设置</span>
        </router-link>
        <div class="status-block" title="System Online">
          <span class="status-dot pulse"></span>
        </div>
      </div>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-title">{{ currentTitle }}</div>
        <div class="header-right">
          <el-tag v-if="activeLLMName" size="small" effect="plain" type="success">
            ▸ {{ activeLLMName }}
          </el-tag>
          <el-tag v-else size="small" effect="plain" type="warning">
            ▸ 未配置 LLM
          </el-tag>
          <el-link
            type="primary"
            :underline="false"
            href="/docs"
            target="_blank"
          >
            API ↗
          </el-link>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataLine,
  Reading,
  MagicStick,
  Notebook,
  Setting,
  Document,
  Download,
  Aim,
  StarFilled,
  Tools,
} from '@element-plus/icons-vue'
import { useLLMConfigStore } from '@/stores/llmConfig'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()

interface MenuItem {
  path: string
  title: string
  icon: any
}

const mainMenu: MenuItem[] = [
  { path: '/', title: '概览', icon: DataLine },
  { path: '/learning-path', title: '学习路线', icon: Reading },
  { path: '/practice', title: '在线练习', icon: Aim },
  { path: '/review', title: '复习清单', icon: StarFilled },
  { path: '/generate', title: '题目生成', icon: MagicStick },
  { path: '/exercises', title: '题库管理', icon: Notebook },
  { path: '/llm-configs', title: '大模型配置', icon: Setting },
  { path: '/logs', title: '生成日志', icon: Document },
  { path: '/export', title: '导出题库', icon: Download },
]

const activeRoute = computed(() => route.path)
const currentTitle = computed(
  () => (route.meta?.title as string | undefined) ?? '',
)

const llmStore = useLLMConfigStore()
useThemeStore() // ensures theme is applied to <html data-theme="..."> on mount

const activeLLMName = computed(() => llmStore.active?.name ?? '')

onMounted(() => {
  llmStore.refresh().catch(() => void 0)
})
</script>

<style scoped>
.layout-root {
  height: 100vh;
  position: relative;
  z-index: 1;
}

.layout-aside {
  background: linear-gradient(
    180deg,
    rgba(8, 12, 24, 0.95) 0%,
    rgba(15, 22, 40, 0.95) 100%
  );
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid var(--el-border-color);
  color: var(--el-text-color-primary);
  display: flex;
  flex-direction: column;
  position: relative;
}

.layout-aside::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(
    180deg,
    transparent 0%,
    var(--neon-cyan) 50%,
    transparent 100%
  );
  opacity: 0.4;
}

.brand {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 1.5px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  text-transform: uppercase;
}

.brand-logo {
  font-size: 24px;
  margin-right: 10px;
  color: var(--neon-cyan);
  text-shadow: 0 0 12px var(--neon-cyan);
}

.brand-text {
  background: linear-gradient(
    90deg,
    var(--el-text-color-primary) 0%,
    var(--neon-cyan) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-accent {
  color: var(--neon-cyan);
  -webkit-text-fill-color: var(--neon-cyan);
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
}

.layout-menu {
  border-right: none;
  flex: 1;
  background: transparent;
  padding-top: 8px;
  overflow-y: auto;
}

.layout-menu :deep(.el-menu-item) {
  color: var(--el-text-color-regular);
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 6px;
  font-size: 13px;
  letter-spacing: 0.3px;
  transition: all 0.2s ease;
}

.layout-menu :deep(.el-menu-item:hover) {
  background: rgba(0, 212, 255, 0.08) !important;
  color: var(--neon-cyan) !important;
}

.layout-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(
    90deg,
    rgba(0, 212, 255, 0.15) 0%,
    rgba(0, 212, 255, 0.05) 100%
  ) !important;
  color: var(--neon-cyan) !important;
  border-left: 2px solid var(--neon-cyan);
  box-shadow: inset 0 0 12px rgba(0, 212, 255, 0.1);
}

.layout-menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

/* === 左下角：设置按钮 + 系统状态 === */
.aside-footer {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.settings-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  background: rgba(15, 22, 40, 0.5);
  border: 1px solid var(--el-border-color);
  color: var(--el-text-color-regular);
  font-size: 13px;
  letter-spacing: 0.3px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.settings-btn .el-icon {
  font-size: 16px;
}

.settings-btn:hover {
  background: rgba(0, 212, 255, 0.08);
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.25);
}

.settings-btn.is-active {
  background: linear-gradient(
    90deg,
    rgba(0, 212, 255, 0.18) 0%,
    rgba(0, 212, 255, 0.06) 100%
  );
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
  box-shadow: inset 0 0 12px rgba(0, 212, 255, 0.15);
}

.status-block {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--neon-green);
  box-shadow: 0 0 8px var(--neon-green);
}

.layout-header {
  background: rgba(15, 22, 40, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  position: relative;
}

.layout-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--neon-cyan) 50%,
    transparent 100%
  );
  opacity: 0.3;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.6px;
  color: var(--el-text-color-primary);
  text-transform: uppercase;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.layout-main {
  background: transparent;
  padding: 0;
  overflow-y: auto;
}
</style>
