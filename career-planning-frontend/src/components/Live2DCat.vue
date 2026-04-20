<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Application } from 'pixi.js'
import * as PIXI from 'pixi.js'
import mascotFallback from '@/assets/Mascot.png'

declare global {
  interface Window {
    PIXI?: typeof PIXI
    Live2DCubismCore?: unknown
    Live2D?: unknown
  }
}

interface Live2DPointLike {
  set: (x?: number, y?: number) => void
}

interface Live2DAnchorLike {
  set: (x?: number, y?: number) => void
}

interface Live2DBoundsLike {
  width?: number
  height?: number
}

interface Live2DModelLike {
  scale: Live2DPointLike
  anchor?: Live2DAnchorLike
  position: Live2DPointLike
  alpha: number
  visible: boolean
  width?: number
  height?: number
  getLocalBounds?: () => Live2DBoundsLike
  motion?: (name: string) => void
  expression?: (name: string) => void
  destroy?: (options?: unknown) => void
}

type Live2DModelFactory = {
  from: (modelUrl: string) => Promise<Live2DModelLike>
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
    draggable: false,
  },
)

const containerRef = ref<HTMLDivElement | null>(null)
const loadFailed = ref(false)

let app: Application | null = null
let model: Live2DModelLike | null = null
let resizeObserver: ResizeObserver | null = null
let intersectionObserver: IntersectionObserver | null = null
let lazyInitialized = false
let disposed = false
let activeInitId = 0
let idleTimer: number | null = null
let mouthTimer: number | null = null
let visibilityPaused = false
let dragPointerId: number | null = null
let dragOffsetX = 0
let dragOffsetY = 0
let lastExpressionAt = 0
let throttledSpeakTimer: number | null = null

const CUBISM4_CORE_URL = 'https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js'
const CUBISM2_CORE_URL = 'https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js'
const EXPRESSION_THROTTLE = 260

function supportsPixiInit(instance: Application): instance is Application & {
  init: (options: Record<string, unknown>) => Promise<void>
} {
  return typeof (instance as Application & { init?: unknown }).init === 'function'
}

function resolvePixiView(instance: Application): HTMLCanvasElement | null {
  const appWithCanvas = instance as Application & {
    canvas?: HTMLCanvasElement
    view?: HTMLCanvasElement
  }

  if (appWithCanvas.canvas instanceof HTMLCanvasElement) return appWithCanvas.canvas
  if (appWithCanvas.view instanceof HTMLCanvasElement) return appWithCanvas.view
  return null
}

