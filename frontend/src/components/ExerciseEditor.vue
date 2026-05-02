<template>
  <div class="ex-editor" v-if="form">
    <!-- Header — read-only meta -->
    <div class="meta-bar">
      <DifficultyTag :value="exercise.difficulty" />
      <QuestionTypeTag :value="exercise.question_type" />
      <el-tag size="small" effect="plain">
        知识点 #{{ exercise.knowledge_point_id }}
      </el-tag>
      <span class="muted">
        难度/题型/知识点不可编辑（如需更改请重新生成）
      </span>
    </div>

    <el-divider />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="ex-form"
    >
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" maxlength="200" show-word-limit />
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio-button value="draft">草稿</el-radio-button>
          <el-radio-button value="published">已发布</el-radio-button>
          <el-radio-button value="archived">已归档</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="题目描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :autosize="{ minRows: 4, maxRows: 12 }"
        />
      </el-form-item>

      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="示例输入">
            <el-input
              v-model="form.example_input"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 8 }"
              class="mono"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="示例输出">
            <el-input
              v-model="form.example_output"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 8 }"
              class="mono"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="提示">
        <el-input
          v-model="form.hint"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
        />
      </el-form-item>

      <el-form-item label="标准答案">
        <el-input
          v-model="form.standard_answer"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 8 }"
        />
      </el-form-item>

      <el-form-item label="参考代码">
        <el-input
          v-model="form.reference_code"
          type="textarea"
          :autosize="{ minRows: 6, maxRows: 24 }"
          class="mono code-area"
          placeholder="# Python code"
        />
      </el-form-item>

      <el-form-item label="测试用例">
        <el-table
          :data="form.test_cases"
          stripe
          size="small"
          empty-text="暂无测试用例"
        >
          <el-table-column type="index" label="#" width="50" />
          <el-table-column label="输入" min-width="220">
            <template #default="{ row }">
              <el-input
                v-model="row.input"
                type="textarea"
                :autosize="{ minRows: 1, maxRows: 4 }"
                class="mono"
              />
            </template>
          </el-table-column>
          <el-table-column label="期望输出" min-width="220">
            <template #default="{ row }">
              <el-input
                v-model="row.expected_output"
                type="textarea"
                :autosize="{ minRows: 1, maxRows: 4 }"
                class="mono"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" fixed="right">
            <template #default="{ $index }">
              <el-button
                size="small"
                type="danger"
                link
                :icon="Delete"
                @click="removeTestCase($index)"
              />
            </template>
          </el-table-column>
        </el-table>
        <el-button
          size="small"
          @click="addTestCase"
          style="margin-top: 8px"
        >
          <el-icon><Plus /></el-icon><span>添加用例</span>
        </el-button>
      </el-form-item>

      <el-form-item label="解析">
        <el-input
          v-model="form.explanation"
          type="textarea"
          :autosize="{ minRows: 3, maxRows: 12 }"
        />
      </el-form-item>

      <el-form-item label="易错点">
        <el-input
          v-model="form.common_mistakes"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 8 }"
        />
      </el-form-item>

      <!-- Choice options editor (only when question_type is choice) -->
      <el-form-item
        v-if="exercise.question_type === 'choice'"
        label="选项 (extra.options)"
      >
        <div class="options-list">
          <div
            v-for="(opt, idx) in choiceOptions"
            :key="idx"
            class="option-row"
          >
            <el-input
              v-model="opt.label"
              size="small"
              style="width: 80px"
              placeholder="A"
            />
            <el-input
              v-model="opt.text"
              size="small"
              style="flex: 1"
              placeholder="选项文本"
            />
            <el-button
              size="small"
              type="danger"
              link
              :icon="Delete"
              @click="removeChoice(idx)"
            />
          </div>
          <el-button size="small" @click="addChoice">
            <el-icon><Plus /></el-icon><span>添加选项</span>
          </el-button>
        </div>
      </el-form-item>
    </el-form>

    <div class="footer">
      <span class="muted">
        ID #{{ exercise.id }} · 修改后点击保存写回服务器
      </span>
      <div>
        <el-button @click="onCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">
          保存
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { exerciseApi } from '@/api'
import type {
  Exercise,
  ExerciseUpdate,
  TestCase,
} from '@/types/exercise'
import type { ExerciseStatus } from '@/types/common'
import DifficultyTag from './DifficultyTag.vue'
import QuestionTypeTag from './QuestionTypeTag.vue'

