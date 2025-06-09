<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Login</h2>
        </div>
      </template>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="Username" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Enter your username"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Enter your password"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="login-button"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>
      <div class="switch-auth">
        <span>Don't have an account?</span>
        <el-button type="text" @click="$router.push('/register')">Register</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import eventBus from '../utils/eventBus'
import { Auth } from 'aws-amplify'

const router = useRouter()
const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const rules = {
  username: [
    { required: true, message: 'Please enter your username', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        console.log('[Login] Login:', loginForm.username)
        const signInResult = await Auth.signIn(loginForm.username, loginForm.password)
        console.log('[Login] signInResult:', signInResult)
        eventBus.emit('auth-state-changed')
        const currentUser = await Auth.currentAuthenticatedUser()
        console.log('[Login] currentAuthenticatedUser:', currentUser)
        router.push('/home')
        console.log('[Login] transfrom /home')
      } catch (error) {
        console.error('[Login] Login error:', error, JSON.stringify(error))
        ElMessage.error(error.message || 'Login failed')
      } finally {
        loading.value = false
        console.log('[Login] login end')
      }
    } else {
      console.log('[Login] login error')
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.login-button {
  width: 100%;
  margin-top: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.switch-auth {
  margin-top: 20px;
  text-align: center;
  color: #909399;
}
.switch-auth .el-button {
  padding: 0 4px;
  font-size: 14px;
  vertical-align: baseline;
}

@media (max-width: 900px) {
  .login-container {
    padding: 8px;
    margin: 10px auto;
  }
  .login-card {
    padding: 12px 4px;
  }
  .login-title {
    font-size: 18px;
  }
  .el-button, .el-input, .el-form-item {
    font-size: 14px;
  }
}
@media (max-width: 600px) {
  .login-container {
    padding: 2px;
    margin: 2px auto;
  }
  .login-card {
    padding: 4px 0;
  }
  .login-title {
    font-size: 16px;
  }
  .el-button, .el-input, .el-form-item {
    font-size: 12px;
  }
}
</style> 