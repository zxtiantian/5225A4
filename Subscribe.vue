<template>
  <div class="subscribe-container">
    <el-card class="subscribe-card">
      <div class="subscribe-title">Subscribe to Bird Notifications</div>
      <el-form :model="form" label-width="120px" class="subscribe-form">
        <el-form-item label="Email">
          <el-input v-model="form.email" readonly />
        </el-form-item>
        <el-form-item label="Bird Species">
          <el-select
            v-model="form.species"
            multiple
            filterable
            placeholder="Select bird species to subscribe"
            style="width: 100%"
          >
            <el-option
              v-for="item in uniqueSortedSpecies"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="center-btn-item">
          <el-button type="primary" @click="handleSubscribe" :loading="subscribing">Subscribe</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Auth } from 'aws-amplify'

const form = ref({
  email: '',
  species: []
})
const speciesList = ref([])
const subscribing = ref(false)

const uniqueSortedSpecies = computed(() => {
  return Array.from(new Set(speciesList.value)).sort((a, b) => a.localeCompare(b))
})

onMounted(async () => {
  // 获取当前用户邮箱
  try {
    const user = await Auth.currentAuthenticatedUser()
    form.value.email = user.attributes.email
  } catch {
    form.value.email = ''
  }
  // 获取鸟类种类列表
  try {
    const res = await fetch('https://dkwigqlnck.execute-api.us-east-1.amazonaws.com/api/species_list')
    const data = await res.json()
    speciesList.value = data.body || []
  } catch {
    speciesList.value = []
  }
})

const handleSubscribe = async () => {
  if (!form.value.species.length) {
    ElMessage.warning('Please select at least one bird species')
    return
  }
  subscribing.value = true
  try {
    const res = await fetch('https://5p4dvox6h9.execute-api.us-east-1.amazonaws.com/api/subscribe_tag', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: form.value.email,
        tags: form.value.species
      })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      ElMessage.success('Subscribed successfully. Please check your email to confirm.')
    } else {
      ElMessage.error('Subscription failed')
    }
  } catch (e) {
    ElMessage.error('Subscription failed')
  } finally {
    subscribing.value = false
  }
}
</script>

<style scoped>
.subscribe-container {
  max-width: 800px;
  margin: 60px auto;
  padding: 30px;
}

.subscribe-card {
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.subscribe-title {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 40px;
  color: #303133;
}

.subscribe-form {
  margin-top: 20px;
}

.subscribe-form :deep(.el-form-item) {
  margin-bottom: 30px;
}

.subscribe-form :deep(.el-form-item__label) {
  font-size: 16px;
  padding-bottom: 8px;
}

.subscribe-form :deep(.el-input__wrapper),
.subscribe-form :deep(.el-select) {
  font-size: 16px;
}

.subscribe-form :deep(.el-button) {
  font-size: 16px;
  padding: 12px 24px;
  margin-top: 10px;
}

.subscribe-form :deep(.el-select-dropdown__item) {
  font-size: 16px;
  padding: 8px 12px;
}

.center-btn-item {
  display: flex;
  justify-content: center;
}

.subscribe-form :deep(.el-form-item__content) {
  display: flex;
  align-items: center;
}

.subscribe-form :deep(.el-form-item__label) {
  min-width: 120px;
  text-align: right;
  margin-right: 12px;
}

@media (max-width: 900px) {
  .subscribe-container {
    max-width: 600px;
    padding: 20px;
    margin: 30px auto;
  }
  
  .subscribe-card {
    padding: 30px;
  }
  
  .subscribe-title {
    font-size: 24px;
    margin-bottom: 30px;
  }
  
  .subscribe-form :deep(.el-form-item) {
    margin-bottom: 24px;
  }
  
  .subscribe-form :deep(.el-form-item__label) {
    font-size: 15px;
  }
  
  .subscribe-form :deep(.el-input__wrapper),
  .subscribe-form :deep(.el-select) {
    font-size: 15px;
  }
  
  .subscribe-form :deep(.el-button) {
    font-size: 15px;
    padding: 10px 20px;
  }
}

@media (max-width: 600px) {
  .subscribe-container {
    max-width: 100%;
    padding: 15px;
    margin: 20px auto;
  }
  
  .subscribe-card {
    padding: 20px;
  }
  
  .subscribe-title {
    font-size: 20px;
    margin-bottom: 25px;
  }
  
  .subscribe-form :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  .subscribe-form :deep(.el-form-item__label) {
    font-size: 14px;
  }
  
  .subscribe-form :deep(.el-input__wrapper),
  .subscribe-form :deep(.el-select) {
    font-size: 14px;
  }
  
  .subscribe-form :deep(.el-button) {
    font-size: 14px;
    padding: 8px 16px;
  }
}
</style> 