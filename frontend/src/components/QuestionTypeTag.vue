<template>
  <el-tag size="small" effect="plain" :type="tagType">{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { QUESTION_TYPE_LABEL, type QuestionType } from '@/types/common'

const props = defineProps<{ value: QuestionType | string }>()

const label = computed(
  () => QUESTION_TYPE_LABEL[props.value as QuestionType] ?? props.value,
)

const TYPE_MAP: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
  choice: 'primary',
  fill: 'success',
  judge: 'info',
  read: 'warning',
  complete: 'warning',
  program: 'danger',
  debug: 'danger',
}

const tagType = computed(() => TYPE_MAP[props.value] ?? 'info')
</script>
