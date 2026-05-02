<template>
  <el-cascader
    v-model="selected"
    :options="options"
    :props="cascaderProps"
    :placeholder="placeholder"
    clearable
    filterable
    style="width: 100%"
    @change="onChange"
  >
    <template #default="{ data }">
      <span>
        <el-tag size="small" effect="plain" style="margin-right: 6px">{{ data.code }}</el-tag>
        {{ data.label }}
      </span>
    </template>
  </el-cascader>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { learningPathApi } from '@/api'
import { useLanguageStore } from '@/stores/language'
import type { ChapterWithKnowledgePoints } from '@/types/chapter'

const props = withDefaults(
  defineProps<{
    modelValue: number | null
    placeholder?: string
    /** Override store's language; if not given, uses store's current. */
    language?: string
  }>(),
  { placeholder: '请选择知识点（章节 → 知识点）' },
)

const emit = defineEmits<{
  (e: 'update:modelValue', v: number | null): void
}>()

interface CascadeOption {
  value: number
  label: string
  code: string
  children?: CascadeOption[]
  [key: string]: any
}

const langStore = useLanguageStore()
const tree = ref<ChapterWithKnowledgePoints[]>([])
const selected = ref<(number | string)[]>([])

const cascaderProps = {
  expandTrigger: 'hover' as const,
  emitPath: true,
}

const effectiveLanguage = computed(
  () => props.language ?? langStore.current,
)

const options = computed<CascadeOption[]>(() =>
  tree.value.map((c) => ({
    value: c.id,
    label: c.title,
    code: c.code,
    children: (c.knowledge_points ?? []).map((kp) => ({
      value: kp.id,
      label: kp.title,
      code: kp.code,
    })),
  })),
)

async function reload() {
  tree.value = await learningPathApi.tree(effectiveLanguage.value)
  syncFromModel(props.modelValue)
}

watch(effectiveLanguage, () => {
  // language changed — clear selection if the current KP is no longer valid
  // and reload the tree.
  reload().then(() => {
    if (props.modelValue) {
      const stillValid = tree.value.some((c) =>
        (c.knowledge_points ?? []).some((kp) => kp.id === props.modelValue),
      )
      if (!stillValid) {
        emit('update:modelValue', null)
      }
    }
  })
})

watch(
  () => props.modelValue,
  (v) => syncFromModel(v),
)

function syncFromModel(kpId: number | null) {
  if (!kpId || !tree.value.length) {
    selected.value = []
    return
  }
  for (const c of tree.value) {
    const found = (c.knowledge_points ?? []).find((kp) => kp.id === kpId)
    if (found) {
      selected.value = [c.id, kpId]
      return
    }
  }
  selected.value = []
}

function onChange(val: any) {
  if (Array.isArray(val) && val.length === 2) {
    emit('update:modelValue', Number(val[1]))
  } else {
    emit('update:modelValue', null)
  }
}

onMounted(reload)
</script>
