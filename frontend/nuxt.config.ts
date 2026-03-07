export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
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
})