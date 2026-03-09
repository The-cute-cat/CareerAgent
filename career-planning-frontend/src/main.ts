import './assets/main.css'
import { createApp } from 'vue'
import pinia from './stores/index'
import App from './App.vue'
import router from './router'
//引入echarts
import * as echarts from 'echarts'

const app = createApp(App)

app.use(router)
app.use(pinia)

//放入全局
app.config.globalProperties.$echarts = echarts

app.mount('#app')
