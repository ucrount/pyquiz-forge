<template>
  <div class="practice-question">
    <!-- Header: question number + tags + timer -->
    <div class="pq-header">
      <div class="pq-meta">
        <span class="pq-number mono">#{{ index + 1 }} / {{ total }}</span>
        <DifficultyTag :value="exercise.difficulty" />
        <QuestionTypeTag :value="exercise.question_type" />
        <ScoreBadge :value="exercise.score_overall" v-if="exercise.score_overall !== null" />
      </div>
      <span v-if="elapsedText" class="pq-timer mono">⏱ {{ elapsedText }}</span>
    </div>

    <!-- Title -->
    <h3 class="pq-title">{{ exercise.title }}</h3>

    <!-- Description -->
    <div class="pq-section">
      <div class="pq-desc">{{ exercise.description || '（无题干）' }}</div>
    </div>

    <!-- Examples -->
    <div v-if="exercise.example_input || exercise.example_output" class="pq-section pq-examples">
      <div v-if="exercise.example_input">
        <span class="muted">示例输入：</span>
        <pre class="ex-pre">{{ exercise.example_input }}</pre>
      </div>
      <div v-if="exercise.example_output" style="margin-top:8px">
        <span class="muted">示例输出：</span>
        <pre class="ex-pre">{{ exercise.example_output }}</pre>
      </div>
    </div>

    <!-- Hint (collapsible, only before submit) -->
    <div v-if="!submitted && exercise.hint" class="pq-section">
      <el-collapse>
        <el-collapse-item title="💡 提示（点击展开）" name="hint">
          <p class="pq-hint">{{ exercise.hint }}</p>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- Reference code for complete/debug (read-only display) -->
    <div
      v-if="!submitted && (exercise.question_type === 'complete' || exercise.question_type === 'debug') && exercise.reference_code"
      class="pq-section"
    >
      <span class="muted">代码：</span>
      <CodeBlock :code="exercise.reference_code" language="python" :copyable="false" />
    </div>

    <!-- Answer area, varies by type -->
    <div v-if="!submitted" class="pq-section pq-answer-area">
      <!-- Choice -->
      <template v-if="exercise.question_type === 'choice'">
        <div class="choice-grid">
          <button
            v-for="opt in choiceOptions"
            :key="opt.label"
            class="choice-btn"
            :class="{ 'is-active': userAnswer === opt.label }"
            @click="userAnswer = opt.label"
          >
            <span class="choice-label">{{ opt.label }}</span>
            <span class="choice-text">{{ opt.text || '（无文本）' }}</span>
          </button>
        </div>
      </template>

      <!-- Judge -->
      <template v-else-if="exercise.question_type === 'judge'">
        <div class="judge-row">
          <button
            class="judge-btn ok"
            :class="{ 'is-active': userAnswer === '正确' }"
            @click="userAnswer = '正确'"
          >
            ✓ 正确
          </button>
          <button
            class="judge-btn fail"
            :class="{ 'is-active': userAnswer === '错误' }"
            @click="userAnswer = '错误'"
          >
            ✗ 错误
          </button>
        </div>
      </template>

      <!-- Fill / read -->
      <template v-else-if="exercise.question_type === 'fill' || exercise.question_type === 'read'">
        <el-input
          v-model="userAnswer"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
          class="mono"
          :placeholder="exercise.question_type === 'read' ? '在此填写代码运行后的输出...' : '在此填写答案...'"
        />
      </template>

      <!-- Complete -->
      <template v-else-if="exercise.question_type === 'complete'">
        <el-input
          v-model="userAnswer"
          type="textarea"
          :autosize="{ minRows: 4, maxRows: 12 }"
          class="mono"
          placeholder="在此填写需补全的代码..."
        />
      </template>

      <!-- Program / Debug — no auto-grade, just an answer area + reveal button -->
      <template v-else>
        <el-input
          v-model="userAnswer"
          type="textarea"
          :autosize="{ minRows: 6, maxRows: 20 }"
          class="mono code-area"
          placeholder="在此写下你的代码（或思路）..."
        />
        <p class="hint-text">
          <template v-if="useSandbox">
            ⓘ 提交后会用真实沙盒运行你的代码，自动对比测试用例。
          </template>
          <template v-else>
            ⓘ 此题没有测试用例，提交后请对照参考答案自评。
          </template>
        </p>
      </template>
    </div>

    <!-- Result section after submit -->
    <div v-if="submitted" class="pq-section pq-result">
      <div class="result-banner" :class="`result-${gradeResult}`">
        <span class="result-icon">
          {{ gradeResult === 'correct' ? '✓' : gradeResult === 'wrong' ? '✗' : 'ⓘ' }}
        </span>
        <span class="result-text">
          {{ resultText }}
        </span>
      </div>

      <!-- Sandbox per-case detail (only for code questions with test cases) -->
      <div v-if="judgeResult" class="result-section">
        <SandboxResult :result="judgeResult" />
      </div>

      <div v-if="!judgeResult" class="result-section">
        <span class="muted">你的答案：</span>
        <div class="user-answer">{{ userAnswer || '（空）' }}</div>
      </div>

      <div v-if="judgeResult && userAnswer" class="result-section">
        <span class="muted">你的代码：</span>
        <CodeBlock :code="userAnswer" :language="exercise.language || 'python'" :copyable="true" />
      </div>

      <div v-if="exercise.standard_answer && !judgeResult" class="result-section">
        <span class="muted">标准答案：</span>
        <div class="std-answer">{{ exercise.standard_answer }}</div>
      </div>

      <div v-if="exercise.reference_code" class="result-section">
        <span class="muted">参考代码：</span>
        <CodeBlock :code="exercise.reference_code" :language="exercise.language || 'python'" :copyable="true" />
      </div>

      <div v-if="exercise.explanation" class="result-section">
        <span class="muted">解析：</span>
        <p class="explain">{{ exercise.explanation }}</p>
      </div>

      <div v-if="exercise.common_mistakes" class="result-section">
        <span class="muted">易错点：</span>
        <p class="mistakes">{{ exercise.common_mistakes }}</p>
      </div>
    </div>

    <!-- Action bar -->
    <div class="pq-actions">
      <template v-if="!submitted">
        <el-button @click="onSkip" :disabled="judging">跳过</el-button>
        <el-button
          type="primary"
          :disabled="!canSubmit || judging"
          :loading="judging"
          @click="onSubmit"
        >
          {{ judging ? '沙盒运行中...' : '提交答案' }}
        </el-button>
      </template>
      <template v-else>
        <el-button type="primary" @click="onNext">
          {{ index + 1 < total ? '下一题 →' : '查看总结 ✓' }}
        </el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import type { Exercise } from '@/types/exercise'
