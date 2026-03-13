<!-- pages/trocar-senha.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
    style="background: #0c0e14">

    <!-- Glow de fundo reativo à força da senha -->
    <div class="absolute inset-0 pointer-events-none transition-all duration-1000"
      :style="`background: radial-gradient(ellipse 600px 400px at 50% 60%, ${glowBg}15 0%, transparent 70%)`" />

    <!-- Grid sutil -->
    <div class="absolute inset-0 pointer-events-none opacity-[0.025]"
      style="background-image: linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);background-size:48px 48px" />

    <div class="relative z-10 w-full max-w-[420px]">

      <!-- Cabeçalho -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-5 transition-all duration-700"
          :style="`background:${glowBg}20;border:1px solid ${glowBg}40;box-shadow:0 0 32px ${glowBg}25`">
          <svg class="w-8 h-8 transition-colors duration-700" fill="none" viewBox="0 0 24 24"
            stroke-width="1.5" :stroke="glowBg">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
          </svg>
        </div>
        <h1 class="text-[22px] font-black text-white tracking-tight">Crie sua senha pessoal</h1>
        <p class="text-sm text-gray-500 mt-1.5 leading-snug">
          Primeiro acesso detectado.<br>Defina uma senha forte e segura.
        </p>
      </div>

      <!-- Card -->
      <div class="rounded-2xl p-6 space-y-5"
        style="background:#131720;border:1px solid rgba(255,255,255,0.07);box-shadow:0 24px 64px rgba(0,0,0,0.5)">

        <!-- Campo: senha provisória -->
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-widest text-gray-500">Senha provisória</label>
          <div class="relative">
            <input
              v-model="senhaAtual"
              :type="show.atual ? 'text' : 'password'"
              placeholder="Senha recebida por e-mail"
              autocomplete="current-password"
              class="w-full rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 pr-10 outline-none transition-all duration-200"
              style="background:#0c0e14;border:1px solid rgba(255,255,255,0.1)"
              @focus="(e: FocusEvent) => (e.target as HTMLElement).style.borderColor='rgba(255,255,255,0.25)'"
              @blur="(e: FocusEvent) => (e.target as HTMLElement).style.borderColor='rgba(255,255,255,0.1)'"
            />
            <button type="button" @click="show.atual = !show.atual" tabindex="-1"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors">
              <EyeIcon :open="show.atual" />
            </button>
          </div>
        </div>

        <!-- Campo: nova senha -->
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-widest text-gray-500">Nova senha</label>
          <div class="relative">
            <input
              v-model="novaSenha"
              :type="show.nova ? 'text' : 'password'"
              placeholder="Mínimo 8 caracteres"
              autocomplete="new-password"
              class="w-full rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 pr-10 outline-none transition-all duration-200"
              :style="`background:#0c0e14;border:1px solid ${novaSenha ? glowBorder : 'rgba(255,255,255,0.1)'}`"
            />
            <button type="button" @click="show.nova = !show.nova" tabindex="-1"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors">
              <EyeIcon :open="show.nova" />
            </button>
          </div>

          <!-- Barra de força -->
          <Transition name="expand">
            <div v-if="novaSenha" class="space-y-2 pt-0.5">
              <div class="flex gap-1.5">
                <div v-for="i in 5" :key="i" class="h-1 flex-1 rounded-full transition-all duration-500"
                  :style="i <= forcaNivel ? `background:${glowBg}` : 'background:rgba(255,255,255,0.07)'" />
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-semibold transition-colors duration-500"
                  :style="`color:${glowBg}`">{{ forcaLabel }}</span>
                <span class="text-[11px] text-gray-600">{{ novaSenha.length }}/16</span>
              </div>

              <!-- Checklist de requisitos -->
              <div class="grid grid-cols-2 gap-1 pt-0.5">
                <div v-for="r in requisitos" :key="r.label"
                  class="flex items-center gap-1.5 transition-all duration-300"
                  :class="r.ok ? 'opacity-100' : 'opacity-40'">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300"
                    :style="r.ok ? `background:${glowBg}25;` : 'background:rgba(255,255,255,0.05)'">
                    <svg v-if="r.ok" class="w-2.5 h-2.5" fill="none" viewBox="0 0 12 12"
                      :style="`stroke:${glowBg}`" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2 6l3 3 5-5" />
                    </svg>
                    <div v-else class="w-1 h-1 rounded-full bg-gray-600" />
                  </div>
                  <span class="text-[11px] text-gray-400">{{ r.label }}</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Campo: confirmação -->
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-widest text-gray-500">Confirmar nova senha</label>
          <div class="relative">
            <input
              v-model="confirmar"
              :type="show.confirmar ? 'text' : 'password'"
              placeholder="Repita a nova senha"
              autocomplete="new-password"
              class="w-full rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 pr-10 outline-none transition-all duration-200"
              :style="`background:#0c0e14;border:1px solid ${
                confirmar
                  ? (senhasIguais ? 'rgba(16,185,129,0.5)' : 'rgba(239,68,68,0.4)')
                  : 'rgba(255,255,255,0.1)'
              }`"
              @keydown.enter="submeter"
            />
            <button type="button" @click="show.confirmar = !show.confirmar" tabindex="-1"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors">
              <EyeIcon :open="show.confirmar" />
            </button>
          </div>
          <Transition name="slide">
            <p v-if="confirmar && !senhasIguais"
              class="text-[11px] text-red-400 flex items-center gap-1.5">
              <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM8.28 7.22a.75.75 0 0 0-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 1 0 1.06 1.06L10 11.06l1.72 1.72a.75.75 0 1 0 1.06-1.06L11.06 10l1.72-1.72a.75.75 0 0 0-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd"/>
              </svg>
              As senhas não coincidem
            </p>
          </Transition>
        </div>

        <!-- Erro geral -->
        <Transition name="slide">
          <div v-if="erro"
            class="flex gap-2.5 rounded-xl px-4 py-3"
            style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2)">
            <svg class="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM8.28 7.22a.75.75 0 0 0-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 1 0 1.06 1.06L10 11.06l1.72 1.72a.75.75 0 1 0 1.06-1.06L11.06 10l1.72-1.72a.75.75 0 0 0-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd"/>
            </svg>
            <p class="text-xs text-red-400 leading-relaxed">{{ erro }}</p>
          </div>
        </Transition>

        <!-- Botão -->
        <button
          @click="submeter"
          :disabled="!podeSubmeter || loading"
          class="w-full py-3.5 rounded-xl text-sm font-bold tracking-wide transition-all duration-300 relative overflow-hidden"
          :class="podeSubmeter && !loading
            ? 'text-white cursor-pointer hover:brightness-110 active:scale-[0.98]'
            : 'cursor-not-allowed'"
          :style="podeSubmeter && !loading
            ? `background:linear-gradient(135deg,${glowBg},${glowBg}bb);box-shadow:0 8px 24px ${glowBg}35`
            : 'background:rgba(255,255,255,0.05);color:rgba(255,255,255,0.2)'">
          <span v-if="!loading" class="flex items-center justify-center gap-2">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
            </svg>
            Definir senha e entrar
          </span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            Aguarde…
          </span>
        </button>
      </div>

      <p class="text-center text-[11px] text-gray-700 mt-5">
        SAMBA Simulator · Acesso restrito à instituição
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

// ── ícone de olho inline ────────────────────────────────────────────────────
const EyeIcon = defineComponent({
  props: { open: Boolean },
  template: `
    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
      <template v-if="open">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"/>
      </template>
      <template v-else>
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.964-7.178Z"/>
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
      </template>
    </svg>
  `
})

const { user, fetchMe, getDashboardRoute } = useAuth()
const { accessToken } = useApi()

const senhaAtual = ref('')
const novaSenha  = ref('')
const confirmar  = ref('')
const show       = reactive({ atual: false, nova: false, confirmar: false })
const loading    = ref(false)
const erro       = ref('')

// Requisitos de senha
const requisitos = computed(() => [
  { label: '8 a 16 caracteres',   ok: novaSenha.value.length >= 8 && novaSenha.value.length <= 16 },
  { label: 'Letra maiúscula',     ok: /[A-Z]/.test(novaSenha.value) },
  { label: 'Letra minúscula',     ok: /[a-z]/.test(novaSenha.value) },
  { label: 'Número',              ok: /\d/.test(novaSenha.value) },
  { label: 'Caractere especial',  ok: /[@#$%&*!?]/.test(novaSenha.value) },
])

const forcaNivel = computed(() => requisitos.value.filter(r => r.ok).length)

const forcaLabel = computed(() =>
  ['', 'Muito fraca', 'Fraca', 'Razoável', 'Boa', 'Forte'][forcaNivel.value] ?? ''
)

// Cor reativa conforme força
const glowBg = computed(() => {
  if (!novaSenha.value) return '#6366f1'
  if (forcaNivel.value <= 1) return '#ef4444'
  if (forcaNivel.value === 2) return '#f97316'
  if (forcaNivel.value === 3) return '#eab308'
  if (forcaNivel.value === 4) return '#22c55e'
  return '#10b981'
})

const glowBorder = computed(() => {
  if (forcaNivel.value === 5) return 'rgba(16,185,129,0.5)'
  if (forcaNivel.value >= 3)  return 'rgba(234,179,8,0.4)'
  return 'rgba(239,68,68,0.35)'
})

const senhasIguais = computed(() =>
  novaSenha.value.length > 0 && novaSenha.value === confirmar.value
)

const podeSubmeter = computed(() =>
  senhaAtual.value.length > 0 &&
  forcaNivel.value === 5 &&
  senhasIguais.value
)

async function submeter() {
  if (!podeSubmeter.value || loading.value) return
  erro.value = ''
  loading.value = true

  try {
    const token = accessToken.value
    const res = await fetch('http://localhost:8000/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      credentials: 'include',
      body: JSON.stringify({
        current_password: senhaAtual.value,
        new_password:     novaSenha.value,
      }),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      erro.value = data.detail ?? 'Não foi possível alterar a senha.'
      return
    }

    await fetchMe()
    if (!user.value) { await navigateTo('/login'); return }
    await navigateTo(getDashboardRoute(user.value.role))

  } catch {
    erro.value = 'Erro de conexão. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.expand-enter-active { transition: all 0.3s ease; }
.expand-leave-active { transition: all 0.2s ease; }
.expand-enter-from, .expand-leave-to { opacity: 0; transform: translateY(-6px); }

.slide-enter-active { transition: all 0.2s ease; }
.slide-leave-active { transition: all 0.15s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
