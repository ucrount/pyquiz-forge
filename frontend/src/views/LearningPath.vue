<template>
  <div class="page">
    <div class="page-header">
      <h2>学习路线</h2>
      <el-button type="primary" @click="onCreateChapter">
        <el-icon><Plus /></el-icon><span>新建章节</span>
      </el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never" v-loading="loading">
          <el-input
            v-model="filterText"
            placeholder="搜索章节或知识点..."
            clearable
            style="margin-bottom: 12px"
          />
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="key"
            :filter-node-method="filterNode"
            :expand-on-click-node="false"
            :default-expand-all="false"
            highlight-current
            empty-text="该语言暂无章节，点击右上角新建"
            @node-click="onNodeClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <span class="tree-title">
                  <el-tag
                    v-if="data.type === 'chapter'"
                    size="small"
                    type="info"
                    effect="plain"
                  >{{ data.code }}</el-tag>
                  <el-tag v-else size="small" type="primary" effect="plain">
                    {{ data.code }}
                  </el-tag>
                  {{ node.label }}
                </span>

                <!-- Hover actions -->
                <span class="tree-actions" v-if="data.type === 'chapter'">
                  <el-button
                    size="small"
                    link
                    type="primary"
                    @click.stop="onAddKP(data.raw)"
                  >+ 知识点</el-button>
                  <el-button
                    size="small"
                    link
                    @click.stop="onEditChapter(data.raw)"
                  >编辑</el-button>
                  <el-button
                    size="small"
                    link
                    type="danger"
                    @click.stop="onDeleteChapter(data.raw)"
                  >删除</el-button>
                </span>
                <span class="tree-actions" v-else>
                  <el-button
                    size="small"
                    link
                    type="primary"
                    @click.stop="onGenerate(data.raw)"
                  >生成 →</el-button>
                  <el-button
                    size="small"
                    link
                    @click.stop="onEditKP(data.raw)"
                  >编辑</el-button>
                  <el-button
                    size="small"
                    link
                    type="danger"
                    @click.stop="onDeleteKP(data.raw)"
                  >删除</el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never" v-if="selectedKP">
          <template #header>
            <span class="kp-title">{{ selectedKP.title }}</span>
            <el-tag size="small" effect="plain" style="margin-left: 8px">
              {{ selectedKP.code }}
            </el-tag>
          </template>
          <p class="desc">{{ selectedKP.description || '（无描述）' }}</p>
          <el-divider />
          <div class="kw-section">
            <strong>关键词</strong>
            <div class="kw-list">
              <el-tag
                v-for="k in selectedKP.keywords"
                :key="k"
                size="small"
                effect="plain"
              >{{ k }}</el-tag>
              <span v-if="!selectedKP.keywords?.length" class="muted">（无）</span>
            </div>
          </div>
          <el-divider />
          <el-button
            type="primary"
            @click="$router.push({ path: '/generate', query: { kp: selectedKP.id } })"
          >
            <el-icon><MagicStick /></el-icon>
            <span>用此知识点生成题目</span>
          </el-button>
          <el-button @click="onEditKP(selectedKP)">
            <el-icon><Edit /></el-icon><span>编辑</span>
          </el-button>
        </el-card>
        <el-card shadow="never" v-else class="empty-card">
          <el-empty description="点击左侧某个知识点查看详情" />
        </el-card>
      </el-col>
    </el-row>

    <ChapterDialog
      v-model="chapterDialogVisible"
      :editing="editingChapter"
      :default-language="langStore.current"
      @saved="onChapterSaved"
    />

    <KnowledgePointDialog
      v-model="kpDialogVisible"
      :chapter="kpDialogChapter"
      :editing="editingKP"
      @saved="onKPSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { MagicStick, Plus, Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { learningPathApi } from '@/api'
import { useLanguageStore } from '@/stores/language'
import type { Chapter, ChapterWithKnowledgePoints } from '@/types/chapter'
import type { KnowledgePoint } from '@/types/knowledge_point'
import ChapterDialog from '@/components/ChapterDialog.vue'
import KnowledgePointDialog from '@/components/KnowledgePointDialog.vue'

interface TreeNode {
  key: string
  label: string
  code: string
  type: 'chapter' | 'kp'
  raw: any
  children?: TreeNode[]
}

const router = useRouter()
const langStore = useLanguageStore()
const tree = ref<ChapterWithKnowledgePoints[]>([])
const loading = ref(false)
const filterText = ref('')
const selectedKP = ref<KnowledgePoint | null>(null)
const treeRef = ref()

const chapterDialogVisible = ref(false)
const editingChapter = ref<Chapter | null>(null)

