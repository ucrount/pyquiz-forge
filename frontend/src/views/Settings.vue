<template>
  <div class="page page--narrow settings-page">
    <div class="page-header">
      <h2>SETTINGS</h2>
    </div>

    <CyberCard accent="cyan" class="settings-card">
      <template #header>
        <span class="cyber-card__title">▸ 视觉主题</span>
      </template>
      <div class="theme-grid">
        <div
          v-for="t in THEMES"
          :key="t.id"
          class="theme-card"
          :class="{ 'is-active': theme.current === t.id }"
          :style="{
            '--theme-bg': t.preview.bg,
            '--theme-primary': t.preview.primary,
            '--theme-secondary': t.preview.secondary,
          }"
          @click="theme.setTheme(t.id)"
        >
          <div class="theme-preview">
            <div class="dot dot-1"></div>
            <div class="dot dot-2"></div>
            <div class="bar bar-1"></div>
            <div class="bar bar-2"></div>
          </div>
          <div class="theme-info">
            <div class="theme-name">{{ t.name }}</div>
            <div class="theme-desc">{{ t.description }}</div>
          </div>
          <div class="theme-check" v-if="theme.current === t.id">✓</div>
        </div>
      </div>
    </CyberCard>

    <CyberCard accent="green" class="settings-card">
      <template #header>
        <span class="cyber-card__title">▸ 可读性</span>
      </template>
      <el-form label-position="top">
        <el-form-item label="对比度">
          <el-radio-group
            :model-value="theme.contrast"
            @update:model-value="(v: any) => theme.setContrast(v)"
          >
            <el-radio-button
              v-for="opt in CONTRAST_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
          <span class="muted ml">
            {{ CONTRAST_OPTIONS.find(o => o.value === theme.contrast)?.hint }}
          </span>
        </el-form-item>

        <el-form-item label="字号">
          <el-radio-group
            :model-value="theme.fontSize"
            @update:model-value="(v: any) => theme.setFontSize(v)"
          >
            <el-radio-button
              v-for="opt in FONT_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
              <span class="opt-hint mono">{{ opt.hint }}</span>
            </el-radio-button>
          </el-radio-group>
          <span class="muted ml">影响整体页面字号</span>
        </el-form-item>

        <el-form-item label="效果预览">
          <div class="contrast-preview">
            <h4 class="preview-h4">这是主标题（primary）</h4>
            <p class="preview-p">
              这是正文文字（regular）—— 这一行用来感觉对比度。
              切换主题或对比度时，这段文字应该始终清晰可读。
            </p>
            <p class="preview-secondary">
              这是次要文字（secondary）—— 标签 / 说明性文字常用这个色阶。
            </p>
            <p class="preview-placeholder">
              这是占位符文字（placeholder）—— 如输入框未填时的提示。
            </p>
          </div>
        </el-form-item>
      </el-form>
    </CyberCard>

    <CyberCard accent="purple" class="settings-card">
      <template #header>
        <span class="cyber-card__title">▸ 默认练习偏好</span>
      </template>
      <el-form label-position="top">
        <el-form-item label="默认题目数量">
          <el-input-number
            v-model="prefs.defaultPracticeSize"
            :min="1"
            :max="50"
            controls-position="right"
            @change="savePrefs"
          />
          <span class="muted ml">每次开始练习的默认数量</span>
        </el-form-item>
        <el-form-item label="默认难度">
          <el-checkbox-group v-model="prefs.defaultDifficulties" @change="savePrefs">
            <el-checkbox
              v-for="opt in DIFFICULTY_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="默认题型">
          <el-checkbox-group v-model="prefs.defaultQuestionTypes" @change="savePrefs">
            <el-checkbox
              v-for="opt in QUESTION_TYPE_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
    </CyberCard>

    <CyberCard accent="cyan" class="settings-card">
      <template #header>
        <span class="cyber-card__title">▸ 关于</span>
      </template>
      <div class="about-grid">
        <div>
          <span class="muted">版本</span>
          <span class="mono neon-text-cyan">v0.3.1</span>
        </div>
        <div>
          <span class="muted">许可</span>
          <span class="mono">MIT</span>
        </div>
        <div>
          <span class="muted">仓库</span>
          <el-link
            type="primary"
            :underline="false"
            href="https://github.com/ucrount/pyquiz-forge"
            target="_blank"
          >
            github.com/ucrount/pyquiz-forge ↗
          </el-link>
        </div>
        <div>
          <span class="muted">API 文档</span>
          <el-link type="primary" :underline="false" href="/docs" target="_blank">
            Swagger UI ↗
          </el-link>
        </div>
      </div>
    </CyberCard>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import {
  useThemeStore,
  THEMES,
  CONTRAST_OPTIONS,
  FONT_OPTIONS,
} from '@/stores/theme'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  type Difficulty,
  type QuestionType,
} from '@/types/common'
import CyberCard from '@/components/CyberCard.vue'

