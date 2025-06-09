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