const kpDialogVisible = ref(false)
const kpDialogChapter = ref<Chapter | null>(null)
const editingKP = ref<KnowledgePoint | null>(null)

const treeProps = { children: 'children', label: 'label' }

const treeData = computed<TreeNode[]>(() =>
  tree.value.map((c) => ({
    key: `c-${c.id}`,
    label: c.title,
    code: c.code,
    type: 'chapter',
    raw: c,
    children: (c.knowledge_points ?? []).map((kp) => ({
      key: `k-${kp.id}`,
      label: kp.title,
      code: kp.code,
      type: 'kp' as const,
      raw: kp,
    })),
  })),
)

watch(filterText, (v) => treeRef.value?.filter(v))

function filterNode(value: string, data: any) {
  if (!value) return true
  return (
    String(data.label || '').includes(value) ||
    String(data.code || '').includes(value)
  )
}

function onNodeClick(data: TreeNode) {
  if (data.type === 'kp') {
    selectedKP.value = data.raw as KnowledgePoint
  }
}

async function load() {
  loading.value = true
  try {
    tree.value = await learningPathApi.tree(langStore.current)
  } finally {
    loading.value = false
  }
}

watch(() => langStore.current, () => {
  selectedKP.value = null
  load()
})

// ===== Chapter actions =====

function onCreateChapter() {
  editingChapter.value = null
  chapterDialogVisible.value = true
}

function onEditChapter(c: Chapter) {
  editingChapter.value = c
  chapterDialogVisible.value = true
}

async function onDeleteChapter(c: Chapter) {
  let info: { knowledge_points: number; exercises: number }
  try {
    info = await learningPathApi.chapterCascadeInfo(c.id)
  } catch {
    return
  }
  const msg =
    info.knowledge_points || info.exercises
      ? `章节 "${c.title}" 下有 ${info.knowledge_points} 个知识点和 ${info.exercises} 道题目，` +
        '删除章节将一并删除它们。此操作不可恢复，确定继续？'
      : `确定删除章节 "${c.title}"？`
  await ElMessageBox.confirm(msg, '删除确认', {
    type: 'warning',
    confirmButtonText: '确认删除',
    confirmButtonClass: 'el-button--danger',
  })
  await learningPathApi.deleteChapter(c.id)
  ElMessage.success('已删除')
  if (selectedKP.value && tree.value
      .find((ch) => ch.id === c.id)
      ?.knowledge_points
      ?.some((kp) => kp.id === selectedKP.value!.id)) {
    selectedKP.value = null
  }
  load()
}

function onChapterSaved() {
  load()
}

// ===== KP actions =====

function onAddKP(c: Chapter) {
  kpDialogChapter.value = c
  editingKP.value = null
  kpDialogVisible.value = true
}

function onEditKP(kp: KnowledgePoint) {
  // Locate the parent chapter for context (used by the dialog header).
  const parent = tree.value.find((c) => c.id === kp.chapter_id) as Chapter | undefined
  kpDialogChapter.value = parent ?? null
  editingKP.value = kp
  kpDialogVisible.value = true
}

async function onDeleteKP(kp: KnowledgePoint) {
  let info: { exercises: number }
  try {
    info = await learningPathApi.kpCascadeInfo(kp.id)
  } catch {
    return
  }
  const msg = info.exercises
    ? `知识点 "${kp.title}" 下有 ${info.exercises} 道题目，删除将一并清除。确定继续？`
    : `确定删除知识点 "${kp.title}"？`
  await ElMessageBox.confirm(msg, '删除确认', {
    type: 'warning',
    confirmButtonText: '确认删除',
    confirmButtonClass: 'el-button--danger',
  })
  await learningPathApi.deleteKP(kp.id)
  ElMessage.success('已删除')
  if (selectedKP.value?.id === kp.id) selectedKP.value = null
  load()
}

function onKPSaved(saved: KnowledgePoint) {
  if (selectedKP.value && selectedKP.value.id === saved.id) {
    selectedKP.value = saved
  }
  load()
}

function onGenerate(kp: KnowledgePoint) {
  router.push({ path: '/generate', query: { kp: kp.id } })
}

onMounted(load)
</script>

<style scoped>
.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
}

.tree-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tree-actions {
  visibility: hidden;
  display: flex;
  gap: 4px;
}

:deep(.el-tree-node__content:hover) .tree-actions {
  visibility: visible;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) .tree-actions {
  visibility: visible;
}

.kp-title {
  font-weight: 600;
  font-size: 16px;
}

.desc {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.kw-section strong {
  display: block;
  margin-bottom: 8px;
  color: #303133;
}

.kw-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.muted {
  color: #909399;
  font-size: 13px;
}

.empty-card {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
