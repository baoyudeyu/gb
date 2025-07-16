<template>
  <div class="telegram-account">
    <!-- Telegram账号登录卡片 -->
    <t-card class="login-card" v-if="!telegramInfo.isLoggedIn">
      <template #header>
        <div class="card-header">
          <t-icon name="logo-telegram" size="20px" />
          <span class="card-title">Telegram账号登录</span>
        </div>
      </template>
      
      <div class="login-form">
        <t-form :data="loginForm" @submit="handleLogin">
          <t-form-item label="手机号码" name="phone">
            <t-input 
              v-model="loginForm.phone" 
              placeholder="请输入手机号码（包含国家代码，如：+8613800138000）"
              prefix-icon="mobile"
            />
          </t-form-item>
          
          <t-form-item v-if="showVerificationCode" label="验证码" name="verificationCode">
            <t-input 
              v-model="loginForm.verificationCode" 
              placeholder="请输入收到的验证码"
              prefix-icon="secured"
            />
          </t-form-item>
          
          <t-form-item>
            <t-button 
              theme="primary" 
              type="submit" 
              block
              :loading="loginLoading"
            >
              {{ showVerificationCode ? '验证登录' : '发送验证码' }}
            </t-button>
          </t-form-item>
        </t-form>
        
        <t-divider>
          <span class="divider-text">登录说明</span>
        </t-divider>
        
        <div class="login-help">
          <p>登录流程：</p>
          <ol>
            <li>输入您的手机号码（需包含国家代码）</li>
            <li>点击"发送验证码"按钮</li>
            <li>在您的Telegram应用中查看验证码</li>
            <li>输入验证码并点击"验证登录"</li>
          </ol>
          <p class="note">注意：请确保您的手机号码已注册Telegram账号</p>
        </div>
      </div>
    </t-card>

    <!-- 已登录的Telegram账号信息 -->
    <t-card class="account-info-card" v-else>
      <template #header>
        <div class="card-header">
          <t-icon name="logo-telegram" size="20px" />
          <span class="card-title">Telegram账号信息</span>
        </div>
      </template>
      
      <div class="account-info">
        <t-row :gutter="[16, 16]">
          <t-col :span="12">
            <div class="info-item">
              <label class="info-label">用户名：</label>
              <span class="info-value">{{ telegramInfo.username || '未设置' }}</span>
            </div>
          </t-col>
          <t-col :span="12">
            <div class="info-item">
              <label class="info-label">姓名：</label>
              <span class="info-value">{{ telegramInfo.firstName }} {{ telegramInfo.lastName || '' }}</span>
            </div>
          </t-col>
          <t-col :span="12">
            <div class="info-item">
              <label class="info-label">手机号：</label>
              <span class="info-value">{{ telegramInfo.phone }}</span>
            </div>
          </t-col>
          <t-col :span="12">
            <div class="info-item">
              <label class="info-label">用户ID：</label>
              <span class="info-value">{{ telegramInfo.userId }}</span>
            </div>
          </t-col>
        </t-row>
      </div>
    </t-card>

    <!-- 账号操作卡片 -->
    <t-card class="account-actions-card" v-if="telegramInfo.isLoggedIn">
      <template #header>
        <div class="card-header">
          <t-icon name="setting" size="20px" />
          <span class="card-title">账号操作</span>
        </div>
      </template>
      
      <div class="account-actions">
        <t-row :gutter="[16, 16]">
          <t-col :span="8">
            <t-button 
              theme="primary" 
              variant="outline" 
              block
              @click="handleRefreshInfo"
            >
              <template #icon>
                <t-icon name="refresh" />
              </template>
              刷新信息
            </t-button>
          </t-col>
          <t-col :span="8">
            <t-button 
              theme="warning" 
              variant="outline" 
              block
              @click="handleExportSession"
            >
              <template #icon>
                <t-icon name="download" />
              </template>
              导出会话
            </t-button>
          </t-col>
          <t-col :span="8">
            <t-button 
              theme="danger" 
              variant="outline" 
              block
              @click="handleLogout"
            >
              <template #icon>
                <t-icon name="logout" />
              </template>
              退出登录
            </t-button>
          </t-col>
        </t-row>
      </div>
    </t-card>

    <!-- 会话管理卡片 -->
    <t-card class="session-card" v-if="telegramInfo.isLoggedIn">
      <template #header>
        <div class="card-header">
          <t-icon name="server" size="20px" />
          <span class="card-title">会话管理</span>
        </div>
      </template>
      
      <div class="session-settings">
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-title">自动重连</div>
            <div class="setting-desc">连接断开时自动重新连接</div>
          </div>
          <t-switch 
            v-model="sessionSettings.autoReconnect" 
            @change="handleAutoReconnectChange"
          />
        </div>
        
        <t-divider />
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-title">保持在线</div>
            <div class="setting-desc">保持Telegram在线状态</div>
          </div>
          <t-switch 
            v-model="sessionSettings.keepOnline" 
            @change="handleKeepOnlineChange"
          />
        </div>
      </div>
    </t-card>
  </div>
