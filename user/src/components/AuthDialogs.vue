<template>
  <div>
    <!-- 登录弹窗 -->
    <t-dialog
      v-model:visible="loginVisible"
      header="登录账号"
      width="400px"
      :footer="false"
      :close-on-overlay-click="false"
    >
      <t-form
        :data="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        @submit="handleLogin"
      >
        <t-form-item label="账号" name="username">
          <t-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="密码" name="password">
          <t-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            clearable
          />
        </t-form-item>
        
        <t-form-item>
          <t-button
            theme="primary"
            type="submit"
            block
            :loading="loginLoading"
          >
            登录
          </t-button>
        </t-form-item>
      </t-form>
      
      <div class="auth-links">
        <t-link @click="showRegister">还没有账号？立即注册</t-link>
        <t-link @click="showResetPassword">忘记密码？</t-link>
      </div>
    </t-dialog>

    <!-- 注册弹窗 -->
    <t-dialog
      v-model:visible="registerVisible"
      header="注册账号"
      width="400px"
      :footer="false"
      :close-on-overlay-click="false"
    >
      <t-form
        :data="registerForm"
        :rules="registerRules"
        ref="registerFormRef"
        @submit="handleRegister"
      >
        <t-form-item label="用户名" name="username">
          <t-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20位）"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="密码" name="password">
          <t-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="确认密码" name="confirmPassword">
          <t-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="暗语" name="secretPhrase">
          <t-input
            v-model="registerForm.secretPhrase"
            placeholder="请输入暗语（用于找回密码）"
            clearable
          />
        </t-form-item>
        
        <t-form-item>
          <t-button
            theme="primary"
            type="submit"
            block
            :loading="registerLoading"
          >
            注册
          </t-button>
        </t-form-item>
      </t-form>
      
      <div class="auth-links">
        <t-link @click="showLogin">已有账号？立即登录</t-link>
      </div>
    </t-dialog>

    <!-- 找回密码弹窗 -->
    <t-dialog
      v-model:visible="resetPasswordVisible"
      header="找回密码"
      width="400px"
      :footer="false"
      :close-on-overlay-click="false"
    >
      <t-form
        :data="resetPasswordForm"
        :rules="resetPasswordRules"
        ref="resetPasswordFormRef"
        @submit="handleResetPassword"
      >
        <t-form-item label="用户名" name="username">
          <t-input
            v-model="resetPasswordForm.username"
            placeholder="请输入用户名"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="暗语" name="secretPhrase">
          <t-input
            v-model="resetPasswordForm.secretPhrase"
            placeholder="请输入注册时的暗语"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="新密码" name="newPassword">
          <t-input
            v-model="resetPasswordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            clearable
          />
        </t-form-item>
        
        <t-form-item label="确认新密码" name="confirmNewPassword">
          <t-input
            v-model="resetPasswordForm.confirmNewPassword"
            type="password"
            placeholder="请再次输入新密码"
            clearable
          />
        </t-form-item>
        
        <t-form-item>
          <t-button
            theme="primary"
            type="submit"
            block
            :loading="resetPasswordLoading"
          >
            重置密码
          </t-button>
        </t-form-item>
      </t-form>
      
      <div class="auth-links">
        <t-link @click="showLogin">返回登录</t-link>
      </div>
    </t-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AuthDialogs',
  props: {
    visible: {
      type: String,
      default: '' // 'login', 'register', 'resetPassword'
    }
  },
  emits: ['update:visible', 'loginSuccess'],
  data() {
    return {
      // 登录表单
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loginLoading: false,
      
      // 注册表单
      registerForm: {
        username: '',
        password: '',
        confirmPassword: '',
        secretPhrase: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { 
            validator: (val) => val === this.registerForm.password, 
            message: '两次输入的密码不一致', 
            trigger: 'blur' 
          }
        ],
        secretPhrase: [
          { required: true, message: '请输入暗语', trigger: 'blur' }
        ]
      },
      registerLoading: false,
      
      // 找回密码表单
      resetPasswordForm: {
        username: '',
        secretPhrase: '',
        newPassword: '',
        confirmNewPassword: ''
      },
      resetPasswordRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        secretPhrase: [
          { required: true, message: '请输入暗语', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ],
        confirmNewPassword: [
          { required: true, message: '请确认新密码', trigger: 'blur' },
          { 
            validator: (val) => val === this.resetPasswordForm.newPassword, 
            message: '两次输入的密码不一致', 
            trigger: 'blur' 
          }
        ]
      },
      resetPasswordLoading: false
    }
  },
  computed: {
    loginVisible: {
      get() {
        return this.visible === 'login'
      },
      set(val) {
        this.$emit('update:visible', val ? 'login' : '')
      }
    },
    registerVisible: {
      get() {
        return this.visible === 'register'
      },
      set(val) {
        this.$emit('update:visible', val ? 'register' : '')
      }
    },
    resetPasswordVisible: {
      get() {
        return this.visible === 'resetPassword'
      },
      set(val) {
        this.$emit('update:visible', val ? 'resetPassword' : '')
      }
    }
  },
  methods: {
    showLogin() {
      this.$emit('update:visible', 'login')
    },
    showRegister() {
      this.$emit('update:visible', 'register')
    },
    showResetPassword() {
      this.$emit('update:visible', 'resetPassword')
    },
    
    async handleLogin() {
      try {
        this.loginLoading = true
        
        const response = await axios.post('http://localhost:8000/api/auth/login', {
          username: this.loginForm.username,
          password: this.loginForm.password
        })
        
        this.$message.success(response.data.message)
        this.$emit('loginSuccess', response.data.user)
        this.$emit('update:visible', '')
        
        // 清空表单
        this.loginForm = { username: '', password: '' }
        
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '登录失败')
      } finally {
        this.loginLoading = false
      }
    },
    
    async handleRegister() {
      try {
        this.registerLoading = true
        
        const response = await axios.post('http://localhost:8000/api/auth/register', {
          username: this.registerForm.username,
          password: this.registerForm.password,
          confirm_password: this.registerForm.confirmPassword,
          secret_phrase: this.registerForm.secretPhrase
        })
        
        this.$message.success(response.data.message)
        this.showLogin()
        
        // 清空表单
        this.registerForm = {
          username: '',
          password: '',
          confirmPassword: '',
          secretPhrase: ''
        }
        
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '注册失败')
      } finally {
        this.registerLoading = false
      }
    },
    
    async handleResetPassword() {
      try {
        this.resetPasswordLoading = true
        
        const response = await axios.post('http://localhost:8000/api/auth/reset-password', {
          username: this.resetPasswordForm.username,
          secret_phrase: this.resetPasswordForm.secretPhrase,
          new_password: this.resetPasswordForm.newPassword,
          confirm_new_password: this.resetPasswordForm.confirmNewPassword
        })
        
        this.$message.success(response.data.message)
        this.showLogin()
        
        // 清空表单
        this.resetPasswordForm = {
          username: '',
          secretPhrase: '',
          newPassword: '',
          confirmNewPassword: ''
        }
        
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '密码重置失败')
      } finally {
        this.resetPasswordLoading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-links {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

.auth-links .t-link {
  font-size: 14px;
  color: #0052d9;
  cursor: pointer;
}

.auth-links .t-link:hover {
  text-decoration: underline;
}

/* 表单样式优化 */
.t-form-item {
  margin-bottom: 20px;
}

.t-input {
  height: 40px;
}

.t-button {
  height: 40px;
  font-size: 16px;
}

/* 弹窗样式优化 */
:deep(.t-dialog__header) {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  border-bottom: 1px solid #e5e6eb;
  padding-bottom: 16px;
}

:deep(.t-dialog__body) {
  padding: 24px;
}
</style> 