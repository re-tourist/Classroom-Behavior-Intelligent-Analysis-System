<template>
  <div class="not-found-page">
    <!-- 404 核心提示 -->
    <div class="not-found-container">
      <div class="error-code">404</div>
      <div class="error-desc">页面不存在或已被移除</div>
      <div class="error-tip">您访问的路径有误，或该页面已迁移</div>
      
      <!-- 跳转按钮（匹配项目核心页面） -->
      <div class="btn-group">
        <el-button 
          type="primary" 
          @click="$router.push('/detect')"
          icon="Home"
        >
          返回检测主页
        </el-button>
        <el-button 
          type="default" 
          @click="$router.push('/login')"
          icon="ArrowLeft"
        >
          返回登录页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElButton, ElIcon } from 'element-plus'
import { Home, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
// 引入全局样式变量（与项目主样式一致）
@import '@/styles/variables.scss';

.not-found-page {
  width: 100vw;
  height: 100vh;
  background-color: $bg-color;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.not-found-container {
  text-align: center;
  background-color: #fff;
  padding: 50px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-code {
  font-size: 80px;
  font-weight: 700;
  color: $primary-color;
  margin-bottom: 20px;
}

.error-desc {
  font-size: 22px;
  color: $text-color;
  margin-bottom: 10px;
}

.error-tip {
  font-size: 14px;
  color: $text-light-color;
  margin-bottom: 30px;
}

.btn-group {
  display: flex;
  justify-content: center;
  gap: 15px;
}
</style>