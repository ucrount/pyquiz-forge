<template>
  <div class="page page--medium">
    <div class="page-header">
      <h2>SYSTEM OVERVIEW</h2>
      <span class="header-meta mono">
        <span class="meta-key">v0.3.1</span>
      </span>
    </div>

    <!-- ========================================================
         区块 1：当前学习语言（用大按钮组，更醒目）
         ======================================================== -->
    <CyberCard accent="cyan" class="lang-card">
      <template #header>
        <span class="cyber-card__title">▸ 当前学习语言</span>
      </template>
      <template #extra>
        <span class="muted small">切换会影响所有页面的内容显示</span>
      </template>
      <div class="lang-grid">
        <button
          v-for="opt in LANGUAGE_OPTIONS"
          :key="opt.value"
          class="lang-btn"
          :class="{ 'is-active': langStore.current === opt.value }"
          :style="{ '--lang-color': LANGUAGE_COLOR[opt.value as Language] }"
          @click="onPickLanguage(opt.value as Language)"
        >
          <span class="lang-name">{{ opt.label }}</span>
          <span class="lang-counts mono">
            <span>{{ perLangCounts[opt.value as Language]?.kps ?? '—' }} KP</span>
            <span class="dot">·</span>
            <span>{{ perLangCounts[opt.value as Language]?.exercises ?? '—' }} 题</span>
          </span>
          <span v-if="langStore.current === opt.value" class="lang-check">✓</span>
        </button>
      </div>
    </CyberCard>

    <!-- ========================================================
         区块 2：当前语言的核心统计（4 卡）
         ======================================================== -->
    <el-row :gutter="14" class="stats-row">
      <el-col :span="6">
        <CyberCard accent="cyan">
          <StatNumber
            :label="`${langLabel} · 章节`"
            :value="stats.chapters"
            accent="cyan"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="purple">
          <StatNumber
            :label="`${langLabel} · 知识点`"
            :value="stats.kps"
            accent="purple"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="pink">
          <StatNumber
            :label="`${langLabel} · 题目`"
            :value="stats.exercises"
            accent="pink"
          />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="green">
          <StatNumber
            label="掌握进度"
            :value="masteryProgressText"
            accent="green"
            :hint="masteryProgressHint"
          />
        </CyberCard>
      </el-col>
    </el-row>

    <!-- ========================================================
         区块 3：学习进度分布 + LLM 配置
         ======================================================== -->
    <el-row :gutter="14" class="dual-row">
      <el-col :span="14">
        <CyberCard accent="purple" class="full-card">
          <template #header>
            <span class="cyber-card__title">▸ 学习进度分布</span>
          </template>
          <template #extra>
            <el-link type="primary" :underline="false" @click="$router.push('/review')">
              复习清单 →
            </el-link>
          </template>

          <div class="mastery-grid">
            <div
              v-for="row in masteryRows"
              :key="row.key"
              class="mastery-row"
              @click="$router.push({ path: '/review', query: { tab: row.key } })"
            >
              <span class="mr-icon" :style="{ color: row.color }">{{ row.icon }}</span>
              <span class="mr-label">{{ row.label }}</span>
              <div class="mr-bar">
                <div
                  class="mr-bar-fill"
                  :style="{
                    width: row.pct + '%',
                    background: row.color,
                    boxShadow: `0 0 8px ${row.color}`,
                  }"
                ></div>
              </div>
              <span class="mr-num mono" :style="{ color: row.color }">
                {{ row.count }}
              </span>
            </div>
          </div>
        </CyberCard>
      </el-col>

      <el-col :span="10">
        <CyberCard accent="pink" class="full-card">
          <template #header>
            <span class="cyber-card__title">▸ 大模型配置</span>
          </template>
          <template #extra>
            <el-link type="primary" :underline="false" @click="$router.push('/llm-configs')">
              管理 →
            </el-link>
          </template>
          <div v-if="activeLLM" class="llm-block">
            <div class="llm-row">
              <span class="llm-label">激活</span>
              <span class="llm-value mono active">
                <span class="dot pulse"></span>
                {{ activeLLM.name }}
              </span>
            </div>
            <div class="llm-row">
              <span class="llm-label">Provider</span>
              <span class="llm-value">{{ activeLLM.provider }}</span>
            </div>
            <div class="llm-row">
              <span class="llm-label">模型</span>
              <span class="llm-value mono" :title="activeLLM.model">
                {{ activeLLM.model }}
              </span>
            </div>
            <div class="llm-row">
              <span class="llm-label">温度</span>
              <span class="llm-value mono">{{ activeLLM.temperature }}</span>
            </div>
            <div class="llm-row">
              <span class="llm-label">配置数</span>
              <span class="llm-value mono">{{ llmStore.list.length }}</span>
            </div>
          </div>
          <div v-else class="llm-empty">
            <p class="muted">还没有激活的 LLM 配置</p>
            <el-button type="primary" size="small" @click="$router.push('/llm-configs')">
              <el-icon><Setting /></el-icon><span>去配置</span>
            </el-button>
          </div>
        </CyberCard>
      </el-col>
    </el-row>

    <!-- ========================================================
         区块 4：最近日志 + 快捷入口
         ======================================================== -->
    <el-row :gutter="14" class="dual-row">
      <el-col :span="14">
        <CyberCard accent="cyan" class="full-card">
          <template #header>
            <span class="cyber-card__title">▸ 最近生成日志</span>
          </template>
          <template #extra>
            <el-link type="primary" :underline="false" @click="$router.push('/logs')">
              全部 →
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
              <template #default="{ row }">
                <span class="mono">#{{ row.knowledge_point_id ?? '-' }}</span>
              </template>
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
              <template #default="{ row }">
                <span class="mono">{{ formatDuration(row.latency_ms) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </CyberCard>
      </el-col>

      <el-col :span="10">
        <CyberCard accent="green" class="full-card">
          <template #header>
            <span class="cyber-card__title">▸ 快捷入口</span>
          </template>
          <div class="shortcuts">
            <el-button
              type="primary"
              size="large"
              @click="$router.push('/learning-path')"
            >
              <el-icon><Reading /></el-icon><span>学习路线</span>
            </el-button>
            <el-button
              type="success"
              size="large"
              @click="$router.push('/practice')"
            >
              <el-icon><Aim /></el-icon><span>开始练习</span>
            </el-button>
            <el-button size="large" @click="$router.push('/generate')">
              <el-icon><MagicStick /></el-icon><span>生成题目</span>
            </el-button>
            <el-button size="large" @click="$router.push('/review')">
              <el-icon><StarFilled /></el-icon><span>复习清单</span>
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
  Reading,
  Aim,
  Setting,
  StarFilled,
} from '@element-plus/icons-vue'
import {
  learningPathApi,
  exerciseApi,
  generationApi,
} from '@/api'
import { useLLMConfigStore } from '@/stores/llmConfig'
import { useLanguageStore } from '@/stores/language'
import {
  LANGUAGE_LABEL,
  LANGUAGE_OPTIONS,
  LANGUAGE_COLOR,
  MASTERY_LABEL,
  MASTERY_COLOR,
  MASTERY_ICON,
  type Language,
  type Mastery,
} from '@/types/common'
import type { MasteryCounts } from '@/types/knowledge_point'
import { formatDuration } from '@/utils/format'
import type { GenerationLog } from '@/types/generation'
import DifficultyTag from '@/components/DifficultyTag.vue'
import QuestionTypeTag from '@/components/QuestionTypeTag.vue'
import CyberCard from '@/components/CyberCard.vue'
import StatNumber from '@/components/StatNumber.vue'

const llmStore = useLLMConfigStore()
const langStore = useLanguageStore()

const activeLLM = computed(() => llmStore.active)
const langLabel = computed(
  () => LANGUAGE_LABEL[langStore.current as Language] ?? langStore.current,
)

// ===== Per-language counts (for the language picker buttons) =====
interface LangCount { kps: number; exercises: number }
const perLangCounts = reactive<Record<string, LangCount>>({})

async function loadPerLangCounts() {
  await Promise.all(
    LANGUAGE_OPTIONS.map(async (opt) => {
      const lang = opt.value
      try {
        const [kps, exs] = await Promise.all([
          learningPathApi.listKPs(undefined, lang),
          exerciseApi.list({ language: lang, page: 1, size: 1 }),
        ])
        perLangCounts[lang] = { kps: kps.length, exercises: exs.total }
      } catch {
        perLangCounts[lang] = { kps: 0, exercises: 0 }
      }
    }),
  )
}

// ===== Current-language stats =====
const stats = reactive({
  chapters: 0,
  kps: 0,
  exercises: 0,
})
const masteryCounts = ref<MasteryCounts>({
  not_started: 0,
  learning: 0,
  mastered: 0,
  unknown: 0,
})

async function loadStats() {
  const [chapters, kps, exercises, mc] = await Promise.all([
    learningPathApi.listChapters(langStore.current),
    learningPathApi.listKPs(undefined, langStore.current),
    exerciseApi.list({ language: langStore.current, page: 1, size: 1 }),
    learningPathApi.masteryCounts(langStore.current),
  ])
  stats.chapters = chapters.length
  stats.kps = kps.length
  stats.exercises = exercises.total
  masteryCounts.value = mc
}

// ===== Mastery progress bars =====
const masteryRows = computed(() =>
  (['mastered', 'learning', 'not_started', 'unknown'] as Mastery[]).map((k) => {
    const count = masteryCounts.value[k]
    const total = stats.kps || 1
    return {
      key: k,
      label: MASTERY_LABEL[k],
      icon: MASTERY_ICON[k],
      color: MASTERY_COLOR[k],
      count,
      pct: Math.round((count / total) * 100),
    }
  }),
)

const masteryProgressText = computed(() => {
  if (stats.kps === 0) return '—'
  const learnt = masteryCounts.value.mastered
  return `${learnt}/${stats.kps}`
})

const masteryProgressHint = computed(() => {
  if (stats.kps === 0) return ''
  const pct = Math.round((masteryCounts.value.mastered / stats.kps) * 100)
  return `${pct}% 已掌握`
})

// ===== Recent logs =====
const recentLogs = ref<GenerationLog[]>([])
const loadingLogs = ref(false)

async function loadLogs() {
  loadingLogs.value = true
  try {
    recentLogs.value = await generationApi.listLogs(1, 6)
  } finally {
    loadingLogs.value = false
  }
}

function onPickLanguage(lang: Language) {
  langStore.setLanguage(lang)
}

watch(() => langStore.current, () => {
  loadStats()
})

onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadLogs(),
    loadPerLangCounts(),
    llmStore.refresh(true),
  ])
})
</script>

