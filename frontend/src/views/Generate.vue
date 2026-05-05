<template>
  <div class="page page--medium">
    <!-- Form -->
    <CyberCard accent="cyan" class="form-card">
      <template #header>
        <span class="cyber-card__title">▸ 生成参数</span>
      </template>
      <template #extra>
        <el-button size="small" @click="batchVisible = true">
          <el-icon><Operation /></el-icon><span>批量生成</span>
        </el-button>
      </template>
      <el-form :model="form" label-width="100px" label-position="right">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="知识点" required>
              <KnowledgePointPicker v-model="form.knowledge_point_id" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="LLM 配置">
              <el-select
                v-model="form.llm_config_id"
                clearable
                placeholder="使用当前激活的配置"
                style="width: 100%"
              >
                <el-option
                  v-for="cfg in llmStore.list"
                  :key="cfg.id"
                  :label="`${cfg.name} (${cfg.provider}/${cfg.model})${cfg.is_active ? ' ★' : ''}`"
                  :value="cfg.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="难度" required>
          <el-radio-group v-model="form.difficulty">
            <el-radio-button
              v-for="opt in DIFFICULTY_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="题型" required>
          <el-radio-group v-model="form.question_type">
            <el-radio-button
              v-for="opt in QUESTION_TYPE_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="!canGenerate"
            @click="onGenerate"
          >
            <el-icon><MagicStick /></el-icon>
            <span>{{ generating ? '生成中...' : '生成题目' }}</span>
          </el-button>
          <span v-if="!llmStore.active" class="warn-hint">
            ⚠ 请先在「大模型配置」页激活一条 LLM 配置
          </span>
        </el-form-item>
      </el-form>
    </CyberCard>

    <!-- Progress stepper（生成中） -->
    <CyberCard
      v-if="generating"
      accent="purple"
      class="progress-card pulse"
    >
      <template #header>
        <span class="cyber-card__title">⚡ 生成进行中</span>
      </template>
      <template #extra>
        <span class="elapsed mono">{{ elapsedText }}</span>
      </template>
      <el-steps :active="genStage" align-center finish-status="success">
        <el-step
          v-for="(s, i) in stages"
          :key="i"
          :title="s.title"
          :description="i === genStage ? s.hint : ''"
        />
      </el-steps>
    </CyberCard>

    <!-- Result -->
    <CyberCard
      v-if="result || error"
      accent="green"
      class="result-card"
    >
      <template #header>
        <span class="cyber-card__title">▸ 结果</span>
      </template>
      <template #extra>
        <el-button v-if="result" link type="primary" @click="onGenerate">
          <el-icon><RefreshRight /></el-icon><span>重新生成</span>
        </el-button>
      </template>

      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <p>{{ error }}</p>
          <el-link type="primary" @click="$router.push('/logs')">
            查看生成日志原始响应 →
          </el-link>
        </template>
      </el-alert>

      <ExerciseDetail v-if="result" :exercise="result" />
    </CyberCard>

    <!-- Batch drawer -->
    <el-drawer v-model="batchVisible" title="批量生成" size="600px">
      <el-form :model="batchForm" label-width="80px">
        <el-form-item label="知识点" required>
          <KnowledgePointPicker v-model="batchForm.knowledge_point_id" />
        </el-form-item>
        <el-divider>组合（可添加多组）</el-divider>
        <div
          v-for="(item, idx) in batchForm.items"
          :key="idx"
          class="batch-item"
        >
          <el-row :gutter="8" align="middle">
            <el-col :span="9">
              <el-select v-model="item.difficulty" size="small">
                <el-option
                  v-for="opt in DIFFICULTY_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-col>
            <el-col :span="9">
              <el-select v-model="item.question_type" size="small">
                <el-option
                  v-for="opt in QUESTION_TYPE_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-input-number
                v-model="item.count"
                :min="1"
                :max="10"
                size="small"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="2">
              <el-button
                size="small"
                type="danger"
                link
                :icon="Delete"
                @click="removeBatchItem(idx)"
              />
            </el-col>
          </el-row>
        </div>
        <el-button size="small" @click="addBatchItem">
          <el-icon><Plus /></el-icon><span>添加一组</span>
        </el-button>

        <el-divider />

        <p class="muted">
          预计生成 <strong class="neon-text-cyan">{{ batchTotal }}</strong> 道题。
          每题约 5-30 秒，串行生成，可以最小化此抽屉。
        </p>

        <el-button
          type="primary"
          :loading="batching && !job"
          :disabled="!canBatch || batching"
          @click="onBatchGenerate"
          style="width: 100%"
        >
          {{ batching ? '生成中（详见进度）' : '开始批量生成' }}
        </el-button>

        <!-- Live job progress -->
        <div v-if="job" class="job-block">
          <el-divider />
          <div class="job-header">
            <span class="cyber-card__title">▸ 实时进度</span>
            <span class="mono">
              {{ job.completed }} / {{ job.total }}
              <span v-if="job.status === 'done'" class="neon-text-cyan">[完成]</span>
            </span>
          </div>
          <el-progress
            :percentage="jobPercent"
            :status="job.status === 'done' ? 'success' : ''"
            :stroke-width="10"
          />
          <p v-if="etaText && job.status === 'running'" class="job-eta mono">
            <span class="muted">⏱ </span>{{ etaText }}
          </p>

          <!-- Streaming event log -->
          <div v-if="job.events && job.events.length" class="job-events" ref="eventsRef">
            <div
              v-for="(ev, i) in job.events"
              :key="i"
              class="job-event"
              :class="`evt-${ev.kind}`"
            >
              <span class="evt-time mono">{{ formatTs(ev.ts) }}</span>
              <span class="evt-icon">{{ evtIcon(ev.kind) }}</span>
              <span class="evt-label">{{ ev.label }}</span>
              <span v-if="ev.kind === 'success'" class="evt-meta mono">
                → #{{ ev.exercise_id }} · {{ formatLatency(ev.latency_ms) }}
              </span>
              <span v-else-if="ev.kind === 'fail'" class="evt-meta">
                → <span class="evt-err">{{ ev.error }}</span>
              </span>
              <span v-else-if="ev.kind === 'start'" class="evt-meta muted">
                生成中…
              </span>
            </div>
          </div>

          <div class="job-summary">
            <span class="job-stat ok">✓ {{ job.succeeded.length }} 成功</span>
            <span class="job-stat fail" v-if="job.failed.length">
              ✗ {{ job.failed.length }} 失败
            </span>
          </div>
          <el-button
            v-if="job.status === 'done'"
            link
            type="primary"
            @click="$router.push('/exercises')"
          >
            去题库查看 →
          </el-button>
        </div>
      </el-form>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  MagicStick,
  Operation,
  RefreshRight,
  Plus,
  Delete,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { generationApi } from '@/api'
