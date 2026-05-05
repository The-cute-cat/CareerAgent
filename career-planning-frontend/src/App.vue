<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useCareerModeStore } from '@/stores/careerMode'
import PointsDialogs from '@/components/PointsDialogs/index.vue'

onMounted(() => {
  const modeStore = useCareerModeStore()
  modeStore.initMode()
})
</script>

<template>
  <RouterView />
  <!-- 全局积分相关弹窗 -->
  <PointsDialogs />
</template>

<style>
/* 引入全局原子化样式 */
@import '/css/style.css';

/* 基础布局重置：确保全屏显示 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  width: 100%;
}

/* 根容器布局：使用 Flex 纵向排列 */
#app {
  display: flex;
  flex-direction: column;
}
</style>