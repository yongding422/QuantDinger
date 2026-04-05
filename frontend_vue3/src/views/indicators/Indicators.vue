<template>
  <div class="indicators-page">
    <div class="page-header">
      <h1>{{ $t('indicator.title') }}</h1>
      <a-button type="primary" @click="showCreateModal = true">
        <template #icon><PlusOutlined /></template>
        {{ $t('indicator.createIndicator') }}
      </a-button>
    </div>

    <!-- Indicators list -->
    <a-card class="indicators-card">
      <a-table
        :columns="columns"
        :data-source="store.indicators"
        :loading="store.loading"
        :pagination="{ pageSize: 20 }"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <strong>{{ record.name }}</strong>
            <div style="font-size: 11px; color: var(--color-text-secondary);">{{ record.type }}</div>
          </template>
          <template v-if="column.key === 'code'">
            <code style="font-size: 12px; background: var(--color-bg-hover); padding: 2px 6px; border-radius: 4px;">
              {{ record.code?.slice(0, 60) }}{{ record.code?.length > 60 ? '...' : '' }}
            </code>
          </template>
          <template v-if="column.key === 'actions'">
            <a-button type="link" size="small" @click="editIndicator(record)">{{ $t('common.edit') }}</a-button>
            <a-popconfirm :title="$t('common.confirmDelete')" @confirm="handleDelete(record.id)">
              <a-button type="link" danger size="small">{{ $t('common.delete') }}</a-button>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
      <a-empty v-if="!store.loading && store.indicators.length === 0" :description="$t('indicator.noIndicators')" />
    </a-card>

    <!-- Create/Edit modal -->
    <a-modal
      v-model:open="showCreateModal"
      :title="editingIndicator ? $t('indicator.editIndicator') : $t('indicator.createIndicator')"
      width="700px"
      @ok="handleSave"
      :confirm-loading="saving"
    >
      <a-form layout="vertical">
        <a-form-item :label="$t('indicator.indicatorName')" required>
          <a-input v-model:value="form.name" />
        </a-form-item>
        <a-form-item :label="$t('indicator.indicatorType')">
          <a-select v-model:value="form.type">
            <a-select-option value="momentum">Momentum</a-select-option>
            <a-select-option value="trend">Trend</a-select-option>
            <a-select-option value="volatility">Volatility</a-select-option>
            <a-select-option value="volume">Volume</a-select-option>
            <a-select-option value="custom">Custom</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="$t('indicator.indicatorCode')" required>
          <a-textarea v-model:value="form.code" :rows="8" placeholder="def calculate(prices): ..." />
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button @click="handleVerify" :loading="verifying">Verify Code</a-button>
            <a-button @click="handleAiGenerate" :loading="generating">AI Generate</a-button>
          </a-space>
          <div v-if="verifyResult" style="margin-top: 8px;">
            <a-alert :type="verifyResult.ok ? 'success' : 'error'" :message="verifyResult.msg" />
          </div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useIndicatorsStore, type Indicator } from '@/stores/indicators'
import { indicatorApi } from '@/api/indicator'

const store = useIndicatorsStore()
const showCreateModal = ref(false)
const editingIndicator = ref<Indicator | null>(null)
const saving = ref(false)
const verifying = ref(false)
const generating = ref(false)
const verifyResult = ref<{ ok: boolean; msg: string } | null>(null)

const form = reactive({ name: '', type: 'custom', code: '' })

const columns = [
  { title: 'Name', key: 'name' },
  { title: 'Type', dataIndex: 'type', key: 'type', width: 120 },
  { title: 'Code', key: 'code' },
  { title: 'Actions', key: 'actions', width: 160 },
]

onMounted(() => {
  store.fetchIndicators()
})

function editIndicator(ind: Indicator) {
  editingIndicator.value = ind
  form.name = ind.name
  form.type = ind.type || 'custom'
  form.code = ind.code
  showCreateModal.value = true
}

async function handleSave() {
  if (!form.name || !form.code) {
    message.error('Name and code are required')
    return
  }
  saving.value = true
  try {
    await store.saveIndicator({
      id: editingIndicator.value?.id,
      name: form.name,
      type: form.type,
      code: form.code,
    })
    message.success('Indicator saved')
    showCreateModal.value = false
    editingIndicator.value = null
    Object.assign(form, { name: '', type: 'custom', code: '' })
  } catch (e: unknown) {
    const err = e as { msg?: string }
    message.error(err.msg || 'Failed to save')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await store.deleteIndicator(id)
    message.success('Indicator deleted')
  } catch {
    message.error('Failed to delete')
  }
}

async function handleVerify() {
  verifying.value = true
  verifyResult.value = null
  try {
    const res = await indicatorApi.verifyCode(form.code)
    verifyResult.value = { ok: true, msg: 'Code is valid' }
  } catch {
    verifyResult.value = { ok: false, msg: 'Code has errors' }
  } finally {
    verifying.value = false
  }
}

async function handleAiGenerate() {
  generating.value = true
  try {
    const res = await indicatorApi.aiGenerate({ description: `${form.name || 'custom'} indicator` })
    form.code = res.data.data?.data?.code || ''
    message.success('Code generated')
  } catch {
    message.error('AI generation failed')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.indicators-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; }
.indicators-card { margin-bottom: 16px; }
</style>
