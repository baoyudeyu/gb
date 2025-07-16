<template>
  <div class="page-container">

    <!-- Telegram账号列表卡片 -->
    <t-card class="page-card account-list-card">
      <template #header>
        <div class="card-header">
          <t-icon name="view-list" size="20px" />
          <span class="card-title">Telegram账号列表</span>
          <div class="header-actions">
            <t-button 
              theme="success" 
              size="small" 
              @click="showAddAccountDialog"
            >
              <template #icon>
                <t-icon name="add" />
              </template>
              添加账号
            </t-button>
            <t-button 
              theme="primary" 
              size="small" 
              @click="handleRefreshList"
            >
              <template #icon>
                <t-icon name="refresh" />
              </template>
              刷新列表
            </t-button>
          </div>
        </div>
      </template>
      
      <div class="page-card-content account-list">
        <t-table
          :data="telegramAccountList"
          :columns="tableColumns"
          :loading="tableLoading"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
          row-key="id"
        >
          <template #status="{ row }">
            <t-tag 
              :theme="row.status === 'online' ? 'success' : row.status === 'offline' ? 'danger' : 'warning'"
              variant="light"
            >
              {{ getStatusText(row.status) }}
            </t-tag>
          </template>
          
          <template #actions="{ row }">
            <t-space>
              <t-button
                theme="primary"
                variant="text"
                size="small"
                @click="handleViewAccount(row)"
              >
                查看详情
              </t-button>
              <t-button
                theme="warning"
                variant="text"
                size="small"
                @click="handleEditAccount(row)"
              >
                编辑
              </t-button>
              <t-button
                theme="danger"
                variant="text"
                size="small"
                @click="handleDeleteAccount(row)"
              >
                删除
              </t-button>
            </t-space>
          </template>
        </t-table>
      </div>
    </t-card>

    <!-- 添加账号弹窗 -->
    <t-dialog
      v-model:visible="addAccountDialogVisible"
      header="添加Telegram账号"
      width="480px"
      :footer="false"
      :close-on-overlay-click="false"
      class="add-account-dialog"
    >
      <div class="add-account-content">
        <div class="dialog-icon">
          <t-icon name="logo-telegram" size="48px" />
        </div>
        
        <div class="add-account-form">
          <!-- 第一行：区号和手机号输入 -->
          <div class="form-row">
            <t-row :gutter="[12, 0]">
              <t-col :span="4">
                <div class="form-item">
                  <label class="form-label">区号</label>
                  <t-input 
                    v-model="addAccountForm.countryCode" 
                    placeholder="+86"
                    class="country-code-input"
                  />
                </div>
              </t-col>
              <t-col :span="12">
                <div class="form-item">
                  <label class="form-label">手机号</label>
                  <t-input 
                    v-model="addAccountForm.phoneNumber" 
                    placeholder="请输入手机号码"
                    class="phone-input"
                  />
                </div>
              </t-col>
            </t-row>
          </div>
          
          <!-- 第二行：验证码和二级密码输入 -->
          <div class="form-row">
            <t-row :gutter="[12, 0]">
              <t-col :span="12">
                <div class="form-item">
                  <label class="form-label">验证码</label>
                  <t-input 
                    v-model="addAccountForm.verificationCode" 
                    placeholder="6位数字"
                    class="verification-input"
                    :disabled="!showAddAccountVerificationCode"
                  />
                </div>
              </t-col>
              <t-col :span="12">
                <div class="form-item">
                  <label class="form-label">二级密码</label>
                  <t-input 
                    v-model="addAccountForm.twoFactorPassword" 
                    placeholder="二级密码(可选)"
                    type="password"
                    class="two-factor-input"
                  />
                </div>
              </t-col>
            </t-row>
          </div>
        </div>
        
        <!-- 第三行：登录和取消按钮 -->
        <div class="dialog-footer">
          <div class="button-group">
            <t-button 
              theme="primary"
              :loading="loginLoading"
              @click="handleLogin"
              class="login-btn"
            >
              {{ showAddAccountVerificationCode ? '登录' : '发送验证码' }}
            </t-button>
            <t-button 
              variant="outline" 
              @click="closeAddAccountDialog" 
              class="cancel-btn"
            >
              取消
            </t-button>
          </div>
        </div>
      </div>
    </t-dialog>
  </div>