</template>

<script>
import TELEGRAM_CONFIG from '../config/telegram.js'

export default {
  name: 'TelegramAccountManagement',
  data() {
    return {
      telegramInfo: {
        isLoggedIn: false,
        username: '',
        firstName: '',
        lastName: '',
        phone: '',
        userId: ''
      },
      loginForm: {
        phone: '',
        verificationCode: ''
      },
      sessionSettings: {
        autoReconnect: true,
        keepOnline: false
      },
      showVerificationCode: false,
      loginLoading: false
    }
  },
  methods: {
    handleLogin() {
      if (!this.showVerificationCode) {
        // 第一步：发送验证码
        if (!this.loginForm.phone) {
          this.$message.error('请输入手机号码')
          return
        }
        
        this.loginLoading = true
        // 这里调用后端API发送验证码，使用全局配置的API_ID和API_HASH
        const loginData = {
          phone: this.loginForm.phone,
          apiId: TELEGRAM_CONFIG.API_ID,
          apiHash: TELEGRAM_CONFIG.API_HASH
        }
        
        console.log('发送验证码请求:', loginData)
        
        setTimeout(() => {
          this.showVerificationCode = true
          this.loginLoading = false
          this.$message.success('验证码已发送到您的Telegram')
        }, 2000)
      } else {
        // 第二步：验证登录
        if (!this.loginForm.verificationCode) {
          this.$message.error('请输入验证码')
          return
        }
        
        this.loginLoading = true
        // 这里调用后端API验证登录
        const verifyData = {
          phone: this.loginForm.phone,
          verificationCode: this.loginForm.verificationCode,
          apiId: TELEGRAM_CONFIG.API_ID,
          apiHash: TELEGRAM_CONFIG.API_HASH
        }
        
        console.log('验证登录请求:', verifyData)
        
        setTimeout(() => {
          this.telegramInfo = {
            isLoggedIn: true,
            username: '@example_user',
            firstName: '示例',
            lastName: '用户',
            phone: this.loginForm.phone,
            userId: '123456789'
          }
          this.loginLoading = false
          this.$message.success('Telegram账号登录成功')
        }, 2000)
      }
    },
    handleRefreshInfo() {
      this.$message.info('正在刷新Telegram账号信息...')
      // 这里调用后端API刷新信息
    },
    handleExportSession() {
      this.$message.info('正在导出会话文件...')
      // 这里调用后端API导出会话
    },
    handleLogout() {
      this.$confirm('确定要退出Telegram账号吗？', '确认退出', {
        confirmBtn: '确定',
        cancelBtn: '取消'
      }).then(() => {
        this.telegramInfo.isLoggedIn = false
        this.showVerificationCode = false
        this.loginForm = {
          phone: '',
          verificationCode: ''
        }
        this.$message.success('已退出Telegram账号')
      }).catch(() => {
        // 用户取消
      })
    },
    handleAutoReconnectChange(value) {
      this.$message.info(`自动重连已${value ? '开启' : '关闭'}`)
      // 这里调用后端API设置自动重连
    },
    handleKeepOnlineChange(value) {
      this.$message.info(`保持在线已${value ? '开启' : '关闭'}`)
      // 这里调用后端API设置保持在线
    }
  }
}
</script>

<style scoped>
.telegram-account {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.login-card,
.account-info-card,
.account-actions-card,
.session-card {
  margin-bottom: 24px;
}

.login-form {
  padding: 16px 0;
}

.login-help {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 14px;
  color: #6b7280;
}

.login-help p {
  margin: 0 0 8px 0;
  font-weight: 500;
}

.login-help ol {
  margin: 0 0 12px 0;
  padding-left: 20px;
}

.login-help li {
  margin-bottom: 4px;
}

.login-help .note {
  margin: 0;
  padding: 8px 12px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
  font-size: 13px;
}

.divider-text {
  color: #6b7280;
  font-size: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.account-info {
  padding: 16px 0;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.info-label {
  font-weight: 500;
  color: #6b7280;
  min-width: 80px;
}

.info-value {
  color: #1f2937;
  flex: 1;
}

.account-actions {
  padding: 16px 0;
}

.session-settings {
  padding: 16px 0;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
}

.setting-info {
  flex: 1;
}

.setting-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 12px;
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .account-actions .t-col {
    span: 24;
    margin-bottom: 12px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-label {
    margin-bottom: 4px;
  }
}
</style> 