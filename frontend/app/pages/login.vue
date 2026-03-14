<template>
  <div class="shell">

    <!-- Fundo com grid sutil -->
    <div class="bg-grid" />

    <!-- Card central -->
    <div class="card" :class="{ ready: mounted }">

      <!-- Topo: logo + status -->
      <div class="card-top">
        <div class="logo-wrap">
          <img src="/svg/edvance-logo2.svg" alt="Edvance" class="logo-img" />
        </div>
        <div class="status-pill">
          <span class="status-dot" />
          Sistema online
        </div>
      </div>

      <!-- Título -->
      <div class="card-heading">
        <div class="lock-icon">
          <Icon name="lucide:lock-keyhole" class="w-5 h-5 text-white" />
        </div>
        <h1 class="heading-title">Acesso seguro</h1>
        <p class="heading-sub">Plataforma de Simulados — samba edvance</p>
      </div>

      <!-- Formulário -->
      <div class="form">

        <!-- Usuário -->
        <div class="field">
          <label class="field-label">Usuário</label>
          <div class="input-wrap" :class="focused==='email'?'input-wrap--focus':''">
            <Icon name="lucide:at-sign" class="input-icon" :class="focused==='email'?'text-blue-500':'text-gray-400'" />
            <input
              ref="emailInput"
              v-model="emailRaw"
              type="text"
              inputmode="email"
              placeholder="nome.sobrenome"
              :disabled="loading"
              autocomplete="username"
              class="field-input"
              @focus="focused='email'"
              @blur="onEmailBlur"
              @keyup.enter="$refs.passwordInput?.focus()"
            />
            <!-- Preview do domínio -->
            <span v-if="emailRaw && !emailRaw.includes('@')" class="domain-hint">@samba.edvance</span>
          </div>
          <!-- Mostra o e-mail que será enviado -->
          <p v-if="emailRaw && !emailRaw.includes('@') && focused!=='email'" class="field-resolved">
            <Icon name="lucide:check-circle" class="w-3 h-3 text-emerald-500" />
            {{ resolvedEmail }}
          </p>
        </div>

        <!-- Senha -->
        <div class="field">
          <label class="field-label">Senha</label>
          <div class="input-wrap" :class="focused==='password'?'input-wrap--focus':''">
            <Icon name="lucide:key-round" class="input-icon" :class="focused==='password'?'text-blue-500':'text-gray-400'" />
            <input
              ref="passwordInput"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
              :disabled="loading"
              autocomplete="current-password"
              class="field-input pr-10"
              @focus="focused='password'"
              @blur="focused=''"
              @keyup.enter="handleLogin"
            />
            <button type="button" class="eye-btn" tabindex="-1" @click="showPassword=!showPassword">
              <Icon :name="showPassword?'lucide:eye-off':'lucide:eye'" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Erro -->
        <Transition name="shake">
          <div v-if="error" class="error-box">
            <Icon name="lucide:shield-alert" class="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{{ error }}</span>
          </div>
        </Transition>

        <!-- Botão entrar -->
        <button
          class="btn-enter"
          :class="canSubmit && !loading ? 'btn-enter--on' : 'btn-enter--off'"
          :disabled="!canSubmit || loading"
          @click="handleLogin">
          <template v-if="loading">
            <svg class="spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
              <path fill="currentColor" d="M4 12a8 8 0 018-8v8z" class="opacity-75"/>
            </svg>
            Autenticando...
          </template>
          <template v-else>
            <Icon name="lucide:log-in" class="w-4 h-4" />
            Entrar
          </template>
        </button>
      </div>

      <!-- Acessos rápidos (dev) -->
      <div class="dev-section">
        <div class="dev-divider"><span>Acessos rápidos</span></div>
        <div class="dev-list">
          <button v-for="acc in devAccounts" :key="acc.email"
            class="dev-btn" @click="fillMock(acc)">
            <div class="dev-icon" :class="acc.iconBg">
              <Icon :name="acc.icon" class="w-3.5 h-3.5" :class="acc.iconColor" />
            </div>
            <span class="dev-label">{{ acc.label }}</span>
            <Icon name="lucide:arrow-right" class="w-3.5 h-3.5 text-gray-300 ml-auto" />
          </button>
        </div>
      </div>

      <!-- Rodapé -->
      <p class="card-footer">© 2026 samba edvance · Acesso restrito</p>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { login, user, getDashboardRoute } = useAuth()

