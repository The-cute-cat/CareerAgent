import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import mkcert from 'vite-plugin-mkcert'

export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    mkcert({ source: 'coding' })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 8081,
    open: true,
    proxy: {
      '/api': {
        // 👇 修改这里：把 localhost 换成你的服务器公网 IP
        target: 'http://49.235.164.243:8080',

        changeOrigin: true, // 保持为 true，这会把请求头的 Host 修改为目标地址

        // ⚠️ 注意：关于 rewrite 的说明请看下面的“重要检查”
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  }
})