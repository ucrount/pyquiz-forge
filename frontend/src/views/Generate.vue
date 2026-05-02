<template>
  <div class="page">
    <div class="page-header">
      <h2>题目生成</h2>
      <div>
        <el-button @click="batchVisible = true">
          <el-icon><Operation /></el-icon><span>批量生成</span>
        </el-button>
      </div>
    </div>

    <!-- Form -->
    <el-card shadow="never" class="form-card">
      <el-form :model="form" label-width="100px" label-position="right">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="知识点" required>
              <KnowledgePointPicker v-model="form.knowledge_point_id" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="LLM 配置">
              <el-select
                v-model="form.llm_config_id"
                clearable
                placeholder="使用当前激活的配置"
                style="width: 100%"
              >
                <el-option
                  v-for="cfg in llmStore.list"
                  :key="cfg.id"
                  :label="`${cfg.name} (${cfg.provider}/${cfg.model})${cfg.is_active ? ' ★' : ''}`"
                  :value="cfg.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="难度" required>
          <el-radio-group v-model="form.difficulty">
            <el-radio-button
              v-for="opt in DIFFICULTY_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="题型" required>
          <el-radio-group v-model="form.question_type">
            <el-radio-button
              v-for="opt in QUESTION_TYPE_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="!canGenerate"
            @click="onGenerate"
          >
            <el-icon><MagicStick /></el-icon>
            <span>{{ generating ? '生成中...' : '生成题目' }}</span>
          </el-button>
          <span v-if="!llmStore.active" class="warn-hint">
            请先在「大模型配置」页激活一条 LLM 配置
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Result -->
    <el-card v-if="result || error" shadow="never" class="result-card">
      <template #header>
        <div class="result-header">
          <span>生成结果</span>
          <el-button v-if="result" link type="primary" @click="onGenerate">
            <el-icon><RefreshRight /></el-icon><span>重新生成</span>
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <p>{{ error }}</p>
          <el-link type="primary" @click="$router.push('/logs')">
            查看生成日志原始响应 →
          </el-link>
        </template>
      </el-alert>

      <ExerciseDetail v-if="result" :exercise="result" />
    </el-card>

    <!-- Batch drawer -->
    <el-drawer v-model="batchVisible" title="批量生成" size="560px">
      <el-form :model="batchForm" label-width="80px">
        <el-form-item label="知识点" required>
          <KnowledgePointPicker v-model="batchForm.knowledge_point_id" />
        </el-form-item>
        <el-divider>组合（可添加多组）</el-divider>
        <div
          v-for="(item, idx) in batchForm.items"
          :key="idx"
          class="batch-item"
        >
          <el-row :gutter="8" align="middle">
            <el-col :span="9">
              <el-select v-model="item.difficulty" size="small">
                <el-option
                  v-for="opt in DIFFICULTY_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-col>
            <el-col :span="9">
              <el-select v-model="item.question_type" size="small">
                <el-option
                  v-for="opt in QUESTION_TYPE_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-input-number
                v-model="item.count"
                :min="1"
                :max="10"
                size="small"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="2">
              <el-button
                size="small"
                type="danger"
                link
                :icon="Delete"
                @click="removeBatchItem(idx)"
              />
            </el-col>
          </el-row>
        </div>
        <el-button size="small" @click="addBatchItem">
          <el-icon><Plus /></el-icon><span>添加一组</span>
        </el-button>

        <el-divider />

        <p class="muted">
          预计生成 <strong>{{ batchTotal }}</strong> 道题。
          每题约 5-30 秒，串行生成，请耐心等待。
        </p>

        <el-button
          type="primary"
          :loading="batching"
          :disabled="!canBatch"
          @click="onBatchGenerate"
          style="width: 100%"
        >
          {{ batching ? `正在生成 ... (${batchProgress.done}/${batchTotal})` : '开始批量生成' }}
        </el-button>

        <div v-if="batchResult" class="batch-summary">
          <el-divider />
          <h4>结果汇总</h4>
          <p>
            ✓ 成功：<strong>{{ batchResult.succeeded.length }}</strong> 道
          </p>
          <p v-if="batchResult.failed.length">
            ✗ 失败：<strong>{{ batchResult.failed.length }}</strong> 道
          </p>
          <el-button link type="primary" @click="$router.push('/exercises')">
            去题库查看 →
          </el-button>
        </div>
      </el-form>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  MagicStick,
  Operation,
  RefreshRight,
  Plus,
  Delete,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { generationApi } from '@/api'
