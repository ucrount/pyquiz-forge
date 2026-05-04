<template>
  <div class="practice-summary">
    <div class="hero">
      <div class="hero-icon">⬡</div>
      <h2 class="hero-title">练习完成</h2>
      <p class="hero-sub mono">SESSION TERMINATED</p>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <CyberCard accent="cyan">
          <StatNumber label="题目总数" :value="stats.total" accent="cyan" />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="green">
          <StatNumber
            label="答对"
            :value="stats.correct"
            accent="green"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="pink">
          <StatNumber
            label="答错"
            :value="stats.wrong"
            accent="pink"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="purple">
          <StatNumber
            label="正确率"
            :value="accuracyText"
            accent="purple"
          />
        </CyberCard>
      </el-col>
    </el-row>

    <CyberCard accent="cyan" class="meta-card">
      <template #header>
        <span class="cyber-card__title">▸ 总览</span>
      </template>
      <div class="meta-grid">
        <div>
          <span class="muted">总用时</span>
          <span class="mono neon-text-cyan">{{ durationText }}</span>
        </div>
        <div>
          <span class="muted">平均每题</span>
          <span class="mono neon-text-cyan">{{ avgPerQuestion }}</span>
        </div>
        <div>
          <span class="muted">未评判</span>
          <span class="mono">{{ stats.noGrade }}</span>
        </div>
        <div>
          <span class="muted">跳过</span>
          <span class="mono">{{ stats.skipped }}</span>
        </div>
      </div>
    </CyberCard>

    <CyberCard accent="purple" v-if="byTypeRows.length" class="bytype-card">
      <template #header>
        <span class="cyber-card__title">▸ 按题型表现</span>
      </template>
      <el-table :data="byTypeRows" size="small">
        <el-table-column label="题型" min-width="140">
          <template #default="{ row }">
            <QuestionTypeTag :value="row.type" />
          </template>
        </el-table-column>
        <el-table-column label="正确数" width="100">
          <template #default="{ row }">
            <span class="neon-text-cyan mono">{{ row.correct }}/{{ row.total }}</span>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.percent"
              :stroke-width="6"
              :show-text="false"
            />
            <span class="mono small-pct">{{ row.percent }}%</span>
          </template>
        </el-table-column>
      </el-table>
    </CyberCard>

    <CyberCard
      v-if="wrongList.length"
      accent="pink"
      class="wrong-card"
    >
      <template #header>
        <span class="cyber-card__title">▸ 错题回顾</span>
      </template>
      <ul class="wrong-list">
        <li
          v-for="(w, i) in wrongList"
          :key="w.exercise.id"
          class="wrong-item"
          @click="onClickWrong(w.exercise)"
        >
          <span class="wrong-num mono">#{{ i + 1 }}</span>
          <DifficultyTag :value="w.exercise.difficulty" />
          <QuestionTypeTag :value="w.exercise.question_type" />
          <span class="wrong-title">{{ w.exercise.title }}</span>
          <span class="muted small">→ 你答：{{ w.userAnswer || '（空）' }}</span>
        </li>
      </ul>
    </CyberCard>

    <div class="actions">
      <el-button size="large" type="primary" @click="$emit('restart')">
        <el-icon><RefreshRight /></el-icon><span>再来一组</span>
      </el-button>
      <el-button size="large" @click="$emit('exit')">
        <el-icon><HomeFilled /></el-icon><span>回到主页</span>
      </el-button>
    </div>

    <!-- Drawer for wrong-question detail -->
    <el-drawer v-model="detailVisible" size="60%" title="错题详情">
      <ExerciseDetail :exercise="detailExercise" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RefreshRight, HomeFilled } from '@element-plus/icons-vue'
