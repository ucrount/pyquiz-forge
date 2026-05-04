<template>
  <div class="page learning-page">
    <div class="page-header">
      <h2>LEARNING PATH</h2>
      <el-button type="primary" @click="onCreateChapter">
        <el-icon><Plus /></el-icon><span>新建章节</span>
      </el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="9">
        <CyberCard accent="cyan" class="tree-card">
          <template #header>
            <span class="cyber-card__title">▸ 章节 / 知识点</span>
          </template>
          <template #extra>
            <span class="mono small-stat">{{ flatKpCount }}</span>
          </template>

          <el-input
            v-model="treeFilter"
            placeholder="搜索章节 / 知识点..."
            clearable
            size="small"
            style="margin-bottom: 10px"
          />

          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="key"
            :filter-node-method="filterNode"
            :expand-on-click-node="false"
            :default-expanded-keys="defaultExpandedKeys"
            :current-node-key="selectedKey ?? undefined"
            highlight-current
            empty-text="该语言暂无章节"
            @node-click="onNodeClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <span class="tree-label">
                  <span v-if="data.type === 'kp'" class="mastery-icon" :style="{ color: data.masteryColor }">
                    {{ data.masteryIcon }}
                  </span>
                  <el-tag
                    v-if="data.type === 'chapter'"
                    size="small"
                    type="info"
                    effect="plain"
                  >{{ data.code }}</el-tag>
                  <el-tag
                    v-else
                    size="small"
                    type="primary"
                    effect="plain"
                  >{{ data.code }}</el-tag>
                  <span class="tree-text">{{ node.label }}</span>
                </span>
                <span class="tree-actions" v-if="data.type === 'chapter'">
                  <el-button size="small" link type="primary" @click.stop="onAddKP(data.raw)">+ 知识点</el-button>
                  <el-button size="small" link @click.stop="onEditChapter(data.raw)">编辑</el-button>
                  <el-button size="small" link type="danger" @click.stop="onDeleteChapter(data.raw)">删除</el-button>
                </span>
                <span class="tree-actions" v-else>
                  <el-button size="small" link @click.stop="onEditKP(data.raw)">编辑</el-button>
                  <el-button size="small" link type="danger" @click.stop="onDeleteKP(data.raw)">删除</el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </CyberCard>
      </el-col>

      <el-col :span="15">
        <CyberCard accent="purple" class="detail-card">
          <KnowledgePointDetail
            :kp="selectedKP"
            :prev="prevKp"
            :next="nextKp"
            @updated="onKpUpdated"
            @navigate="onNavigateKp"
          />
        </CyberCard>
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
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { learningPathApi } from '@/api'
import { useLanguageStore } from '@/stores/language'
import { MASTERY_COLOR, MASTERY_ICON, type Mastery } from '@/types/common'
import type { Chapter, ChapterWithKnowledgePoints } from '@/types/chapter'
import type { KnowledgePoint } from '@/types/knowledge_point'
import ChapterDialog from '@/components/ChapterDialog.vue'
import KnowledgePointDialog from '@/components/KnowledgePointDialog.vue'
import KnowledgePointDetail from '@/components/KnowledgePointDetail.vue'
import CyberCard from '@/components/CyberCard.vue'

interface TreeNode {
  key: string
  label: string
  code: string
  type: 'chapter' | 'kp'
  raw: any
  masteryIcon?: string
  masteryColor?: string
  children?: TreeNode[]
}

const route = useRoute()
const router = useRouter()
const langStore = useLanguageStore()
const tree = ref<ChapterWithKnowledgePoints[]>([])
const treeFilter = ref('')
const selectedKP = ref<KnowledgePoint | null>(null)
const treeRef = ref()

const chapterDialogVisible = ref(false)
const editingChapter = ref<Chapter | null>(null)
const kpDialogVisible = ref(false)
const kpDialogChapter = ref<Chapter | null>(null)
const editingKP = ref<KnowledgePoint | null>(null)

const treeProps = { children: 'children', label: 'label' }

const flatKpList = computed(() => {
  const list: KnowledgePoint[] = []
  for (const c of tree.value) for (const kp of c.knowledge_points ?? []) list.push(kp)
  return list
})

const flatKpCount = computed(() => flatKpList.value.length)

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
      masteryIcon: kp.mastery !== 'not_started' ? MASTERY_ICON[kp.mastery as Mastery] : '',
      masteryColor: MASTERY_COLOR[kp.mastery as Mastery] ?? '',
    })),
  })),
)

const selectedKey = computed(() =>
  selectedKP.value ? `k-${selectedKP.value.id}` : null,
)

