<template>
  <span v-if="value === null || value === undefined" class="badge none">未评分</span>
  <span v-else class="badge" :style="{ background: color, color: '#fff' }">
    <span class="num">{{ formatted }}</span>
    <span class="unit">/10</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ value: number | null | undefined }>()

const formatted = computed(() => {
  if (props.value === null || props.value === undefined) return ''
  return Number(props.value).toFixed(1)
})

const color = computed(() => {
  const v = Number(props.value)
  if (isNaN(v)) return '#909399'
  if (v >= 8.5) return '#67c23a' // green
  if (v >= 7) return '#409eff'   // blue
  if (v >= 5) return '#e6a23c'   // amber
  return '#f56c6c'               // red
})
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  font-variant-numeric: tabular-nums;
}

.badge.none {
  background: #f4f4f5;
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.num {
  font-size: 13px;
}

.unit {
  font-size: 10px;
  opacity: 0.85;
}
</style>
