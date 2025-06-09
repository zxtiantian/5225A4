<template>
  <el-container class="app-container">
    <el-header height="60px">
      <el-menu
        mode="horizontal"
        :router="true"
        class="nav-menu"
        :ellipsis="false"
      >
        <el-menu-item index="/">
          <el-icon><Picture /></el-icon>
          Bird Recognition
        </el-menu-item>
        <div class="flex-grow" />
        <template v-if="isAuthenticated">
          <el-menu-item index="/upload">
            <el-icon><Upload /></el-icon>
            Upload
          </el-menu-item>
          <el-menu-item index="/search">
            <el-icon><Search /></el-icon>
            Search
          </el-menu-item>
          <el-sub-menu index="profile">
            <template #title>
              <el-icon><User /></el-icon>
              <span>{{ username }}</span>
            </template>
            <el-menu-item index="/history">
              <el-icon><Clock /></el-icon>
              Recognition History
            </el-menu-item>
            <el-menu-item index="/subscribe">
              <el-icon><Clock /></el-icon>
              Subscribe Notification
            </el-menu-item>
            <el-menu-item @click="handleSignOut">
              <el-icon><SwitchButton /></el-icon>
              Sign Out
            </el-menu-item>
          </el-sub-menu>
        </template>
        <template v-else>
          <el-menu-item index="/login">
            <el-icon><User /></el-icon>
            Sign In
          </el-menu-item>
        </template>
      </el-menu>
    </el-header>

    <el-main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <el-footer height="60px">
      <div class="footer-content">
        <p>© 2024 Bird Recognition System</p>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Auth } from 'aws-amplify'
import { useRouter } from 'vue-router'
import {
  Picture,
  Upload,
  Search,
  User,
  SwitchButton,
  Clock
} from '@element-plus/icons-vue'
import eventBus from './utils/eventBus'

const router = useRouter()
const isAuthenticated = ref(false)
const username = ref('')

const checkAuth = async () => {
  try {
    const user = await Auth.currentAuthenticatedUser()
    isAuthenticated.value = true
    username.value = user.username
  } catch {
    isAuthenticated.value = false
    username.value = ''
  }
}

const handleSignOut = async () => {
  await Auth.signOut()
  isAuthenticated.value = false
  username.value = ''
  router.push('/login')
}

const handleAuthChange = () => {
  checkAuth()
}

onMounted(() => {
  checkAuth()
  eventBus.on('auth-state-changed', handleAuthChange)
})

onUnmounted(() => {
  eventBus.off('auth-state-changed', handleAuthChange)
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.nav-menu {
  display: flex;
  align-items: center;
  overflow-x: auto;
}

.flex-grow {
  flex-grow: 1;
}

.el-header {
  padding: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
}

.el-footer {
  background-color: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  text-align: center;
  color: #909399;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.el-sub-menu :deep(.el-sub-menu__title) {
  display: flex;
  align-items: center;
  gap: 5px;
}

.el-sub-menu :deep(.el-sub-menu__title span) {
  margin-left: 4px;
}

/* 响应式：手机和平板适配 */
@media (max-width: 900px) {
  .el-main {
    padding: 8px;
  }
  .el-header {
    height: 48px !important;
  }
  .nav-menu {
    font-size: 14px;
    padding: 0 4px;
  }
  .footer-content {
    font-size: 12px;
  }
}
@media (max-width: 600px) {
  .el-header {
    height: 40px !important;
  }
  .nav-menu {
    font-size: 12px;
    padding: 0 2px;
  }
  .footer-content {
    font-size: 10px;
  }
  .el-main {
    padding: 2px;
  }
}
</style>
