<template>
  <div class="markdown-view" v-html="rendered"></div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import javascript from 'highlight.js/lib/languages/javascript'
import java from 'highlight.js/lib/languages/java'
import go from 'highlight.js/lib/languages/go'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import plaintext from 'highlight.js/lib/languages/plaintext'

hljs.registerLanguage('python', python)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('java', java)
hljs.registerLanguage('go', go)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('plaintext', plaintext)

const md: MarkdownIt = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: false,
  highlight: (code: string, lang: string): string => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return (
          '<pre class="hljs"><code>' +
          hljs.highlight(code, { language: lang, ignoreIllegals: true }).value +
          '</code></pre>'
        )
      } catch {
        // fall through to default escaping
      }
    }
    return (
      '<pre class="hljs"><code>' +
      md.utils.escapeHtml(code) +
      '</code></pre>'
    )
  },
})

const props = defineProps<{
  source: string
}>()

const rendered = computed(() => md.render(props.source || ''))

// Force re-render when source changes (computed handles it, but this is explicit)
watch(() => props.source, () => void 0)
onMounted(() => void 0)
</script>

<style scoped>
.markdown-view {
  color: var(--el-text-color-primary);
  line-height: 1.75;
  font-size: 14.5px;
}

.markdown-view :deep(h1),
.markdown-view :deep(h2),
.markdown-view :deep(h3),
.markdown-view :deep(h4) {
  color: var(--neon-cyan);
  margin: 1.5em 0 0.6em;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.markdown-view :deep(h1) {
  font-size: 22px;
  border-bottom: 1px solid var(--el-border-color);
  padding-bottom: 8px;
}

.markdown-view :deep(h2) {
  font-size: 18px;
}

.markdown-view :deep(h3) {
  font-size: 16px;
  color: var(--neon-purple);
}

.markdown-view :deep(h4) {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.markdown-view :deep(p) {
  margin: 0.8em 0;
  color: var(--el-text-color-primary);
}

.markdown-view :deep(strong) {
  color: var(--neon-cyan);
  font-weight: 600;
}

.markdown-view :deep(em) {
  color: var(--neon-purple);
}

.markdown-view :deep(code:not(pre code)) {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 1px 6px;
  font-family: 'JetBrains Mono', 'SF Mono', Monaco, Menlo, Consolas, monospace;
  font-size: 13px;
  color: var(--neon-cyan);
}

.markdown-view :deep(pre.hljs) {
  background: #0a0f1c;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 14px 18px;
  margin: 1em 0;
  overflow-x: auto;
  font-family: 'JetBrains Mono', 'SF Mono', Monaco, Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
}

.markdown-view :deep(pre.hljs code) {
  background: transparent;
  border: none;
  padding: 0;
  color: #d4d4d4;
}

.markdown-view :deep(blockquote) {
  border-left: 3px solid var(--neon-cyan);
  background: rgba(0, 212, 255, 0.05);
  padding: 8px 16px;
  margin: 1em 0;
  color: var(--el-text-color-regular);
}

.markdown-view :deep(ul),
.markdown-view :deep(ol) {
  padding-left: 24px;
  margin: 0.8em 0;
}

.markdown-view :deep(li) {
  margin: 0.3em 0;
}

.markdown-view :deep(li::marker) {
  color: var(--neon-cyan);
}

.markdown-view :deep(a) {
  color: var(--neon-cyan);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}

.markdown-view :deep(table) {
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 13px;
}

.markdown-view :deep(th),
.markdown-view :deep(td) {
  border: 1px solid var(--el-border-color);
  padding: 6px 12px;
}

.markdown-view :deep(th) {
  background: rgba(15, 22, 40, 0.7);
  color: var(--neon-cyan);
}

.markdown-view :deep(hr) {
  border: none;
  border-top: 1px solid var(--el-border-color);
  margin: 2em 0;
}
</style>
