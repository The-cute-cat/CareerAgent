<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Application } from 'pixi.js'
import * as PIXI from 'pixi.js'
import mascotFallback from '@/assets/Mascot.png'

/**
 * 兼容性说明
 * 当前项目 package-lock / node_modules 实际安装的是：
 * - pixi.js: 6.5.10
 * - pixi-live2d-display: 0.4.0
 *
 * 这组依赖本身是兼容的，因此本组件现在优先兼容 PixiJS v6，
 * 同时保留对 PixiJS v8 Application.init() 的分支支持。
 *

 * 若后续你再次升级到 Pixi v8：
 * - 本组件会优先尝试 app.init()
 * - 但 pixi-live2d-display 0.4.0 官方仍主要面向 Pixi v6
 * - 正式方案依然建议同步升级/替换 Live2D 库，而不是只升 Pixi
 */

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
let idleTimer: number | null = null
let mouthTimer: number | null = null
let activeInitId = 0
let disposed = false

let isDragging = false
let dragOffsetX = 0
let dragOffsetY = 0

const CUBISM4_CORE_URL = 'https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js'
const CUBISM2_CORE_URL = 'https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js'

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

  if (appWithCanvas.canvas instanceof HTMLCanvasElement) {
    return appWithCanvas.canvas
  }

  if (appWithCanvas.view instanceof HTMLCanvasElement) {
    return appWithCanvas.view
  }

  return null
}