import type { JudgeResult } from '@/types/sandbox'
import { gradeAnswer, type GradeResult } from '@/utils/grading'
import { sandboxApi } from '@/api'
import DifficultyTag from './DifficultyTag.vue'
import QuestionTypeTag from './QuestionTypeTag.vue'
import ScoreBadge from './ScoreBadge.vue'
import CodeBlock from './CodeBlock.vue'
import SandboxResult from './SandboxResult.vue'

const props = defineProps<{
  exercise: Exercise
  index: number
  total: number
}>()

const emit = defineEmits<{
  (e: 'submit', payload: { answer: string; result: GradeResult; durationMs: number }): void
  (e: 'skip'): void
  (e: 'next'): void
}>()

const userAnswer = ref<string>('')
const submitted = ref(false)
const gradeResult = ref<GradeResult>('skipped')
const judging = ref(false)
const judgeResult = ref<JudgeResult | null>(null)

const startTime = ref(0)
const elapsedMs = ref(0)
const tickTimer = ref<number | null>(null)

const elapsedText = computed(() => {
  const s = Math.floor(elapsedMs.value / 1000)
  const m = Math.floor(s / 60)
  return m > 0 ? `${m}:${String(s % 60).padStart(2, '0')}` : `${s}s`
})

interface ChoiceOption {
  label: string
  text: string
}

const choiceOptions = computed<ChoiceOption[]>(() => {
  const ex = props.exercise
  if (ex.question_type !== 'choice') return []
  const opts = ex.extra?.options
  if (Array.isArray(opts)) {
    return opts.map((o, i) => {
      if (typeof o === 'string') {
        return { label: String.fromCharCode(65 + i), text: o }
      }
      const obj = o as Record<string, any>
      return {
        label: String(obj.label ?? obj.key ?? String.fromCharCode(65 + i)),
        text: String(obj.text ?? obj.value ?? ''),
      }
    })
  }
  if (opts && typeof opts === 'object') {
    return Object.entries(opts).map(([k, v]) => ({ label: k, text: String(v) }))
  }
  // Fallback if LLM didn't fill options, derive 4 placeholders
  return ['A', 'B', 'C', 'D'].map((l) => ({ label: l, text: '' }))
})

const canSubmit = computed(() => {
  // Programs/debug — allow submit even with empty answer (just reveals)
  if (
    props.exercise.question_type === 'program' ||
    props.exercise.question_type === 'debug'
  ) {
    return !useSandbox.value || userAnswer.value.trim().length > 0
  }
  return userAnswer.value.trim().length > 0
})

// True if the question is code-type AND has executable test cases
const useSandbox = computed(() => {
  const type = props.exercise.question_type
  const isCodeType = type === 'complete' || type === 'program' || type === 'debug'
  const hasTestCases = Array.isArray(props.exercise.test_cases) && props.exercise.test_cases.length > 0
  return isCodeType && hasTestCases
})

const resultText = computed(() => {
  switch (gradeResult.value) {
    case 'correct':
      return judgeResult.value
        ? `全部 ${judgeResult.value.total} 个测试用例通过！`
        : '回答正确！'
    case 'wrong':
      if (judgeResult.value) {
        return `${judgeResult.value.passed} / ${judgeResult.value.total} 个用例通过`
      }
      return '答错了，看下标准答案。'
    case 'no-grade':
      return '此题没有自动判分依据，请对比参考答案自评。'
    case 'skipped':
      return '已跳过。'
    default:
      return ''
  }
})

