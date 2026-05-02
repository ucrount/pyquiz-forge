<template>
  <div class="page">
    <div class="page-header"><h2>导出题库</h2></div>

    <el-card shadow="never" class="export-card">
      <el-form :model="filters" label-width="80px">
        <el-form-item label="知识点">
          <KnowledgePointPicker
            v-model="filters.knowledge_point_id"
            placeholder="（全部）"
          />
        </el-form-item>
        <el-form-item label="难度">
          <el-select
            v-model="filters.difficulty"
            clearable
            placeholder="全部"
            style="width: 200px"
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
            style="width: 200px"
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
            controls-position="right"
            placeholder="（不限）"
            style="width: 200px"
          />
          <span class="muted hint-tip">仅导出综合分 ≥ 此值的题目</span>
        </el-form-item>
        <el-divider />
        <p class="match-info">
          <span>当前条件下匹配 </span>
          <strong>{{ matchCount }}</strong>
          <span> 道题。</span>
          <el-link type="primary" @click="updateMatchCount">刷新</el-link>
        </p>
        <el-form-item>
          <el-button
            type="primary"
            :loading="downloading === 'json'"
            :disabled="!matchCount"
            @click="onExport('json')"
          >
            <el-icon><Download /></el-icon><span>下载 JSON</span>
          </el-button>
          <el-button
            type="success"
            :loading="downloading === 'markdown'"
            :disabled="!matchCount"
            @click="onExport('markdown')"
          >
            <el-icon><Document /></el-icon><span>下载 Markdown</span>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { Download, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { exerciseApi, exportApi } from '@/api'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  type Difficulty,
  type QuestionType,
} from '@/types/common'
import KnowledgePointPicker from '@/components/KnowledgePointPicker.vue'

interface Filters {
  knowledge_point_id: number | null
  difficulty: Difficulty | null
  question_type: QuestionType | null
  min_score: number | null
}

const filters = reactive<Filters>({
  knowledge_point_id: null,
  difficulty: null,
  question_type: null,
  min_score: null,
})

const matchCount = ref(0)
const downloading = ref<'json' | 'markdown' | ''>('')

async function updateMatchCount() {
  const r = await exerciseApi.list({
    knowledge_point_id: filters.knowledge_point_id ?? undefined,
    difficulty: filters.difficulty ?? undefined,
    question_type: filters.question_type ?? undefined,
    min_score: filters.min_score ?? undefined,
    page: 1,
    size: 1,
  })
  matchCount.value = r.total
}

async function onExport(format: 'json' | 'markdown') {
  if (!matchCount.value) {
    ElMessage.warning('当前没有可导出的题目')
    return
  }
  downloading.value = format
  try {
    const params = {
      knowledge_point_id: filters.knowledge_point_id ?? undefined,
      difficulty: filters.difficulty ?? undefined,
      question_type: filters.question_type ?? undefined,
      min_score: filters.min_score ?? undefined,
    }
    if (format === 'json') {
      await exportApi.json(params)
    } else {
      await exportApi.markdown(params)
    }
    ElMessage.success('已开始下载')
  } finally {
    downloading.value = ''
  }
}

watch(filters, updateMatchCount, { deep: true })
onMounted(updateMatchCount)
</script>

<style scoped>
.export-card {
  max-width: 720px;
}

.match-info {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
  margin: 0 0 16px;
}

.muted {
  color: #909399;
  font-size: 13px;
}

.hint-tip {
  margin-left: 12px;
}
</style>
