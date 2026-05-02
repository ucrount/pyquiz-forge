<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑 LLM 配置' : '新建 LLM 配置'"
    width="560px"
    :close-on-click-modal="false"
    @closed="onClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="例如 deepseek-default" />
      </el-form-item>
      <el-form-item label="Provider" prop="provider">
        <el-select v-model="form.provider" style="width: 100%">
          <el-option
            v-for="opt in PROVIDER_OPTIONS"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="API Key" prop="api_key">
        <el-input
          v-model="form.api_key"
          :placeholder="isEdit ? '留空则保持原值' : 'sk-xxxxxxxx'"
          type="password"
          show-password
        />
      </el-form-item>
      <el-form-item label="API Base">
        <el-input
          v-model="form.api_base"
          placeholder="https://api.deepseek.com/v1"
        />
      </el-form-item>
      <el-form-item label="模型" prop="model">
        <el-input v-model="form.model" placeholder="deepseek-chat" />
      </el-form-item>
      <el-form-item label="Temperature">
        <el-slider
          v-model="form.temperature"
          :min="0"
          :max="2"
          :step="0.1"
          show-input
        />
      </el-form-item>
      <el-form-item label="Max Tokens">
        <el-input-number
          v-model="form.max_tokens"
          :min="1"
          :max="32000"
          :step="256"
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
import { ref, watch, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { llmConfigApi } from '@/api'
import { PROVIDER_OPTIONS, type Provider } from '@/types/common'
import type {
  LLMConfig,
  LLMConfigCreate,
  LLMConfigUpdate,
} from '@/types/llm_config'

const props = defineProps<{
  modelValue: boolean
  editing?: LLMConfig | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved'): void
}>()

const visible = ref(props.modelValue)
watch(
  () => props.modelValue,
  (v) => {
    visible.value = v
    if (v) initForm()
  },
)
watch(visible, (v) => emit('update:modelValue', v))

const isEdit = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

interface FormState {
  name: string
  provider: Provider
  api_key: string
  api_base: string
  model: string
  temperature: number
  max_tokens: number
}

const form = reactive<FormState>({
  name: '',
  provider: 'deepseek',
  api_key: '',
  api_base: 'https://api.deepseek.com/v1',
  model: 'deepseek-chat',
  temperature: 0.7,
  max_tokens: 2048,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择 provider', trigger: 'change' }],
  api_key: [
    {
      validator: (_r, _v, cb) => {
        if (!isEdit.value && !form.api_key) {
          cb(new Error('请填写 API Key'))
        } else {
          cb()
        }
      },
      trigger: 'blur',
    },
  ],
  model: [{ required: true, message: '请填写模型名', trigger: 'blur' }],
}

function initForm() {
  if (props.editing) {
    isEdit.value = true
    Object.assign(form, {
      name: props.editing.name,
      provider: props.editing.provider,
      api_key: '', // never reuse the masked one
      api_base: props.editing.api_base,
      model: props.editing.model,
      temperature: props.editing.temperature,
      max_tokens: props.editing.max_tokens,
    })
  } else {
    isEdit.value = false
    Object.assign(form, {
      name: '',
      provider: 'deepseek',
      api_key: '',
      api_base: 'https://api.deepseek.com/v1',
      model: 'deepseek-chat',
      temperature: 0.7,
      max_tokens: 2048,
    })
  }
}

function onClosed() {
  formRef.value?.resetFields()
}

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  saving.value = true
  try {
    if (isEdit.value && props.editing) {
      const payload: LLMConfigUpdate = {
        name: form.name,
        provider: form.provider,
        api_base: form.api_base,
        model: form.model,
        temperature: form.temperature,
        max_tokens: form.max_tokens,
      }
      if (form.api_key) payload.api_key = form.api_key
      await llmConfigApi.update(props.editing.id, payload)
      ElMessage.success('已更新')
    } else {
      const payload: LLMConfigCreate = {
        name: form.name,
        provider: form.provider,
        api_key: form.api_key,
        api_base: form.api_base,
        model: form.model,
        temperature: form.temperature,
        max_tokens: form.max_tokens,
      }
      await llmConfigApi.create(payload)
      ElMessage.success('已创建')
    }
    emit('saved')
    visible.value = false
  } finally {
    saving.value = false
  }
}
</script>
