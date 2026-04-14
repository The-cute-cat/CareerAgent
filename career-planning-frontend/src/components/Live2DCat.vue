<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as PIXI from 'pixi.js'
import mascotFallback from '@/assets/Mascot.png'

declare global {
  interface Window {
    PIXI?: typeof PIXI
    Live2DCubismCore?: unknown
    Live2D?: unknown
  }
}

const props = withDefaults(
  defineProps<{
    modelUrl?: string
    speakingText?: string
    active?: boolean
    draggable?: boolean
  }>(),
  {
    modelUrl: 'https://cdn.jsdelivr.net/npm/live2d-widget-model-hijiki@1.0.5/assets/hijiki.model.json',
    speakingText: '',
    active: false,
    draggable: false
  }
)

const container = ref<HTMLDivElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
const loadFailed = ref(false)

let app: PIXI.Application | null = null
let model: any = null
let resizeObserver: ResizeObserver | null = null
let idleTimer: number | null = null
let mouthTimer: number | null = null
let isDragging = false
let offsetX = 0
let offsetY = 0

const CUBISM_CORE_URL = 'https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js'
const CUBISM2_CORE_URL = 'https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js'

function isCubism2Model(modelUrl: string) {
  return /\.model\.json(?:[?#].*)?$/i.test(modelUrl)
}

function loadScript(src: string) {
  return new Promise<void>((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[data-live2d-core="${src}"]`)
    if (existing) {
      if (window.Live2DCubismCore) {
        resolve()
      } else {
        existing.addEventListener('load', () => resolve(), { once: true })
        existing.addEventListener('error', () => reject(new Error(`Failed to load ${src}`)), { once: true })
      }
      return
    }

    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.dataset.live2dCore = src
    script.onload = () => resolve()
    script.onerror = () => reject(new Error(`Failed to load ${src}`))
    document.head.appendChild(script)
  })
}

function fitModel() {
  if (!container.value || !app || !model) return

  const width = container.value.clientWidth || 220
  const height = container.value.clientHeight || 280
  app.renderer.resize(width, height)

  model.scale.set(1)
  model.anchor.set(0.5, 1)
  model.alpha = 1
  model.visible = true

  const bounds = model.getLocalBounds?.() ?? { width: model.width || 1, height: model.height || 1 }
  const modelWidth = Math.max(bounds.width || 0, 1)
  const modelHeight = Math.max(bounds.height || 0, 1)
  const scaleX = (width * 0.74) / modelWidth
  const scaleY = (height * 0.86) / modelHeight
  const scale = Math.max(Math.min(scaleX, scaleY), 0.0001)

  model.scale.set(scale)
  model.position.set(width / 2, height * 0.98)
}

function tryMotion(names: string[]) {
  if (!model) return
  for (const name of names) {
    try {
      model.motion(name)
      return
    } catch {
      continue
    }
  }
}

function tryExpression(names: string[]) {
  if (!model) return
  for (const name of names) {
    try {
      model.expression(name)
      return
    } catch {
      continue
    }
  }
}

function hoverEffect() {
  tryExpression(['Happy', 'happy', 'F01', 'f01'])
}

function clickAction() {
  tryMotion(['TapBody', 'tap_body', 'Idle', 'idle'])
  randomExpression()
}

function randomExpression() {
  const expressions = [
    ['Happy', 'happy', 'F01'],
    ['Angry', 'angry', 'F02'],
    ['Sad', 'sad', 'F03'],
    ['Neutral', 'neutral', 'F04']
  ]
  const picked = expressions[Math.floor(Math.random() * expressions.length)]!
  tryExpression(picked)
}

function speakExpression(text: string) {
  if (!text) return
  if (text.includes('高兴') || text.includes('开心') || text.includes('喜欢')) {
    tryExpression(['Happy', 'happy', 'F01'])
    return
  }
  if (text.includes('生气') || text.includes('压力') || text.includes('困难')) {
    tryExpression(['Angry', 'angry', 'F02'])
    return
  }
  if (text.includes('难过') || text.includes('失落')) {
    tryExpression(['Sad', 'sad', 'F03'])
    return
  }
  tryExpression(['Neutral', 'neutral', 'F04'])
}

function startIdleLoop() {
  stopLoops()
  idleTimer = window.setInterval(() => {
    tryMotion(['Idle', 'idle'])
    randomExpression()
  }, 4000)

  mouthTimer = window.setInterval(() => {
    tryMotion(['TapBody', 'tap_body'])
  }, 6000)
}

function stopLoops() {
  if (idleTimer) window.clearInterval(idleTimer)
  if (mouthTimer) window.clearInterval(mouthTimer)
  idleTimer = null
  mouthTimer = null
}

function startDrag(event: MouseEvent | TouchEvent) {
  if (!props.draggable || !container.value) return
  isDragging = true
  const point = 'touches' in event ? event.touches[0] : event
  if (!point) return
  const rect = container.value.getBoundingClientRect()
  offsetX = point.clientX - rect.left
  offsetY = point.clientY - rect.top
  container.value.style.left = `${rect.left}px`
  container.value.style.top = `${rect.top}px`
}

function stopDrag() {
  isDragging = false
}

function drag(event: MouseEvent | TouchEvent) {
  if (!props.draggable || !isDragging || !container.value) return
  const point = 'touches' in event ? event.touches[0] : event
  if (!point) return
  container.value.style.left = `${point.clientX - offsetX}px`
  container.value.style.top = `${point.clientY - offsetY}px`
}

async function initLive2D() {
  if (!canvas.value || !container.value) return

  try {
    window.PIXI = PIXI
    let Live2DModel: any

    if (isCubism2Model(props.modelUrl)) {
      if (!window.Live2D) {
        await loadScript(CUBISM2_CORE_URL)
      }
      ;({ Live2DModel } = await import('pixi-live2d-display/cubism2'))
    } else {
      if (!window.Live2DCubismCore) {
        await loadScript(CUBISM_CORE_URL)
      }
      ;({ Live2DModel } = await import('pixi-live2d-display/cubism4'))
    }

    app = new PIXI.Application({
      view: canvas.value,
      autoStart: true,
      backgroundAlpha: 0,
      antialias: true,
      autoDensity: true,
      resolution: window.devicePixelRatio || 1,
      width: container.value.clientWidth || 220,
      height: container.value.clientHeight || 280
    })

    model = await Live2DModel.from(props.modelUrl)
    app.stage.addChild(model)
    fitModel()
    window.setTimeout(() => fitModel(), 120)
    window.requestAnimationFrame(() => fitModel())
    startIdleLoop()

    resizeObserver = new ResizeObserver(() => fitModel())
    resizeObserver.observe(container.value)
  } catch (error) {
    console.error('Live2D init failed:', error)
    loadFailed.value = true
  }
}

onMounted(() => {
  initLive2D()
})

watch(
  () => props.speakingText,
  (text) => {
    speakExpression(text)
  }
)

watch(
  () => props.active,
  (active) => {
    if (active) {
      tryMotion(['TapBody', 'tap_body', 'Idle', 'idle'])
    }
  }
)

onBeforeUnmount(() => {
  stopLoops()
  resizeObserver?.disconnect()
  if (app) {
    app.destroy(true, { children: true })
  }
  model = null
  app = null
})
</script>

<template>
  <div
    ref="container"
    class="live2d-container"
    :class="{ draggable }"
    @mousedown="startDrag"
    @mouseup="stopDrag"
    @mouseleave="stopDrag"
    @mousemove="drag"
    @touchstart="startDrag"
    @touchmove="drag"
    @touchend="stopDrag"
    @mouseenter="hoverEffect"
    @click="clickAction"
  >
    <canvas v-show="!loadFailed" ref="canvas"></canvas>
    <img v-if="loadFailed" :src="mascotFallback" alt="Pixie" class="live2d-fallback" />
  </div>
</template>

<style scoped>
.live2d-container {
  position: relative;
  width: 220px;
  height: 280px;
  cursor: default;
  user-select: none;
}

.live2d-container.draggable {
  position: fixed;
  left: 10px;
  top: 10px;
  cursor: grab;
  z-index: 9999;
}

canvas,
.live2d-fallback {
  display: block;
  width: 100%;
  height: 100%;
}

.live2d-fallback {
  object-fit: contain;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.15));
}
</style>
