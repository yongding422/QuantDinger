<template>
  <div class="community-page">
    <div class="page-header">
      <h1>{{ $t('community.title') }}</h1>
      <a-button type="primary" @click="showShareModal = true">
        <template #icon><ShareAltOutlined /></template>
        Share Strategy
      </a-button>
    </div>

    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="browse" tab="Browse Strategies">
        <!-- Filters -->
        <a-space style="margin-bottom: 16px;">
          <a-input-search v-model:value="search" placeholder="Search strategies..." style="width: 240px;" @search="loadStrategies" />
          <a-select v-model:value="sortBy" style="width: 160px;" @change="loadStrategies">
            <a-select-option value="popular">Most Popular</a-select-option>
            <a-select-option value="recent">Most Recent</a-select-option>
            <a-select-option value="most_liked">Most Liked</a-select-option>
          </a-select>
        </a-space>

        <!-- Strategies grid -->
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12" :lg="8" v-for="s in strategies" :key="s.id">
            <a-card size="small" class="strategy-card" hoverable>
              <div class="strategy-header">
                <strong>{{ s.strategyName }}</strong>
                <span class="user-name">by {{ s.userName }}</span>
              </div>
              <p class="strategy-desc">{{ s.description || 'No description' }}</p>
              <div class="strategy-stats">
                <span><EyeOutlined /> {{ s.views }}</span>
                <span><LikeOutlined /> {{ s.likes }}</span>
                <span><CommentOutlined /> {{ s.commentCount || 0 }}</span>
              </div>
              <a-divider style="margin: 8px 0;" />
              <a-space>
                <a-button size="small" type="primary" @click="viewStrategy(s)">View</a-button>
                <a-button size="small" @click="handleLike(s)">
                  <component :is="s.isLiked ? LikeFilled : LikeOutlined" />
                </a-button>
              </a-space>
            </a-card>
          </a-col>
        </a-row>
        <a-empty v-if="!loading && strategies.length === 0" description="No strategies shared yet" style="margin-top: 48px;" />
      </a-tab-pane>

      <a-tab-pane key="my-shares" tab="My Shares">
        <a-list :data-source="myShares" size="default" item-layout="horizontal">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta
                :title="item.strategyName"
                :description="item.description"
              >
                <template #avatar><UserOutlined /></template>
              </a-list-item-meta>
              <template #actions>
                <a-button type="link" size="small" @click="viewStrategy(item)">View</a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
        <a-empty v-if="!loading && myShares.length === 0" description="You haven't shared any strategies yet" />
      </a-tab-pane>
    </a-tabs>

    <!-- Strategy detail modal -->
    <a-modal v-model:open="showDetailModal" title="Strategy Detail" width="700px" :footer="null">
      <div v-if="selectedStrategy">
        <h3>{{ selectedStrategy.strategyName }}</h3>
        <p><strong>By:</strong> {{ selectedStrategy.userName }}</p>
        <p><strong>Description:</strong> {{ selectedStrategy.description }}</p>
        <a-divider />
        <a-typography-title level="5">Code</a-typography-title>
        <pre class="code-block">{{ selectedStrategy.strategyCode }}</pre>
        <a-divider />
        <h4>Comments</h4>
        <a-list :data-source="comments" size="small">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta :title="item.userName" :description="item.content" />
            </a-list-item>
          </template>
        </a-list>
        <a-input-search v-model:value="newComment" placeholder="Add a comment..." @search="handleAddComment" style="margin-top: 8px;" />
      </div>
    </a-modal>

    <!-- Share modal -->
    <a-modal v-model:open="showShareModal" title="Share Strategy" @ok="handleShare">
      <a-form layout="vertical">
        <a-form-item label="Select Strategy" required>
          <a-select v-model:value="shareForm.strategyId" placeholder="Choose a strategy">
            <a-select-option v-for="s in availableStrategies" :key="s.id" :value="s.id">
              {{ s.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="Description">
          <a-textarea v-model:value="shareForm.description" :rows="3" placeholder="Describe your strategy..." />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ShareAltOutlined, EyeOutlined, LikeOutlined, LikeFilled, CommentOutlined, UserOutlined } from '@ant-design/icons-vue'
import { communityApi, type StrategyShare, type Comment } from '@/api/community'

const activeTab = ref('browse')
const loading = ref(false)
const strategies = ref<StrategyShare[]>([])
const myShares = ref<StrategyShare[]>([])
const comments = ref<Comment[]>([])
const selectedStrategy = ref<StrategyShare | null>(null)
const showDetailModal = ref(false)
const showShareModal = ref(false)
const newComment = ref('')
const sortBy = ref('popular')
const search = ref('')

const shareForm = reactive({ strategyId: undefined as number | undefined, description: '' })
const availableStrategies = ref<{ id: number; name: string }[]>([])

onMounted(() => {
  loadStrategies()
})

async function loadStrategies() {
  loading.value = true
  try {
    const res = await communityApi.getSharedStrategies({ sortBy: sortBy.value })
    strategies.value = res.data.data?.data?.items ?? []
  } finally { loading.value = false }
}

async function viewStrategy(s: StrategyShare) {
  selectedStrategy.value = s
  showDetailModal.value = true
  try {
    const res = await communityApi.getComments(s.id)
    comments.value = res.data.data?.data ?? []
  } catch {}
}

async function handleLike(s: StrategyShare) {
  try {
    if (s.isLiked) {
      await communityApi.unlikeStrategy(s.id)
      s.likes--
    } else {
      await communityApi.likeStrategy(s.id)
      s.likes++
    }
    s.isLiked = !s.isLiked
  } catch { message.error('Failed to like') }
}

async function handleAddComment() {
  if (!newComment.value.trim() || !selectedStrategy.value) return
  try {
    await communityApi.addComment(selectedStrategy.value.id, newComment.value)
    const res = await communityApi.getComments(selectedStrategy.value.id)
    comments.value = res.data.data?.data ?? []
    newComment.value = ''
  } catch { message.error('Failed to add comment') }
}

async function handleShare() {
  if (!shareForm.strategyId) { message.error('Select a strategy'); return }
  try {
    await communityApi.shareStrategy({ strategyId: shareForm.strategyId, description: shareForm.description })
    message.success('Strategy shared')
    showShareModal.value = false
    activeTab.value = 'my-shares'
  } catch { message.error('Failed to share') }
}
</script>

<style scoped>
.community-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; }
.strategy-card { height: 100%; }
.strategy-header { display: flex; justify-content: space-between; align-items: center; }
.user-name { font-size: 12px; color: #999; }
.strategy-desc { font-size: 13px; color: #666; min-height: 40px; }
.strategy-stats { display: flex; gap: 16px; font-size: 13px; color: #999; }
.strategy-stats span { display: flex; align-items: center; gap: 4px; }
.code-block { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 12px; max-height: 300px; }
</style>
