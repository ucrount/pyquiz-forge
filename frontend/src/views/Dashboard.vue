<template>
  <div class="page">
    <div class="page-header"><h2>概览</h2></div>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-blue">
          <div class="stat-label">章节数</div>
          <div class="stat-value">{{ stats.chapters }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-green">
          <div class="stat-label">知识点</div>
          <div class="stat-value">{{ stats.kps }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-orange">
          <div class="stat-label">题目总数</div>
          <div class="stat-value">{{ stats.exercises }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-purple">
          <div class="stat-label">激活 LLM</div>
          <div class="stat-value text" :title="activeLLMName || '未配置'">
            {{ activeLLMName || '未配置' }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>最近生成日志</span>
              <el-link type="primary" @click="$router.push('/logs')">查看全部 →</el-link>
            </div>
          </template>
          <el-table :data="recentLogs" v-loading="loadingLogs" empty-text="暂无生成记录" size="small">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column label="知识点" width="80">
              <template #default="{ row }">#{{ row.knowledge_point_id ?? '-' }}</template>
            </el-table-column>
            <el-table-column label="难度" width="80">
              <template #default="{ row }">
                <DifficultyTag v-if="row.difficulty" :value="row.difficulty" />
              </template>
            </el-table-column>
            <el-table-column label="题型" width="100">
              <template #default="{ row }">
                <QuestionTypeTag v-if="row.question_type" :value="row.question_type" />
              </template>
            </el-table-column>
            <el-table-column label="状态" width="70">
              <template #default="{ row }">
                <el-tag v-if="row.parsed_ok" type="success" size="small">成功</el-tag>
                <el-tag v-else type="danger" size="small">失败</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="耗时" width="80">
              <template #default="{ row }">{{ formatDuration(row.latency_ms) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span>快捷入口</span></template>
          <div class="actions">
            <el-button
              type="primary"
              size="large"
              @click="$router.push('/generate')"
            >
              <el-icon><MagicStick /></el-icon><span>生成题目</span>
            </el-button>
            <el-button size="large" @click="$router.push('/llm-configs')">
              <el-icon><Setting /></el-icon><span>大模型配置</span>
            </el-button>
            <el-button size="large" @click="$router.push('/exercises')">
              <el-icon><Notebook /></el-icon><span>题库管理</span>
            </el-button>
            <el-button size="large" @click="$router.push('/export')">
              <el-icon><Download /></el-icon><span>导出题库</span>
            </el-button>
          </div>
          <el-divider />
          <p class="hint">
            提示：第一次使用，请先在
            <el-link type="primary" @click="$router.push('/llm-configs')">大模型配置</el-link>
            添加并激活一条配置。
          </p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  MagicStick,
  Setting,
  Notebook,
  Download,
} from '@element-plus/icons-vue'
import {
  learningPathApi,
  exerciseApi,
  generationApi,
} from '@/api'
import { useLLMConfigStore } from '@/stores/llmConfig'
import { formatDuration } from '@/utils/format'
import type { GenerationLog } from '@/types/generation'
import DifficultyTag from '@/components/DifficultyTag.vue'
import QuestionTypeTag from '@/components/QuestionTypeTag.vue'

const llmStore = useLLMConfigStore()
const activeLLMName = computed(() => llmStore.active?.name ?? '')

const stats = reactive({
  chapters: 0,
  kps: 0,
  exercises: 0,
})

const recentLogs = ref<GenerationLog[]>([])
const loadingLogs = ref(false)

async function loadStats() {
  const [chapters, kps, exercises] = await Promise.all([
    learningPathApi.listChapters(),
    learningPathApi.listKPs(),
    exerciseApi.list({ page: 1, size: 1 }),
  ])
  stats.chapters = chapters.length
  stats.kps = kps.length
  stats.exercises = exercises.total
}

async function loadLogs() {
  loadingLogs.value = true
  try {
    recentLogs.value = await generationApi.listLogs(1, 5)
  } finally {
    loadingLogs.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadStats(), loadLogs(), llmStore.refresh(true)])
})
</script>

<style scoped>
.stat-row {
  margin-bottom: 0;
}

.stat-card {
  border-left: 4px solid #409eff;
}

.stat-blue {
  border-left-color: #409eff;
}

.stat-green {
  border-left-color: #67c23a;
}

.stat-orange {
  border-left-color: #e6a23c;
}

.stat-purple {
  border-left-color: #b88ce6;
}

.stat-label {
  color: #909399;
  font-size: 13px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-top: 4px;
}

.stat-value.text {
  font-size: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.actions .el-button {
  margin-left: 0 !important;
  width: 100%;
}

.hint {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}
</style>
