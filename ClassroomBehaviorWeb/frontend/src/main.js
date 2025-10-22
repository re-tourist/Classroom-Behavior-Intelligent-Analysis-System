// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 导入路由实例
import { createPinia } from 'pinia' // 状态管理
import ElementPlus from 'element-plus' // UI组件库
import 'element-plus/dist/index.css' // UI样式

import ECharts from 'vue-echarts'
// 创建应用实例
const app = createApp(App)

// 安装插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.component('echarts', ECharts) // 注册为全局组件
// 挂载到DOM
app.mount('#app') // 确保index.html中有id为app的元素