import type { Exercise } from '@/types/exercise'
import type { GradeResult } from '@/utils/grading'
import { QUESTION_TYPE_LABEL } from '@/types/common'
import CyberCard from './CyberCard.vue'
import StatNumber from './StatNumber.vue'
import DifficultyTag from './DifficultyTag.vue'
import QuestionTypeTag from './QuestionTypeTag.vue'
import ExerciseDetail from './ExerciseDetail.vue'

interface AnswerRecord {
  exercise: Exercise
  userAnswer: string
  result: GradeResult
  durationMs: number
}

const props = defineProps<{
  records: AnswerRecord[]
  totalDurationMs: number
}>()

defineEmits<{
  (e: 'restart'): void
  (e: 'exit'): void
}>()

const stats = computed(() => {
  let correct = 0
  let wrong = 0
  let noGrade = 0
  let skipped = 0
  for (const r of props.records) {
    if (r.result === 'correct') correct++
    else if (r.result === 'wrong') wrong++
    else if (r.result === 'no-grade') noGrade++
    else skipped++
  }
  return {
    total: props.records.length,
    correct,
    wrong,
    noGrade,
    skipped,
  }
})

const accuracyText = computed(() => {
  const denom = stats.value.correct + stats.value.wrong
  if (denom === 0) return '—'
  return `${Math.round((stats.value.correct / denom) * 100)}%`
})

const durationText = computed(() => {
  const sec = Math.floor(props.totalDurationMs / 1000)
  const m = Math.floor(sec / 60)
  return m > 0 ? `${m}:${String(sec % 60).padStart(2, '0')}` : `${sec}s`
})

const avgPerQuestion = computed(() => {
  if (props.records.length === 0) return '—'
  const sec = Math.floor(props.totalDurationMs / props.records.length / 1000)
  return `${sec}s`
})

const byTypeRows = computed(() => {
  const acc: Record<string, { type: string; total: number; correct: number }> = {}
  for (const r of props.records) {
    const k = r.exercise.question_type
    if (!acc[k]) acc[k] = { type: k, total: 0, correct: 0 }
    acc[k].total++
    if (r.result === 'correct') acc[k].correct++
  }
  return Object.values(acc).map((x) => ({
    ...x,
    label: QUESTION_TYPE_LABEL[x.type as keyof typeof QUESTION_TYPE_LABEL] || x.type,
    percent: x.total ? Math.round((x.correct / x.total) * 100) : 0,
  }))
})

const wrongList = computed(() =>
  props.records.filter((r) => r.result === 'wrong'),
)

const detailVisible = ref(false)
const detailExercise = ref<Exercise | null>(null)

function onClickWrong(ex: Exercise) {
  detailExercise.value = ex
  detailVisible.value = true
}
</script>

<style scoped>
.practice-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero {
  text-align: center;
  padding: 24px 0;
}

.hero-icon {
  font-size: 56px;
  color: var(--neon-cyan);
  text-shadow: 0 0 32px var(--neon-cyan);
  margin-bottom: 8px;
}

.hero-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(
    90deg,
    var(--neon-cyan) 0%,
    var(--neon-purple) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-sub {
  margin-top: 4px;
  letter-spacing: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.stats-row {
  margin-bottom: 0;
}

.meta-card .meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 16px;
}

.meta-card .meta-grid > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.meta-card .mono {
  font-size: 18px;
  font-weight: 600;
}

.muted {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  letter-spacing: 0.5px;
}

.bytype-card {
  margin-top: 0;
}

.small-pct {
  font-size: 12px;
  margin-left: 8px;
  color: var(--el-text-color-regular);
}

.wrong-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.wrong-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(15, 22, 40, 0.5);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--el-border-color-lighter);
}

.wrong-item:hover {
  border-color: var(--neon-pink);
  background: rgba(255, 77, 141, 0.05);
}

.wrong-num {
  font-weight: 700;
  color: var(--neon-pink);
  min-width: 30px;
}

.wrong-title {
  flex: 1;
  font-weight: 500;
}

.small {
  font-size: 12px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}
</style>
