<template>
  <div class="page">
    <div class="page-header">
      <h2>题库管理</h2>
      <div>
        <el-button @click="$router.push('/generate')">
          <el-icon><MagicStick /></el-icon><span>去生成新题</span>
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="filters" @submit.prevent>
        <el-form-item label="知识点">
          <KnowledgePointPicker
            v-model="filters.knowledge_point_id"
            placeholder="（全部）"
            style="width: 320px"
          />
        </el-form-item>
        <el-form-item label="难度">
          <el-select
            v-model="filters.difficulty"
            clearable
            placeholder="全部"
            style="width: 120px"
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
            style="width: 140px"
          >
            <el-option
              v-for="opt in QUESTION_TYPE_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSearch">查询</el-button>
          <el-button @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card shadow="never">
      <div class="bulk-bar" v-if="selectedIds.length">
        <span>已选 {{ selectedIds.length }} 项</span>
        <el-button size="small" type="danger" @click="onBulkDelete">
          批量删除
        </el-button>
      </div>

      <el-table
        :data="items"
        v-loading="loading"
        stripe
        empty-text="暂无题目"
        @selection-change="onSelectionChange"
        @row-click="onRowClick"
      >
        <el-table-column type="selection" width="40" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
        <el-table-column label="难度" width="90">
          <template #default="{ row }"><DifficultyTag :value="row.difficulty" /></template>
        </el-table-column>
        <el-table-column label="题型" width="110">
          <template #default="{ row }"><QuestionTypeTag :value="row.question_type" /></template>
        </el-table-column>
        <el-table-column label="知识点" width="100">
          <template #default="{ row }">#{{ row.knowledge_point_id }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click.stop="openDetail(row.id)">
              详情
            </el-button>
            <el-button size="small" link @click.stop="onRegenerate(row)">
              重新生成
            </el-button>
            <el-button size="small" link type="danger" @click.stop="onDelete(row)">
              删除
            </el-button>
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
    </el-card>

    <!-- Detail drawer -->
    <el-drawer
      v-model="detailVisible"
      size="60%"
      title="题目详情"
      :destroy-on-close="true"
    >
      <ExerciseDetail :exercise="detailExercise" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { exerciseApi, generationApi } from '@/api'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  type Difficulty,
  type QuestionType,
} from '@/types/common'
import type { Exercise, ExerciseListItem } from '@/types/exercise'
import KnowledgePointPicker from '@/components/KnowledgePointPicker.vue'
import DifficultyTag from '@/components/DifficultyTag.vue'
import QuestionTypeTag from '@/components/QuestionTypeTag.vue'
import ExerciseDetail from '@/components/ExerciseDetail.vue'

interface Filters {
  knowledge_point_id: number | null
  difficulty: Difficulty | null
  question_type: QuestionType | null
  page: number
  size: number
}

const filters = reactive<Filters>({
  knowledge_point_id: null,
  difficulty: null,
  question_type: null,
  page: 1,
  size: 20,
})

const items = ref<ExerciseListItem[]>([])
const total = ref(0)
const loading = ref(false)
const selectedIds = ref<number[]>([])

const detailVisible = ref(false)
const detailExercise = ref<Exercise | null>(null)

async function load() {
  loading.value = true
  try {
    const r = await exerciseApi.list({
      knowledge_point_id: filters.knowledge_point_id ?? undefined,
      difficulty: filters.difficulty ?? undefined,
      question_type: filters.question_type ?? undefined,
      page: filters.page,
      size: filters.size,
    })
    items.value = r.items
    total.value = r.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  filters.page = 1
  load()
}

function onReset() {
  filters.knowledge_point_id = null
  filters.difficulty = null
  filters.question_type = null
  filters.page = 1
  load()
}

function onSelectionChange(rows: ExerciseListItem[]) {
  selectedIds.value = rows.map((r) => r.id)
}

function onRowClick(row: ExerciseListItem) {
  openDetail(row.id)
}

async function openDetail(id: number) {
  detailExercise.value = null
  detailVisible.value = true
  detailExercise.value = await exerciseApi.get(id)
}

async function onDelete(row: ExerciseListItem) {
  await ElMessageBox.confirm(
    `确定删除题目 #${row.id}「${row.title}」？`,
    '删除确认',
    { type: 'warning' },
  )
  await exerciseApi.remove(row.id)
  ElMessage.success('已删除')
  load()
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
  load()
}

async function onRegenerate(row: ExerciseListItem) {
  ElMessage.info('重新生成中，请稍候...')
  try {
    await generationApi.regenerate(row.id, { mode: 'new' })
    ElMessage.success('重新生成完成')
    load()
  } catch {
    // interceptor already toasted
  }
}

onMounted(load)
</script>

<style scoped>
.filter-card {
  margin-bottom: 16px;
}

.bulk-bar {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #ecf5ff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
  display: flex;
}
</style>
