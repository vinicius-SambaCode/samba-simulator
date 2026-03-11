<!-- pages/login.vue -->
<template>
  <div class="min-h-screen bg-white flex">

    <!-- Painel esquerdo — visual -->
    <div class="hidden lg:flex flex-col justify-between w-[52%] bg-[#0A0A0F] p-12 relative overflow-hidden">

      <!-- Grid de fundo -->
      <div class="absolute inset-0"
        style="background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 48px 48px;" />

      <!-- Orbs de luz -->
      <div class="absolute top-[-120px] left-[-80px] w-[420px] h-[420px] rounded-full"
        style="background: radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);" />
      <div class="absolute bottom-[-80px] right-[-60px] w-[320px] h-[320px] rounded-full"
        style="background: radial-gradient(circle, rgba(99,102,241,0.14) 0%, transparent 70%);" />

      <!-- Logo + badge -->
      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-9 h-9 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center">
            <Icon name="lucide:graduation-cap" class="w-5 h-5 text-white" />
          </div>
          <span class="text-white font-bold text-lg tracking-tight">samba edvance</span>
        </div>
        <span class="text-xs font-semibold text-blue-400 tracking-widest uppercase">
          Plataforma de Simulados
        </span>
      </div>

      <!-- Centro: headline -->
      <div class="relative z-10 space-y-6">
        <div class="space-y-3">
          <p class="text-white/30 text-xs font-semibold tracking-widest uppercase">Secretaria Municipal de Educação</p>
          <h1 class="text-4xl font-black text-white leading-[1.15] tracking-tight">
            Gestão inteligente<br />
            <span class="text-transparent"
              style="background: linear-gradient(90deg, #60a5fa, #818cf8); -webkit-background-clip: text; background-clip: text;">
              de simulados
            </span>
          </h1>
          <p class="text-white/40 text-sm leading-relaxed max-w-xs">
            Crie, distribua e acompanhe simulados pedagógicos com precisão e eficiência.
          </p>
        </div>

        <!-- Três pilares -->
        <div class="space-y-3 pt-2">
          <div v-for="item in pilares" :key="item.label"
            class="flex items-center gap-3 p-3 rounded-xl border border-white/5 bg-white/[0.03]">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              :style="`background: ${item.color}18; border: 1px solid ${item.color}30;`">
              <Icon :name="item.icon" class="w-4 h-4" :style="`color: ${item.color}`" />
            </div>
            <div>
              <p class="text-white text-xs font-semibold">{{ item.label }}</p>
              <p class="text-white/30 text-[11px]">{{ item.sub }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Rodapé -->
      <div class="relative z-10 flex items-center justify-between">
        <p class="text-white/20 text-xs">© 2026 samba edvance</p>
        <div class="flex items-center gap-1.5">
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span class="text-white/30 text-xs">Sistema online</span>
        </div>
      </div>
    </div>

    <!-- Painel direito — formulário -->
    <div class="flex-1 flex flex-col items-center justify-center px-6 py-12 relative">

      <!-- Logo mobile -->
      <div class="lg:hidden flex items-center gap-2 mb-10">
        <div class="w-8 h-8 rounded-xl bg-gray-900 flex items-center justify-center">
          <Icon name="lucide:graduation-cap" class="w-4 h-4 text-white" />
        </div>
        <span class="font-black text-gray-900 tracking-tight">samba edvance</span>
      </div>

      <div class="w-full max-w-[360px] space-y-8">

        <!-- Cabeçalho do form -->
        <div>
          <h2 class="text-2xl font-black text-gray-900 tracking-tight">Bem-vindo de volta</h2>
          <p class="text-gray-400 text-sm mt-1">Entre com suas credenciais institucionais</p>
        </div>

        <!-- Form -->
        <div class="space-y-4">

          <!-- Email -->
          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-widest">E-mail</label>
            <div class="relative group">
              <Icon name="lucide:at-sign"
                class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors duration-200"
                :class="focused === 'email' ? 'text-blue-500' : 'text-gray-300'" />
              <input
                v-model="form.email"
                type="email"
                placeholder="seu@email.edu.br"
                :disabled="loading"
                autocomplete="email"
                class="w-full pl-10 pr-4 py-3 bg-gray-50 border rounded-xl text-sm text-gray-900 placeholder-gray-300 transition-all duration-200 outline-none disabled:opacity-50"
                :class="focused === 'email'
                  ? 'border-blue-400 bg-white ring-4 ring-blue-50'
                  : 'border-gray-200 hover:border-gray-300'"
                @focus="focused = 'email'"
                @blur="focused = ''"
              />
            </div>
          </div>

          <!-- Senha -->
          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-widest">Senha</label>
            <div class="relative group">
              <Icon name="lucide:key-round"
                class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors duration-200"
                :class="focused === 'password' ? 'text-blue-500' : 'text-gray-300'" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                :disabled="loading"
                autocomplete="current-password"
                class="w-full pl-10 pr-11 py-3 bg-gray-50 border rounded-xl text-sm text-gray-900 placeholder-gray-300 transition-all duration-200 outline-none disabled:opacity-50"
                :class="focused === 'password'
                  ? 'border-blue-400 bg-white ring-4 ring-blue-50'
                  : 'border-gray-200 hover:border-gray-300'"
                @focus="focused = 'password'"
                @blur="focused = ''"
                @keyup.enter="handleLogin"
              />
              <button type="button"
                class="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500 transition-colors"
                tabindex="-1"
                @click="showPassword = !showPassword">
                <Icon :name="showPassword ? 'lucide:eye-off' : 'lucide:eye'" class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Erro -->
          <Transition name="shake">
            <div v-if="error"
              class="flex items-center gap-2.5 px-4 py-3 bg-red-50 border border-red-100 rounded-xl">
              <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
              <p class="text-xs text-red-500 font-medium">{{ error }}</p>
            </div>
          </Transition>

          <!-- Botão entrar -->
          <button
            :disabled="loading || !form.email || !form.password"
            class="w-full py-3 rounded-xl text-sm font-bold transition-all duration-200 flex items-center justify-center gap-2 relative overflow-hidden"
            :class="loading || !form.email || !form.password
              ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
              : 'bg-gray-900 hover:bg-gray-800 text-white shadow-lg shadow-gray-900/10 active:scale-[0.98]'"
            @click="handleLogin">
            <svg v-if="loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <Icon v-else name="lucide:log-in" class="w-4 h-4" />
            {{ loading ? 'Autenticando...' : 'Entrar' }}
          </button>
        </div>

        <!-- Divisor -->
        <div class="flex items-center gap-3">
          <div class="flex-1 h-px bg-gray-100" />
          <span class="text-[11px] text-gray-300 font-semibold tracking-widest uppercase">Dev</span>
          <div class="flex-1 h-px bg-gray-100" />
        </div>

        <!-- Atalhos dev -->
        <div class="space-y-2">
          <p class="text-[11px] text-gray-300 font-semibold uppercase tracking-widest mb-3">Acessos rápidos</p>
          <button
            v-for="acc in devAccounts"
            :key="acc.email"
            class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl border border-gray-100 hover:border-gray-200 hover:bg-gray-50 transition-all duration-150 group text-left"
            @click="fillMock(acc.email, acc.password)">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors"
              :class="[acc.iconBg, 'group-hover:opacity-90']">
              <Icon :name="acc.icon" class="w-3.5 h-3.5" :class="acc.iconColor" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-gray-700">{{ acc.label }}</p>
              <p class="text-[11px] text-gray-400 truncate">{{ acc.email }}</p>
            </div>
            <Icon name="lucide:arrow-right"
              class="w-3.5 h-3.5 text-gray-200 group-hover:text-gray-400 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { login, user, getDashboardRoute } = useAuth()

const form         = reactive({ email: '', password: '' })
const loading      = ref(false)
const error        = ref('')
const showPassword = ref(false)
const focused      = ref('')

const pilares = [
  { icon: 'lucide:file-text',     label: 'Criação de simulados',    sub: 'Wizards guiados passo a passo',  color: '#60a5fa' },
  { icon: 'lucide:users',         label: 'Gestão de professores',   sub: 'Atribuição e acompanhamento',    color: '#818cf8' },
  { icon: 'lucide:bar-chart-2',   label: 'Resultados em tempo real', sub: 'Gabaritos e relatórios',         color: '#34d399' },
]

const devAccounts = [
  { label: 'Root / Admin',     email: 'admin@samba.local',           password: 'admin123', icon: 'lucide:shield',         iconBg: 'bg-gray-900',    iconColor: 'text-white' },
  { label: 'Coordenador',      email: 'coord@samba.local',           password: 'coord123', icon: 'lucide:layout-dashboard', iconBg: 'bg-blue-50',    iconColor: 'text-blue-600' },
  { label: 'Prof. Matemática', email: 'prof.matematica@samba.local', password: 'prof123',  icon: 'lucide:book-open',      iconBg: 'bg-orange-50',   iconColor: 'text-orange-500' },
]

function fillMock(email: string, password: string) {
  form.email    = email
  form.password = password
  error.value   = ''
}

async function handleLogin() {
  if (!form.email || !form.password) {
    error.value = 'Preencha e-mail e senha.'
    return
  }
  loading.value = true
  error.value   = ''

  const success = await login(form.email, form.password)
  loading.value = false

  if (!success) {
    error.value = 'Credenciais inválidas. Verifique e tente novamente.'
    return
  }

  if (user.value) {
    await navigateTo(getDashboardRoute(user.value.role))
  }
}
</script>

<style scoped>
.shake-enter-active {
  animation: shake 0.35s ease;
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%       { transform: translateX(-6px); }
  40%       { transform: translateX(6px); }
  60%       { transform: translateX(-4px); }
  80%       { transform: translateX(4px); }
}
</style>