import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // 이미 설정되어 있다면 생략 가능
  },
  server: {
    historyApiFallback: true, // Vite 내장 개발 서버에서 history fallback 설정
  },
  base: '/', // 배포 경로에 맞게 설정
});
