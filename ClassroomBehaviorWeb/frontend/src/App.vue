<template>
  <!-- 路由出口：所有页面必须通过此组件渲染 -->
  <router-view />
</template>

<script setup>
// 根组件无需额外逻辑，确保路由出口存在即可
</script>

<style>
/* 基础样式：避免页面塌陷 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: sans-serif;
}
</style>