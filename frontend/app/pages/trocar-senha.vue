<template>
  <div class="shell">
    <div class="bg-grid" />

    <div class="card" :class="{ ready: mounted }">

      <!-- Topo -->
      <div class="card-top">
        <div class="logo-wrap">
          <img src="/svg/edvance-logo2.svg" alt="Edvance" class="logo-img" />
        </div>
        <span class="first-badge">Primeiro acesso</span>
      </div>

      <!-- Heading -->
      <div class="card-heading">
        <div class="lock-icon" :style="`background:linear-gradient(135deg,${glowBg},${glowBgDark});box-shadow:0 8px 24px ${glowBg}40`">
          <Icon name="lucide:lock-keyhole-open" class="w-5 h-5 text-white" />
        </div>
        <h1 class="heading-title">Crie sua senha pessoal</h1>
        <p class="heading-sub">Primeiro acesso detectado. Defina uma senha forte.</p>
      </div>

      <!-- Formulário -->
      <div class="form">

        <!-- Senha provisória -->
        <div class="field">
          <label class="field-label">Senha provisória</label>
          <div class="input-wrap" :class="focused==='atual'?'input-wrap--focus':''">
            <Icon name="lucide:key-round" class="input-icon" :class="focused==='atual'?'text-blue-500':'text-gray-400'" />
            <input v-model="senhaAtual"
              :type="show.atual?'text':'password'"
              placeholder="Senha recebida por e-mail"
              autocomplete="current-password"
              class="field-input"
              @focus="focused='atual'" @blur="focused=''" />
            <button type="button" class="eye-btn" tabindex="-1" @click="show.atual=!show.atual">
              <Icon :name="show.atual?'lucide:eye-off':'lucide:eye'" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Nova senha -->
        <div class="field">
          <label class="field-label">Nova senha</label>
          <div class="input-wrap" :class="focused==='nova'?'input-wrap--focus':''">
            <Icon name="lucide:lock" class="input-icon" :class="focused==='nova'?'text-blue-500':'text-gray-400'" />
            <input v-model="novaSenha"
              :type="show.nova?'text':'password'"
              placeholder="Mínimo 8 caracteres"
              autocomplete="new-password"
              class="field-input"
              @focus="focused='nova'" @blur="focused=''" />
            <button type="button" class="eye-btn" tabindex="-1" @click="show.nova=!show.nova">
              <Icon :name="show.nova?'lucide:eye-off':'lucide:eye'" class="w-4 h-4" />
            </button>
          </div>

          <!-- Barra de força -->
          <Transition name="expand">
            <div v-if="novaSenha" class="strength-block">
              <div class="strength-bars">
                <div v-for="i in 5" :key="i" class="strength-bar"
                  :style="i<=forcaNivel?`background:${glowBg}`:'background:#e5e7eb'" />
              </div>
              <div class="strength-row">
                <span class="strength-label" :style="`color:${glowBg}`">{{ forcaLabel }}</span>
                <span class="strength-len">{{ novaSenha.length }}/16</span>
              </div>
              <!-- Requisitos -->
              <div class="req-grid">
                <div v-for="r in requisitos" :key="r.label"
                  class="req-item" :class="r.ok?'req-ok':'req-off'">
                  <div class="req-dot" :style="r.ok?`background:${glowBg}25`:'background:#f3f4f6'">
                    <Icon v-if="r.ok" name="lucide:check" class="w-2.5 h-2.5" :style="`color:${glowBg}`" />
                    <div v-else class="w-1 h-1 rounded-full bg-gray-300" />
                  </div>
                  <span>{{ r.label }}</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Confirmar -->
        <div class="field">
          <label class="field-label">Confirmar nova senha</label>
          <div class="input-wrap"
            :class="[focused==='confirmar'?'input-wrap--focus':'', confirmar&&senhasIguais?'input-wrap--ok':confirmar&&!senhasIguais?'input-wrap--err':'']">
            <Icon name="lucide:shield-check" class="input-icon text-gray-400" />
            <input v-model="confirmar"
              :type="show.confirmar?'text':'password'"
              placeholder="Repita a nova senha"
              autocomplete="new-password"
              class="field-input"
              @focus="focused='confirmar'" @blur="focused=''"
              @keyup.enter="submeter" />
            <button type="button" class="eye-btn" tabindex="-1" @click="show.confirmar=!show.confirmar">
              <Icon :name="show.confirmar?'lucide:eye-off':'lucide:eye'" class="w-4 h-4" />
            </button>
          </div>
          <Transition name="slide">
            <p v-if="confirmar&&!senhasIguais" class="match-error">
              <Icon name="lucide:x-circle" class="w-3 h-3 flex-shrink-0" /> As senhas não coincidem
            </p>
          </Transition>
        </div>

        <!-- Erro geral -->
        <Transition name="shake">
          <div v-if="erro" class="error-box">
            <Icon name="lucide:shield-alert" class="w-4 h-4 flex-shrink-0 text-red-400" />
            {{ erro }}
          </div>
        </Transition>

        <!-- Botão -->
        <button class="btn-submit"
          :class="podeSubmeter&&!loading?'btn-submit--on':'btn-submit--off'"
          :style="podeSubmeter&&!loading?`background:linear-gradient(135deg,${glowBg},${glowBgDark});box-shadow:0 8px 20px ${glowBg}35`:undefined"
          :disabled="!podeSubmeter||loading"
          @click="submeter">
          <template v-if="!loading">
            <Icon name="lucide:shield-check" class="w-4 h-4" />
            Definir senha e entrar
          </template>
          <template v-else>
            <svg class="spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
              <path fill="currentColor" d="M4 12a8 8 0 018-8v8z" class="opacity-75"/>
            </svg>
            Aguarde…
          </template>
        </button>
      </div>

      <p class="card-footer">© 2026 samba edvance · Acesso restrito</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { user, fetchMe, getDashboardRoute } = useAuth()
