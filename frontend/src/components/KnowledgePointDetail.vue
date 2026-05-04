<template>
  <div class="kp-detail" v-if="kp">
    <!-- Header: title + mastery -->
    <div class="header">
      <div class="header-main">
        <el-tag size="small" effect="plain" type="info">{{ kp.code }}</el-tag>
        <h3 class="title">{{ kp.title }}</h3>
      </div>
      <MasteryTag :value="kp.mastery" />
    </div>

    <!-- Keywords -->
    <div v-if="kp.keywords?.length" class="keywords">
      <el-tag
        v-for="k in kp.keywords"
        :key="k"
        size="small"
        effect="plain"
      >{{ k }}</el-tag>
    </div>

    <el-divider />

    <!-- Learning content body -->
    <div class="content-section">
      <div class="section-header">
        <span class="section-title">📚 学习内容</span>
        <div class="section-actions">
          <el-button
            v-if="!editMode"
            size="small"
            type="primary"
            :loading="generating"
            @click="onGenerate"
          >
            <el-icon><MagicStick /></el-icon>
            <span>{{ kp.content ? '重新生成' : '生成内容' }}</span>
          </el-button>
          <el-button
            v-if="!editMode && kp.content"
            size="small"
            @click="onEdit"
          >
            <el-icon><Edit /></el-icon><span>编辑</span>
          </el-button>
          <el-button v-if="editMode" size="small" @click="onCancelEdit">
            取消
          </el-button>
          <el-button
            v-if="editMode"
            size="small"
            type="primary"
            :loading="savingContent"
            @click="onSaveContent"
          >
            保存
          </el-button>
        </div>
      </div>

      <!-- View mode -->
      <div v-if="!editMode">
        <div v-if="kp.content" class="content-body">
          <MarkdownView :source="kp.content" />
        </div>
        <div v-else class="content-empty">
          <p class="muted">尚无学习内容。</p>
          <p class="hint">
            点击「生成内容」让大模型为这个知识点写一份详细的 Markdown 学习材料（约 30-60 秒）。
          </p>
        </div>

        <!-- Generation in progress -->
        <div v-if="generating" class="gen-progress">
          <el-icon class="rotating"><Loading /></el-icon>
          <span>正在生成中... 已用 {{ genElapsed }}s</span>
        </div>
      </div>

      <!-- Edit mode -->
      <div v-else>
        <el-input
          v-model="editingContent"
          type="textarea"
          :autosize="{ minRows: 12, maxRows: 30 }"
          class="mono"
          placeholder="在此编辑 Markdown 内容..."
        />
        <p class="hint">支持 Markdown：标题、列表、代码块（用 ```python 等围栏）。</p>
      </div>
    </div>

    <el-divider />

    <!-- Mastery actions + practice -->
    <div class="actions-section">
      <div class="action-group">
        <span class="group-label">📊 状态</span>
        <el-button
          size="small"
          :type="kp.mastery === 'learning' ? 'primary' : 'default'"
          @click="onSetMastery('learning')"
        >
          📖 学习中
        </el-button>
        <el-button
          size="small"
          :type="kp.mastery === 'mastered' ? 'success' : 'default'"
          @click="onSetMastery('mastered')"
        >
          ✓ 已掌握
        </el-button>
        <el-button
          size="small"
          :type="kp.mastery === 'unknown' ? 'danger' : 'default'"
          @click="onSetMastery('unknown')"
        >
          ❓ 不懂
        </el-button>
      </div>

      <div class="action-group">
        <span class="group-label">🎯 练习</span>
        <el-button
          size="small"
          type="primary"
          :loading="quickGenLoading"
          @click="onQuickGenerate"
        >
          <el-icon><Aim /></el-icon>
          <span>一键 3 道入门</span>
        </el-button>
        <el-button size="small" @click="onCustomGenerate">
          <el-icon><MagicStick /></el-icon><span>自定义出题</span>
        </el-button>
      </div>
    </div>

    <!-- Notes -->
    <div class="notes-section">
      <div class="section-header">
        <span class="section-title">📝 我的备注</span>
        <el-button size="small" v-if="!editingNote" @click="editingNote = true">
          编辑
        </el-button>
        <div v-else>
          <el-button size="small" @click="cancelNote">取消</el-button>
          <el-button size="small" type="primary" @click="saveNote">保存</el-button>
        </div>
      </div>
      <p v-if="!editingNote" class="note-display">
        {{ kp.mastery_note || '（暂无备注，点编辑添加你的笔记）' }}
      </p>
      <el-input
        v-else
        v-model="noteDraft"
        type="textarea"
        :autosize="{ minRows: 3, maxRows: 8 }"
        placeholder="自己的笔记 / 还需要复习的点..."
      />
    </div>

    <!-- Prev / Next -->
    <div v-if="prev || next" class="nav-row">
      <el-button v-if="prev" link @click="$emit('navigate', prev)">
        ← {{ prev.code }} {{ prev.title }}
      </el-button>
      <span v-else></span>
      <el-button v-if="next" link @click="$emit('navigate', next)">
        {{ next.code }} {{ next.title }} →
      </el-button>
      <span v-else></span>
    </div>
  </div>

  <el-empty v-else description="选择左侧任一知识点查看学习内容" />
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  MagicStick,
  Edit,
  Loading,
  Aim,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { learningPathApi, generationApi } from '@/api'
import type { KnowledgePoint } from '@/types/knowledge_point'
import type { Mastery } from '@/types/common'
import MarkdownView from './MarkdownView.vue'
import MasteryTag from './MasteryTag.vue'

const props = defineProps<{
  kp: KnowledgePoint | null
  prev?: KnowledgePoint | null
  next?: KnowledgePoint | null
}>()

const emit = defineEmits<{
  (e: 'updated', kp: KnowledgePoint): void
  (e: 'navigate', target: KnowledgePoint): void
}>()

const router = useRouter()

// === Generation ===
const generating = ref(false)
const genStart = ref(0)
const genElapsed = ref(0)
let genTimer: number | null = null

async function onGenerate() {
  if (!props.kp) return
  if (props.kp.content) {
    await ElMessageBox.confirm(
      '已有学习内容，重新生成会覆盖现有内容。继续吗？',
      '确认',
      { type: 'warning' },
    )
  }
  generating.value = true
  genStart.value = Date.now()
  genElapsed.value = 0
  genTimer = window.setInterval(() => {
    genElapsed.value = Math.floor((Date.now() - genStart.value) / 1000)
  }, 250)
  try {
    const updated = await learningPathApi.generateContent(props.kp.id)
    emit('updated', updated)
    ElMessage.success(`生成完成 (${genElapsed.value}s)`)
  } finally {
    generating.value = false
    if (genTimer) clearInterval(genTimer)
  }
}

// === Edit content ===
const editMode = ref(false)
const editingContent = ref('')
const savingContent = ref(false)

function onEdit() {
  if (!props.kp) return
  editingContent.value = props.kp.content
  editMode.value = true
}

function onCancelEdit() {
  editMode.value = false
}

async function onSaveContent() {
  if (!props.kp) return
  savingContent.value = true
  try {
    const updated = await learningPathApi.updateContent(
      props.kp.id,
      editingContent.value,
    )
    emit('updated', updated)
    editMode.value = false
    ElMessage.success('内容已保存')
  } finally {
    savingContent.value = false
  }
}

// === Mastery ===
async function onSetMastery(m: Mastery) {
  if (!props.kp) return
  // Toggle off if clicking the same state
  const target: Mastery = props.kp.mastery === m ? 'not_started' : m
  const updated = await learningPathApi.setMastery(props.kp.id, target)
  emit('updated', updated)
  ElMessage.success(`已标记为「${target === 'not_started' ? '未开始' : labelOf(target)}」`)
}

function labelOf(m: Mastery): string {
  return { not_started: '未开始', learning: '学习中', mastered: '已掌握', unknown: '不懂' }[m]
}

// === Notes ===
const editingNote = ref(false)
const noteDraft = ref('')

watch(
  () => props.kp,
  (v) => {
    if (v) {
      noteDraft.value = v.mastery_note
    }
    editingNote.value = false
    editMode.value = false
  },
)

function cancelNote() {
  editingNote.value = false
  if (props.kp) noteDraft.value = props.kp.mastery_note
}

async function saveNote() {
  if (!props.kp) return
  const updated = await learningPathApi.setMastery(
    props.kp.id,
    props.kp.mastery,
    noteDraft.value,
  )
  emit('updated', updated)
  editingNote.value = false
  ElMessage.success('备注已保存')
}

// === Quick generate ===
const quickGenLoading = ref(false)

async function onQuickGenerate() {
  if (!props.kp) return
  quickGenLoading.value = true
  try {
    const r = await generationApi.generateBatch({
      knowledge_point_id: props.kp.id,
      items: [
        { difficulty: 'entry', question_type: 'choice', count: 1 },
        { difficulty: 'entry', question_type: 'fill', count: 1 },
        { difficulty: 'basic', question_type: 'program', count: 1 },
      ],
    })
    ElMessage.success(`已开始生成 3 道题（任务 ${r.job_id.slice(0, 8)}）`)
    setTimeout(() => router.push('/exercises'), 800)
  } finally {
    quickGenLoading.value = false
  }
}

function onCustomGenerate() {
  if (!props.kp) return
  router.push({ path: '/generate', query: { kp: props.kp.id } })
}
</script>

<style scoped>
.kp-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--el-text-color-regular);
  text-transform: uppercase;
}

.section-actions {
  display: flex;
  gap: 6px;
}

.content-body {
  background: rgba(15, 22, 40, 0.4);
  border-radius: 6px;
  padding: 16px 20px;
  max-height: 600px;
  overflow-y: auto;
}

.content-empty {
  background: rgba(15, 22, 40, 0.4);
  border-radius: 6px;
  padding: 32px 20px;
  text-align: center;
}

.muted {
  color: var(--el-text-color-secondary);
  margin: 0 0 8px;
}

.hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin: 6px 0 0;
}

.gen-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  margin-top: 10px;
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 4px;
  font-size: 13px;
  color: var(--neon-cyan);
}

.rotating {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(15, 22, 40, 0.4);
  border-radius: 6px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.group-label {
  min-width: 60px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  letter-spacing: 0.4px;
}

.notes-section {
  margin-top: 4px;
}

.note-display {
  background: rgba(15, 22, 40, 0.4);
  border-radius: 4px;
  padding: 10px 14px;
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 13px;
  white-space: pre-wrap;
  line-height: 1.6;
}

.nav-row {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 13px;
}

.mono :deep(.el-textarea__inner) {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 13px;
}
</style>
