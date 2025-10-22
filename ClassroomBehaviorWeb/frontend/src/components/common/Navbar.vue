<template>
  <el-menu
    mode="horizontal"
    background-color="#2563eb"
    text-color="#fff"
    active-text-color="#ffd04b"
    class="navbar"
  >
    <!-- 系统名称 -->
    <el-menu-item index="1" class="brand">
      <span class="brand-name">YOLO抬头检测系统</span>
    </el-menu-item>

    <!-- 用户信息与退出 -->
    <el-menu-item index="2" class="user-item">
      <el-dropdown trigger="click">
        <span class="user-info">
          <el-avatar :icon="User" class="avatar"></el-avatar>
          <span class="username">{{ userStore.userInfo.username }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="userStore.logout()">
              <el-icon><Logout /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { useUserStore } from '@/stores/userStore'
import { ElMenu, ElMenuItem, ElDropdown, ElDropdownMenu, ElDropdownItem, ElAvatar, ElIcon } from 'element-plus'
import { User, Logout } from '@element-plus/icons-vue'

const userStore = useUserStore()
</script>

<style scoped lang="scss">
.navbar {
  width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.brand {
  font-size: 18px;
  font-weight: 600;
}

.brand-name {
  margin-left: 8px;
}

.user-item {
  margin-left: auto;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.avatar {
  background-color: #fff;
  color: #2563eb;
}

.username {
  font-size: 14px;
}
</style>