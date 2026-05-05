<template>
  <div class="page">
    <div class="page-header">
      <h2>生成日志</h2>
      <el-button @click="load">
        <el-icon><Refresh /></el-icon><span>刷新</span>
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="logs" v-loading="loading" stripe empty-text="暂无日志">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="知识点" width="100">
          <template #default="{ row }">#{{ row.knowledge_point_id ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="难度" width="90">
          <template #default="{ row }">
            <DifficultyTag v-if="row.difficulty" :value="row.difficulty" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="题型" width="110">
          <template #default="{ row }">
            <QuestionTypeTag v-if="row.question_type" :value="row.question_type" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.parsed_ok" type="success" size="small">成功</el-tag>
            <el-tag v-else type="danger" size="small">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误信息" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="muted">{{ row.error_message || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">{{ formatDuration(row.latency_ms) }}</template>
        </el-table-column>
        <el-table-column label="Tokens" width="140">
          <template #default="{ row }">
            <span class="muted">
              ↑{{ row.prompt_tokens }} / ↓{{ row.completion_tokens }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="openDetail(row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="page"
        :page-size="size"
        :total="total"
        layout="prev, pager, next"
        @current-change="load"
        background
      />
    </el-card>

    <el-drawer
      v-model="detailVisible"
      size="60%"
      title="日志详情"
      :destroy-on-close="true"
    >
      <div v-if="detail" class="log-detail">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="知识点">
            #{{ detail.knowledge_point_id ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="难度">{{ detail.difficulty }}</el-descriptions-item>
          <el-descriptions-item label="题型">{{ detail.question_type }}</el-descriptions-item>
          <el-descriptions-item label="解析结果">
            <el-tag v-if="detail.parsed_ok" type="success" size="small">成功</el-tag>
            <el-tag v-else type="danger" size="small">失败</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ formatDuration(detail.latency_ms) }}
          </el-descriptions-item>
          <el-descriptions-item label="Tokens" :span="2">
            prompt: {{ detail.prompt_tokens }} / completion: {{ detail.completion_tokens }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" :span="2">
            <span class="error-text">{{ detail.error_message || '（无）' }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <h4>原始响应</h4>
        <CodeBlock
          :code="detail.raw_response || '(empty)'"
          language="json"
          :copyable="true"
        />

        <h4>Prompt</h4>
        <el-collapse>
          <el-collapse-item title="展开查看完整 Prompt" name="prompt">
            <CodeBlock :code="detail.prompt || '(empty)'" language="json" :copyable="true" />
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { generationApi } from '@/api'
import { formatDuration } from '@/utils/format'
import type {
  GenerationLog,
  GenerationLogDetail,
} from '@/types/generation'
import DifficultyTag from '@/components/DifficultyTag.vue'
import QuestionTypeTag from '@/components/QuestionTypeTag.vue'
import CodeBlock from '@/components/CodeBlock.vue'

const logs = ref<GenerationLog[]>([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)

const detailVisible = ref(false)
const detail = ref<GenerationLogDetail | null>(null)

async function load() {
  loading.value = true
  try {
    // Backend returns array directly (no total). Approximate by length until paged endpoint is added.
    const r = await generationApi.listLogs(page.value, size.value)
    logs.value = r
    if (page.value === 1 && r.length < size.value) {
      total.value = r.length
    } else if (r.length === size.value) {
      total.value = page.value * size.value + 1 // hint for "next" availability
    } else {
      total.value = (page.value - 1) * size.value + r.length
    }
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = null
  detailVisible.value = true
  detail.value = await generationApi.getLog(id)
}

onMounted(load)
</script>

<style scoped>
.muted {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
  display: flex;
}

.log-detail {
  padding: 0 8px;
}

.log-detail h4 {
  margin: 16px 0 8px;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.error-text {
  color: #f56c6c;
  white-space: pre-wrap;
}
</style>