const defaultExpandedKeys = computed(() => {
  if (selectedKP.value) {
    return [`c-${selectedKP.value.chapter_id}`]
  }
  if (tree.value.length > 0) {
    return [`c-${tree.value[0].id}`]
  }
  return []
})

// Prev / Next within the flat KP list
const prevKp = computed<KnowledgePoint | null>(() => {
  if (!selectedKP.value) return null
  const idx = flatKpList.value.findIndex((k) => k.id === selectedKP.value!.id)
  return idx > 0 ? flatKpList.value[idx - 1] : null
})
const nextKp = computed<KnowledgePoint | null>(() => {
  if (!selectedKP.value) return null
  const idx = flatKpList.value.findIndex((k) => k.id === selectedKP.value!.id)
  return idx >= 0 && idx < flatKpList.value.length - 1
    ? flatKpList.value[idx + 1]
    : null
})

watch(treeFilter, (v) => treeRef.value?.filter(v))

watch(() => langStore.current, () => {
  selectedKP.value = null
  load()
})

watch(
  () => route.query.kp,
  (kp) => {
    if (kp) {
      const id = Number(kp)
      const target = flatKpList.value.find((k) => k.id === id)
      if (target) {
        selectedKP.value = target
      }
    }
  },
)

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
  tree.value = await learningPathApi.tree(langStore.current)
  // After reload, if there's a ?kp= query, select that one
  await nextTick()
  const kpFromQuery = route.query.kp ? Number(route.query.kp) : null
  if (kpFromQuery) {
    const t = flatKpList.value.find((k) => k.id === kpFromQuery)
    if (t) selectedKP.value = t
  }
}

function onKpUpdated(updated: KnowledgePoint) {
  // Update local tree array so mastery icon / content reflect immediately
  for (const c of tree.value) {
    const idx = (c.knowledge_points ?? []).findIndex((k) => k.id === updated.id)
    if (idx >= 0) {
      c.knowledge_points![idx] = updated
      break
    }
  }
  if (selectedKP.value && selectedKP.value.id === updated.id) {
    selectedKP.value = updated
  }
}

function onNavigateKp(target: KnowledgePoint) {
  selectedKP.value = target
  // Update URL so deep link works
  router.replace({ path: '/learning-path', query: { kp: target.id } })
}

// === Chapter actions ===
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
  } catch { return }
  const msg =
    info.knowledge_points || info.exercises
      ? `章节「${c.title}」下有 ${info.knowledge_points} 个知识点和 ${info.exercises} 道题目，删除会一并清除。继续？`
      : `确定删除章节「${c.title}」？`
  await ElMessageBox.confirm(msg, '删除确认', {
    type: 'warning',
    confirmButtonText: '确认删除',
    confirmButtonClass: 'el-button--danger',
  })
  await learningPathApi.deleteChapter(c.id)
  ElMessage.success('已删除')
  if (selectedKP.value?.chapter_id === c.id) selectedKP.value = null
  load()
}
function onChapterSaved() { load() }

// === KP actions ===
function onAddKP(c: Chapter) {
  kpDialogChapter.value = c
  editingKP.value = null
  kpDialogVisible.value = true
}
function onEditKP(kp: KnowledgePoint) {
  const parent = tree.value.find((c) => c.id === kp.chapter_id) as Chapter | undefined
  kpDialogChapter.value = parent ?? null
  editingKP.value = kp
  kpDialogVisible.value = true
}
async function onDeleteKP(kp: KnowledgePoint) {
  let info: { exercises: number }
  try {
    info = await learningPathApi.kpCascadeInfo(kp.id)
  } catch { return }
  const msg = info.exercises
    ? `知识点「${kp.title}」下有 ${info.exercises} 道题目，删除将一并清除。继续？`
    : `确定删除知识点「${kp.title}」？`
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
  if (selectedKP.value?.id === saved.id) selectedKP.value = saved
  load()
}

onMounted(load)
</script>

<style scoped>
.learning-page {
  /* 锁住整个页面高度，禁止页面级滚动 */
  height: calc(100vh - 64px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.learning-page :deep(.el-row) {
  flex: 1;
  min-height: 0;
}

.learning-page :deep(.el-col) {
  height: 100%;
}

.tree-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-card :deep(.cyber-card__body) {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.tree-card :deep(.el-tree) {
  background: transparent;
  flex: 1;
}

.detail-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-card :deep(.cyber-card__body) {
  flex: 1;
  min-height: 0;
  padding: 14px 20px;
  display: flex;
  flex-direction: column;
}

.small-stat {
  color: var(--neon-cyan);
  font-size: 12px;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
  font-size: 13px;
}

.tree-label {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.tree-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mastery-icon {
  font-size: 13px;
  width: 14px;
  text-align: center;
  display: inline-block;
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
</style>
