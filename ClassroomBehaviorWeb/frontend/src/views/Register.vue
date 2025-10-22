<template>
  <div class="register-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration bg-circle1"></div>
    <div class="bg-decoration bg-circle2"></div>
    <div class="bg-decoration bg-circle3"></div>
    
    <!-- 注册卡片 -->
    <div class="register-card">
      <div class="logo-group">
        <div class="logo-icon pulse-animation">
          <i class="el-icon-user-plus"></i>
        </div>
        <h2 class="project-title">账号注册</h2>
        <p class="project-desc">创建账号，体验课堂抬头检测功能</p>
      </div>

      <!-- 注册表单 -->
      <el-form
        ref="registerFormRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        class="register-form"
        autocomplete="off"
      >
        <el-form-item 
          label="用户名" 
          prop="username" 
          class="form-item"
        >
          <el-input
            v-model="form.username"
            placeholder="3-20位字符，支持中文、字母"
            class="custom-input"
            @input="handleUsernameInput"
          >
            <template #prefix><i class="el-icon-user input-icon"></i></template>
            <template #suffix>
              <i v-if="usernameCheckStatus === 'valid'" class="el-icon-check valid-icon"></i>
              <i v-if="usernameCheckStatus === 'invalid'" class="el-icon-close invalid-icon"></i>
            </template>
          </el-input>
          <div v-if="usernameTips" class="input-tip">{{ usernameTips }}</div>
        </el-form-item>

        <el-form-item 
          label="密码" 
          prop="password" 
          class="form-item"
        >
          <el-input
            v-model="form.password"
            type="password"
            placeholder="6-32位字符，建议包含数字和字母"
            class="custom-input"
            @input="checkPasswordStrength"
          >
            <template #prefix><i class="el-icon-lock input-icon"></i></template>
          </el-input>
          <!-- 密码强度指示器 -->
          <div class="password-strength" v-if="form.password">
            <div class="strength-labels">
              <span>弱</span>
              <span>中</span>
              <span>强</span>
            </div>
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :style="{ width: strengthWidth, background: strengthColor }"
              ></div>
            </div>
          </div>
        </el-form-item>

        <el-form-item 
          label="确认密码" 
          prop="confirmPwd" 
          class="form-item"
        >
          <el-input
            v-model="form.confirmPwd"
            type="password"
            placeholder="请再次输入密码"
            class="custom-input"
          >
            <template #prefix><i class="el-icon-lock input-icon"></i></template>
          </el-input>
        </el-form-item>

        <!-- 操作按钮 -->
        <div class="btn-group">
          <el-button
            type="primary"
            @click="handleRegister"
            :loading="userStore.loading"
            class="register-btn"
          >
            注册账号
          </el-button>
          <el-button
            type="text"
            @click="$router.push('/login')"
            class="login-link"
          >
            已有账号？返回登录
          </el-button>
        </div>
      </el-form>

      <!-- 底部装饰条 -->
      <div class="card-footer">
        <div class="footer-line"></div>
        <p class="footer-text">注册即表示同意<a href="#" class="terms-link">用户协议</a>和<a href="#" class="terms-link">隐私政策</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { ElForm, ElFormItem, ElInput, ElButton, ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()
const registerFormRef = ref(null)
const form = reactive({ username: '', password: '', confirmPwd: '' })

// 新增状态管理
const usernameCheckStatus = ref('') // valid/invalid
const usernameTips = ref('')
const strengthWidth = ref('0%')
const strengthColor = ref('')

// 检查用户名是否已存在
const checkUsernameExists = (username) => {
  const registeredUsers = JSON.parse(localStorage.getItem('registeredUsers') || '[]')
  return registeredUsers.some(u => u.username === username)
}

// 用户名输入处理
const handleUsernameInput = (val) => {
  if (!val) {
    usernameCheckStatus.value = ''
    usernameTips.value = ''
    return
  }

  if (val.length < 3 || val.length > 20) {
    usernameCheckStatus.value = 'invalid'
    usernameTips.value = '用户名长度需在3-20位之间'
    return
  }

  if (checkUsernameExists(val)) {
    usernameCheckStatus.value = 'invalid'
    usernameTips.value = '用户名已存在，请更换'
  } else {
    usernameCheckStatus.value = 'valid'
    usernameTips.value = '用户名可用'
  }
}

// 密码强度检测
const checkPasswordStrength = (val) => {
  let strength = 0
  
  // 基础长度检查
  if (val.length >= 6) strength += 1
  if (val.length >= 12) strength += 1
  
  // 字符类型检查
  if (/[A-Z]/.test(val)) strength += 1
  if (/[a-z]/.test(val)) strength += 1
  if (/[0-9]/.test(val)) strength += 1
  if (/[^A-Za-z0-9]/.test(val)) strength += 1

  // 计算强度百分比
  const percent = Math.min(Math.round((strength / 6) * 100), 100)
  strengthWidth.value = `${percent}%`
  
  // 设置颜色
  if (percent < 30) {
    strengthColor.value = '#ef4444' // 弱
  } else if (percent < 70) {
    strengthColor.value = '#f59e0b' // 中
  } else {
    strengthColor.value = '#10b981' // 强
  }
}

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20字符', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (checkUsernameExists(value)) {
          callback(new Error('用户名已存在，请更换'))
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change']
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度6-32字符', trigger: 'blur' }
  ],
  confirmPwd: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次密码输入不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
})

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    const success = await userStore.register(form.username, form.password)
    if (success) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    }
  } catch (err) { /* 表单验证失败 */ }
}
</script>

<style scoped lang="scss">
// 引入全局变量
@import '@/styles/main.scss';

.register-page {
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

// 背景装饰复用登录页样式
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
  right: -200px;
  animation-delay: 0s;
}

.bg-circle2 {
  width: 500px;
  height: 500px;
  bottom: -150px;
  left: -150px;
  animation-delay: 3s;
}

.bg-circle3 {
  width: 300px;
  height: 300px;
  top: 30%;
  left: 10%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(20px); }
}

.register-card {
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

.register-form {
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

// 用户名验证提示
.valid-icon {
  color: #10b981;
}

.invalid-icon {
  color: $error-color;
}

.input-tip {
  font-size: 12px;
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 4px;

  &::before {
    content: "i";
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background-color: #e5e7eb;
    color: #6b7280;
    font-size: 10px;
    text-align: center;
    line-height: 14px;
  }
}

// 密码强度指示器
.password-strength {
  margin-top: 6px;
}

.strength-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 4px;
  padding: 0 2px;
}

.strength-bar {
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 2px;
}

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.register-btn {
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

.login-link {
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

.terms-link {
  color: #4361ee;
  text-decoration: none;
  transition: color 0.2s;

  &:hover {
    color: #3a0ca3;
    text-decoration: underline;
  }
}
</style>