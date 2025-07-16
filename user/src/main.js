import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import TDesign, { DialogPlugin } from 'tdesign-vue-next'
import 'tdesign-vue-next/es/style/index.css'

const app = createApp(App)
app.use(router)
app.use(TDesign)

// 将DialogPlugin挂载到全局属性上
app.config.globalProperties.$confirm = DialogPlugin.confirm

app.mount('#app') 