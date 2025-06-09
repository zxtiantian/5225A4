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