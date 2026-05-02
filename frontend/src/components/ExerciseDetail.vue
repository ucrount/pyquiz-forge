<template>
  <div class="ex-detail" v-if="exercise">
    <!-- Header -->
    <div class="ex-header">
      <h3 class="ex-title">{{ exercise.title }}</h3>
      <div class="ex-meta">
        <DifficultyTag :value="exercise.difficulty" />
        <QuestionTypeTag :value="exercise.question_type" />
        <el-tag size="small" effect="plain">
          知识点 #{{ exercise.knowledge_point_id }}
        </el-tag>
        <el-tag v-if="exercise.status" size="small" effect="plain" type="info">
          {{ statusLabel }}
        </el-tag>
        <ScoreBadge :value="exercise.score_overall" />
      </div>
    </div>

    <el-divider />

    <!-- Score block (if scored) -->
    <Section
      v-if="exercise.score_overall !== null && exercise.score_overall !== undefined"
      title="质量评分"
    >
      <div class="score-block">
        <div class="score-grid">
          <div class="score-item primary">
            <span class="score-label">综合</span>
            <strong class="score-value">{{ formatScore(exercise.score_overall) }}</strong>
          </div>
          <div class="score-item">
            <span class="score-label">清晰度</span>
            <strong class="score-value">{{ formatScore(exercise.score_detail?.clarity) }}</strong>
          </div>
          <div class="score-item">
            <span class="score-label">正确性</span>
            <strong class="score-value">{{ formatScore(exercise.score_detail?.correctness) }}</strong>
          </div>
          <div class="score-item">
            <span class="score-label">难度匹配</span>
            <strong class="score-value">{{ formatScore(exercise.score_detail?.difficulty_match) }}</strong>
          </div>
          <div class="score-item">
            <span class="score-label">教学价值</span>
            <strong class="score-value">{{ formatScore(exercise.score_detail?.educational_value) }}</strong>
          </div>
        </div>
        <p v-if="exercise.score_comment" class="score-comment">
          <strong>评语：</strong>{{ exercise.score_comment }}
        </p>
        <p v-if="exercise.scored_at" class="score-meta">
          评于 {{ formatDateTime(exercise.scored_at) }}
        </p>
      </div>
    </Section>

    <!-- Description -->
    <Section title="题目描述">
      <p class="text">{{ exercise.description || '（无）' }}</p>
    </Section>

    <!-- Choice options (if any) -->
    <Section v-if="choiceOptions.length" title="选项">
      <ul class="opts">
        <li v-for="opt in choiceOptions" :key="opt.label">
          <strong>{{ opt.label }}.</strong> {{ opt.text }}
        </li>
      </ul>
    </Section>

    <!-- Example -->
    <Section v-if="exercise.example_input || exercise.example_output" title="示例">
      <div v-if="exercise.example_input">
        <span class="muted">输入：</span>
        <pre class="ex-pre">{{ exercise.example_input }}</pre>
      </div>
      <div v-if="exercise.example_output" style="margin-top: 8px">
        <span class="muted">输出：</span>
        <pre class="ex-pre">{{ exercise.example_output }}</pre>
      </div>
    </Section>

    <!-- Hint -->
    <Section v-if="exercise.hint" title="提示">
      <p class="text">{{ exercise.hint }}</p>
    </Section>

    <!-- Standard answer -->
    <Section v-if="exercise.standard_answer" title="标准答案">
      <p class="text answer">{{ exercise.standard_answer }}</p>
    </Section>

    <!-- Reference code -->
    <Section v-if="exercise.reference_code" title="参考代码">
      <CodeBlock :code="exercise.reference_code" language="python" />
    </Section>

    <!-- Test cases -->
    <Section v-if="exercise.test_cases?.length" title="测试用例">
      <el-table :data="exercise.test_cases" stripe size="small">
        <el-table-column type="index" width="50" />
        <el-table-column prop="input" label="输入" />
        <el-table-column prop="expected_output" label="期望输出" />
      </el-table>
    </Section>

    <!-- Explanation -->
    <Section v-if="exercise.explanation" title="解析">
      <p class="text">{{ exercise.explanation }}</p>
    </Section>

    <!-- Common mistakes -->
    <Section v-if="exercise.common_mistakes" title="易错点">
      <p class="text mistakes">{{ exercise.common_mistakes }}</p>
    </Section>
  </div>

  <el-empty v-else description="无数据" />
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import type { Exercise } from '@/types/exercise'
import { EXERCISE_STATUS_LABEL, type ExerciseStatus } from '@/types/common'
import { formatDateTime } from '@/utils/format'
import DifficultyTag from './DifficultyTag.vue'
import QuestionTypeTag from './QuestionTypeTag.vue'
import CodeBlock from './CodeBlock.vue'
import ScoreBadge from './ScoreBadge.vue'

const props = defineProps<{ exercise: Exercise | null }>()

const statusLabel = computed(
  () =>
    EXERCISE_STATUS_LABEL[props.exercise?.status as ExerciseStatus] ??
    props.exercise?.status ??
    '',
)

function formatScore(v: number | null | undefined): string {
  if (v === null || v === undefined || isNaN(Number(v))) return '-'
  return Number(v).toFixed(1)
}

interface ChoiceOption {
  label: string
  text: string
}

const choiceOptions = computed<ChoiceOption[]>(() => {
  const ex = props.exercise
  if (!ex || ex.question_type !== 'choice') return []
  const opts = ex.extra?.options
  if (Array.isArray(opts)) {
    return opts.map((o, i) => {
      if (typeof o === 'string') {
        return { label: String.fromCharCode(65 + i), text: o }
      }
      const obj = o as Record<string, any>
      return {
        label: obj.label ?? obj.key ?? String.fromCharCode(65 + i),
        text: obj.text ?? obj.value ?? '',
      }
    })
  }
  if (opts && typeof opts === 'object') {
    return Object.entries(opts).map(([k, v]) => ({
      label: k,
      text: String(v),
    }))
  }
  return []
})

// Minimal inline section component (closure)
const Section = (_props: any, { slots, attrs }: any) =>
  h('div', { class: 'ex-section' }, [
    h('h4', { class: 'ex-section-title' }, attrs.title as string),
    h('div', { class: 'ex-section-body' }, slots.default?.()),
  ])
</script>

<style scoped>
.ex-detail {
  font-size: 14px;
  line-height: 1.6;
}

.ex-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ex-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.ex-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

:deep(.ex-section) {
  margin-bottom: 20px;
}

:deep(.ex-section-title) {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  border-left: 3px solid #409eff;
  padding-left: 8px;
}

.text {
  margin: 0;
  white-space: pre-wrap;
  color: #303133;
}

.answer {
  background: #f0f9ff;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #67c23a;
  font-weight: 500;
}

.mistakes {
  background: #fef0f0;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #f56c6c;
}

.ex-pre {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 8px 12px;
  margin: 4px 0;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 13px;
  white-space: pre-wrap;
}

.muted {
  color: #909399;
  font-size: 13px;
}

.opts {
  list-style: none;
  padding: 0;
  margin: 0;
}

.opts li {
  padding: 4px 0;
}

.score-block {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px 16px;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff;
  border-radius: 4px;
  padding: 8px 4px;
}

.score-item.primary {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.score-item.primary .score-label,
.score-item.primary .score-value {
  color: #fff;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.score-value {
  font-size: 18px;
  color: #303133;
  font-variant-numeric: tabular-nums;
  margin-top: 4px;
}

.score-comment {
  margin: 8px 0 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.score-meta {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
</style>
