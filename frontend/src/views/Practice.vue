<template>
  <div class="page practice-page">
    <!-- Stage A: Setup -->
    <template v-if="stage === 'setup'">
      <div class="page-header">
        <h2>PRACTICE TERMINAL</h2>
      </div>

      <CyberCard accent="cyan" class="setup-card">
        <template #header>
          <span class="cyber-card__title">▸ 配置练习参数</span>
        </template>

        <el-form :model="cfg" label-position="top">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="练习范围">
                <el-radio-group v-model="cfg.scope" size="default">
                  <el-radio-button value="lang">整个语言</el-radio-button>
                  <el-radio-button value="chapter">某个章节</el-radio-button>
                  <el-radio-button value="kp">某个知识点</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="题目数量">
                <el-input-number
                  v-model="cfg.size"
                  :min="1"
                  :max="50"
                  :step="5"
                  controls-position="right"
                />
                <span class="muted ml">默认 10，最多 50</span>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item v-if="cfg.scope === 'chapter'" label="选择章节">
            <el-select
              v-model="cfg.chapter_id"
              placeholder="请选择章节"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="c in chapters"
                :key="c.id"
                :label="`${c.code} · ${c.title}`"
                :value="c.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item v-if="cfg.scope === 'kp'" label="选择知识点">
            <KnowledgePointPicker v-model="cfg.knowledge_point_id" />
          </el-form-item>

          <el-form-item label="难度（多选）">
            <el-checkbox-group v-model="cfg.difficulties">
              <el-checkbox
                v-for="opt in DIFFICULTY_OPTIONS"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="题型（多选）">
            <el-checkbox-group v-model="cfg.question_types">
              <el-checkbox
                v-for="opt in QUESTION_TYPE_OPTIONS"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="最低质量分（可选）">
            <el-input-number
              v-model="cfg.min_score"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
              controls-position="right"
              style="width: 140px"
            />
            <span class="muted ml">仅做评分 ≥ 此值的题</span>
          </el-form-item>

          <el-divider />

          <div class="match-info" v-if="totalAvailable !== null">
            <span class="muted">符合条件的题目：</span>
            <span class="neon-text-cyan mono">{{ totalAvailable }}</span>
            <span class="muted"> 道</span>
            <span v-if="totalAvailable < cfg.size" class="warn ml">
              ⚠ 不足 {{ cfg.size }} 道，将按现有数量出题
            </span>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="starting"
              :disabled="!canStart"
              @click="onStart"
            >
              <el-icon><Aim /></el-icon>
              <span>开始练习 →</span>
            </el-button>
            <el-button size="large" @click="onCheckAvailable" :loading="checking">
              查看可用题数
            </el-button>
          </el-form-item>
        </el-form>
      </CyberCard>
    </template>

    <!-- Stage B: Practice -->
    <template v-else-if="stage === 'practice'">
      <div class="page-header">
        <h2>{{ langLabel }} · 进行中</h2>
        <div class="header-meta">
          <el-progress
            :percentage="overallPercent"
            :stroke-width="8"
            :show-text="false"
            style="width: 200px"
          />
          <span class="mono progress-text">
            {{ currentIdx + 1 }} / {{ questions.length }}
          </span>
          <el-button size="small" @click="onAbort">退出</el-button>
        </div>
      </div>

      <CyberCard accent="cyan" class="practice-card">
        <PracticeQuestion
          v-if="questions[currentIdx]"
          :key="currentIdx"
          :exercise="questions[currentIdx]"
          :index="currentIdx"
          :total="questions.length"
          @submit="onAnswerSubmit"
          @skip="onAnswerSkip"
          @next="onNext"
        />
      </CyberCard>
    </template>

    <!-- Stage C: Summary -->
    <template v-else>
      <div class="page-header">
        <h2>SESSION REPORT</h2>
      </div>

      <PracticeSummary
        :records="answers"
        :total-duration-ms="totalDuration"
        @restart="onRestart"
        @exit="onExit"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Aim } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { practiceApi, learningPathApi } from '@/api'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  LANGUAGE_LABEL,
  type Difficulty,
  type Language,
  type QuestionType,
} from '@/types/common'
import type { Exercise } from '@/types/exercise'
import type { Chapter } from '@/types/chapter'
import { useLanguageStore } from '@/stores/language'
import KnowledgePointPicker from '@/components/KnowledgePointPicker.vue'
import PracticeQuestion from '@/components/PracticeQuestion.vue'
import PracticeSummary from '@/components/PracticeSummary.vue'
import CyberCard from '@/components/CyberCard.vue'
import type { GradeResult } from '@/utils/grading'

const langStore = useLanguageStore()
const langLabel = computed(
  () => LANGUAGE_LABEL[langStore.current as Language] ?? langStore.current,
)

type Stage = 'setup' | 'practice' | 'summary'

const stage = ref<Stage>('setup')

