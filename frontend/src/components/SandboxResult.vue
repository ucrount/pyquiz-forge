<template>
  <div class="sb-result" :class="bannerClass">
    <!-- Top banner: pass / fail summary -->
    <div class="sb-banner">
      <span class="sb-icon">{{ bannerIcon }}</span>
      <span class="sb-text">{{ bannerText }}</span>
      <span class="sb-meta mono">
        {{ result.passed }} / {{ result.total }} 通过
      </span>
    </div>

    <!-- Per-case detail -->
    <div v-if="result.results.length" class="sb-cases">
      <div
        v-for="r in result.results"
        :key="r.test_index"
        class="sb-case"
        :class="`sb-case-${r.status}`"
      >
        <div class="sb-case-header" @click="toggle(r.test_index)">
          <span class="case-status-icon">{{ statusIcon(r.status) }}</span>
          <span class="case-title mono">用例 #{{ r.test_index + 1 }}</span>
          <span class="case-status-text">{{ statusLabel(r.status) }}</span>
          <span class="case-runtime mono">{{ r.runtime_ms }} ms</span>
          <span class="case-toggle">{{ expanded[r.test_index] ? '▾' : '▸' }}</span>
        </div>
        <div v-if="expanded[r.test_index]" class="sb-case-body">
          <div v-if="r.input" class="sb-row">
            <span class="muted">输入：</span>
            <pre class="sb-code">{{ r.input }}</pre>
          </div>
          <div class="sb-row">
            <span class="muted">期望输出：</span>
            <pre class="sb-code">{{ r.expected || '（空）' }}</pre>
          </div>
          <div class="sb-row">
            <span class="muted">实际输出：</span>
            <pre class="sb-code" :class="{ 'is-bad': r.status !== 'pass' }">
{{ r.actual || '（空）' }}
            </pre>
          </div>
          <div v-if="r.stderr && r.status !== 'pass'" class="sb-row">
            <span class="muted">错误信息：</span>
            <pre class="sb-code is-err">{{ r.stderr }}</pre>
          </div>
        </div>
      </div>
    </div>

    <p v-if="result.early_stop" class="sb-early-stop muted">
      ⓘ 编译失败，已跳过剩余用例。
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { JudgeResult, TestStatus } from '@/types/sandbox'

const props = defineProps<{
  result: JudgeResult
}>()

const expanded = reactive<Record<number, boolean>>({})

// Auto-expand first failing case so user immediately sees what's wrong
const firstFailing = computed(() =>
  props.result.results.find((r) => r.status !== 'pass'),
)
if (firstFailing.value) {
  expanded[firstFailing.value.test_index] = true
}

function toggle(idx: number) {
  expanded[idx] = !expanded[idx]
}

const bannerClass = computed(() => {
  if (props.result.all_passed) return 'banner-ok'
  const r0 = props.result.results[0]
  if (r0?.status === 'compile_error') return 'banner-compile'
  if (r0?.status === 'infra_error') return 'banner-infra'
  return 'banner-fail'
})

const bannerIcon = computed(() => {
  if (props.result.all_passed) return '✓'
  const r0 = props.result.results[0]
  if (r0?.status === 'compile_error') return '⚙'
  if (r0?.status === 'infra_error') return '⚠'
  return '✗'
})

const bannerText = computed(() => {
  if (props.result.all_passed) return '全部通过！'
  const r0 = props.result.results[0]
  if (r0?.status === 'compile_error') return '编译失败'
  if (r0?.status === 'infra_error') return '沙箱不可达'
  if (props.result.passed === 0) return '全部未通过'
  return '部分用例未通过'
})

function statusIcon(s: TestStatus): string {
  return {
    pass: '✓',
    wrong_answer: '✗',
    runtime_error: '⚡',
    compile_error: '⚙',
    timeout: '⏱',
    infra_error: '⚠',
  }[s]
}

function statusLabel(s: TestStatus): string {
  return {
    pass: '通过',
    wrong_answer: '答案错误',
    runtime_error: '运行时错误',
    compile_error: '编译错误',
    timeout: '超时',
    infra_error: '沙箱故障',
  }[s]
}
</script>

<style scoped>
.sb-result {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sb-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 15px;
}

.sb-banner .sb-icon {
  font-size: 22px;
  font-weight: 800;
}

.sb-banner .sb-meta {
  margin-left: auto;
  font-size: 13px;
  font-weight: 500;
}

.banner-ok .sb-banner {
  background: rgba(0, 255, 157, 0.1);
  border: 1px solid var(--neon-green);
  color: var(--neon-green);
  box-shadow: 0 0 16px rgba(0, 255, 157, 0.2);
}

.banner-fail .sb-banner {
  background: rgba(255, 77, 141, 0.08);
  border: 1px solid var(--neon-pink);
  color: var(--neon-pink);
}

.banner-compile .sb-banner {
  background: rgba(255, 170, 0, 0.08);
  border: 1px solid var(--neon-yellow);
  color: var(--neon-yellow);
}

.banner-infra .sb-banner {
  background: rgba(155, 165, 192, 0.08);
  border: 1px solid var(--el-text-color-secondary);
  color: var(--el-text-color-regular);
}

/* Cases */
.sb-cases {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sb-case {
  background: rgba(15, 22, 40, 0.4);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.sb-case-pass {
  border-color: rgba(0, 255, 157, 0.3);
}

.sb-case-wrong_answer {
  border-color: rgba(255, 77, 141, 0.4);
}

.sb-case-runtime_error,
.sb-case-timeout {
  border-color: rgba(255, 77, 141, 0.4);
}

.sb-case-compile_error {
  border-color: rgba(255, 170, 0, 0.4);
}

.sb-case-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s ease;
}

.sb-case-header:hover {
  background: rgba(0, 212, 255, 0.04);
}

.case-status-icon {
  width: 18px;
  text-align: center;
  font-weight: 800;
}

.sb-case-pass .case-status-icon {
  color: var(--neon-green);
}

.sb-case-wrong_answer .case-status-icon,
.sb-case-runtime_error .case-status-icon,
.sb-case-timeout .case-status-icon {
  color: var(--neon-pink);
}

.sb-case-compile_error .case-status-icon {
  color: var(--neon-yellow);
}

.case-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.case-status-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.case-runtime {
  margin-left: auto;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.case-toggle {
  color: var(--neon-cyan);
  font-size: 12px;
  width: 12px;
  text-align: center;
}

.sb-case-body {
  padding: 8px 12px 12px;
  border-top: 1px dashed var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sb-row .muted {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  display: block;
  margin-bottom: 2px;
}

.sb-code {
  margin: 0;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 6px 10px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 12.5px;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.sb-code.is-bad {
  border-color: rgba(255, 77, 141, 0.4);
  color: var(--neon-pink);
}

.sb-code.is-err {
  border-color: rgba(255, 77, 141, 0.4);
  color: var(--neon-pink);
  background: rgba(255, 77, 141, 0.04);
}

.sb-early-stop {
  font-size: 12px;
  margin: 0;
}

.muted {
  color: var(--el-text-color-secondary);
}
</style>
