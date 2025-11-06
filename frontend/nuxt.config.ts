import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  ssr: false,
  runtimeConfig: {
    public: {
      backendUrl: process.env.FRONTEND_BACKEND_URL ?? 'http://localhost:5001'
    }
  }
})