// === Setup state ===
interface Config {
  scope: 'lang' | 'chapter' | 'kp'
  chapter_id: number | null
  knowledge_point_id: number | null
  difficulties: Difficulty[]
  question_types: QuestionType[]
  min_score: number | null
  size: number
}

const cfg = reactive<Config>({
  scope: 'lang',
  chapter_id: null,
  knowledge_point_id: null,
  difficulties: ['entry', 'basic', 'intermediate'],
  question_types: ['choice', 'fill', 'judge', 'read'],
  min_score: null,
  size: 10,
})

const chapters = ref<Chapter[]>([])
const totalAvailable = ref<number | null>(null)
const checking = ref(false)
const starting = ref(false)

const canStart = computed(() => {
  if (cfg.difficulties.length === 0 || cfg.question_types.length === 0) return false
  if (cfg.scope === 'chapter' && !cfg.chapter_id) return false
  if (cfg.scope === 'kp' && !cfg.knowledge_point_id) return false
  return true
})

watch(
  () => langStore.current,
  () => {
    cfg.chapter_id = null
    cfg.knowledge_point_id = null
    totalAvailable.value = null
    loadChapters()
  },
)

// Re-run availability check when filters change
watch(
  () => [cfg.scope, cfg.chapter_id, cfg.knowledge_point_id, cfg.difficulties.length, cfg.question_types.length, cfg.min_score],
  () => {
    totalAvailable.value = null
  },
)

async function loadChapters() {
  chapters.value = await learningPathApi.listChapters(langStore.current)
}

function buildSessionReq() {
  return {
    language: langStore.current,
    chapter_id: cfg.scope === 'chapter' ? cfg.chapter_id ?? undefined : undefined,
    knowledge_point_id:
      cfg.scope === 'kp' ? cfg.knowledge_point_id ?? undefined : undefined,
    difficulties: cfg.difficulties,
    question_types: cfg.question_types,
    min_score: cfg.min_score ?? undefined,
    status: 'published' as const,
    size: cfg.size,
    random_order: true,
  }
}

async function onCheckAvailable() {
  if (!canStart.value) {
    ElMessage.warning('请先完成必选项')
    return
  }
  checking.value = true
  try {
    const r = await practiceApi.createSession({ ...buildSessionReq(), size: 1 })
    totalAvailable.value = r.total_available
    if (r.total_available === 0) {
      ElMessage.warning('当前条件下没有题目，请放宽筛选')
    }
  } finally {
    checking.value = false
  }
}

async function onStart() {
  if (!canStart.value) return
  starting.value = true
  try {
    const r = await practiceApi.createSession(buildSessionReq())
    if (r.questions.length === 0) {
      ElMessage.warning('该条件下没有题目，请去生成题目或放宽筛选')
      return
    }
    questions.value = r.questions
    answers.value = []
    currentIdx.value = 0
    sessionStart.value = Date.now()
    stage.value = 'practice'
  } finally {
    starting.value = false
  }
}

// === Practice state ===
const questions = ref<Exercise[]>([])
const currentIdx = ref(0)
const sessionStart = ref(0)
const totalDuration = ref(0)

interface AnswerRecord {
  exercise: Exercise
  userAnswer: string
  result: GradeResult
  durationMs: number
}

const answers = ref<AnswerRecord[]>([])

const overallPercent = computed(() =>
  questions.value.length === 0
    ? 0
    : Math.round((currentIdx.value / questions.value.length) * 100),
)

function onAnswerSubmit(payload: {
  answer: string
  result: GradeResult
  durationMs: number
}) {
  answers.value.push({
    exercise: questions.value[currentIdx.value],
    userAnswer: payload.answer,
    result: payload.result,
    durationMs: payload.durationMs,
  })
}

function onAnswerSkip() {
  answers.value.push({
    exercise: questions.value[currentIdx.value],
    userAnswer: '',
    result: 'skipped',
    durationMs: 0,
  })
}

function onNext() {
  if (currentIdx.value + 1 < questions.value.length) {
    currentIdx.value++
  } else {
    finishSession()
  }
}

function finishSession() {
  totalDuration.value = Date.now() - sessionStart.value
  stage.value = 'summary'
}

function onAbort() {
  if (answers.value.length === 0) {
    stage.value = 'setup'
    return
  }
  finishSession()
}

function onRestart() {
  totalAvailable.value = null
  stage.value = 'setup'
}

function onExit() {
  // Just navigate back to dashboard via router; we'll use window.location for simplicity
  window.location.href = '/'
}

onMounted(loadChapters)
</script>

<style scoped>
.practice-page {
  min-height: calc(100vh - 64px);
}

.setup-card {
  max-width: 880px;
}

.muted {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.ml {
  margin-left: 8px;
}

.match-info {
  margin: 12px 0;
  padding: 12px 16px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  font-size: 14px;
}

.warn {
  color: var(--neon-yellow);
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-text {
  font-size: 14px;
  color: var(--neon-cyan);
}

.practice-card {
  max-width: 1000px;
  margin: 0 auto;
}
</style>