const theme = useThemeStore()

// Practice preferences (stored in localStorage)
const PREFS_KEY = 'pyquiz.practicePrefs'

interface Prefs {
  defaultPracticeSize: number
  defaultDifficulties: Difficulty[]
  defaultQuestionTypes: QuestionType[]
}

function loadPrefs(): Prefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    if (raw) {
      const p = JSON.parse(raw)
      return {
        defaultPracticeSize: p.defaultPracticeSize ?? 10,
        defaultDifficulties: p.defaultDifficulties ?? ['entry', 'basic'],
        defaultQuestionTypes: p.defaultQuestionTypes ?? [
          'choice', 'fill', 'judge', 'read',
        ],
      }
    }
  } catch {}
  return {
    defaultPracticeSize: 10,
    defaultDifficulties: ['entry', 'basic'],
    defaultQuestionTypes: ['choice', 'fill', 'judge', 'read'],
  }
}

const prefs = reactive<Prefs>(loadPrefs())

function savePrefs() {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
  } catch {}
}

watch(prefs, savePrefs, { deep: true })
</script>

<style scoped>
.settings-page {
  /* 用全局 .page--narrow 控制宽度 */
}

.settings-card {
  margin-bottom: 16px;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.theme-card {
  position: relative;
  background: var(--theme-bg);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
  overflow: hidden;
}

.theme-card:hover {
  border-color: var(--theme-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px var(--theme-primary);
}

.theme-card.is-active {
  border-color: var(--theme-primary);
  box-shadow: 0 0 18px var(--theme-primary), inset 0 0 12px var(--theme-primary);
}

.theme-preview {
  height: 80px;
  position: relative;
  background: var(--theme-bg);
  border-radius: 6px;
  margin-bottom: 10px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--theme-primary) 20%, transparent);
}

.theme-preview .dot {
  position: absolute;
  border-radius: 50%;
  filter: blur(8px);
}

.theme-preview .dot-1 {
  width: 50px;
  height: 50px;
  top: -10px;
  left: -10px;
  background: var(--theme-primary);
  opacity: 0.6;
}

.theme-preview .dot-2 {
  width: 40px;
  height: 40px;
  bottom: -8px;
  right: -8px;
  background: var(--theme-secondary);
  opacity: 0.6;
}

.theme-preview .bar {
  position: absolute;
  height: 4px;
  border-radius: 2px;
  left: 16px;
}

.theme-preview .bar-1 {
  background: var(--theme-primary);
  width: 60%;
  top: 30%;
  box-shadow: 0 0 8px var(--theme-primary);
}

.theme-preview .bar-2 {
  background: var(--theme-secondary);
  width: 40%;
  top: 50%;
  box-shadow: 0 0 6px var(--theme-secondary);
}

.theme-info {
  text-align: center;
}

.theme-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--theme-primary);
  text-shadow: 0 0 8px var(--theme-primary);
  letter-spacing: 0.5px;
}

.theme-desc {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.theme-check {
  position: absolute;
  top: 6px;
  right: 8px;
  font-size: 14px;
  color: var(--theme-primary);
  font-weight: 700;
}

.muted {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  letter-spacing: 0.4px;
}

.ml {
  margin-left: 8px;
}

.opt-hint {
  margin-left: 6px;
  font-size: 11px;
  opacity: 0.7;
}

.contrast-preview {
  padding: 14px 18px;
  width: 100%;
  background: var(--glass-bg);
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
}

.preview-h4 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.preview-p {
  margin: 0 0 6px;
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.preview-secondary {
  margin: 0 0 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

.preview-placeholder {
  margin: 0;
  font-size: 12.5px;
  color: var(--el-text-color-placeholder);
}

.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 24px;
}

.about-grid > div {
  display: flex;
  align-items: center;
  gap: 12px;
}

.about-grid .muted {
  width: 60px;
  flex-shrink: 0;
}
</style>