<style scoped>
.header-meta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}
.meta-key {
  color: var(--neon-cyan);
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
}

.muted {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.small {
  font-size: 11px;
}

/* ===== Language picker ===== */
.lang-card {
  margin-bottom: 14px;
}

.lang-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.lang-btn {
  position: relative;
  background: rgba(15, 22, 40, 0.5);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.lang-btn:hover {
  border-color: var(--lang-color);
  box-shadow: 0 0 14px var(--lang-color);
  transform: translateY(-2px);
}

.lang-btn.is-active {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--lang-color) 18%, transparent) 0%,
    color-mix(in srgb, var(--lang-color) 4%, transparent) 100%
  );
  border-color: var(--lang-color);
  box-shadow: 0 0 18px var(--lang-color), inset 0 0 12px var(--lang-color);
}

.lang-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--lang-color);
  text-shadow: 0 0 8px var(--lang-color);
  letter-spacing: 0.5px;
}

.lang-counts {
  font-size: 12px;
  color: var(--el-text-color-regular);
  display: flex;
  align-items: center;
  gap: 4px;
}

.lang-counts .dot {
  opacity: 0.5;
}

.lang-check {
  position: absolute;
  top: 8px;
  right: 10px;
  font-size: 14px;
  color: var(--lang-color);
  font-weight: 700;
}

