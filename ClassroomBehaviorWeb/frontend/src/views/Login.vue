<template>
  <div class="login-page">
    <!-- 背景装饰增强 -->
    <div class="bg-decoration bg-circle1"></div>
    <div class="bg-decoration bg-circle2"></div>
    <div class="bg-decoration bg-circle3"></div>
    
    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="logo-group">
        <div class="logo-icon pulse-animation">
          <i class="el-icon-camera"></i>
        </div>
        <h2 class="project-title">YOLO课堂抬头检测系统</h2>
        <p class="project-desc">专注课堂专注度分析，提升教学质量</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        class="login-form"
        autocomplete="off"
      >
        <el-form-item 
          label="用户名" 
          prop="username" 
          class="form-item"
          :error="fieldErrors.username"
        >
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            autocomplete="new-username"
            class="custom-input"
            :class="{ 'input-error': fieldErrors.username }"
          >
            <template #prefix>
              <i class="el-icon-user input-icon"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item 
          label="密码" 
          prop="password" 
          class="form-item"
          :error="fieldErrors.password"
        >
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="new-password"
            class="custom-input"
            :class="{ 'input-error': fieldErrors.password }"
          >
            <template #prefix>
              <i class="el-icon-lock input-icon"></i>
            </template>
          </el-input>
        </el-form-item>

        <!-- 操作按钮 -->
        <div class="btn-group">
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="userStore.loading"
            class="login-btn"
          >
            登录系统
          </el-button>
          <el-button
            type="text"
            @click="$router.push('/register')"
            class="register-btn"
          >
            还没有账号？立即注册
          </el-button>
        </div>
      </el-form>

      <!-- 底部装饰条 -->
      <div class="card-footer">
        <div class="footer-line"></div>
        <p class="footer-text">© 15组 YOLO课堂检测系统 版权所有</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { ElForm, ElFormItem, ElInput, ElButton, ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()
const loginFormRef = ref(null)
const form = reactive({ username: '', password: '' })
const fieldErrors = reactive({ username: '', password: '' }) // 字段级错误提示

const rules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

const handleLogin = async () => {
  // 重置错误状态
  fieldErrors.username = ''
  fieldErrors.password = ''
  
  try {
    await loginFormRef.value.validate()
    const success = await userStore.login(form.username, form.password)
    if (success) {
      ElMessage.success('登录成功，正在进入系统...')
      // router.push('/history/')
      router.replace('/history')
    } else {
      // 根据后端返回的错误信息分配到对应字段
      if (userStore.error.includes('用户名')) {
        fieldErrors.username = userStore.error
      } else if (userStore.error.includes('密码')) {
        fieldErrors.password = userStore.error
      } else if (userStore.error.includes('读取登录信息失败')) {
        // 服务器端错误，显示通用提示
        ElMessage.error(userStore.error)
      } else {
        // 通用错误，显示在用户名字段
        fieldErrors.username = userStore.error
      }
    }
  } catch (err) {
    // 表单验证失败不做额外处理，element-plus会自动显示验证信息
  }
}
</script>

<style scoped lang="scss">
// 引入全局变量
@use '@/styles/main.scss' as *;

.login-page {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #4361ee, #3a0ca3);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding: 20px;
  box-sizing: border-box;
}

// 增强背景装饰
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  filter: blur(80px);
  z-index: 0;
  animation: float 8s infinite ease-in-out;
}

.bg-circle1 {
  width: 600px;
  height: 600px;
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.bg-circle2 {
  width: 500px;
  height: 500px;
  bottom: -150px;
  right: -150px;
  animation-delay: 2s;
}

.bg-circle3 {
  width: 300px;
  height: 300px;
  top: 50%;
  right: 10%;
  animation-delay: 4s;
}

// 浮动动画
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(20px); }
}

.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(31, 38, 135, 0.2);
  padding: 40px 30px;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(12px);
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
  }
}

.logo-group {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(45deg, #4361ee, #3a0ca3);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 15px;
  color: white;
  font-size: 28px;
  box-shadow: 0 4px 15px rgba(67, 97, 238, 0.3);
}

// 呼吸动画
.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0.4); }
  70% { box-shadow: 0 0 0 15px rgba(67, 97, 238, 0); }
  100% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0); }
}

.project-title {
  font-size: 24px;
  color: #2d3748;
  margin-bottom: 8px;
  font-weight: 600;
  background: linear-gradient(90deg, #4361ee, #3a0ca3);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.project-desc {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

.login-form {
  margin-top: 10px;
}

.form-item {
  margin-bottom: 20px;
}

.custom-input {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  height: 48px;

  &:focus-within {
    border-color: #4361ee;
    box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.15);
    transform: translateY(-1px);
  }
}

.input-icon {
  color: #a0aec0;
}

// 错误状态样式
.input-error {
  border-color: $error-color !important;

  &:focus-within {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15) !important;
  }
}

.el-form-item__error {
  padding-top: 5px;
  font-size: 12px;
  color: $error-color;
  display: flex;
  align-items: center;
  gap: 4px;

  &::before {
    content: "!";
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: $error-color;
    color: white;
    font-size: 10px;
    text-align: center;
    line-height: 16px;
  }
}

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.login-btn {
  width: 100%;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(45deg, #4361ee, #3a0ca3);
  border: none;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &::after {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: 0.6s;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(67, 97, 238, 0.35);
    background: linear-gradient(45deg, #3a56d4, #320a91);
  }

  &:hover::after {
    left: 100%;
  }

  &:active {
    transform: translateY(0);
  }
}

.register-btn {
  color: #4361ee;
  font-size: 14px;
  margin: 0 auto;
  transition: all 0.3s ease;
  padding: 5px 15px;

  &:hover {
    color: #3a0ca3;
    background-color: rgba(67, 97, 238, 0.05);
    border-radius: 4px;
  }
}

// 底部装饰
.card-footer {
  margin-top: 30px;
  text-align: center;
}

.footer-line {
  width: 80%;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  margin: 0 auto 15px;
}

.footer-text {
  font-size: 12px;
  color: #a0aec0;
  margin: 0;
}
</style>
