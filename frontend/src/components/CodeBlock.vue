<template>
  <div class="code-wrap">
    <div v-if="title || copyable" class="code-header">
      <span class="code-title">{{ title }}</span>
      <el-button
        v-if="copyable"
        link
        size="small"
        type="primary"
        @click="onCopy"
      >
        {{ copied ? '已复制' : '复制' }}
      </el-button>
    </div>
    <pre class="code-block"><code ref="codeRef" :class="`language-${language}`">{{ code }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import json from 'highlight.js/lib/languages/json'
import plaintext from 'highlight.js/lib/languages/plaintext'

hljs.registerLanguage('python', python)
hljs.registerLanguage('json', json)
hljs.registerLanguage('plaintext', plaintext)

const props = withDefaults(
  defineProps<{
    code: string
    language?: string
    title?: string
    copyable?: boolean
  }>(),
  {
    language: 'python',
    title: '',
    copyable: true,
  },
)

const codeRef = ref<HTMLElement | null>(null)
const copied = ref(false)

async function highlight() {
  await nextTick()
  if (codeRef.value && props.code) {
    hljs.highlightElement(codeRef.value)
  }
}

watch(() => props.code, highlight)
onMounted(highlight)

async function onCopy() {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => (copied.value = false), 1500)
  } catch {
    // ignore
  }
}
</script>

<style scoped>
.code-wrap {
  background: #1e1e1e;
  border-radius: 6px;
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #2d2d2d;
  padding: 6px 12px;
  font-size: 12px;
  color: #d4d4d4;
}

.code-title {
  color: #aaa;
}

.code-block {
  margin: 0;
  padding: 12px 16px;
  background: #1e1e1e;
  font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
}

.code-block code {
  background: transparent;
  padding: 0;
}
</style>
