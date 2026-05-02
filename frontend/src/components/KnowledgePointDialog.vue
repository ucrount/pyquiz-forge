<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? `编辑知识点 #${editing?.id}` : '新建知识点'"
    width="560px"
    :close-on-click-modal="false"
    @open="initForm"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="90px"
      label-position="right"
    >
      <el-form-item label="所属章节">
        <span class="muted">
          {{ chapter ? `${chapter.code} · ${chapter.title}` : '加载中...' }}
        </span>
      </el-form-item>
      <el-form-item label="知识点编号" prop="code">
        <el-input
          v-model="form.code"
          :placeholder="codeHint"
          maxlength="20"
        />
        <span class="hint">在所有语言中全局唯一</span>
      </el-form-item>
      <el-form-item label="知识点标题" prop="title">
        <el-input v-model="form.title" maxlength="200" show-word-limit />
      </el-form-item>
      <el-form-item label="顺序">
        <el-input-number
          v-model="form.order_index"
          :min="0"
          :max="9999"
          controls-position="right"
        />
      </el-form-item>
      <el-form-item label="关键词">
        <el-input
          v-model="keywordsText"
          placeholder="逗号分隔，例如  list, append, 切片"
        />
        <span class="hint">用于辅助 LLM 出题更精准</span>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 5 }"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { learningPathApi } from '@/api'
import type { Chapter } from '@/types/chapter'
import type {
  KnowledgePoint,
  KnowledgePointCreate,
  KnowledgePointUpdate,
} from '@/types/knowledge_point'

const props = defineProps<{
  modelValue: boolean
  /** Required: which chapter is this KP under. Used both for create + edit. */
  chapter: Chapter | null
  /** When set: edit mode. When null: create mode under given chapter. */
  editing?: KnowledgePoint | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved', kp: KnowledgePoint): void
}>()

const visible = ref(props.modelValue)
watch(() => props.modelValue, (v) => (visible.value = v))
watch(visible, (v) => emit('update:modelValue', v))

const isEdit = computed(() => !!props.editing)
const formRef = ref<FormInstance>()
const saving = ref(false)

interface FormState {
  code: string
  title: string
  order_index: number
  description: string
}

const form = reactive<FormState>({
  code: '',
  title: '',
  order_index: 1,
  description: '',
})

const keywordsText = ref('')

const codeHint = computed(() => {
  if (!props.chapter) return '例如 1.6'
  // Suggest <chapterCode>-N where N is something like the next index
  const ch = props.chapter
  const prefix = ch.code.split('-')[0]
  if (prefix === ch.code) {
    // chapter code is like "ch01" -> suggest "1.X"
    const num = ch.code.replace(/[^\d]/g, '')
    return num ? `例如 ${num}.${form.order_index}` : '例如 1.1'
  }
  return `例如 ${prefix}-${num(ch.code)}.${form.order_index}`
})

function num(s: string): string {
  return s.replace(/[^\d]/g, '') || '1'
}

const rules: FormRules = {
  code: [
    { required: true, message: '请填写编号', trigger: 'blur' },
    { max: 20, message: '编号最长 20 字符', trigger: 'blur' },
  ],
  title: [{ required: true, message: '请填写标题', trigger: 'blur' }],
}

async function initForm() {
  if (props.editing) {
    Object.assign(form, {
      code: props.editing.code,
      title: props.editing.title,
      order_index: props.editing.order_index,
      description: props.editing.description,
    })
    keywordsText.value = (props.editing.keywords ?? []).join(', ')
  } else {
    Object.assign(form, {
      code: '',
      title: '',
      order_index: 1,
      description: '',
    })
    keywordsText.value = ''
    // Suggest next order_index in the chapter
    if (props.chapter) {
      try {
        const r = await learningPathApi.nextOrder(
          String(props.chapter.language),
          props.chapter.id,
        )
        form.order_index = r.next
      } catch {
        // ignore
      }
    }
  }
}

function parseKeywords(text: string): string[] {
  return text
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean)
}

async function onSubmit() {
  if (!formRef.value || !props.chapter) return
  await formRef.value.validate()
  saving.value = true
  try {
    const keywords = parseKeywords(keywordsText.value)
    let saved: KnowledgePoint
    if (props.editing) {
      const payload: KnowledgePointUpdate = {
        code: form.code,
        title: form.title,
        order_index: form.order_index,
        keywords,
        description: form.description,
      }
      saved = await learningPathApi.updateKP(props.editing.id, payload)
      ElMessage.success('已更新')
    } else {
      const payload: KnowledgePointCreate = {
        chapter_id: props.chapter.id,
        code: form.code,
        title: form.title,
        language: props.chapter.language as string,
        order_index: form.order_index,
        keywords,
        description: form.description,
      }
      saved = await learningPathApi.createKP(payload)
      ElMessage.success('已创建')
    }
    emit('saved', saved)
    visible.value = false
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.muted {
  color: #909399;
}

.hint {
  display: block;
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}
</style>