</template>

<script>
import TELEGRAM_CONFIG from '../config/telegram.js'
import axios from 'axios'

export default {
  name: 'TelegramAccountManagement',
  data() {
    return {
      // 添加账号弹窗相关
      addAccountDialogVisible: false,
      addAccountForm: {
        countryCode: '+86',
        phoneNumber: '',
        verificationCode: '',
        twoFactorPassword: '' // 新增：二级密码
      },
      showAddAccountVerificationCode: false,
      loginLoading: false, // 登录按钮的加载状态
      // 表格相关数据
      telegramAccountList: [],
      tableColumns: [
        {
          colKey: 'username',
          title: '用户名',
          width: 150,
          ellipsis: true
        },
        {
          colKey: 'firstName',
          title: '姓名',
          width: 120,
          cell: (h, { row }) => `${row.firstName} ${row.lastName || ''}`
        },
        {
          colKey: 'phone',
          title: '手机号',
          width: 150
        },
        {
          colKey: 'status',
          title: '状态',
          width: 100,
          cell: { col: 'status' }
        },
        {
          colKey: 'lastActive',
          title: '最后活跃',
          width: 160
        },
        {
          colKey: 'createTime',
          title: '添加时间',
          width: 160
        },
        {
          colKey: 'actions',
          title: '操作',
          width: 200,
          cell: { col: 'actions' }
        }
      ],
      tableLoading: false,
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0,
        showJumper: true,
        showSizer: true
      }
    }
  },
  methods: {
    // 弹窗相关方法
    showAddAccountDialog() {
      this.addAccountDialogVisible = true
    },
    
    closeAddAccountDialog() {
      this.addAccountDialogVisible = false
      this.showAddAccountVerificationCode = false
              this.addAccountForm = {
          countryCode: '+86',
          phoneNumber: '',
          verificationCode: '',
          twoFactorPassword: ''
        }
        this.loginLoading = false
    },
    

    
    // 表格相关方法
    async loadTelegramAccounts() {
      this.tableLoading = true
      try {
        const response = await axios.get('http://localhost:8000/api/telegram/accounts', {
          headers: {
            'Authorization': 'Bearer dummy_token' // 临时token，后续需要完善
          }
        })
        
        this.telegramAccountList = response.data.accounts.map(account => ({
          id: account.id,
          username: account.username || '未设置',
          firstName: account.first_name || '',
          lastName: account.last_name || '',
          phone: account.phone,
          status: account.status,
          lastActive: account.last_active,
          createTime: account.created_at
        }))
        
        this.pagination.total = response.data.total
        
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '加载账号列表失败')
      } finally {
        this.tableLoading = false
      }
    },
    
    async handleRefreshList() {
      this.tableLoading = true
      try {
        const response = await axios.post('http://localhost:8000/api/telegram/refresh_accounts', {}, {
          headers: {
            'Authorization': 'Bearer dummy_token' // 临时token，后续需要完善
          }
        })
        
        this.telegramAccountList = response.data.accounts.map(account => ({
          id: account.id,
          username: account.username || '未设置',
          firstName: account.first_name || '',
          lastName: account.last_name || '',
          phone: account.phone,
          status: account.status,
          lastActive: account.last_active,
          createTime: account.created_at
        }))
        
        this.pagination.total = response.data.total
        this.$message.success('账号列表已刷新')
        
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '刷新账号列表失败')
      } finally {
        this.tableLoading = false
      }
    },
    
    handlePageChange(pageInfo) {
      this.pagination.current = pageInfo.current
      // 这里可以调用API获取对应页面的数据
    },
    
    handlePageSizeChange(pageInfo) {
      this.pagination.pageSize = pageInfo.pageSize
      this.pagination.current = 1
      // 这里可以调用API获取对应页面大小的数据
    },
    
    getStatusText(status) {
      const statusMap = {
        online: '在线',
        offline: '离线',
        connecting: '连接中'
      }
      return statusMap[status] || '未知'
    },
    
    handleViewAccount(row) {
      this.$message.info(`查看账号详情: ${row.username}`)
      // 这里可以打开详情弹窗或跳转到详情页面
    },
    
    handleEditAccount(row) {
      this.$message.info(`编辑账号: ${row.username}`)
      // 这里可以打开编辑弹窗
    },
    
    async handleDeleteAccount(row) {
      this.$confirm(`确定要删除账号 ${row.username} 吗？`, '确认删除', {
        confirmBtn: '确定',
        cancelBtn: '取消'
      }).then(async () => {
        try {
          await axios.delete(`http://localhost:8000/api/telegram/accounts/${row.id}`, {
            headers: {
              'Authorization': 'Bearer dummy_token' // 临时token，后续需要完善
            }
          })
          
          this.$message.success('账号删除成功')
          
          // 重新加载账号列表
          this.loadTelegramAccounts()
          
        } catch (error) {
          this.$message.error(error.response?.data?.detail || '删除账号失败')
        }
      }).catch(() => {
        // 用户取消删除
      })
    },

         handleLogin() {
       if (!this.showAddAccountVerificationCode) {
         // 第一步：发送验证码
         if (!this.addAccountForm.phoneNumber) {
           this.$message.error('请输入手机号码')
           return
         }
         const fullPhone = this.addAccountForm.countryCode + this.addAccountForm.phoneNumber
         this.loginLoading = true
         axios.post('http://localhost:8000/api/telegram/send_code', {
           phone: fullPhone,
           api_id: TELEGRAM_CONFIG.API_ID,
           api_hash: TELEGRAM_CONFIG.API_HASH
         })
         .then(() => {
           this.showAddAccountVerificationCode = true
           this.$message.success('验证码已发送到您的Telegram')
         })
         .catch(error => {
           this.$message.error(error.response?.data?.detail || '发送验证码失败')
         })
         .finally(() => {
           this.loginLoading = false
         })
       } else {
         // 第二步：验证登录
         if (!this.addAccountForm.verificationCode) {
           this.$message.error('请输入验证码')
           return
         }
         const fullPhone = this.addAccountForm.countryCode + this.addAccountForm.phoneNumber
         this.loginLoading = true
         
         const loginData = {
           phone: fullPhone,
           verification_code: this.addAccountForm.verificationCode,
           api_id: TELEGRAM_CONFIG.API_ID,
           api_hash: TELEGRAM_CONFIG.API_HASH
         }
         
         // 如果有二级密码，添加到请求数据中
         if (this.addAccountForm.twoFactorPassword) {
           loginData.two_factor_password = this.addAccountForm.twoFactorPassword
         }
         
         axios.post('http://localhost:8000/api/telegram/verify_login', loginData, {
           headers: {
             'Authorization': 'Bearer dummy_token' // 临时token，后续需要完善
           }
         })
         .then(() => {
           this.$message.success('Telegram账号添加成功')
           this.closeAddAccountDialog()
           this.loadTelegramAccounts()
         })
         .catch(error => {
           this.$message.error(error.response?.data?.detail || '验证登录失败')
         })
         .finally(() => {
           this.loginLoading = false
         })
       }
     },

     
  },
  mounted() {
    // 页面加载时获取账号列表
    this.loadTelegramAccounts()
  }
}
</script>

<style scoped>





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



.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
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





.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
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

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}



.account-list .t-table {
  border-radius: 6px;
  overflow: hidden;
}

/* 添加账号弹窗样式 */
.add-account-dialog {
  text-align: center;
}

.add-account-content {
  padding: 24px 32px;
}

.dialog-icon {
  margin-bottom: 32px;
  color: #0088cc;
  text-align: center;
}

.add-account-form {
  margin-bottom: 32px;
}

.form-row {
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  height: 40px;
}

.form-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  width: 70px;
  text-align: right;
  white-space: nowrap;
  flex-shrink: 0;
}

.country-code-input,
.phone-input,
.verification-input,
.two-factor-input {
  flex: 1;
  height: 40px;
}

.country-code-input {
  text-align: center;
}

.verification-input {
  text-align: center;
  letter-spacing: 1px;
}

.two-factor-input {
  letter-spacing: 1px;
}



.button-group {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.login-btn,
.cancel-btn {
  min-width: 100px;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
}

.dialog-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #e5e6eb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .account-actions .t-col {
    span: 24;
    margin-bottom: 8px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 6px;
  }
  
  .info-label {
    margin-bottom: 2px;
  }
}
</style> 