/* ===== Stats row ===== */
.stats-row,
.dual-row {
  margin-bottom: 14px;
}

.full-card {
  height: 100%;
}

/* ===== Mastery distribution ===== */
.mastery-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mastery-row {
  display: grid;
  grid-template-columns: 28px 80px 1fr 60px;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(15, 22, 40, 0.4);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: all 0.2s ease;
}

.mastery-row:hover {
  background: rgba(0, 212, 255, 0.06);
  border-color: var(--neon-cyan);
}

.mr-icon {
  font-size: 16px;
  text-align: center;
}

.mr-label {
  color: var(--el-text-color-primary);
  font-size: 13px;
  font-weight: 500;
}

.mr-bar {
  height: 8px;
  background: rgba(15, 22, 40, 0.7);
  border-radius: 4px;
  overflow: hidden;
}

.mr-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}

.mr-num {
  text-align: right;
  font-weight: 700;
  font-size: 14px;
}

/* ===== LLM block ===== */
.llm-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.llm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px dashed var(--el-border-color-lighter);
  font-size: 13px;
}

.llm-row:last-child {
  border-bottom: none;
}

.llm-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  letter-spacing: 0.4px;
}

.llm-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
  text-align: right;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.llm-value.active {
  color: var(--neon-green);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.llm-value .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--neon-green);
  box-shadow: 0 0 8px var(--neon-green);
}

.llm-empty {
  text-align: center;
  padding: 16px 0;
}

@keyframes pulse-anim {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.pulse {
  animation: pulse-anim 1.6s ease-in-out infinite;
}

/* ===== Shortcuts ===== */
.shortcuts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.shortcuts .el-button {
  margin-left: 0 !important;
  width: 100%;
  height: 48px;
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