const { accessToken } = useApi()
const mounted = ref(false)
onMounted(async () => { await nextTick(); setTimeout(() => { mounted.value = true }, 40) })

const senhaAtual = ref(''); const novaSenha = ref(''); const confirmar = ref('')
const show     = reactive({ atual: false, nova: false, confirmar: false })
const focused  = ref(''); const loading = ref(false); const erro = ref('')

const requisitos = computed(() => [
  { label: '8 a 16 caracteres',  ok: novaSenha.value.length >= 8 && novaSenha.value.length <= 16 },
  { label: 'Letra maiúscula',    ok: /[A-Z]/.test(novaSenha.value) },
  { label: 'Letra minúscula',    ok: /[a-z]/.test(novaSenha.value) },
  { label: 'Número',             ok: /\d/.test(novaSenha.value) },
  { label: 'Caractere especial', ok: /[@#$%&*!?]/.test(novaSenha.value) },
])
const forcaNivel = computed(() => requisitos.value.filter(r => r.ok).length)
const forcaLabel = computed(() =>
  ['', 'Muito fraca', 'Fraca', 'Razoável', 'Boa', 'Forte'][forcaNivel.value] ?? ''
)
const glowBg = computed(() => {
  if (!novaSenha.value) return '#3b82f6'
  if (forcaNivel.value <= 1) return '#ef4444'
  if (forcaNivel.value === 2) return '#f97316'
  if (forcaNivel.value === 3) return '#eab308'
  if (forcaNivel.value === 4) return '#22c55e'
  return '#10b981'
})
const glowBgDark = computed(() => {
  if (!novaSenha.value) return '#2563eb'
  if (forcaNivel.value <= 1) return '#dc2626'
  if (forcaNivel.value === 2) return '#ea580c'
  if (forcaNivel.value === 3) return '#ca8a04'
  if (forcaNivel.value === 4) return '#16a34a'
  return '#059669'
})
const senhasIguais = computed(() => novaSenha.value.length > 0 && novaSenha.value === confirmar.value)
const podeSubmeter = computed(() =>
  senhaAtual.value.length > 0 && forcaNivel.value === 5 && senhasIguais.value
)

async function submeter() {
  if (!podeSubmeter.value || loading.value) return
  erro.value = ''; loading.value = true
  try {
    const token = accessToken.value
    const { apiBase } = useRuntimeConfig().public
    const res = await fetch(`${apiBase}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      credentials: 'include',
      body: JSON.stringify({ current_password: senhaAtual.value, new_password: novaSenha.value }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      erro.value = data.detail ?? 'Não foi possível alterar a senha.'
      return
    }
    await fetchMe()
    if (!user.value) { await navigateTo('/login'); return }
    await navigateTo(getDashboardRoute(user.value.role))
  } catch { erro.value = 'Erro de conexão. Tente novamente.' }
  finally { loading.value = false }
}
</script>

<style scoped>
.shell {
  min-height:100vh; display:flex; align-items:center; justify-content:center;
  background:#f1f5f9; padding:1.5rem; position:relative; overflow:hidden;
}
.bg-grid {
  position:absolute; inset:0;
  background-image:linear-gradient(rgba(0,0,0,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,0,0,.04) 1px,transparent 1px);
  background-size:52px 52px;
}
.shell::before {
  content:''; position:absolute; top:-15%; left:50%; transform:translateX(-50%);
  width:700px; height:400px; border-radius:50%;
  background:radial-gradient(ellipse,rgba(37,99,235,.07) 0%,transparent 70%);
  pointer-events:none;
}
.card {
  position:relative; width:100%; max-width:420px; background:white;
  border:1px solid #e2e8f0; border-radius:1.25rem; padding:2rem;
  display:flex; flex-direction:column; gap:1.75rem;
  box-shadow:0 20px 48px rgba(0,0,0,.1);
  opacity:0; transform:translateY(16px) scale(.98);
  transition:opacity .45s ease, transform .45s cubic-bezier(.22,1,.36,1);
}
.card.ready { opacity:1; transform:translateY(0) scale(1); }

.card-top { display:flex; align-items:center; justify-content:space-between; }
.logo-wrap { display:flex; align-items:center; }
.logo-img  { height:1.75rem; width:auto; }
.first-badge {
  font-size:.65rem; font-weight:700; padding:.25rem .75rem;
  background:#fef3c7; border:1px solid #fde68a; border-radius:9999px; color:#92400e;
}

.card-heading { display:flex; flex-direction:column; align-items:center; gap:.75rem; text-align:center; }
.lock-icon {
  width:3rem; height:3rem; border-radius:1rem;
  display:flex; align-items:center; justify-content:center;
  transition:background .5s ease, box-shadow .5s ease;
}
.heading-title { font-size:1.35rem; font-weight:800; color:#0f172a; margin:0; letter-spacing:-.02em; }
.heading-sub   { font-size:.75rem; color:#64748b; margin:0; }

.form { display:flex; flex-direction:column; gap:1rem; }
.field { display:flex; flex-direction:column; gap:.4rem; }
.field-label { font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:#64748b; }
.input-wrap {
  position:relative; display:flex; align-items:center;
  background:#f8fafc; border:1px solid #e2e8f0; border-radius:.75rem;
  transition:border-color .15s, box-shadow .15s, background .15s;
}
.input-wrap--focus { border-color:#3b82f6; box-shadow:0 0 0 3px rgba(59,130,246,.12); background:white; }
.input-wrap--ok    { border-color:#10b981; box-shadow:0 0 0 3px rgba(16,185,129,.1); }
.input-wrap--err   { border-color:#f87171; box-shadow:0 0 0 3px rgba(239,68,68,.08); }
.input-icon { position:absolute; left:.875rem; width:1rem; height:1rem; pointer-events:none; transition:color .15s; }
.field-input {
  width:100%; padding:.75rem .875rem .75rem 2.5rem; background:none;
  border:none; outline:none; font-size:.875rem; color:#0f172a; caret-color:#3b82f6;
}
.field-input::placeholder { color:#cbd5e1; }
.eye-btn { position:absolute; right:.75rem; background:none; border:none; cursor:pointer; color:#94a3b8; padding:.25rem; transition:color .13s; }
.eye-btn:hover { color:#475569; }

/* Força da senha */
.strength-block { display:flex; flex-direction:column; gap:.5rem; padding:.5rem 0 .25rem; }
.strength-bars  { display:flex; gap:.25rem; }
.strength-bar   { flex:1; height:.25rem; border-radius:9999px; transition:background .4s ease; }
.strength-row   { display:flex; align-items:center; justify-content:space-between; }
.strength-label { font-size:.7rem; font-weight:700; transition:color .4s ease; }
.strength-len   { font-size:.65rem; color:#94a3b8; }
.req-grid { display:grid; grid-template-columns:1fr 1fr; gap:.35rem; }
.req-item { display:flex; align-items:center; gap:.5rem; font-size:.68rem; color:#6b7280; transition:opacity .2s; }
.req-off  { opacity:.5; }
.req-ok   { opacity:1; color:#374151; }
.req-dot  { width:1.125rem; height:1.125rem; border-radius:9999px; display:flex; align-items:center; justify-content:center; flex-shrink:0; transition:background .3s; }

.match-error { display:flex; align-items:center; gap:.35rem; font-size:.68rem; color:#ef4444; font-weight:600; }
.error-box   { display:flex; align-items:center; gap:.625rem; padding:.625rem .875rem; background:#fef2f2; border:1px solid #fecaca; border-radius:.75rem; font-size:.75rem; color:#dc2626; font-weight:500; }

.btn-submit {
  width:100%; padding:.8rem; border-radius:.875rem; border:none;
  font-size:.875rem; font-weight:700; display:flex; align-items:center; justify-content:center; gap:.5rem;
  cursor:pointer; transition:all .2s;
}
.btn-submit--on:hover  { filter:brightness(1.05); transform:translateY(-1px); }
.btn-submit--on:active { transform:scale(.98); }
.btn-submit--off { background:#f1f5f9; color:#94a3b8; cursor:not-allowed; }

.card-footer { font-size:.65rem; color:#94a3b8; text-align:center; margin:0; border-top:1px solid #f1f5f9; padding-top:1rem; }

@keyframes spin { to { transform:rotate(360deg); } }
.spin { animation:spin .8s linear infinite; }

.expand-enter-active { transition:all .3s ease; }
.expand-leave-active { transition:all .2s ease; }
.expand-enter-from, .expand-leave-to { opacity:0; transform:translateY(-6px); }

.slide-enter-active { transition:all .2s ease; }
.slide-leave-active { transition:all .15s ease; }
.slide-enter-from, .slide-leave-to { opacity:0; transform:translateY(-4px); }

.shake-enter-active { animation:shake .35s ease; }
@keyframes shake {
  0%,100% { transform:translateX(0); }
  20%     { transform:translateX(-5px); }
  40%     { transform:translateX(5px); }
  60%     { transform:translateX(-3px); }
  80%     { transform:translateX(3px); }
}
</style>