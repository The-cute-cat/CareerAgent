<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
@import '/css/style.css';

/* 添加全局样式确保全屏显示 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  width: 100%;
}

#app {
  display: flex;
  flex-direction: column;
}
</style>