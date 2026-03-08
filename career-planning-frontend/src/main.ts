import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
//引入echarts
import * as echarts from 'echarts';
import 'element-plus/dist/index.css'                            

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(ElementPlus)

//放入全局
app.config.globalProperties.$echarts = echarts

app.mount('#app')