function isCubism2Model(modelUrl: string): boolean {
  return /\.model\.json(?:[?#].*)?$/i.test(modelUrl)
}

function clearTimers(): void {
  if (idleTimer !== null) window.clearInterval(idleTimer)
  if (mouthTimer !== null) window.clearInterval(mouthTimer)
  if (throttledSpeakTimer !== null) window.clearTimeout(throttledSpeakTimer)
  idleTimer = null
  mouthTimer = null
  throttledSpeakTimer = null
}

function loadScript(src: string, runtimeType: 'cubism2' | 'cubism4') {
  return new Promise<void>((resolve, reject) => {
    const allowedDomains = ['cubism.live2d.com', 'cdn.jsdelivr.net']
    try {
      const url = new URL(src)
      if (!allowedDomains.includes(url.hostname)) {
        reject(new Error(`Unsafe script source: ${src}`))
        return
      }
    } catch {
      reject(new Error(`Invalid script url: ${src}`))
      return
    }

    const existing = document.querySelector<HTMLScriptElement>(`script[data-live2d-core="${CSS.escape(src)}"]`)
    const runtimeReady = runtimeType === 'cubism2' ? Boolean(window.Live2D) : Boolean(window.Live2DCubismCore)

    if (existing) {
      if (runtimeReady) {
        resolve()
        return
      }
      existing.addEventListener('load', () => resolve(), { once: true })
      existing.addEventListener('error', () => reject(new Error(`Failed to load runtime script: ${src}`)), { once: true })
      return
    }

    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.dataset.live2dCore = src

    const timeoutId = window.setTimeout(() => {
      reject(new Error(`Script load timeout: ${src}`))
      script.remove()
    }, 30000)

    script.onload = () => {
      window.clearTimeout(timeoutId)
      resolve()
    }
    script.onerror = () => {
      window.clearTimeout(timeoutId)
      reject(new Error(`Failed to load runtime script: ${src}`))
    }
    document.head.appendChild(script)
  })
}

async function resolveLive2DFactory(modelUrl: string): Promise<Live2DModelFactory> {
  if (isCubism2Model(modelUrl)) {
    if (!window.Live2D) await loadScript(CUBISM2_CORE_URL, 'cubism2')
    const module = await import('pixi-live2d-display/cubism2')
    return module.Live2DModel as unknown as Live2DModelFactory
  }

  if (!window.Live2DCubismCore) await loadScript(CUBISM4_CORE_URL, 'cubism4')
  const module = await import('pixi-live2d-display/cubism4')
  return module.Live2DModel as unknown as Live2DModelFactory
}

function fitModel(): void {
  const container = containerRef.value
  if (!container || !app || !app.renderer || !model) return

  const width = Math.max(container.clientWidth || 0, 1)
  const height = Math.max(container.clientHeight || 0, 1)

  app.renderer.resize(width, height)
  model.scale.set(1, 1)
  if (model.anchor?.set) model.anchor.set(0.5, 1)
  model.alpha = 1
  model.visible = true

  const bounds = model.getLocalBounds?.() ?? { width: model.width ?? 0, height: model.height ?? 0 }
  const rawWidth = Math.max(bounds.width ?? model.width ?? 100, 1)
  const rawHeight = Math.max(bounds.height ?? model.height ?? 100, 1)

  const scaleX = (width * 0.72) / rawWidth
  const scaleY = (height * 0.88) / rawHeight
  const scale = Math.max(Math.min(scaleX, scaleY), 0.0001)

  model.scale.set(scale, scale)
  model.position.set(width / 2, height * 0.98)
}

function tryMotion(names: string[]): void {
  if (!model?.motion || visibilityPaused) return
  for (const name of names) {
    try {
      model.motion(name)
      return
    } catch {
      continue
    }
  }
}

function tryExpression(names: string[]): void {
  if (!model?.expression || visibilityPaused) return
  for (const name of names) {
    try {
      model.expression(name)
      return
    } catch {
      continue
    }
  }
}

function randomExpression(): void {
  const expressions = [
    ['Happy', 'happy', 'F01'],
    ['Angry', 'angry', 'F02'],
    ['Sad', 'sad', 'F03'],
    ['Neutral', 'neutral', 'F04'],
  ]
  const picked = expressions[Math.floor(Math.random() * expressions.length)]!
  tryExpression(picked)
}

function speakExpression(text: string): void {
  const run = () => {
    if (!text) return
    const normalized = text.toLowerCase()

    if (normalized.includes('高兴') || normalized.includes('喜欢') || normalized.includes('完成')) {
      tryExpression(['Happy', 'happy', 'F01'])
      return
    }
    if (normalized.includes('压力') || normalized.includes('困难') || normalized.includes('生气')) {
      tryExpression(['Angry', 'angry', 'F02'])
      return
    }
    if (normalized.includes('难过') || normalized.includes('失落')) {
      tryExpression(['Sad', 'sad', 'F03'])
      return
    }
    tryExpression(['Neutral', 'neutral', 'F04'])
  }

  const now = Date.now()
  const delta = now - lastExpressionAt
  if (delta >= EXPRESSION_THROTTLE) {
    lastExpressionAt = now
    run()
    return
  }

  if (throttledSpeakTimer !== null) window.clearTimeout(throttledSpeakTimer)
  throttledSpeakTimer = window.setTimeout(() => {
    lastExpressionAt = Date.now()
    throttledSpeakTimer = null
    run()
  }, EXPRESSION_THROTTLE - delta)
}

function startIdleLoop(): void {
  clearTimers()
  if (visibilityPaused) return

  idleTimer = window.setInterval(() => {
    tryMotion(['Idle', 'idle'])
    randomExpression()
  }, 4000)

  mouthTimer = window.setInterval(() => {
    tryMotion(['TapBody', 'tap_body'])
  }, 6500)
}

function teardownLive2D(): void {
  clearTimers()
  resizeObserver?.disconnect()
  resizeObserver = null

  if (model) {
    try {
      model.destroy?.({ children: true })
    } catch (error) {
      console.warn('[Live2D] model destroy warning:', error)
    }
    model = null
  }

  if (app) {
    try {
      app.destroy(true)
    } catch (error) {
      console.warn('[Live2D] app destroy warning:', error)
    }
    app = null
  }

  const container = containerRef.value
  if (container) container.querySelector('canvas')?.remove()
}

async function initPixiApp(container: HTMLDivElement, initId: number) {
  const width = Math.max(container.clientWidth || 220, 1)
  const height = Math.max(container.clientHeight || 280, 1)
  const baseOptions = {
    autoStart: true,
    backgroundAlpha: 0,
    antialias: true,
    autoDensity: true,
    resolution: window.devicePixelRatio || 1,
    width,
    height,
  }

  let instance: Application | undefined
  try {
    const testApp = new Application()
    const isV8 = supportsPixiInit(testApp)
    testApp.destroy(true)
    instance = isV8 ? new Application() : new Application(baseOptions as ConstructorParameters<typeof Application>[0])
    if (supportsPixiInit(instance)) await instance.init(baseOptions)
  } catch (error) {
    instance?.destroy(true)
    throw error
  }

  if (disposed || initId !== activeInitId) {
    instance.destroy(true)
    throw new Error('Live2D init expired')
  }

  const canvasElement = resolvePixiView(instance)
  if (!canvasElement) {
    instance.destroy(true)
    throw new Error('Canvas create failed')
  }

  container.appendChild(canvasElement)
  canvasElement.classList.add('live2d-canvas')
  return instance
}

async function initLive2D(): Promise<void> {
  const container = containerRef.value
  const initId = ++activeInitId
  loadFailed.value = false
  teardownLive2D()

  if (!container) return

  try {
    window.PIXI = PIXI
    const factory = await resolveLive2DFactory(props.modelUrl)
    if (disposed || initId !== activeInitId) return

    const pixiApp = await initPixiApp(container, initId)
    if (disposed || initId !== activeInitId) {
      pixiApp.destroy(true)
      return
    }

    app = pixiApp
    const live2DModel = await factory.from(props.modelUrl)
    if (disposed || initId !== activeInitId || !app?.stage) {
      live2DModel.destroy?.({ children: true })
      return
    }

    model = live2DModel
    app.stage.addChild(model as never)
    fitModel()

    resizeObserver = new ResizeObserver(() => fitModel())
    resizeObserver.observe(container)
    startIdleLoop()
  } catch (error) {
    console.error('[Live2D] init failed:', error)
    loadFailed.value = true
    teardownLive2D()
  }
}

function maybeInitLive2D(): void {
  if (lazyInitialized || !containerRef.value) return
  lazyInitialized = true
  nextTick(() => {
    initLive2D()
  })
}

function handleVisibilityChange(): void {
  visibilityPaused = document.hidden
  if (visibilityPaused) {
    clearTimers()
    return
  }
  if (model) {
    startIdleLoop()
    if (props.active) tryMotion(['TapBody', 'tap_body', 'Idle', 'idle'])
  } else {
    maybeInitLive2D()
  }
}

function updateDragPosition(clientX: number, clientY: number): void {
  const container = containerRef.value
  if (!container) return
  container.style.left = `${clientX - dragOffsetX}px`
  container.style.top = `${clientY - dragOffsetY}px`
}

function onPointerDown(event: PointerEvent): void {
  if (!props.draggable || !containerRef.value) return
  dragPointerId = event.pointerId
  const rect = containerRef.value.getBoundingClientRect()
  dragOffsetX = event.clientX - rect.left
  dragOffsetY = event.clientY - rect.top
  containerRef.value.style.left = `${rect.left}px`
  containerRef.value.style.top = `${rect.top}px`
  containerRef.value.setPointerCapture(event.pointerId)
}

function onPointerMove(event: PointerEvent): void {
  if (!props.draggable || dragPointerId !== event.pointerId) return
  updateDragPosition(event.clientX, event.clientY)
}

function endPointerDrag(event?: PointerEvent): void {
  if (event && dragPointerId === event.pointerId) {
    containerRef.value?.releasePointerCapture(event.pointerId)
  }
  dragPointerId = null
}

onMounted(() => {
  disposed = false

  if ('IntersectionObserver' in window) {
    intersectionObserver = new IntersectionObserver((entries) => {
      if (entries.some(entry => entry.isIntersecting)) {
        maybeInitLive2D()
        intersectionObserver?.disconnect()
        intersectionObserver = null
      }
    }, { threshold: 0.15 })

    if (containerRef.value) intersectionObserver.observe(containerRef.value)
  } else {
    maybeInitLive2D()
  }

  document.addEventListener('visibilitychange', handleVisibilityChange)
})

watch(
  () => props.modelUrl,
  async (nextUrl, prevUrl) => {
    if (nextUrl === prevUrl) return
    lazyInitialized = true
    await initLive2D()
  },
)

watch(
  () => props.speakingText,
  (text) => {
    speakExpression(text)
  },
)

watch(
  () => props.active,
  (active) => {
    if (active) {
      tryMotion(['TapBody', 'tap_body', 'Idle', 'idle'])
      randomExpression()
    } else if (!visibilityPaused) {
      startIdleLoop()
    }
  },
)

onBeforeUnmount(() => {
  disposed = true
  activeInitId += 1
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  intersectionObserver?.disconnect()
  intersectionObserver = null
  endPointerDrag()
  teardownLive2D()
})
</script>

<template>
  <div
    ref="containerRef"
    class="live2d-container"
    :class="{ draggable }"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="endPointerDrag"
    @pointercancel="endPointerDrag"
    @pointerleave="endPointerDrag"
  >
    <img v-if="loadFailed" :src="mascotFallback" alt="Pixie" class="live2d-fallback" />
  </div>
</template>

<style scoped>
.live2d-container {
  position: relative;
  width: 220px;
  height: 280px;
  overflow: hidden;
  user-select: none;
}

.live2d-container.draggable {
  position: fixed;
  left: 10px;
  top: 10px;
  z-index: 9999;
  touch-action: none;
  cursor: grab;
}

.live2d-container.draggable:active {
  cursor: grabbing;
}

.live2d-container:deep(.live2d-canvas),
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
