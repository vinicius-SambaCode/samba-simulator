// plugins/auth.client.ts
//
// Executado UMA VEZ no client, antes de qualquer rota ser resolvida.
// Se existe token no cookie mas currentUser ainda está null (ex: F5),
// chama fetchMe para reidratar o user antes do middleware rodar.

export default defineNuxtPlugin(async () => {
  const { user, fetchMe } = useAuth()
  const { accessToken }   = useApi()

  if (accessToken.value && !user.value) {
    await fetchMe()
  }
})