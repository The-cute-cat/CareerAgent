import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import mkcert from 'vite-plugin-mkcert'
// import vueDevTools from 'vite-plugin-vue-devtools'


export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    // vueDevTools(),测试插件
    //利用插件mkcert生成本地开发环境的SSL证书，解决HTTPS请求时的安全警告问题
    mkcert({
      source: 'coding' // 使用国内镜像源
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // 配置代理，将/api开头的请求代理到http://localhost:8080/api
  server: {
    port: 8081,
    open: true,
    proxy: {
      '/api': {
<<<<<<< HEAD
<<<<<<< HEAD
        // target: 'http://49.235.164.243:8080',
        target: 'http://localhost:8080',
=======
        //target: 'http://49.235.164.243:8080',
        target: 'http://127.0.0.1:8080',
>>>>>>> origin/master
=======
        //target: 'http://49.235.164.243:8080',
        target: 'http://127.0.0.1:8080',
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  }
})
