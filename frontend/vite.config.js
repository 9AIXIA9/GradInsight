import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      host: env.VITE_DEV_HOST || 'localhost',
      port: parseInt(env.VITE_DEV_PORT) || 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
    define: {
      // 将环境变量暴露给前端代码
      __APP_NAME__: JSON.stringify(env.VITE_APP_NAME || 'GradInsight'),
      __APP_TITLE__: JSON.stringify(env.VITE_APP_TITLE || '高校数据分析平台'),
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION || '1.0.0'),
    },
  }
})
