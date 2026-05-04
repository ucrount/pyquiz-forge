<template>
  <span class="mastery-tag" :style="{ '--c': color }">
    <span class="icon">{{ icon }}</span>
    <span>{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  MASTERY_LABEL,
  MASTERY_COLOR,
  MASTERY_ICON,
  type Mastery,
} from '@/types/common'

const props = defineProps<{
  value: Mastery | string
}>()

const label = computed(
  () => MASTERY_LABEL[props.value as Mastery] ?? props.value,
)
const color = computed(
  () => MASTERY_COLOR[props.value as Mastery] ?? '#909399',
)
const icon = computed(
  () => MASTERY_ICON[props.value as Mastery] ?? '○',
)
</script>

<style scoped>
.mastery-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--c);
  color: var(--c);
  background: color-mix(in srgb, var(--c) 8%, transparent);
  text-shadow: 0 0 6px color-mix(in srgb, var(--c) 50%, transparent);
}

.icon {
  font-size: 12px;
  line-height: 1;
}
</style>
