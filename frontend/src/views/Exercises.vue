<template>
  <div class="page exercises-page">
    <el-row :gutter="16">
      <!-- 左侧：树形分类 -->
      <el-col :span="7">
        <CyberCard accent="cyan" class="tree-card">
          <template #header>
            <span class="cyber-card__title">▸ 分类</span>
          </template>
          <template #extra>
            <el-link type="primary" :underline="false" @click="loadAll">
              <el-icon><Refresh /></el-icon>
            </el-link>
          </template>

          <el-input
            v-model="treeFilter"
            placeholder="搜索章节 / 知识点"
            clearable
            size="small"
            class="tree-search"
          />

          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="key"
            :filter-node-method="filterTreeNode"
            :expand-on-click-node="false"
            :default-expanded-keys="defaultExpandedKeys"
            highlight-current
            empty-text="暂无数据"
            @node-click="onTreeNodeClick"
            v-loading="treeLoading"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <span class="tree-label">
                  <el-tag
                    v-if="data.type === 'all'"
                    size="small"
                    type="info"
                    effect="plain"
                  >
                    *
                  </el-tag>
                  <el-tag
                    v-else-if="data.type === 'chapter'"
                    size="small"
                    type="primary"
                    effect="plain"
                  >
                    {{ data.code }}
                  </el-tag>
                  <el-tag v-else size="small" effect="plain">
                    {{ data.code }}
                  </el-tag>
                  <span class="tree-text">{{ node.label }}</span>
                </span>
                <span
                  class="tree-count mono"
                  :class="{ 'tree-count--zero': data.count === 0 }"
                >
                  {{ data.count }}
                </span>
              </span>
            </template>
          </el-tree>
        </CyberCard>
      </el-col>

      <!-- 右侧：题目列表 -->
      <el-col :span="17">
        <CyberCard accent="purple">
          <template #header>
            <span class="cyber-card__title">
              ▸ {{ currentNodeLabel }}
            </span>
          </template>
          <template #extra>
            <div class="list-card-extra">
              <span class="filter-summary mono">
                {{ total }} 题
              </span>
              <el-button size="small" @click="$router.push('/practice')">
                <el-icon><Aim /></el-icon><span>开始练习</span>
              </el-button>
              <el-button size="small" type="primary" @click="$router.push('/generate')">
                <el-icon><MagicStick /></el-icon><span>生成新题</span>
              </el-button>
            </div>
          </template>

          <!-- 筛选器 -->
          <el-form :inline="true" :model="filters" @submit.prevent class="inline-filters">
            <el-form-item label="难度">
              <el-select
                v-model="filters.difficulty"
                clearable
                placeholder="全部"
                size="small"
                style="width: 110px"
              >
                <el-option
                  v-for="opt in DIFFICULTY_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="题型">
              <el-select
                v-model="filters.question_type"
                clearable
                placeholder="全部"
                size="small"
                style="width: 130px"
              >
                <el-option
                  v-for="opt in QUESTION_TYPE_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="最低分">
              <el-input-number
                v-model="filters.min_score"
                :min="0"
                :max="10"
                :step="0.5"
                :precision="1"
                size="small"
                controls-position="right"
                style="width: 110px"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="small" @click="onSearch">查询</el-button>
              <el-button size="small" @click="onResetFilters">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 批量操作 -->
          <div class="bulk-bar" v-if="selectedIds.length">
            <span class="bulk-count">已选 {{ selectedIds.length }} 项</span>
            <el-button size="small" type="primary" :loading="batchScoring" @click="onBulkScore">
              批量评分
            </el-button>
            <el-button size="small" type="danger" @click="onBulkDelete">
              批量删除
            </el-button>
          </div>

          <!-- 表格 -->
          <el-table
            :data="items"
            v-loading="loading"
            stripe
            empty-text="此分类下暂无题目"
            @selection-change="onSelectionChange"
            @row-click="onRowClick"
          >
            <el-table-column type="selection" width="40" />
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
            <el-table-column label="难度" width="80">
              <template #default="{ row }"><DifficultyTag :value="row.difficulty" /></template>
            </el-table-column>
            <el-table-column label="题型" width="100">
              <template #default="{ row }"><QuestionTypeTag :value="row.question_type" /></template>
            </el-table-column>
            <el-table-column label="评分" width="90" align="center">
              <template #default="{ row }">
                <ScoreBadge :value="row.score_overall" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="{ row }">
                <el-button size="small" link type="primary" @click.stop="openDetail(row.id, false)">详情</el-button>
                <el-button size="small" link type="primary" @click.stop="openDetail(row.id, true)">编辑</el-button>
                <el-button
                  size="small"
                  link
                  type="success"
                  :loading="scoringIds.has(row.id)"
                  @click.stop="onScore(row)"
                >评分</el-button>
                <el-button size="small" link type="danger" @click.stop="onDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            class="pagination"
            v-model:current-page="filters.page"
            v-model:page-size="filters.size"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="load"
            @size-change="load"
            background
          />
        </CyberCard>
      </el-col>
    </el-row>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      size="65%"
      :destroy-on-close="true"
      :close-on-click-modal="!editMode"
    >
      <template #header>
        <div class="drawer-header">
          <span class="drawer-title">{{ drawerTitle }}</span>
          <div v-if="detailExercise && !editMode" class="drawer-actions">
            <el-button
              size="small"
              type="success"
              :loading="detailScoring"
              @click="onScoreCurrent"
            >
              <el-icon><StarFilled /></el-icon>
              <span>{{ detailExercise.score_overall === null ? '评分' : '重新评分' }}</span>
            </el-button>
            <el-button size="small" type="primary" @click="editMode = true">
              <el-icon><Edit /></el-icon><span>编辑</span>
            </el-button>
          </div>
        </div>
      </template>
      <ExerciseEditor
        v-if="detailExercise && editMode"
        :exercise="detailExercise"
        @saved="onSaved"
        @cancel="editMode = false"
      />
      <ExerciseDetail v-else :exercise="detailExercise" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick,
  Aim,
  Edit,
  StarFilled,
  Refresh,
} from '@element-plus/icons-vue'
import {
  exerciseApi,
  generationApi,
  scoringApi,
  learningPathApi,
} from '@/api'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  type Difficulty,
  type QuestionType,
} from '@/types/common'
import type { Exercise, ExerciseListItem } from '@/types/exercise'
import type { ChapterWithKnowledgePoints } from '@/types/chapter'
import { useLanguageStore } from '@/stores/language'
import DifficultyTag from '@/components/DifficultyTag.vue'
import QuestionTypeTag from '@/components/QuestionTypeTag.vue'
import ScoreBadge from '@/components/ScoreBadge.vue'
import ExerciseDetail from '@/components/ExerciseDetail.vue'
import ExerciseEditor from '@/components/ExerciseEditor.vue'
import CyberCard from '@/components/CyberCard.vue'

