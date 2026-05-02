<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? `编辑章节 #${editing?.id}` : '新建章节'"
    width="520px"
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
      <el-form-item label="语言" prop="language">
        <el-select
          v-model="form.language"
          style="width: 100%"
          :disabled="isEdit"
        >
          <el-option
            v-for="opt in LANGUAGE_OPTIONS"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="章节编号" prop="code">
        <el-input
          v-model="form.code"
          :placeholder="codeHint"
          maxlength="20"
        />
        <span class="hint">在所有语言中全局唯一；建议加语言前缀</span>
      </el-form-item>
      <el-form-item label="章节标题" prop="title">
        <el-input v-model="form.title" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="顺序">
        <el-input-number
          v-model="form.order_index"
          :min="0"
          :max="9999"
          controls-position="right"
        />
        <span class="hint">数字小的排在前面</span>
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
import { LANGUAGE_OPTIONS, type Language } from '@/types/common'
import type { Chapter, ChapterCreate, ChapterUpdate } from '@/types/chapter'

const props = defineProps<{
  modelValue: boolean
  /** When set: edit mode. When null: create mode. */
  editing?: Chapter | null
  /** Default language for new chapters. */
  defaultLanguage?: Language | string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved', chapter: Chapter): void
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
  language: string
  order_index: number
  description: string
}

const form = reactive<FormState>({
  code: '',
  title: '',
  language: 'python',
  order_index: 1,
  description: '',
})

const codeHint = computed(() => {
  switch (form.language) {
    case 'python': return '例如 ch13'
    case 'java': return '例如 java-ch07'
    case 'go': return '例如 go-ch07'
    case 'javascript': return '例如 js-ch07'
    default: return '唯一 code'
  }
})

const rules: FormRules = {
  language: [{ required: true, message: '请选择语言', trigger: 'change' }],
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
      language: props.editing.language,
      order_index: props.editing.order_index,
      description: props.editing.description,
    })
  } else {
    const lang = props.defaultLanguage || 'python'
    Object.assign(form, {
      code: '',
      title: '',
      language: lang,
      order_index: 1,
      description: '',
    })
    // Suggest next order_index
    try {
      const r = await learningPathApi.nextOrder(String(lang))
      form.order_index = r.next
    } catch {
      // ignore
    }
  }
}

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  saving.value = true
  try {
    let saved: Chapter
    if (props.editing) {
      const payload: ChapterUpdate = {
        code: form.code,
        title: form.title,
        order_index: form.order_index,
        description: form.description,
      }
      saved = await learningPathApi.updateChapter(props.editing.id, payload)
      ElMessage.success('已更新')
    } else {
      const payload: ChapterCreate = {
        code: form.code,
        title: form.title,
        language: form.language,
        order_index: form.order_index,
        description: form.description,
      }
      saved = await learningPathApi.createChapter(payload)
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
.hint {
  display: block;
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}
</style>
