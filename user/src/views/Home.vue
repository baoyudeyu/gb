<template>
  <div class="page-container">
    <t-card class="page-card">
      <template #header>
        <div class="card-header">
          <t-icon name="home" size="20px" />
          <span class="card-title">欢迎使用跟投系统</span>
        </div>
      </template>
      
      <div class="page-card-content">
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

.page-card-content {
  color: #6b7280;
  line-height: 1.6;
}
</style> 