async function onSubmit() {
  // Code questions with test cases — use the sandbox
  if (useSandbox.value) {
    judging.value = true
    try {
      const result = await sandboxApi.judgeExercise(props.exercise.id, {
        source: userAnswer.value,
        language: props.exercise.language || undefined,
      })
      judgeResult.value = result
      gradeResult.value = result.all_passed ? 'correct' : 'wrong'
      submitted.value = true
      stopTimer()
      emit('submit', {
        answer: userAnswer.value,
        result: gradeResult.value,
        durationMs: elapsedMs.value,
      })
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || '沙盒服务调用失败'
      ElMessage.error(`沙盒判分失败：${msg}`)
    } finally {
      judging.value = false
    }
    return
  }

  // Non-code or no test cases — fall back to string comparison
  const result = gradeAnswer(props.exercise, userAnswer.value)
  gradeResult.value = result
  submitted.value = true
  stopTimer()
  emit('submit', {
    answer: userAnswer.value,
    result,
    durationMs: elapsedMs.value,
  })
}

function onSkip() {
  gradeResult.value = 'skipped'
  submitted.value = true
  stopTimer()
  emit('skip')
}

function onNext() {
  emit('next')
}

function stopTimer() {
  if (tickTimer.value) {
    clearInterval(tickTimer.value)
    tickTimer.value = null
  }
}

onMounted(() => {
  startTime.value = Date.now()
  elapsedMs.value = 0
  tickTimer.value = window.setInterval(() => {
    elapsedMs.value = Date.now() - startTime.value
  }, 500)
})

onBeforeUnmount(stopTimer)
</script>

<style scoped>
.practice-question {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pq-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.pq-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.pq-number {
  font-size: 14px;
  font-weight: 700;
  color: var(--neon-cyan);
  letter-spacing: 0.5px;
}

.pq-timer {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.pq-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.pq-section {
  margin: 0;
}

.pq-desc {
  white-space: pre-wrap;
  line-height: 1.7;
  color: var(--el-text-color-primary);
  font-size: 15px;
}

.pq-examples {
  background: rgba(15, 22, 40, 0.5);
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 10px 14px;
}

.ex-pre {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  padding: 6px 10px;
  margin: 4px 0;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  color: var(--el-text-color-primary);
}

.muted {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.pq-hint {
  margin: 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

/* Choice */
.choice-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.choice-btn {
  background: rgba(15, 22, 40, 0.6);
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: inherit;
  font-size: 14px;
  color: var(--el-text-color-primary);
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.choice-btn:hover {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.3);
}

.choice-btn.is-active {
  border-color: var(--neon-cyan);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.4);
}

.choice-label {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: var(--neon-cyan);
  font-size: 18px;
  flex-shrink: 0;
}

.choice-text {
  flex: 1;
}

/* Judge */
.judge-row {
  display: flex;
  gap: 16px;
}

.judge-btn {
  flex: 1;
  background: rgba(15, 22, 40, 0.6);
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.judge-btn.ok {
  color: var(--neon-green);
}
.judge-btn.fail {
  color: var(--neon-pink);
}

.judge-btn:hover,
.judge-btn.is-active {
  background: rgba(0, 212, 255, 0.1);
  border-color: currentColor;
  box-shadow: 0 0 16px currentColor;
}

.code-area :deep(.el-textarea__inner) {
  background: rgba(0, 0, 0, 0.3) !important;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 13px;
}

.hint-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin: 6px 0 0;
}

/* Result */
.result-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 8px;
}

.result-banner.result-correct {
  background: rgba(0, 255, 157, 0.1);
  border: 1px solid var(--neon-green);
  color: var(--neon-green);
  box-shadow: 0 0 16px rgba(0, 255, 157, 0.2);
}
.result-banner.result-wrong {
  background: rgba(255, 77, 141, 0.08);
  border: 1px solid var(--neon-pink);
  color: var(--neon-pink);
}
.result-banner.result-no-grade {
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
}
.result-banner.result-skipped {
  background: rgba(155, 165, 192, 0.08);
  border: 1px solid var(--el-text-color-secondary);
  color: var(--el-text-color-secondary);
}

.result-icon {
  font-size: 24px;
  font-weight: 800;
}

.result-section {
  margin: 12px 0;
}

.user-answer,
.std-answer {
  background: rgba(15, 22, 40, 0.6);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 8px 12px;
  margin-top: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  color: var(--el-text-color-primary);
}

.std-answer {
  border-color: var(--neon-green);
  background: rgba(0, 255, 157, 0.05);
}

.explain {
  margin: 4px 0 0;
  line-height: 1.7;
  color: var(--el-text-color-regular);
  white-space: pre-wrap;
}

.mistakes {
  margin: 4px 0 0;
  line-height: 1.7;
  color: var(--neon-pink);
  white-space: pre-wrap;
}

.pq-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