import type { JobProgress } from '@/api/generation'
import { useLLMConfigStore } from '@/stores/llmConfig'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  type Difficulty,
  type QuestionType,
} from '@/types/common'
import type { Exercise } from '@/types/exercise'
import type { BatchItem } from '@/types/generation'
import KnowledgePointPicker from '@/components/KnowledgePointPicker.vue'
import ExerciseDetail from '@/components/ExerciseDetail.vue'
import CyberCard from '@/components/CyberCard.vue'

const route = useRoute()
const llmStore = useLLMConfigStore()

interface FormState {
  knowledge_point_id: number | null
  difficulty: Difficulty
  question_type: QuestionType
  llm_config_id: number | null
}

const form = reactive<FormState>({
  knowledge_point_id: null,
  difficulty: 'basic',
  question_type: 'program',
  llm_config_id: null,
})

const generating = ref(false)
const result = ref<Exercise | null>(null)
const error = ref('')

// === Stepper for single generation ===
const stages = [
  { title: '解析参数', hint: '准备 prompt' },
  { title: '调用大模型', hint: '请求中…(主要耗时)' },
  { title: '解析响应', hint: 'JSON 解析' },
  { title: '保存入库', hint: '完成' },
]
const genStage = ref(0)
const stageTimer = ref<number | null>(null)
const startTime = ref(0)
const elapsedMs = ref(0)
const tickTimer = ref<number | null>(null)

