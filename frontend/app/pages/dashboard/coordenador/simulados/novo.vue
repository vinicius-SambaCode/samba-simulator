<!-- pages/dashboard/coordenador/simulados/novo.vue -->
<template>
  <div class="max-w-xl mx-auto space-y-5">

    <!-- Header -->
    <div class="animate-fade-in">
      <NuxtLink to="/dashboard/coordenador/simulados"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-gray-400 hover:text-gray-700 transition-colors mb-4">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" />
        Voltar para simulados
      </NuxtLink>
      <h2 class="text-xl font-black text-gray-900 tracking-tight">Novo simulado</h2>
      <p class="text-sm text-gray-400 mt-0.5">Preencha as informações básicas para criar o simulado</p>
    </div>

    <!-- Card do formulário -->
    <div class="bg-white rounded-2xl border border-gray-100 p-6 space-y-5 animate-fade-up" style="animation-delay:60ms">

      <!-- Título -->
      <div>
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Título *</label>
        <input
          v-model="form.title"
          placeholder="Ex: Simulado SARESP 2025 — 3ª Série"
          class="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all"
          :class="errors.title ? 'border-red-300 focus:ring-red-100 focus:border-red-300' : ''" />
        <p v-if="errors.title" class="text-xs text-red-500 mt-1 font-medium">{{ errors.title }}</p>
      </div>

      <!-- Área -->
      <div>
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Área de conhecimento</label>
        <input
          v-model="form.area"
          placeholder="Ex: Ciências da Natureza, Matemática..."
          class="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all" />
        <p class="text-[11px] text-gray-400 mt-1">Opcional — identifica a área temática do simulado</p>
      </div>

      <!-- Divisor -->
      <div class="h-px bg-gray-50" />

      <!-- Número de opções -->
      <div>
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-2">Número de alternativas *</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="opt in [4, 5]" :key="opt"
            class="py-3 rounded-xl border-2 transition-all duration-150 flex flex-col items-center gap-1"
            :class="form.options_count === opt
              ? 'border-gray-900 bg-gray-900 text-white'
              : 'border-gray-100 bg-gray-50 text-gray-600 hover:border-gray-300'"
            @click="form.options_count = opt">
            <span class="text-lg font-black">{{ opt }}</span>
            <span class="text-[11px] font-semibold opacity-70">
              {{ opt === 4 ? 'A, B, C, D' : 'A, B, C, D, E' }}
            </span>
          </button>
        </div>
      </div>

      <!-- Divisor -->
      <div class="h-px bg-gray-50" />

      <!-- Fonte das respostas -->
      <div>
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-2">Gabarito fornecido por *</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="src in answerSources" :key="src.value"
            class="py-3 px-4 rounded-xl border-2 transition-all duration-150 flex items-start gap-3 text-left"
            :class="form.answer_source === src.value
              ? 'border-gray-900 bg-gray-900 text-white'
              : 'border-gray-100 bg-gray-50 text-gray-600 hover:border-gray-300'"
            @click="form.answer_source = src.value">
            <Icon :name="src.icon" class="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              <p class="text-sm font-bold leading-none">{{ src.label }}</p>
              <p class="text-[11px] mt-1 opacity-60 leading-tight">{{ src.desc }}</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Erro geral -->
      <div v-if="errorMsg" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
        <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
        <p class="text-xs text-red-500 font-medium">{{ errorMsg }}</p>
      </div>

      <!-- Botões -->
      <div class="flex gap-2 pt-1">
        <NuxtLink
          to="/dashboard/coordenador/simulados"
          class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600 transition-all text-center">
          Cancelar
        </NuxtLink>
        <button
          :disabled="saving"
          class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
          :class="saving ? 'bg-gray-100 text-gray-300 cursor-not-allowed' : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
          @click="submit">
          <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
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

const form = reactive({
  title:         '',
  area:          '',
  options_count: 4,
  answer_source: 'teachers',
})

const errors  = reactive({ title: '' })
const errorMsg = ref('')
const saving   = ref(false)

const answerSources = [
  { value: 'teachers',    label: 'Professores',  icon: 'lucide:users',      desc: 'Cada professor informa o gabarito de suas questões' },
  { value: 'coordinator', label: 'Coordenador',  icon: 'lucide:user-check', desc: 'O coordenador define o gabarito após a coleta' },
]

function validate() {
  errors.title = ''
  if (!form.title.trim()) { errors.title = 'O título é obrigatório.'; return false }
  return true
}

async function submit() {
  if (!validate()) return
  saving.value = true
  errorMsg.value = ''
  try {
    const created = await post<any>('/exams/', {
      title:         form.title.trim(),
      area:          form.area.trim() || null,
      options_count: form.options_count,
      answer_source: form.answer_source,
    })
    navigateTo(`/dashboard/coordenador/simulados/${created.id}`)
  } catch (e: any) {
    errorMsg.value = e.message ?? 'Erro ao criar simulado.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
</style>