const DEFAULT_DOMAIN = '@samba.edvance'

const emailRaw     = ref('')
const form         = reactive({ password: '' })
const loading      = ref(false)
const error        = ref('')
const showPassword = ref(false)
const focused      = ref('')
const mounted      = ref(false)

const emailInput    = ref<HTMLInputElement | null>(null)
const passwordInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  await nextTick()
  setTimeout(() => { mounted.value = true }, 40)
  setTimeout(() => { emailInput.value?.focus() }, 200)
})

// E-mail resolvido: adiciona domínio padrão se não tiver @
const resolvedEmail = computed(() => {
  const raw = emailRaw.value.trim()
  if (!raw) return ''
  return raw.includes('@') ? raw : raw + DEFAULT_DOMAIN
})

const canSubmit = computed(() => resolvedEmail.value !== '' && form.password !== '')

function onEmailBlur() {
  focused.value = ''
  // Se digitou com @, mantém como está; se não, não precisa fazer nada — resolvedEmail cuida
}

const devAccounts = [
  { label:'Root / Admin',      email:'root@samba.edvance',              password:'R7D46S*98/4pwd', icon:'lucide:shield',          iconBg:'bg-gray-900',   iconColor:'text-white'      },
  { label:'Coordenador Demo',  email:'coord@samba.edvance',             password:'Coord@123',      icon:'lucide:layout-dashboard',iconBg:'bg-blue-50',    iconColor:'text-blue-600'   },
  { label:'Prof. Matemática',  email:'prof.matematica@samba.edvance',   password:'Prof@123',       icon:'lucide:calculator',      iconBg:'bg-orange-50',  iconColor:'text-orange-500' },
  { label:'Prof. Física',      email:'prof.fisica@samba.edvance',       password:'Prof@123',       icon:'lucide:atom',            iconBg:'bg-violet-50',  iconColor:'text-violet-500' },
]

function fillMock(acc: typeof devAccounts[0]) {
  emailRaw.value  = acc.email
  form.password   = acc.password
  error.value     = ''
}

async function handleLogin() {
  if (!canSubmit.value) return
  loading.value = true
  error.value   = ''
  const result  = await login(resolvedEmail.value, form.password)
  loading.value = false

  if (result === 'error') {
    error.value = 'Credenciais inválidas. Verifique e tente novamente.'
    return
  }
  if (result === 'change_password') {
    await navigateTo('/trocar-senha')
    return
  }
  if (user.value) {
    await navigateTo(getDashboardRoute(user.value.role))
  }
}
</script>

<style scoped>
/* ── Shell ── */
.shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

/* Grade de fundo */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,0,0,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,.04) 1px, transparent 1px);
  background-size: 52px 52px;
}

/* Orb de luz azul-escuro */
.shell::before {
  content: '';
  position: absolute;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(37,99,235,.08) 0%, transparent 70%);
  pointer-events: none;
}

/* ── Card ── */
.card {
  position: relative;
  width: 100%;
  max-width: 400px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 1.25rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  box-shadow: 0 20px 48px rgba(0,0,0,.1), 0 0 0 1px rgba(0,0,0,.03);
  opacity: 0;
  transform: translateY(16px) scale(.98);
  transition: opacity .45s ease, transform .45s cubic-bezier(.22,1,.36,1);
}
.card.ready { opacity: 1; transform: translateY(0) scale(1); }

