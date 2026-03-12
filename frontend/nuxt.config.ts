export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxt/icon',
    '@nuxt/fonts',
  ],
  fonts: {
    families: [
      { name: 'Lato', provider: 'google' },
    ]
  },
  runtimeConfig: {
    public: {
      // Em Docker: NUXT_PUBLIC_API_BASE=http://localhost/api (via Nginx proxy)
      // Em dev local: NUXT_PUBLIC_API_BASE=http://localhost:8000
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    }
  },
  // SSR desligado — SPA pura, ideal para rede escolar sem Node rodando no server
  ssr: false,
})
