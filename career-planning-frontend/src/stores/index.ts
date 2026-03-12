import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

export default pinia

// import { useUserStore } from './modules/user'
// export { useUserStore }
// 等价于下面的从模块导出

export * from './modules/user'
