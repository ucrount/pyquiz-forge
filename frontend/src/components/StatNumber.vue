<template>
  <div class="stat-number" :class="`accent-${accent}`">
    <div v-if="label" class="stat-label">{{ label }}</div>
    <div class="stat-value mono" :title="String(value)">
      <span class="stat-prefix" v-if="prefix">{{ prefix }}</span>
      <span>{{ display }}</span>
      <span class="stat-suffix" v-if="suffix">{{ suffix }}</span>
    </div>
    <div v-if="hint" class="stat-hint">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    label?: string
    value: number | string
    accent?: 'cyan' | 'purple' | 'pink' | 'green' | 'yellow'
    prefix?: string
    suffix?: string
    hint?: string
  }>(),
  { accent: 'cyan' },
)

const display = computed(() => {
  if (typeof props.value === 'number') {
    if (Number.isFinite(props.value)) {
      return props.value.toLocaleString()
    }
    return '—'
  }
  return props.value || '—'
})
</script>

<style scoped>
.stat-number {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  font-size: 12px;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--el-text-color-secondary);
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  color: var(--accent-color);
  text-shadow: 0 0 12px var(--accent-glow);
  letter-spacing: 0.5px;
}

.stat-prefix,
.stat-suffix {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  text-shadow: none;
  opacity: 0.7;
}

.stat-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-number.accent-cyan {
  --accent-color: var(--neon-cyan);
  --accent-glow: rgba(0, 212, 255, 0.4);
}
.stat-number.accent-purple {
  --accent-color: var(--neon-purple);
  --accent-glow: rgba(181, 74, 255, 0.4);
}
.stat-number.accent-pink {
  --accent-color: var(--neon-pink);
  --accent-glow: rgba(255, 77, 141, 0.4);
}
.stat-number.accent-green {
  --accent-color: var(--neon-green);
  --accent-glow: rgba(0, 255, 157, 0.4);
}
.stat-number.accent-yellow {
  --accent-color: var(--neon-yellow);
  --accent-glow: rgba(255, 170, 0, 0.4);
}
</style>
