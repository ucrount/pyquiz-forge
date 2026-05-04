<template>
  <div class="page review-page">
    <div class="page-header">
      <h2>REVIEW QUEUE</h2>
      <span class="header-meta mono">{{ langStore.current.toUpperCase() }}</span>
    </div>

    <!-- Stats cards -->
    <el-row :gutter="14" class="stats-row">
      <el-col :span="6">
        <CyberCard accent="cyan">
          <StatNumber label="未开始" :value="counts.not_started" accent="cyan" />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="cyan">
          <StatNumber label="📖 学习中" :value="counts.learning" accent="cyan" />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="green">
          <StatNumber label="✓ 已掌握" :value="counts.mastered" accent="green" />
        </CyberCard>
      </el-col>
      <el-col :span="6">
        <CyberCard accent="pink">
          <StatNumber label="❓ 不懂" :value="counts.unknown" accent="pink" />
        </CyberCard>
      </el-col>
    </el-row>

    <CyberCard accent="purple" class="list-card">
      <template #header>
        <el-tabs v-model="activeTab" class="review-tabs" @tab-change="reload">
          <el-tab-pane name="unknown" :label="`❓ 不懂 (${counts.unknown})`" />
          <el-tab-pane name="learning" :label="`📖 学习中 (${counts.learning})`" />
          <el-tab-pane name="mastered" :label="`✓ 已掌握 (${counts.mastered})`" />
          <el-tab-pane name="not_started" :label="`未开始 (${counts.not_started})`" />
          <el-tab-pane name="all" label="全部" />
        </el-tabs>
      </template>

      <el-table
        :data="kps"
        v-loading="loading"
        empty-text="此分类下暂无知识点"
        size="small"
        @row-click="(row) => onGoLearn(row)"
        style="cursor: pointer"
      >
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <MasteryTag :value="row.mastery" />
          </template>
        </el-table-column>
        <el-table-column prop="code" label="编号" width="100">
          <template #default="{ row }">
            <span class="mono">{{ row.code }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="知识点" min-width="200" show-overflow-tooltip />
        <el-table-column label="备注" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.mastery_note" class="muted">{{ row.mastery_note }}</span>
            <span v-else class="muted small">—</span>
          </template>
        </el-table-column>
        <el-table-column label="标记时间" width="160">
          <template #default="{ row }">
            <span class="muted small mono">{{ formatDateTime(row.mastery_updated_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click.stop="onGoLearn(row)">
              去学习
            </el-button>
            <el-button size="small" link @click.stop="onPracticeKp(row)">
              出题
            </el-button>
            <el-button size="small" link type="success" @click.stop="onMarkMastered(row)">
              ✓ 掌握
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </CyberCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { learningPathApi } from '@/api'
import { useLanguageStore } from '@/stores/language'
import type { Mastery } from '@/types/common'
import type {
  KnowledgePoint,
  MasteryCounts,
} from '@/types/knowledge_point'
import { formatDateTime } from '@/utils/format'
import CyberCard from '@/components/CyberCard.vue'
import StatNumber from '@/components/StatNumber.vue'
import MasteryTag from '@/components/MasteryTag.vue'

const router = useRouter()
const langStore = useLanguageStore()

const activeTab = ref<Mastery | 'all'>('unknown')
const counts = ref<MasteryCounts>({
  not_started: 0,
  learning: 0,
  mastered: 0,
  unknown: 0,
})
const kps = ref<KnowledgePoint[]>([])
const loading = ref(false)

async function loadCounts() {
  counts.value = await learningPathApi.masteryCounts(langStore.current)
}

async function loadKps() {
  loading.value = true
  try {
    const masteryFilter =
      activeTab.value === 'all' ? undefined : [activeTab.value as Mastery]
    kps.value = await learningPathApi.listKPs(undefined, langStore.current, masteryFilter)
    // Sort by mastery_updated_at desc (most recent first)
    kps.value.sort((a, b) => {
      const at = a.mastery_updated_at ? Date.parse(a.mastery_updated_at) : 0
      const bt = b.mastery_updated_at ? Date.parse(b.mastery_updated_at) : 0
      return bt - at
    })
  } finally {
    loading.value = false
  }
}

async function reload() {
  await Promise.all([loadCounts(), loadKps()])
}

watch(() => langStore.current, reload)

function onGoLearn(kp: KnowledgePoint) {
  router.push({ path: '/learning-path', query: { kp: kp.id } })
}

function onPracticeKp(kp: KnowledgePoint) {
  // Navigate to /generate prefilled with this KP
  router.push({ path: '/generate', query: { kp: kp.id } })
}

async function onMarkMastered(kp: KnowledgePoint) {
  await learningPathApi.setMastery(kp.id, 'mastered')
  ElMessage.success(`已标记「${kp.title}」为掌握`)
  reload()
}

onMounted(reload)
</script>

<style scoped>
.review-page {
  min-height: calc(100vh - 64px);
}

.header-meta {
  font-size: 12px;
  letter-spacing: 1px;
  color: var(--neon-cyan);
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
}

.stats-row {
  margin-bottom: 16px;
}

.list-card :deep(.cyber-card__body) {
  padding-top: 4px;
}

.review-tabs {
  margin: -8px 0;
}

.review-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.muted {
  color: var(--el-text-color-secondary);
}

.small {
  font-size: 12px;
}
</style>
