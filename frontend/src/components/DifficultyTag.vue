<template>
  <el-tag :color="color" effect="dark" size="small" class="diff-tag">
    {{ label }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DIFFICULTY_LABEL, DIFFICULTY_COLOR, type Difficulty } from '@/types/common'

const props = defineProps<{ value: Difficulty | string }>()

const label = computed(
  () => DIFFICULTY_LABEL[props.value as Difficulty] ?? props.value,
)
const color = computed(
  () => DIFFICULTY_COLOR[props.value as Difficulty] ?? '#909399',
)
</script>

<style scoped>
.diff-tag {
  border: none;
  color: #fff !important;
}
</style>
