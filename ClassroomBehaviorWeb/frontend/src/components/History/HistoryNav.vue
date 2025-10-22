<template>
  <header class="top-nav">
    <div class="nav-left">
      <i class="el-icon-camera nav-icon"></i>
      <h1 class="nav-title">YOLO课堂抬头检测系统 - 历史数据</h1>
    </div>
    <el-button
      type="text"
      @click="handleLogout"
      class="logout-btn"
    >
      <i class="el-icon-logout"></i> 退出登录
    </el-button>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { ElButton } from 'element-plus'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}
</script>

<style scoped>
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-icon {
  font-size: 20px;
  color: #4361ee;
  margin-right: 10px;
}

.nav-title {
  color: #333;
  font-size: 18px;
  margin: 0;
}

.logout-btn {
  color: #606266;
}
</style>