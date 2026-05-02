<template>
  <div class="page">
    <div class="page-header">
      <h2>学习路线</h2>
      <span class="hint">点知识点跳转到生成页</span>
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
            empty-text="加载中..."
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
                <span v-if="data.type === 'kp'" class="tree-actions">
                  <el-button size="small" link type="primary">生成 →</el-button>
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
        </el-card>
        <el-card shadow="never" v-else class="empty-card">
          <el-empty description="点击左侧某个知识点查看详情" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import { learningPathApi } from '@/api'
import { useLanguageStore } from '@/stores/language'
import type { ChapterWithKnowledgePoints } from '@/types/chapter'
import type { KnowledgePoint } from '@/types/knowledge_point'

interface TreeNode {
  key: string
  label: string
  code: string
  type: 'chapter' | 'kp'
  raw: any
  children?: TreeNode[]
}

const langStore = useLanguageStore()
const tree = ref<ChapterWithKnowledgePoints[]>([])
const loading = ref(false)
const filterText = ref('')
const selectedKP = ref<KnowledgePoint | null>(null)
const treeRef = ref()

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

onMounted(async () => {
  await load()
})

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
</script>

<style scoped>
.hint {
  color: #909399;
  font-size: 13px;
}

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