/* ── Topo ── */
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo-wrap { display: flex; align-items: center; }
.logo-img  { height: 1.75rem; width: auto; }

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  padding: .25rem .75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 9999px;
  font-size: .65rem;
  font-weight: 700;
  color: #16a34a;
  letter-spacing: .04em;
}
.status-dot {
  width: .4rem;
  height: .4rem;
  border-radius: 50%;
  background: #34d399;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ── Heading ── */
.card-heading { display: flex; flex-direction: column; align-items: center; gap: .75rem; text-align: center; }
.lock-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(37,99,235,.4);
}
.heading-title { font-size: 1.35rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -.02em; }
.heading-sub   { font-size: .75rem; color: #64748b; margin: 0; }

/* ── Form ── */
.form { display: flex; flex-direction: column; gap: 1rem; }

.field { display: flex; flex-direction: column; gap: .4rem; }
.field-label {
  font-size: .65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: #64748b;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: .75rem;
  transition: border-color .15s, box-shadow .15s, background .15s;
}
.input-wrap--focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59,130,246,.12);
  background: white;
}
.input-icon {
  position: absolute;
  left: .875rem;
  width: 1rem;
  height: 1rem;
  pointer-events: none;
  transition: color .15s;
  flex-shrink: 0;
}
.field-input {
  width: 100%;
  padding: .75rem .875rem .75rem 2.5rem;
  background: none;
  border: none;
  outline: none;
  font-size: .875rem;
  color: #0f172a;
  caret-color: #3b82f6;
}
.field-input::placeholder { color: #cbd5e1; }
.field-input:disabled { opacity: .5; }

/* Hint de domínio no input */
.domain-hint {
  position: absolute;
  right: .875rem;
  font-size: .75rem;
  color: #94a3b8;
  pointer-events: none;
  white-space: nowrap;
}

/* E-mail resolvido */
.field-resolved {
  display: flex;
  align-items: center;
  gap: .35rem;
  font-size: .68rem;
  color: #64748b;
  margin: 0;
  padding-left: .25rem;
}

.eye-btn {
  position: absolute;
  right: .75rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: .25rem;
  transition: color .13s;
}
.eye-btn:hover { color: #475569; }

/* Erro */
.error-box {
  display: flex;
  align-items: center;
  gap: .625rem;
  padding: .625rem .875rem;
  background: rgba(239,68,68,.1);
  border: 1px solid rgba(239,68,68,.25);
  border-radius: .75rem;
  font-size: .75rem;
  color: #fca5a5;
  font-weight: 500;
}

/* Botão entrar */
.btn-enter {
  width: 100%;
  padding: .8rem;
  border-radius: .875rem;
  border: none;
  font-size: .875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .5rem;
  cursor: pointer;
  transition: all .15s;
  margin-top: .25rem;
}
.btn-enter--on {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  color: white;
  box-shadow: 0 8px 20px rgba(37,99,235,.35);
}
.btn-enter--on:hover  { transform: translateY(-1px); box-shadow: 0 12px 24px rgba(37,99,235,.4); }
.btn-enter--on:active { transform: scale(.98); }
.btn-enter--off { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; }

/* ── Dev section ── */
.dev-section { display: flex; flex-direction: column; gap: .875rem; }
.dev-divider {
  display: flex;
  align-items: center;
  gap: .75rem;
  font-size: .62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: #94a3b8;
}
.dev-divider::before, .dev-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}
.dev-list { display: flex; flex-direction: column; gap: .375rem; }
.dev-btn {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .625rem .875rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: .75rem;
  cursor: pointer;
  transition: background .13s, border-color .13s;
  text-align: left;
}
.dev-btn:hover { background: #f1f5f9; border-color: #cbd5e1; }
.dev-icon {
  width: 1.875rem;
  height: 1.875rem;
  border-radius: .5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.dev-label { font-size: .78rem; font-weight: 600; color: #374151; }

/* ── Rodapé ── */
.card-footer {
  font-size: .65rem;
  color: #94a3b8;
  text-align: center;
  margin: 0;
  border-top: 1px solid #f1f5f9;
  padding-top: 1rem;
}

/* ── Animações ── */
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .8s linear infinite; }

.shake-enter-active { animation: shake .35s ease; }
@keyframes shake {
  0%,100% { transform: translateX(0); }
  20%     { transform: translateX(-5px); }
  40%     { transform: translateX(5px); }
  60%     { transform: translateX(-3px); }
  80%     { transform: translateX(3px); }
}
</style>