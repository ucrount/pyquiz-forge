<template>
  <el-container class="layout-root">
    <el-aside width="220px" class="layout-aside">
      <div class="brand">
        <span class="brand-logo">⚒️</span>
        <span class="brand-text">pyquiz-forge</span>
      </div>
      <el-menu
        :default-active="activeRoute"
        :router="true"
        class="layout-menu"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-title">{{ currentTitle }}</div>
        <div class="header-right">
          <el-select
            :model-value="langStore.current"
            size="small"
            style="width: 130px"
            @update:model-value="onLanguageChange"
          >
            <template #prefix>
              <span class="lang-prefix">语言</span>
            </template>
            <el-option
              v-for="opt in LANGUAGE_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <el-tag v-if="activeLLMName" size="small" effect="plain" type="success">
            激活: {{ activeLLMName }}
          </el-tag>
          <el-tag v-else size="small" effect="plain" type="warning">
            未配置 LLM
          </el-tag>
          <el-link
            type="primary"
            :underline="false"
            href="/docs"
            target="_blank"
          >
            Swagger ↗
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
} from '@element-plus/icons-vue'
import { useLLMConfigStore } from '@/stores/llmConfig'
import { useLanguageStore } from '@/stores/language'
import { LANGUAGE_OPTIONS, type Language } from '@/types/common'

const route = useRoute()

interface MenuItem {
  path: string
  title: string
  icon: any
}

const menuItems: MenuItem[] = [
  { path: '/', title: '概览', icon: DataLine },
  { path: '/learning-path', title: '学习路线', icon: Reading },
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
const langStore = useLanguageStore()
const activeLLMName = computed(() => llmStore.active?.name ?? '')

function onLanguageChange(v: Language) {
  langStore.setLanguage(v)
}

onMounted(() => {
  llmStore.refresh().catch(() => void 0)
})
</script>

<style scoped>
.layout-root {
  height: 100vh;
}

.layout-aside {
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.brand {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.brand-logo {
  font-size: 22px;
  margin-right: 10px;
}

.layout-menu {
  border-right: none;
  flex: 1;
  background: #001529;
}

.layout-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.75);
}

.layout-menu :deep(.el-menu-item:hover),
.layout-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff;
  color: #fff;
}

.layout-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.layout-main {
  background: #f5f7fa;
  padding: 0;
  overflow-y: auto;
}

.lang-prefix {
  color: #909399;
  font-size: 12px;
  margin-right: 4px;
}
</style>