const langStore = useLanguageStore()

interface TreeNode {
  key: string
  label: string
  code: string
  count: number
  type: 'all' | 'chapter' | 'kp'
  raw: any
  children?: TreeNode[]
}

interface Filters {
  // 树过滤（互斥两选一）
  knowledge_point_id: number | null
  chapter_id: number | null
  // 通用筛选
  difficulty: Difficulty | null
  question_type: QuestionType | null
  min_score: number | null
  page: number
  size: number
}

const filters = reactive<Filters>({
  knowledge_point_id: null,
  chapter_id: null,
  difficulty: null,
  question_type: null,
  min_score: null,
  page: 1,
  size: 20,
})

const treeFilter = ref('')
const treeRef = ref()
const treeLoading = ref(false)
const tree = ref<ChapterWithKnowledgePoints[]>([])
const exerciseCounts = ref<{
  total: number
  byChapter: Record<number, number>
  byKP: Record<number, number>
}>({ total: 0, byChapter: {}, byKP: {} })

const items = ref<ExerciseListItem[]>([])
const total = ref(0)
const loading = ref(false)
const selectedIds = ref<number[]>([])
const scoringIds = ref(new Set<number>())
const batchScoring = ref(false)
const detailScoring = ref(false)

const detailVisible = ref(false)
const detailExercise = ref<Exercise | null>(null)
const editMode = ref(false)

const treeProps = { children: 'children', label: 'label' }

