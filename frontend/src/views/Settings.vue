<template>
  <div class="page settings-page">
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

    <CyberCard accent="green" class="settings-card">
      <template #header>
        <span class="cyber-card__title">▸ 关于</span>
      </template>
      <div class="about-grid">
        <div>
          <span class="muted">版本</span>
          <span class="mono neon-text-cyan">v0.3.0</span>
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
import { useThemeStore, THEMES } from '@/stores/theme'
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
  max-width: 1100px;
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
