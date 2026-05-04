<template>
  <div class="page">
    <div class="page-header">
      <h2>SYSTEM OVERVIEW</h2>
      <span class="header-meta">
        <span class="meta-key">LANG</span>
        <span class="meta-value">{{ langLabel }}</span>
      </span>
    </div>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <CyberCard accent="cyan">
          <StatNumber
            :label="`${langLabel} 章节`"
            :value="stats.chapters"
            accent="cyan"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="green">
          <StatNumber
            :label="`${langLabel} 知识点`"
            :value="stats.kps"
            accent="green"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="purple">
          <StatNumber
            :label="`${langLabel} 题目`"
            :value="stats.exercises"
            accent="purple"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="pink">
          <div class="llm-cell">
            <div class="stat-label">LLM ACTIVE</div>
            <div class="llm-name" :title="activeLLMName || '未配置'">
              {{ activeLLMName || '— offline —' }}
            </div>
          </div>
        </CyberCard>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="14">
        <CyberCard title="RECENT GENERATION LOGS" accent="cyan">
          <template #extra>
            <el-link type="primary" :underline="false" @click="$router.push('/logs')">
              ALL LOGS →
            </el-link>
          </template>
          <el-table
            :data="recentLogs"
            v-loading="loadingLogs"
            empty-text="暂无生成记录"
            size="small"
          >
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
                <el-tag v-if="row.parsed_ok" type="success" size="small">OK</el-tag>
                <el-tag v-else type="danger" size="small">FAIL</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="耗时" width="80">
              <template #default="{ row }">{{ formatDuration(row.latency_ms) }}</template>
            </el-table-column>
          </el-table>
        </CyberCard>
      </el-col>

      <el-col :span="10">
        <CyberCard title="QUICK ACCESS" accent="purple">
          <div class="actions">
            <el-button
              type="primary"
              size="large"
              @click="$router.push('/generate')"
            >
              <el-icon><MagicStick /></el-icon><span>生成题目</span>
            </el-button>
            <el-button
              type="success"
              size="large"
              @click="$router.push('/practice')"
            >
              <el-icon><Aim /></el-icon><span>开始练习</span>
            </el-button>
            <el-button size="large" @click="$router.push('/exercises')">
              <el-icon><Notebook /></el-icon><span>题库</span>
            </el-button>
            <el-button size="large" @click="$router.push('/llm-configs')">
              <el-icon><Setting /></el-icon><span>LLM 配置</span>
            </el-button>
          </div>
          <el-divider />
          <p class="hint">
            <span class="hint-prefix">▸</span>
            首次使用：去
            <el-link type="primary" :underline="false" @click="$router.push('/llm-configs')">
              大模型配置
            </el-link>
            添加并激活一条 API Key。
          </p>
        </CyberCard>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import {
  MagicStick,
  Setting,
  Notebook,
  Aim,
} from '@element-plus/icons-vue'
import {
  learningPathApi,
  exerciseApi,
  generationApi,
} from '@/api'
import { useLLMConfigStore } from '@/stores/llmConfig'
import { useLanguageStore } from '@/stores/language'
import { LANGUAGE_LABEL, type Language } from '@/types/common'
import { formatDuration } from '@/utils/format'
import type { GenerationLog } from '@/types/generation'
import DifficultyTag from '@/components/DifficultyTag.vue'
import QuestionTypeTag from '@/components/QuestionTypeTag.vue'
import CyberCard from '@/components/CyberCard.vue'
import StatNumber from '@/components/StatNumber.vue'

const llmStore = useLLMConfigStore()
const langStore = useLanguageStore()
const activeLLMName = computed(() => llmStore.active?.name ?? '')
const langLabel = computed(
  () => LANGUAGE_LABEL[langStore.current as Language] ?? langStore.current,
)

const stats = reactive({
  chapters: 0,
  kps: 0,
  exercises: 0,
})

const recentLogs = ref<GenerationLog[]>([])
const loadingLogs = ref(false)

async function loadStats() {
  const [chapters, kps, exercises] = await Promise.all([
    learningPathApi.listChapters(langStore.current),
    learningPathApi.listKPs(undefined, langStore.current),
    exerciseApi.list({ language: langStore.current, page: 1, size: 1 }),
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

watch(() => langStore.current, () => {
  loadStats()
})

onMounted(async () => {
  await Promise.all([loadStats(), loadLogs(), llmStore.refresh(true)])
})
</script>

<style scoped>
.header-meta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 12px;
  letter-spacing: 0.5px;
}
.meta-key {
  color: var(--el-text-color-secondary);
}
.meta-value {
  color: var(--neon-cyan);
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
}

.stat-row {
  margin-bottom: 0;
}

.stat-label {
  font-size: 11px;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--el-text-color-secondary);
}

.llm-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.llm-name {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 18px;
  font-weight: 600;
  color: var(--neon-pink);
  text-shadow: 0 0 10px rgba(255, 77, 141, 0.4);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.actions .el-button {
  margin-left: 0 !important;
  width: 100%;
  height: 44px;
}

.hint {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}
.hint-prefix {
  color: var(--neon-cyan);
  margin-right: 6px;
}
</style>
