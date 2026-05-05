import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'

import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import 'highlight.js/styles/atom-one-dark.css'
import './style.css'

// EP 暗色主题需要 <html class="dark"> 才生效。
// 整个应用都是暗色，无论用户切到哪个主题（cyber/nebula/matrix/sunset/minimal）
// 都保持 dark class —— 我们的 style.css 通过 [data-theme] 在此基础上做风格变化。
document.documentElement.classList.add('dark')

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
