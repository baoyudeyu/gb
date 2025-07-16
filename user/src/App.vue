<template>
  <div id="app">
    <t-layout>
      <!-- 左侧导航 -->
      <t-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <img src="/暴雨.png" alt="logo" class="logo" />
          <span class="site-title">跟投系统</span>
        </div>
        
        <!-- 导航菜单 -->
        <t-menu 
          :value="activeMenu" 
          class="nav-menu"
          @change="handleMenuChange"
        >
          <t-menu-item value="home">
            <template #icon>
              <t-icon name="home" />
            </template>
            首页
          </t-menu-item>
          <t-menu-item value="account">
            <template #icon>
              <t-icon name="user" />
            </template>
            账号管理
          </t-menu-item>
        </t-menu>
        
        <!-- 底部登录注册按钮 -->
        <div class="sidebar-footer" v-if="!currentUser">
          <div class="auth-buttons">
            <t-button 
              variant="outline" 
              size="small" 
              class="auth-btn-left"
              @click="showAuthDialog('login')"
            >
              登录
            </t-button>
            <t-button 
              theme="primary" 
              size="small" 
              class="auth-btn-right"
              @click="showAuthDialog('register')"
            >
              注册
            </t-button>
          </div>
        </div>
        
        <!-- 已登录用户信息 -->
        <div class="sidebar-footer" v-else>
          <div class="user-info">
            <div class="user-name">{{ currentUser.username }}</div>
            <t-button 
              variant="text" 
              size="small" 
              @click="handleLogout"
            >
              退出登录
            </t-button>
          </div>
        </div>
      </t-aside>
      
      <!-- 右侧内容区域 -->
      <t-layout>
        <t-content class="main-content">
          <router-view />
        </t-content>
        
        <!-- 认证弹窗 -->
        <AuthDialogs 
          v-model:visible="authDialogVisible"
          @loginSuccess="handleLoginSuccess"
        />
      </t-layout>
    </t-layout>
  </div>
</template>

<script>
import AuthDialogs from './components/AuthDialogs.vue'

export default {
  name: 'App',
  components: {
    AuthDialogs
  },
  data() {
    return {
      activeMenu: '',
      authDialogVisible: '',
      currentUser: null
    }
  },
  methods: {
    updateActiveMenu() {
      // 根据当前路由路径设置activeMenu
      const path = this.$route.path
      if (path === '/home' || path === '/') {
        this.activeMenu = 'home'
      } else if (path === '/account') {
        this.activeMenu = 'account'
      } else {
        // 其他路由，根据路径去掉斜杠
        this.activeMenu = path.replace('/', '') || 'home'
      }
    },
    handleMenuChange(value) {
      this.activeMenu = value
      this.$router.push(`/${value}`)
    },
    showAuthDialog(type) {
      this.authDialogVisible = type
    },
    handleLoginSuccess(user) {
      this.currentUser = user
      this.$message.success(`欢迎回来，${user.username}！`)
    },
    handleLogout() {
      this.$confirm('确定要退出登录吗？', '确认退出', {
        confirmBtn: '确定',
        cancelBtn: '取消'
      }).then(() => {
        this.currentUser = null
        this.$message.success('已退出登录')
      }).catch(() => {
        // 用户取消
      })
    }
  },
  mounted() {
    // 检查本地存储中是否有用户信息
    const savedUser = localStorage.getItem('currentUser')
    if (savedUser) {
      this.currentUser = JSON.parse(savedUser)
    }
    
    // 根据当前路由设置activeMenu
    this.updateActiveMenu()
  },
  watch: {
    currentUser(newUser) {
      // 用户登录状态变化时，保存到本地存储
      if (newUser) {
        localStorage.setItem('currentUser', JSON.stringify(newUser))
      } else {
        localStorage.removeItem('currentUser')
      }
    },
    $route() {
      // 路由变化时更新activeMenu
      this.updateActiveMenu()
    }
  }
}
</script>

<style>
#app {
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.sidebar {
  background: #f8f9fa;
  border-right: 1px solid #e5e6eb;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e5e6eb;
}

.logo {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.site-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.nav-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 16px 0;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #e5e6eb;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.auth-buttons {
  display: flex;
  gap: 8px;
}

.auth-btn-left,
.auth-btn-right {
  flex: 1;
  margin: 0;
}

.user-info {
  text-align: center;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
}

.main-content {
  padding: 24px;
  background: #ffffff;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px !important;
  }
  
  .sidebar-header {
    padding: 16px;
  }
  
  .site-title {
    font-size: 16px;
  }
  
  .main-content {
    padding: 16px;
  }
}
</style> 