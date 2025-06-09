<template>
  <div class="confirm-container">
    <el-card class="confirm-card">
      <template #header>
        <div class="card-header">
          <h2>Email Verification</h2>
        </div>
      </template>
      <el-form ref="confirmFormRef" :model="confirmForm" :rules="rules" label-position="top" @submit.prevent="handleConfirm">
        <el-form-item label="Email" prop="email">
          <el-input v-model="confirmForm.email" placeholder="Enter your email" />
        </el-form-item>
        <el-form-item label="Verification Code" prop="code">
          <el-input v-model="confirmForm.code" placeholder="Enter the code from your email" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="confirm-button">Verify</el-button>
        </el-form-item>
      </el-form>
      <div class="switch-auth">
        <span>Already verified?</span>
        <el-button type="text" @click="$router.push('/login')">Login</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Auth } from 'aws-amplify'

const router = useRouter()
const route = useRoute()
const confirmFormRef = ref(null)
const confirmForm = reactive({
  username: route.query.username || '',
  email: route.query.email || '',
  code: ''
})
const loading = ref(false)
const rules = {
  email: [{ required: true, message: 'Please enter your email', trigger: 'blur' }],
  code: [{ required: true, message: 'Please enter the verification code', trigger: 'blur' }]
}

const handleConfirm = async () => {
  if (!confirmFormRef.value) return
  await confirmFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await Auth.confirmSignUp(confirmForm.username, confirmForm.code)
        ElMessage.success('Email verified! You can now login.')
        router.push('/login')
      } catch (error) {
        ElMessage.error(error.message || 'Verification failed')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.confirm-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}
.confirm-card {
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
.confirm-button {
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
  .confirm-container {
    padding: 8px;
    margin: 10px auto;
  }
  .confirm-card {
    padding: 12px 4px;
  }
  .confirm-title {
    font-size: 18px;
  }
  .el-button, .el-input, .el-form-item {
    font-size: 14px;
  }
}
@media (max-width: 600px) {
  .confirm-container {
    padding: 2px;
    margin: 2px auto;
  }
  .confirm-card {
    padding: 4px 0;
  }
  .confirm-title {
    font-size: 16px;
  }
  .el-button, .el-input, .el-form-item {
    font-size: 12px;
  }
}
</style> 