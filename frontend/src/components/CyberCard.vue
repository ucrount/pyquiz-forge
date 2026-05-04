<template>
  <div class="cyber-card" :class="[`accent-${accent}`, { 'is-clickable': clickable }]">
    <div v-if="$slots.header || title" class="cyber-card__header">
      <slot name="header">
        <span class="cyber-card__title">{{ title }}</span>
      </slot>
      <span v-if="$slots.extra" class="cyber-card__extra">
        <slot name="extra" />
      </span>
    </div>
    <div class="cyber-card__body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    accent?: 'cyan' | 'purple' | 'pink' | 'green' | 'yellow'
    clickable?: boolean
  }>(),
  { accent: 'cyan', clickable: false },
)
</script>

<style scoped>
.cyber-card {
  position: relative;
  background: var(--glass-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.25s ease, box-shadow 0.25s ease,
    transform 0.25s ease;
}

/* Accent left border */
.cyber-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--accent-color);
  opacity: 0.7;
  box-shadow: 0 0 10px var(--accent-color);
}

.cyber-card.accent-cyan {
  --accent-color: var(--neon-cyan);
}
.cyber-card.accent-purple {
  --accent-color: var(--neon-purple);
}
.cyber-card.accent-pink {
  --accent-color: var(--neon-pink);
}
.cyber-card.accent-green {
  --accent-color: var(--neon-green);
}
.cyber-card.accent-yellow {
  --accent-color: var(--neon-yellow);
}

.cyber-card:hover {
  border-color: var(--accent-color);
  box-shadow: 0 0 26px rgba(0, 212, 255, 0.16);
}

.cyber-card.is-clickable {
  cursor: pointer;
}
.cyber-card.is-clickable:hover {
  transform: translateY(-2px);
}

.cyber-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.cyber-card__title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.4px;
  color: var(--el-text-color-primary);
  text-transform: uppercase;
}

.cyber-card__extra {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.cyber-card__body {
  padding: 16px 18px;
}
</style>
