// WangEditor 类型声明文件
// 解决 @wangeditor/editor-for-vue 缺少类型定义的问题

declare module '@wangeditor/editor-for-vue' {
  import type { Component } from 'vue'

  export const Editor: Component
  export const Toolbar: Component
}