const elapsedText = computed(() => {
  const s = Math.floor(elapsedMs.value / 1000)
  return `${s}s`
})

function startStepper() {
  genStage.value = 0
  startTime.value = Date.now()
  elapsedMs.value = 0
  // 阶段 0 → 1（300ms 后切到 LLM 调用）
  stageTimer.value = window.setTimeout(() => {
    genStage.value = 1
  }, 300)
  // tick elapsed
  tickTimer.value = window.setInterval(() => {
    elapsedMs.value = Date.now() - startTime.value
  }, 250)
}

function advanceStepper(target: number) {
  genStage.value = target
}

function stopStepper() {
  if (stageTimer.value) clearTimeout(stageTimer.value)
  if (tickTimer.value) clearInterval(tickTimer.value)
  stageTimer.value = null
  tickTimer.value = null
}

const canGenerate = computed(
  () => !!form.knowledge_point_id && (!!llmStore.active || !!form.llm_config_id),
)

async function onGenerate() {
  if (!form.knowledge_point_id) return
  generating.value = true
  result.value = null
  error.value = ''
  startStepper()
  try {
    result.value = await generationApi.generate({
      knowledge_point_id: form.knowledge_point_id,
      difficulty: form.difficulty,
      question_type: form.question_type,
      llm_config_id: form.llm_config_id ?? undefined,
    })
    advanceStepper(2)
    await new Promise((r) => setTimeout(r, 200))
    advanceStepper(3)
    await new Promise((r) => setTimeout(r, 200))
    advanceStepper(4)
    ElMessage.success(`生成成功 (${(elapsedMs.value / 1000).toFixed(1)}s)`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '生成失败'
  } finally {
    setTimeout(() => {
      generating.value = false
      stopStepper()
    }, 500)
  }
}

// === Batch ===
interface BatchFormState {
  knowledge_point_id: number | null
  items: BatchItem[]
}

const batchVisible = ref(false)
const batching = ref(false)
const job = ref<JobProgress | null>(null)
const jobTimer = ref<number | null>(null)

const batchForm = reactive<BatchFormState>({
  knowledge_point_id: null,
  items: [{ difficulty: 'basic', question_type: 'program', count: 2 }],
})

const batchTotal = computed(() =>
  batchForm.items.reduce((sum, it) => sum + it.count, 0),
)

const canBatch = computed(
  () => !!batchForm.knowledge_point_id && batchTotal.value > 0,
)

const jobPercent = computed(() => {
  if (!job.value || job.value.total === 0) return 0
  return Math.min(100, Math.round((job.value.completed / job.value.total) * 100))
})

// ETA based on the average latency of completed (success+fail) events
const etaText = computed(() => {
  const j = job.value
  if (!j || j.status !== 'running' || !j.events?.length) return ''
  const finished = j.events.filter(
    (e) => (e.kind === 'success' || e.kind === 'fail') && e.latency_ms > 0,
  )
  if (finished.length === 0) return ''
  const avgMs =
    finished.reduce((sum, e) => sum + e.latency_ms, 0) / finished.length
  const remaining = j.total - j.completed
  if (remaining <= 0) return ''
  // Concurrency = 3, so wall-clock ETA ≈ remaining * avg / 3
  const etaMs = (remaining * avgMs) / 3
  const sec = Math.round(etaMs / 1000)
  const avgSec = (avgMs / 1000).toFixed(1)
  if (sec < 60) {
    return `平均 ${avgSec}s/题，预计剩余 ${sec}s`
  }
  const m = Math.floor(sec / 60)
  return `平均 ${avgSec}s/题，预计剩余 ${m}分${sec % 60}秒`
})

function formatTs(unixSec: number): string {
  const d = new Date(unixSec * 1000)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function formatLatency(ms: number): string {
  if (!ms) return ''
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function evtIcon(kind: 'start' | 'success' | 'fail'): string {
  return { start: '▶', success: '✓', fail: '✗' }[kind]
}

const eventsRef = ref<HTMLDivElement | null>(null)

// Auto-scroll the events panel to the bottom as new events stream in
watch(
  () => job.value?.events?.length ?? 0,
  () => {
    nextTick(() => {
      if (eventsRef.value) {
        eventsRef.value.scrollTop = eventsRef.value.scrollHeight
      }
    })
  },
)

function addBatchItem() {
  batchForm.items.push({ difficulty: 'basic', question_type: 'program', count: 1 })
}

function removeBatchItem(idx: number) {
  batchForm.items.splice(idx, 1)
}

async function pollJob(jobId: string) {
  try {
    const j = await generationApi.getJob(jobId)
    job.value = j
    if (j.status !== 'running') {
      stopJobPolling()
      batching.value = false
      if (j.failed.length === 0) {
        ElMessage.success(`成功生成 ${j.succeeded.length} 道题`)
      } else {
        ElMessage.warning(
          `成功 ${j.succeeded.length} / 失败 ${j.failed.length}`,
        )
      }
    }
  } catch (e) {
    // 任务可能被清理，停止轮询
    stopJobPolling()
    batching.value = false
  }
}

function startJobPolling(jobId: string) {
  jobTimer.value = window.setInterval(() => pollJob(jobId), 1500)
  // 立刻 poll 一次
  pollJob(jobId)
}

function stopJobPolling() {
  if (jobTimer.value) {
    clearInterval(jobTimer.value)
    jobTimer.value = null
  }
}

async function onBatchGenerate() {
  if (!batchForm.knowledge_point_id) return
  batching.value = true
  job.value = null
  try {
    const r = await generationApi.generateBatch({
      knowledge_point_id: batchForm.knowledge_point_id,
      items: batchForm.items,
    })
    startJobPolling(r.job_id)
  } catch {
    batching.value = false
  }
}

// Sync from query string ?kp=N
watch(
  () => route.query.kp,
  (kp) => {
    if (kp && !form.knowledge_point_id) {
      form.knowledge_point_id = Number(kp)
    }
  },
  { immediate: true },
)

onMounted(() => llmStore.refresh())
onUnmounted(() => {
  stopStepper()
  stopJobPolling()
})
</script>

<style scoped>
.form-card,
.progress-card,
.result-card {
  margin-bottom: 16px;
}

.warn-hint {
  margin-left: 12px;
  color: var(--neon-yellow);
  font-size: 13px;
  text-shadow: 0 0 8px rgba(255, 170, 0, 0.4);
}

.elapsed {
  color: var(--neon-cyan);
  font-size: 13px;
  font-weight: 600;
}

.batch-item {
  margin-bottom: 12px;
}

.muted {
  color: var(--el-text-color-secondary);
  margin: 8px 0 16px;
}

.job-block {
  margin-top: 8px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.job-current {
  margin-top: 8px;
  font-size: 13px;
}

.job-eta {
  margin: 8px 0 4px;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.job-events {
  margin-top: 10px;
  max-height: 240px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 8px 10px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 12px;
  line-height: 1.7;
}

.job-event {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 1px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.evt-time {
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
  width: 64px;
}

.evt-icon {
  flex-shrink: 0;
  width: 14px;
  text-align: center;
  font-weight: 800;
}

.evt-start .evt-icon {
  color: var(--neon-cyan);
}

.evt-success .evt-icon {
  color: var(--neon-green);
}

.evt-fail .evt-icon {
  color: var(--neon-pink);
}

.evt-label {
  color: var(--el-text-color-primary);
  flex-shrink: 0;
}

.evt-meta {
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
}

.evt-err {
  color: var(--neon-pink);
}

.muted {
  color: var(--el-text-color-secondary);
}

.job-summary {
  margin-top: 10px;
  display: flex;
  gap: 16px;
  font-size: 13px;
}

.job-stat.ok {
  color: var(--neon-green);
}

.job-stat.fail {
  color: var(--neon-pink);
}
</style>
