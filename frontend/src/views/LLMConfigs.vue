<template>
  <div class="page">
    <div class="page-header">
      <h2>大模型配置</h2>
      <el-button type="primary" @click="onCreate">
        <el-icon><Plus /></el-icon><span>新建</span>
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table
        :data="store.list"
        v-loading="store.loading"
        empty-text="暂无配置，点击右上角新建"
        stripe
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="160">
          <template #default="{ row }">
            <span>{{ row.name }}</span>
            <el-tag v-if="row.is_active" type="success" size="small" style="margin-left:8px">激活中</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="provider" label="Provider" width="110" />
        <el-table-column prop="model" label="模型" min-width="160" />
        <el-table-column label="API Key" min-width="200">
          <template #default="{ row }">
            <code class="key">{{ row.api_key }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp" width="80" />
        <el-table-column prop="max_tokens" label="MaxTokens" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.is_active ? 'success' : 'default'"
              :disabled="row.is_active"
              @click="onActivate(row)"
            >激活</el-button>
            <el-button size="small" @click="onTest(row)" :loading="testingId === row.id">
              测试
            </el-button>
            <el-button size="small" @click="onEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <LLMConfigDialog
      v-model="dialogVisible"
      :editing="editingConfig"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { llmConfigApi } from '@/api'
import { useLLMConfigStore } from '@/stores/llmConfig'
import type { LLMConfig } from '@/types/llm_config'
import LLMConfigDialog from '@/components/LLMConfigDialog.vue'

const store = useLLMConfigStore()
const dialogVisible = ref(false)
const editingConfig = ref<LLMConfig | null>(null)
const testingId = ref<number | null>(null)

onMounted(() => store.refresh(true))

function onCreate() {
  editingConfig.value = null
  dialogVisible.value = true
}

function onEdit(row: LLMConfig) {
  editingConfig.value = row
  dialogVisible.value = true
}

async function onSaved() {
  await store.refresh(true)
}

async function onActivate(row: LLMConfig) {
  await llmConfigApi.activate(row.id)
  ElMessage.success(`已激活 ${row.name}`)
  await store.refresh(true)
}

async function onTest(row: LLMConfig) {
  testingId.value = row.id
  try {
    const result = await llmConfigApi.test(row.id)
    if (result.ok) {
      ElMessage.success(`✓ 连通成功 (${result.latency_ms} ms)`)
    } else {
      ElMessage.error(`✗ ${result.message}`)
    }
  } finally {
    testingId.value = null
  }
}

async function onDelete(row: LLMConfig) {
  await ElMessageBox.confirm(
    `确定要删除配置 "${row.name}" 吗？`,
    '删除确认',
    { type: 'warning' },
  )
  await llmConfigApi.remove(row.id)
  ElMessage.success('已删除')
  await store.refresh(true)
}
</script>

<style scoped>
.key {
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
}
</style>