const props = defineProps<{ exercise: Exercise }>()
const emit = defineEmits<{
  (e: 'saved', updated: Exercise): void
  (e: 'cancel'): void
}>()

interface FormState {
  title: string
  status: ExerciseStatus
  description: string
  example_input: string
  example_output: string
  hint: string
  standard_answer: string
  reference_code: string
  test_cases: TestCase[]
  explanation: string
  common_mistakes: string
}

interface ChoiceOption {
  label: string
  text: string
}

const form = ref<FormState | null>(null)
const choiceOptions = ref<ChoiceOption[]>([])
const formRef = ref<FormInstance>()
const saving = ref(false)

const rules: FormRules = {
  title: [
    { required: true, message: '标题不能为空', trigger: 'blur' },
    { max: 200, message: '标题最长 200 字', trigger: 'blur' },
  ],
}

function initForm() {
  const e = props.exercise
  form.value = {
    title: e.title ?? '',
    status: e.status ?? 'published',
    description: e.description ?? '',
    example_input: e.example_input ?? '',
    example_output: e.example_output ?? '',
    hint: e.hint ?? '',
    standard_answer: e.standard_answer ?? '',
    reference_code: e.reference_code ?? '',
    // Deep clone test cases so cancel really discards
    test_cases: (e.test_cases ?? []).map((tc) => ({ ...tc })),
    explanation: e.explanation ?? '',
    common_mistakes: e.common_mistakes ?? '',
  }
  choiceOptions.value = parseChoiceOptions(e)
}

function parseChoiceOptions(e: Exercise): ChoiceOption[] {
  if (e.question_type !== 'choice') return []
  const opts = e.extra?.options
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
    return Object.entries(opts).map(([k, v]) => ({
      label: k,
      text: String(v),
    }))
  }
  return []
}

watch(() => props.exercise, initForm, { immediate: true })

function addTestCase() {
  form.value?.test_cases.push({ input: '', expected_output: '' })
}

function removeTestCase(idx: number) {
  form.value?.test_cases.splice(idx, 1)
}

function addChoice() {
  const next = String.fromCharCode(65 + choiceOptions.value.length)
  choiceOptions.value.push({ label: next, text: '' })
}

function removeChoice(idx: number) {
  choiceOptions.value.splice(idx, 1)
}

function onCancel() {
  emit('cancel')
}

async function onSave() {
  if (!formRef.value || !form.value) return
  await formRef.value.validate()
  const f = form.value

  // Build PATCH payload — only fields the backend allows.
  const payload: ExerciseUpdate = {
    title: f.title,
    description: f.description,
    example_input: f.example_input,
    example_output: f.example_output,
    hint: f.hint,
    standard_answer: f.standard_answer,
    reference_code: f.reference_code,
    test_cases: f.test_cases,
    explanation: f.explanation,
    common_mistakes: f.common_mistakes,
    status: f.status,
  }

  // Carry over `extra`, replacing options if this is a choice question.
  if (props.exercise.question_type === 'choice') {
    const baseExtra = { ...(props.exercise.extra ?? {}) }
    baseExtra.options = choiceOptions.value.map((o) => ({
      label: o.label,
      text: o.text,
    }))
    payload.extra = baseExtra
  }

  saving.value = true
  try {
    const updated = await exerciseApi.update(props.exercise.id, payload)
    ElMessage.success('已保存')
    emit('saved', updated)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.ex-editor {
  font-size: 14px;
}

.meta-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.muted {
  color: #909399;
  font-size: 13px;
}

.ex-form {
  padding: 0;
}

:deep(.mono .el-textarea__inner) {
  font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
}

:deep(.code-area .el-textarea__inner) {
  background: #fafafa;
  border-color: #e4e7ed;
}

.options-list {
  width: 100%;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  position: sticky;
  bottom: 0;
  background: #fff;
}
</style>
