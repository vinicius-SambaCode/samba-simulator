<template>
  <div class="form-page" :class="{ ready: mounted }">

    <NuxtLink to="/dashboard/coordenador/simulados" class="back-link">
      <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" /> Voltar
    </NuxtLink>

    <div class="form-header">
      <h1 class="page-title">Novo simulado</h1>
      <p class="page-sub">Preencha as informações básicas para criar o simulado</p>
    </div>

    <div class="form-card">

      <div class="field">
        <label class="field-label">Título <span class="req">*</span></label>
        <input v-model="form.title" placeholder="Ex: Simulado SARESP 2025 — 3ª Série"
          class="field-input" :class="errors.title ? 'field-input--error' : ''" />
        <p v-if="errors.title" class="field-error">{{ errors.title }}</p>
      </div>

      <div class="field">
        <label class="field-label">Área de conhecimento</label>
        <input v-model="form.area" placeholder="Ex: Ciências da Natureza, Matemática..."
          class="field-input" />
        <p class="field-hint">Opcional — identifica a área temática do simulado</p>
      </div>

      <div class="divider" />

      <div class="field">
        <label class="field-label">Número de alternativas <span class="req">*</span></label>
        <div class="toggle-group">
          <button v-for="opt in [4, 5]" :key="opt"
            class="toggle-btn" :class="form.options_count === opt ? 'toggle-btn--on' : 'toggle-btn--off'"
            @click="form.options_count = opt">
            <span class="toggle-num">{{ opt }}</span>
            <span class="toggle-sub">{{ opt === 4 ? 'A — D' : 'A — E' }}</span>
          </button>
        </div>
      </div>

      <div class="divider" />

      <div class="field">
        <label class="field-label">Gabarito fornecido por <span class="req">*</span></label>
        <div class="source-group">
          <button v-for="src in answerSources" :key="src.value"
            class="source-btn" :class="form.answer_source === src.value ? 'source-btn--on' : 'source-btn--off'"
            @click="form.answer_source = src.value">
            <Icon :name="src.icon" class="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <p class="source-label">{{ src.label }}</p>
              <p class="source-desc">{{ src.desc }}</p>
            </div>
          </button>
        </div>
      </div>

      <div v-if="errorMsg" class="error-box">
        <Icon name="lucide:circle-x" class="w-4 h-4 flex-shrink-0" />
        {{ errorMsg }}
      </div>

      <div class="form-actions">
        <NuxtLink to="/dashboard/coordenador/simulados" class="btn-cancel">Cancelar</NuxtLink>
        <button class="btn-submit" :class="saving ? 'btn-submit--loading' : ''" :disabled="saving" @click="submit">
          <svg v-if="saving" class="spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
            <path fill="currentColor" d="M4 12a8 8 0 018-8v8z" class="opacity-75"/>
          </svg>
          <Icon v-else name="lucide:plus" class="w-4 h-4" />
          {{ saving ? 'Criando...' : 'Criar simulado' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { post } = useApi()
const mounted  = ref(false)
onMounted(async () => { await nextTick(); setTimeout(() => { mounted.value = true }, 30) })

const form = reactive({ title: '', area: '', options_count: 4, answer_source: 'teachers' })
const errors   = reactive({ title: '' })
const errorMsg = ref('')
const saving   = ref(false)

const answerSources = [
  { value:'teachers',        label:'Professores', icon:'lucide:users',      desc:'Cada professor informa o gabarito de suas questões' },
  { value:'coordinator_omr', label:'Coordenador', icon:'lucide:user-check', desc:'O coordenador lança o gabarito via leitura óptica (OMR)' },
]

function validate() {
  errors.title = ''
  if (!form.title.trim()) { errors.title = 'O título é obrigatório.'; return false }
  return true
}
async function submit() {
  if (!validate()) return
  saving.value = true; errorMsg.value = ''
  try {
    const created = await post<any>('/exams/', {
      title: form.title.trim(), area: form.area.trim() || null,
      options_count: form.options_count, answer_source: form.answer_source,
    })
    if (!created?.id) throw new Error('Resposta inválida do servidor.')
    await navigateTo(`/dashboard/coordenador/simulados/${created.id}`)
  } catch (e: any) {
    errorMsg.value = e?.message ?? e?.data?.detail ?? 'Erro ao criar simulado.'
  } finally { saving.value = false }
}
</script>

<style scoped>
.form-page {
  max-width:32rem; margin:0 auto; display:flex; flex-direction:column; gap:1.25rem;
  opacity:0; transform:translateY(10px); transition:opacity .35s ease, transform .35s ease;
}
.form-page.ready { opacity:1; transform:translateY(0); }

.back-link {
  display:inline-flex; align-items:center; gap:.4rem;
  font-size:.75rem; font-weight:700; color:#9ca3af; text-decoration:none;
  transition:color .13s;
}
.back-link:hover { color:#374151; }

.page-title { font-size:1.25rem; font-weight:800; color:#111827; margin:0 0 .25rem; }
.page-sub   { font-size:.8rem; color:#9ca3af; margin:0; }

.form-card {
  background:white; border:1px solid #f3f4f6; border-radius:1rem;
  padding:1.5rem; display:flex; flex-direction:column; gap:1.25rem;
}

.field        { display:flex; flex-direction:column; gap:.4rem; }
.field-label  { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.req          { color:#f87171; }
.field-input  {
  padding:.625rem .875rem; border:1px solid #e5e7eb; border-radius:.75rem;
  font-size:.875rem; color:#111827; outline:none; transition:border-color .15s, box-shadow .15s;
}
.field-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.field-input--error { border-color:#fca5a5; }
.field-input--error:focus { box-shadow:0 0 0 3px #fef2f2; }
.field-error  { font-size:.72rem; color:#ef4444; font-weight:600; }
.field-hint   { font-size:.7rem; color:#9ca3af; }

.divider { height:1px; background:#f9fafb; }

.toggle-group { display:grid; grid-template-columns:1fr 1fr; gap:.5rem; }
.toggle-btn {
  padding:.75rem; border-radius:.75rem; border:2px solid; cursor:pointer;
  display:flex; flex-direction:column; align-items:center; gap:.25rem;
  transition:all .13s;
}
.toggle-btn--off { border-color:#f3f4f6; background:#fafafa; color:#6b7280; }
.toggle-btn--off:hover { border-color:#d1d5db; }
.toggle-btn--on  { border-color:#111827; background:#111827; color:white; }
.toggle-num { font-size:1.25rem; font-weight:800; line-height:1; }
.toggle-sub { font-size:.68rem; font-weight:600; opacity:.7; }

.source-group { display:grid; grid-template-columns:1fr 1fr; gap:.5rem; }
.source-btn {
  padding:.75rem 1rem; border-radius:.75rem; border:2px solid; cursor:pointer;
  display:flex; align-items:flex-start; gap:.75rem; text-align:left;
  transition:all .13s;
}
.source-btn--off { border-color:#f3f4f6; background:#fafafa; color:#374151; }
.source-btn--off:hover { border-color:#d1d5db; }
.source-btn--on  { border-color:#111827; background:#111827; color:white; }
.source-label { font-size:.8rem; font-weight:700; }
.source-desc  { font-size:.68rem; opacity:.6; margin-top:.2rem; line-height:1.4; }

.error-box {
  display:flex; align-items:center; gap:.625rem;
  padding:.625rem .875rem; background:#fef2f2; border:1px solid #fecaca;
  border-radius:.75rem; font-size:.75rem; color:#dc2626; font-weight:500;
}

.form-actions { display:flex; gap:.5rem; }
.btn-cancel {
  flex:1; padding:.625rem; border-radius:.75rem; border:1px solid #e5e7eb;
  font-size:.8rem; font-weight:700; color:#6b7280; text-align:center; text-decoration:none;
  transition:background .13s;
}
.btn-cancel:hover { background:#f9fafb; }
.btn-submit {
  flex:1; padding:.625rem; border-radius:.75rem;
  background:#111827; color:white; font-size:.8rem; font-weight:700;
  border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:.5rem;
  transition:background .13s, transform .13s;
}
.btn-submit:hover:not(:disabled)  { background:#1f2937; }
.btn-submit:active:not(:disabled) { transform:scale(.97); }
.btn-submit--loading { background:#e5e7eb; color:#9ca3af; cursor:not-allowed; }
.btn-submit:disabled { cursor:not-allowed; }

@keyframes spin { to { transform:rotate(360deg); } }
.spin { animation:spin .8s linear infinite; }
</style>