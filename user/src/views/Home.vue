<template>
  <div class="home">
    <t-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <t-icon name="home" size="20px" />
          <span class="card-title">欢迎使用跟投系统</span>
        </div>
      </template>
      
      <div class="welcome-content">
        <p>这是首页内容区域，等待您的进一步完善。</p>
      </div>
    </t-card>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 24px;
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

.welcome-content {
  padding: 16px 0;
  color: #6b7280;
  line-height: 1.6;
}
</style> 