const treeData = computed<TreeNode[]>(() => {
  const all: TreeNode = {
    key: 'all',
    label: '全部',
    code: '*',
    count: exerciseCounts.value.total,
    type: 'all',
    raw: null,
  }
  const chapters: TreeNode[] = tree.value.map((c) => ({
    key: `c-${c.id}`,
    label: c.title,
    code: c.code,
    count: exerciseCounts.value.byChapter[c.id] || 0,
    type: 'chapter',
    raw: c,
    children: (c.knowledge_points ?? []).map((kp) => ({
      key: `k-${kp.id}`,
      label: kp.title,
      code: kp.code,
      count: exerciseCounts.value.byKP[kp.id] || 0,
      type: 'kp',
      raw: kp,
    })),
  }))
  return [all, ...chapters]
})

const defaultExpandedKeys = computed(() => {
  // 默认展开第一个章节
  if (tree.value.length > 0) {
    return ['all', `c-${tree.value[0].id}`]
  }
  return ['all']
})

const currentNodeLabel = computed(() => {
  if (filters.knowledge_point_id) {
    for (const c of tree.value) {
      const kp = (c.knowledge_points ?? []).find(
        (k) => k.id === filters.knowledge_point_id,
      )
      if (kp) return `${kp.code} · ${kp.title}`
    }
  }
  if (filters.chapter_id) {
    const c = tree.value.find((c) => c.id === filters.chapter_id)
    if (c) return `${c.code} · ${c.title}`
  }
  return '全部题目'
})

const drawerTitle = computed(() => {
  if (!detailExercise.value) return editMode.value ? '编辑题目' : '题目详情'
  return editMode.value
    ? `编辑题目 #${detailExercise.value.id}`
    : `题目详情 #${detailExercise.value.id}`
})

watch(treeFilter, (v) => treeRef.value?.filter(v))

watch(() => langStore.current, () => {
  filters.knowledge_point_id = null
  filters.chapter_id = null
  filters.page = 1
  loadAll()
})

function filterTreeNode(value: string, data: any) {
  if (!value) return true
  return (
    String(data.label || '').includes(value) ||
    String(data.code || '').includes(value)
  )
}

function onTreeNodeClick(data: TreeNode) {
  if (data.type === 'all') {
    filters.knowledge_point_id = null
    filters.chapter_id = null
  } else if (data.type === 'chapter') {
    filters.knowledge_point_id = null
    filters.chapter_id = data.raw.id
  } else if (data.type === 'kp') {
    filters.knowledge_point_id = data.raw.id
    filters.chapter_id = null
  }
  filters.page = 1
  load()
}

async function load() {
  loading.value = true
  try {
    const r = await exerciseApi.list({
      knowledge_point_id: filters.knowledge_point_id ?? undefined,
      chapter_id: filters.chapter_id ?? undefined,
      language: langStore.current,
      difficulty: filters.difficulty ?? undefined,
      question_type: filters.question_type ?? undefined,
      min_score: filters.min_score ?? undefined,
      page: filters.page,
      size: filters.size,
    })
    items.value = r.items
    total.value = r.total
  } finally {
    loading.value = false
  }
}

async function loadTree() {
  treeLoading.value = true
  try {
    tree.value = await learningPathApi.tree(langStore.current)
  } finally {
    treeLoading.value = false
  }
}

async function loadCounts() {
  // 一次性把所有题目数取出来，然后前端聚合
  const r = await exerciseApi.list({
    language: langStore.current,
    page: 1,
    size: 1,
  })
  // 取所有题目的 KP 分布——通过分页拉一次大列表
  // 简化：拉 200 道得到分布近似（题库不会爆这数）
  const big = await exerciseApi.list({
    language: langStore.current,
    page: 1,
    size: 200,
  })
  const byKP: Record<number, number> = {}
  for (const it of big.items) {
    byKP[it.knowledge_point_id] = (byKP[it.knowledge_point_id] || 0) + 1
  }
  // chapter 维度：聚合 KP → chapter
  const byChapter: Record<number, number> = {}
  for (const c of tree.value) {
    let sum = 0
    for (const kp of c.knowledge_points ?? []) {
      sum += byKP[kp.id] || 0
    }
    byChapter[c.id] = sum
  }
  exerciseCounts.value = { total: r.total, byChapter, byKP }
}