import { useLLMConfigStore } from '@/stores/llmConfig'
import {
  DIFFICULTY_OPTIONS,
  QUESTION_TYPE_OPTIONS,
  type Difficulty,
  type QuestionType,
} from '@/types/common'
import type { Exercise } from '@/types/exercise'
import type {
  BatchGenerateResult,
  BatchItem,
} from '@/types/generation'
import KnowledgePointPicker from '@/components/KnowledgePointPicker.vue'
import ExerciseDetail from '@/components/ExerciseDetail.vue'

const route = useRoute()
const llmStore = useLLMConfigStore()

interface FormState {
  knowledge_point_id: number | null
  difficulty: Difficulty
  question_type: QuestionType
  llm_config_id: number | null
}

const form = reactive<FormState>({
  knowledge_point_id: null,
  difficulty: 'basic',
  question_type: 'program',
  llm_config_id: null,
})

const generating = ref(false)
const result = ref<Exercise | null>(null)
const error = ref('')

const canGenerate = computed(
  () => !!form.knowledge_point_id && (!!llmStore.active || !!form.llm_config_id),
)

async function onGenerate() {
  if (!form.knowledge_point_id) return
  generating.value = true
  result.value = null
  error.value = ''
  try {
    result.value = await generationApi.generate({
      knowledge_point_id: form.knowledge_point_id,
      difficulty: form.difficulty,
      question_type: form.question_type,
      llm_config_id: form.llm_config_id ?? undefined,
    })
    ElMessage.success('生成成功')
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '生成失败'
  } finally {
    generating.value = false
  }
}

// === Batch ===
interface BatchFormState {
  knowledge_point_id: number | null
  items: BatchItem[]
}

const batchVisible = ref(false)
const batching = ref(false)
const batchProgress = reactive({ done: 0 })
const batchResult = ref<BatchGenerateResult | null>(null)

const batchForm = reactive<BatchFormState>({
  knowledge_point_id: null,
  items: [{ difficulty: 'basic', question_type: 'program', count: 2 }],
})

const batchTotal = computed(() =>
  batchForm.items.reduce((sum, it) => sum + it.count, 0),
)

const canBatch = computed(
  () => !!batchForm.knowledge_point_id && batchTotal.value > 0,
)

function addBatchItem() {
  batchForm.items.push({ difficulty: 'basic', question_type: 'program', count: 1 })
}

function removeBatchItem(idx: number) {
  batchForm.items.splice(idx, 1)
}

async function onBatchGenerate() {
  if (!batchForm.knowledge_point_id) return
  batching.value = true
  batchProgress.done = 0
  batchResult.value = null
  try {
    const r = await generationApi.generateBatch({
      knowledge_point_id: batchForm.knowledge_point_id,
      items: batchForm.items,
    })
    batchResult.value = r
    if (r.failed.length === 0) {
      ElMessage.success(`成功生成 ${r.succeeded.length} 道题`)
    } else {
      ElMessage.warning(
        `成功 ${r.succeeded.length} / 失败 ${r.failed.length}，详情见日志`,
      )
    }
  } finally {
    batching.value = false
  }
}

// Sync from query string ?kp=N
watch(
  () => route.query.kp,
  (kp) => {
    if (kp && !form.knowledge_point_id) {
      form.knowledge_point_id = Number(kp)
    }
  },
  { immediate: true },
)

onMounted(() => llmStore.refresh())
</script>

<style scoped>
.form-card {
  margin-bottom: 16px;
}

.result-card {
  margin-bottom: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.warn-hint {
  margin-left: 12px;
  color: #e6a23c;
  font-size: 13px;
}

.batch-item {
  margin-bottom: 12px;
}

.muted {
  color: #909399;
  margin: 8px 0 16px;
}

.batch-summary h4 {
  margin: 12px 0;
}

.batch-summary p {
  margin: 6px 0;
}
</style>
