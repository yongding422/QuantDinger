<template>
  <div class="equity-chart" :style="{ height: `${height}px` }">
    <svg v-if="points.length >= 2" :width="svgWidth" :height="height" class="chart-svg">
      <!-- Grid lines -->
      <g class="grid">
        <line
          v-for="(y, i) in gridYLines"
          :key="i"
          :x1="padding"
          :y1="y"
          :x2="svgWidth - padding"
          :y2="y"
          stroke="#e8e8e8"
          stroke-width="1"
        />
      </g>
      <!-- Area fill -->
      <path
        :d="areaPath"
        :fill="areaFill"
        stroke="none"
      />
      <!-- Line -->
      <path
        :d="linePath"
        fill="none"
        :stroke="lineColor"
        stroke-width="2"
        stroke-linejoin="round"
        stroke-linecap="round"
      />
      <!-- Hover dot + tooltip -->
      <g v-if="hoverIndex !== null && points[hoverIndex]">
        <circle
          :cx="hoverX"
          :cy="hoverY"
          r="5"
          :fill="lineColor"
          stroke="#fff"
          stroke-width="2"
        />
        <rect
          :x="tooltipX"
          :y="tooltipY - 50"
          width="140"
          height="44"
          rx="4"
          fill="rgba(0,0,0,0.8)"
        />
        <text
          :x="tooltipX + 8"
          :y="tooltipY - 34"
          fill="#fff"
          font-size="11"
          font-family="monospace"
        >
          {{ points[hoverIndex].date }}
        </text>
        <text
          :x="tooltipX + 8"
          :y="tooltipY - 18"
          fill="#fff"
          font-size="12"
          font-weight="600"
          font-family="monospace"
        >
          ${{ Number(points[hoverIndex].equity).toFixed(2) }}
        </text>
      </g>
      <!-- Invisible overlay for mouse events -->
      <rect
        :x="padding"
        y="0"
        :width="svgWidth - padding * 2"
        :height="height"
        fill="transparent"
        @mousemove="onMouseMove"
        @mouseleave="hoverIndex = null"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { EquityCurvePoint } from '@/api/strategies'

const props = withDefaults(
  defineProps<{
    data: EquityCurvePoint[]
    loading?: boolean
    height?: number
  }>(),
  { loading: false, height: 280 }
)

const padding = 40
const svgWidth = 800 // will be updated by container

const points = computed(() => props.data ?? [])

const minEquity = computed(() => Math.min(...points.value.map(p => p.equity)))
const maxEquity = computed(() => Math.max(...points.value.map(p => p.equity)))
const range = computed(() => maxEquity.value - minEquity.value || 1)

function scaleX(i: number) {
  const total = points.value.length - 1
  return padding + (i / total) * (svgWidth - padding * 2)
}

function scaleY(val: number) {
  return padding + ((maxEquity.value - val) / range.value) * (heightInner)
}

const heightInner = computed(() => props.height - padding * 2)

const linePath = computed(() => {
  return points.value
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i)} ${scaleY(p.equity)}`)
    .join(' ')
})

const areaFill = computed(() => {
  const last = points.value.length - 1
  return 'url(#equityGradient)'
})

// Dynamic gradient definition (injected once)
const gradientId = 'equityGradient'
const areaPath = computed(() => {
  if (points.value.length < 2) return ''
  const last = points.value.length - 1
  const bottom = props.height - padding
  const top = padding
  let d = `M ${scaleX(0)} ${bottom} `
  points.value.forEach((p, i) => {
    d += `L ${scaleX(i)} ${scaleY(p.equity)} `
  })
  d += `L ${scaleX(last)} ${bottom} Z`
  return d
})

const lineColor = computed(() => {
  const first = points.value[0]?.equity ?? 0
  const last = points.value[points.value.length - 1]?.equity ?? 0
  return last >= first ? '#52c41a' : '#ff4d4f'
})

// Hover state
const hoverIndex = ref<number | null>(null)
const hoverX = ref(0)
const hoverY = ref(0)
const tooltipX = ref(0)
const tooltipY = ref(0)

const height = computed(() => props.height)

function onMouseMove(e: MouseEvent) {
  const svg = (e.currentTarget as SVGElement).closest('svg') as SVGElement
  if (!svg) return
  svgWidth
  const rect = svg.getBoundingClientRect()
  const relX = e.clientX - rect.left
  const total = points.value.length - 1
  const rawIdx = ((relX - padding) / (svgWidth - padding * 2)) * total
  const idx = Math.max(0, Math.min(total, Math.round(rawIdx)))
  hoverIndex.value = idx
  hoverX.value = scaleX(idx)
  hoverY.value = scaleY(points.value[idx].equity)
  tooltipX.value = hoverX.value + 8 > svgWidth - 148 ? hoverX.value - 148 : hoverX.value + 8
  tooltipY.value = hoverY.value
}

const gridYLines = computed(() => {
  const count = 5
  return Array.from({ length: count }, (_, i) => {
    return padding + (i / (count - 1)) * heightInner.value
  })
})
</script>

<style scoped>
.equity-chart { width: 100%; overflow: hidden; }
.chart-svg { display: block; width: 100%; }
</style>
