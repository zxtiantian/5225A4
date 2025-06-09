<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>Register</h2>
        </div>
      </template>
      <el-form ref="registerFormRef" :model="registerForm" :rules="rules" label-position="top" @submit.prevent="handleRegister">
        <el-form-item label="First Name" prop="firstName">
          <el-input v-model="registerForm.firstName" placeholder="Enter your first name" />
        </el-form-item>
        <el-form-item label="Last Name" prop="lastName">
          <el-input v-model="registerForm.lastName" placeholder="Enter your last name" />
        </el-form-item>
        <el-form-item label="Gender" prop="gender">
          <el-select v-model="registerForm.gender" placeholder="Select gender">
            <el-option label="Male" value="male" />
            <el-option label="Female" value="female" />
            <el-option label="Other" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="registerForm.email" placeholder="Enter your email" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="Enter your password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="register-button">Register</el-button>
        </el-form-item>
      </el-form>
      <div class="switch-auth">
        <span>Already have an account?</span>
        <el-button type="text" @click="$router.push('/login')">Login</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Auth } from 'aws-amplify'

const router = useRouter()
const registerFormRef = ref(null)
const registerForm = reactive({
  firstName: '',
  lastName: '',
  gender: '',
  email: '',
  password: ''
})
const loading = ref(false)
const rules = {
  firstName: [{ required: true, message: 'Please enter your first name', trigger: 'blur' }],
  lastName: [{ required: true, message: 'Please enter your last name', trigger: 'blur' }],
  gender: [{ required: true, message: 'Please select your gender', trigger: 'change' }],
  email: [{ required: true, message: 'Please enter your email', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter your password', trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const username = registerForm.firstName + registerForm.lastName
        await Auth.signUp({
          username,
          password: registerForm.password,
          attributes: {
            email: registerForm.email,
            given_name: registerForm.firstName,
            family_name: registerForm.lastName,
            gender: registerForm.gender
          }
        })
        ElMessage.success('Registration successful! Please check your email for verification.')
        router.push({ path: '/confirm', query: { username, email: registerForm.email } })
      } catch (error) {
        ElMessage.error(error.message || 'Registration failed')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.register-card {
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

.register-button {
  width: 100%;
  margin-top: 20px;
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
  .register-container {
    padding: 8px;
    margin: 10px auto;
  }
  .register-card {
    padding: 12px 4px;
  }
  .register-title {
    font-size: 18px;
  }
  .el-button, .el-input, .el-form-item {
    font-size: 14px;
  }
}
@media (max-width: 600px) {
  .register-container {
    padding: 2px;
    margin: 2px auto;
  }
  .register-card {
    padding: 4px 0;
  }
  .register-title {
    font-size: 16px;
  }
  .el-button, .el-input, .el-form-item {
    font-size: 12px;
  }
}
</style> 