async function loadAll() {
  await loadTree()
  await Promise.all([load(), loadCounts()])
  await nextTick()
}

function onSearch() {
  filters.page = 1
  load()
}

function onResetFilters() {
  filters.difficulty = null
  filters.question_type = null
  filters.min_score = null
  filters.page = 1
  load()
}

function onSelectionChange(rows: ExerciseListItem[]) {
  selectedIds.value = rows.map((r) => r.id)
}

function onRowClick(row: ExerciseListItem) {
  openDetail(row.id, false)
}

async function openDetail(id: number, edit = false) {
  detailExercise.value = null
  editMode.value = edit
  detailVisible.value = true
  detailExercise.value = await exerciseApi.get(id)
}

function onSaved(updated: Exercise) {
  detailExercise.value = updated
  editMode.value = false
  loadAll()
}

async function onDelete(row: ExerciseListItem) {
  await ElMessageBox.confirm(
    `确定删除题目 #${row.id}「${row.title}」？`,
    '删除确认',
    { type: 'warning' },
  )
  await exerciseApi.remove(row.id)
  ElMessage.success('已删除')
  loadAll()
}

async function onBulkDelete() {
  if (!selectedIds.value.length) return
  await ElMessageBox.confirm(
    `确定删除选中的 ${selectedIds.value.length} 道题？`,
    '批量删除',
    { type: 'warning' },
  )
  const r = await exerciseApi.bulkDelete(selectedIds.value)
  ElMessage.success(`已删除 ${r.deleted} 项`)
  selectedIds.value = []
  loadAll()
}

async function onScore(row: ExerciseListItem) {
  scoringIds.value.add(row.id)
  try {
    const updated = await scoringApi.score(row.id)
    const idx = items.value.findIndex((i) => i.id === row.id)
    if (idx >= 0) {
      items.value[idx] = { ...items.value[idx], score_overall: updated.score_overall }
    }
    ElMessage.success(`已评分：${updated.score_overall?.toFixed(1) ?? '-'}`)
  } finally {
    scoringIds.value.delete(row.id)
  }
}

async function onBulkScore() {
  if (!selectedIds.value.length) return
  await ElMessageBox.confirm(
    `对选中的 ${selectedIds.value.length} 道题逐题评分？`,
    '批量评分',
    { type: 'info' },
  )
  batchScoring.value = true
  try {
    const r = await scoringApi.scoreBatch(selectedIds.value)
    ElMessage.success(`成功 ${r.succeeded.length} / 失败 ${r.failed.length}`)
    load()
  } finally {
    batchScoring.value = false
  }
}

async function onScoreCurrent() {
  if (!detailExercise.value) return
  detailScoring.value = true
  try {
    const updated = await scoringApi.score(detailExercise.value.id)
    detailExercise.value = updated
    load()
    ElMessage.success(`已评分：${updated.score_overall?.toFixed(1) ?? '-'}`)
  } finally {
    detailScoring.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.exercises-page {
  min-height: calc(100vh - 64px);
}

.list-card-extra {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tree-card {
  height: calc(100vh - 130px);
  display: flex;
  flex-direction: column;
}

.tree-card :deep(.cyber-card__body) {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.tree-search {
  margin-bottom: 10px;
}

.tree-card :deep(.el-tree) {
  background: transparent;
  flex: 1;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
  font-size: 13px;
}

.tree-label {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.tree-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-count {
  color: var(--neon-cyan);
  font-size: 12px;
  font-weight: 600;
  min-width: 24px;
  text-align: right;
}

.tree-count--zero {
  color: var(--el-text-color-secondary);
}

.inline-filters {
  margin-bottom: 10px;
}

.inline-filters :deep(.el-form-item) {
  margin-bottom: 6px;
}

.bulk-bar {
  margin-bottom: 10px;
  padding: 8px 12px;
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.bulk-count {
  color: var(--neon-cyan);
  font-size: 13px;
  font-weight: 600;
}

.filter-summary {
  color: var(--neon-cyan);
  font-size: 13px;
}

.pagination {
  margin-top: 12px;
  justify-content: flex-end;
  display: flex;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 24px;
}

.drawer-actions {
  display: flex;
  gap: 8px;
}

.drawer-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
</style>
