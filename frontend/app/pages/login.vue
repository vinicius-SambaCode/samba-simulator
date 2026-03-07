<!-- pages/login.vue -->
<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">

      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-4">
          <Icon name="lucide:book-open" class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-white">SimuladoSP</h1>
        <p class="text-blue-200 text-sm mt-1">Secretaria Municipal de Educação</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-2xl p-6 shadow-2xl">
        <h2 class="text-lg font-semibold text-gray-900 mb-5">Acessar sistema</h2>

        <div class="space-y-4">
          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail institucional</label>
            <div class="relative">
              <Icon name="lucide:mail" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                v-model="form.email"
                type="email"
                placeholder="seu@email.edu.br"
                :disabled="loading"
                class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-50"
              />
            </div>
          </div>

          <!-- Senha -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <div class="relative">
              <Icon name="lucide:lock" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                :disabled="loading"
                class="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-50"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                @click="showPassword = !showPassword"
              >
                <Icon :name="showPassword ? 'lucide:eye-off' : 'lucide:eye'" class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Erro -->
          <div v-if="error" class="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <Icon name="lucide:alert-circle" class="w-4 h-4 text-red-500 flex-shrink-0" />
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>

          <!-- Botão -->
          <button
            :disabled="loading"
            class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
            @click="handleLogin"
          >
            <svg v-if="loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            {{ loading ? 'Entrando...' : 'Entrar' }}
          </button>
        </div>

        <!-- Mock dev -->
        <div class="mt-5 p-3 rounded-xl bg-gray-50 border border-dashed border-gray-200">
          <p class="text-xs font-semibold text-gray-500 mb-2">🛠 Modo dev — use qualquer senha:</p>
          <div class="space-y-1">
            <button @click="fillMock('root@')" class="text-xs text-blue-600 hover:underline block">root@... → painel Root</button>
            <button @click="fillMock('coord@')" class="text-xs text-blue-600 hover:underline block">coord@... → painel Coordenador</button>
            <button @click="fillMock('prof@')" class="text-xs text-blue-600 hover:underline block">prof@... → painel Professor</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { login, user, getDashboardRoute } = useAuth()

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

function fillMock(prefix: string) {
  form.email = prefix + 'escola.smesp.edu.br'
  form.password = '12345678'
}

async function handleLogin() {
  if (!form.email || !form.password) {
    error.value = 'Preencha e-mail e senha.'
    return
  }
  loading.value = true
  error.value = ''
  const success = await login(form.email, form.password)
  loading.value = false
  if (!success) {
    error.value = 'Credenciais inválidas. Tente novamente.'
    return
  }
  if (user.value) {
    await navigateTo(getDashboardRoute(user.value.role))
  }
}
</script>