function isCubism2Model(modelUrl: string): boolean {
  return /\.model\.json(?:[?#].*)?$/i.test(modelUrl)
}

function clearTimers() {
  if (idleTimer !== null) {
    window.clearInterval(idleTimer)
    idleTimer = null
  }

  if (mouthTimer !== null) {
    window.clearInterval(mouthTimer)
    mouthTimer = null
  }
}

function stopDrag() {
  isDragging = false
}

function startDrag(event: MouseEvent | TouchEvent) {
  if (!props.draggable || !containerRef.value) return

  const point = 'touches' in event ? event.touches[0] : event
  if (!point) return

  isDragging = true
  const rect = containerRef.value.getBoundingClientRect()
  dragOffsetX = point.clientX - rect.left
  dragOffsetY = point.clientY - rect.top

  containerRef.value.style.left = `${rect.left}px`
  containerRef.value.style.top = `${rect.top}px`
}

function drag(event: MouseEvent | TouchEvent) {
  if (!props.draggable || !isDragging || !containerRef.value) return

  const point = 'touches' in event ? event.touches[0] : event
  if (!point) return

  containerRef.value.style.left = `${point.clientX - dragOffsetX}px`
  containerRef.value.style.top = `${point.clientY - dragOffsetY}px`
}

function loadScript(src: string, runtimeType: 'cubism2' | 'cubism4') {
  return new Promise<void>((resolve, reject) => {
    // 只允许加载白名单内的 CDN 脚本，防止 XSS
    const allowedDomains = [
      'cubism.live2d.com',
      'cdn.jsdelivr.net',
    ]
    try {
      const url = new URL(src)
      if (!allowedDomains.includes(url.hostname)) {
        reject(new Error(`不安全的脚本源: ${src}`))
        return
      }
    } catch {
      reject(new Error(`无效的脚本 URL: ${src}`))
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
      existing.addEventListener('error', () => reject(new Error(`Failed to load runtime script: ${src}`)), {
        once: true,
      })
      return
    }

    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.dataset.live2dCore = src

    // 添加加载超时处理
    const timeoutId = window.setTimeout(() => {
      reject(new Error(`脚本加载超时: ${src}`))
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
    if (!window.Live2D) {
      await loadScript(CUBISM2_CORE_URL, 'cubism2')
    }

    const module = await import('pixi-live2d-display/cubism2')
    return module.Live2DModel as unknown as Live2DModelFactory
  }

  if (!window.Live2DCubismCore) {
    await loadScript(CUBISM4_CORE_URL, 'cubism4')
  }

  const module = await import('pixi-live2d-display/cubism4')
  return module.Live2DModel as unknown as Live2DModelFactory
}

function fitModel() {
  const container = containerRef.value

  if (!container || !app || !app.renderer || !model) {
    return
  }

  const width = Math.max(container.clientWidth || 0, 1)
  const height = Math.max(container.clientHeight || 0, 1)

  app.renderer.resize(width, height)

  model.scale.set(1, 1)
  if (model.anchor?.set) {
    model.anchor.set(0.5, 1)
  }
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

function tryMotion(names: string[]) {
  if (!model?.motion) return

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
  if (!model?.expression) return

  for (const name of names) {
    try {
      model.expression(name)
      return
    } catch {
      continue
    }
  }
}

function randomExpression() {
  const expressions = [
    ['Happy', 'happy', 'F01'],
    ['Angry', 'angry', 'F02'],
    ['Sad', 'sad', 'F03'],
    ['Neutral', 'neutral', 'F04'],
  ]

  const picked = expressions[Math.floor(Math.random() * expressions.length)]!
  tryExpression(picked)
}

function hoverEffect() {
  tryExpression(['Happy', 'happy', 'F01', 'f01'])
}

function clickAction() {
  tryMotion(['TapBody', 'tap_body', 'Idle', 'idle'])
  randomExpression()
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
  clearTimers()

  idleTimer = window.setInterval(() => {
    tryMotion(['Idle', 'idle'])
    randomExpression()
  }, 4000)

  mouthTimer = window.setInterval(() => {
    tryMotion(['TapBody', 'tap_body'])
  }, 6000)
}

function teardownLive2D() {
  clearTimers()
  resizeObserver?.disconnect()
  resizeObserver = null

  if (model) {
    try {
      model.destroy?.({ children: true })
    } catch (error) {
      console.warn('[Live2D] 模型销毁时出现警告:', error)
    }
    model = null
  }

  if (app) {
    try {
      app.destroy(true)
    } catch (error) {
      console.warn('[Live2D] Pixi 实例销毁时出现警告:', error)
    }
    app = null
  }

  const container = containerRef.value
  if (container) {
    container.querySelector('canvas')?.remove()
  }
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
    /**
     * Pixi v8: new Application(); await app.init(options)
     * Pixi v6: new Application(options)
     */
    const testApp = new Application()
    const isV8 = supportsPixiInit(testApp)
    testApp.destroy(true)

    instance = isV8 ? new Application() : new Application(baseOptions as ConstructorParameters<typeof Application>[0])

    if (supportsPixiInit(instance)) {
      await instance.init(baseOptions)
    }
  } catch (error) {
    if (instance) {
      try {
        instance.destroy(true)
      } catch {
        // 忽略销毁时的错误
      }
    }
    console.error('[Live2D] Pixi 初始化失败:', error)
    throw new Error('Pixi 初始化失败')
  }

  if (disposed || initId !== activeInitId) {
    instance.destroy(true)
    throw new Error('组件已销毁或初始化已过期')
  }

  const canvasElement = resolvePixiView(instance)
  if (!canvasElement) {
    instance.destroy(true)
    throw new Error('Pixi 画布创建失败：未获取到 app.view / app.canvas')
  }

  container.appendChild(canvasElement)
  canvasElement.classList.add('live2d-canvas')

  return instance
}

async function initLive2D() {
  const container = containerRef.value
  const initId = ++activeInitId

  loadFailed.value = false
  teardownLive2D()

  if (!container) {
    console.error('[Live2D] 初始化终止: 组件容器不存在')
    loadFailed.value = true
    return
  }

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

    let live2DModel: Live2DModelLike
    try {
      live2DModel = await factory.from(props.modelUrl)
    } catch (error) {
      console.error('[Live2D] 模型加载失败:', error)
      teardownLive2D()
      loadFailed.value = true
      return
    }

    if (disposed || initId !== activeInitId || !app || !app.stage) {
      live2DModel.destroy?.({ children: true })
      return
    }

    model = live2DModel
    app.stage.addChild(model as never)

    fitModel()
    resizeObserver = new ResizeObserver(() => {
      fitModel()
    })
    resizeObserver.observe(container)

    startIdleLoop()
  } catch (error) {
    console.error('[Live2D] 初始化失败:', error)
    loadFailed.value = true
    teardownLive2D()
  }
}

onMounted(async () => {
  disposed = false
  await initLive2D()
})

watch(
  () => props.modelUrl,
  async (nextUrl, prevUrl) => {
    if (nextUrl === prevUrl) return
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
    }
  },
)

onBeforeUnmount(() => {
  disposed = true
  activeInitId += 1
  stopDrag()
  teardownLive2D()
})
</script>

<template>
  <div
    ref="containerRef"
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
    <img v-if="loadFailed" :src="mascotFallback" alt="Pixie" class="live2d-fallback" />
  </div>
</template>

<style scoped>
.live2d-container {
  position: relative;
  width: 220px;
  height: 280px;
  overflow: hidden;
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
