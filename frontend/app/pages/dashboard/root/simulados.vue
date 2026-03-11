<!-- pages/dashboard/root/simulados.vue -->
<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold text-gray-900">Simulados da rede</h2>
      <p class="text-sm text-gray-500 mt-0.5">Visão consolidada de todos os simulados</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div v-for="s in statsCards" :key="s.label"
        class="bg-white rounded-2xl border border-gray-100 p-4">
        <p class="text-2xl font-bold text-gray-900">{{ s.value }}</p>
        <p class="text-xs text-gray-400 mt-0.5">{{ s.label }}</p>
        <div class="w-6 h-1 rounded-full mt-2" :class="s.color" />
      </div>
    </div>

    <!-- Filtro status -->
    <div class="flex items-center gap-2 flex-wrap">
      <button v-for="f in filtros" :key="f.value"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
        :class="filtroAtivo === f.value ? 'bg-gray-900 text-white' : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300'"
        @click="filtroAtivo = f.value">
        {{ f.label }} <span class="ml-1 opacity-60">{{ contarFiltro(f.value) }}</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-16 bg-white rounded-2xl border border-gray-100 animate-pulse" />
    </div>

    <!-- Tabela -->
    <div v-else class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-50">
              <th class="text-left text-[11px] font-semibold text-gray-400 px-5 py-3 uppercase tracking-wider">Simulado</th>
              <th class="text-left text-[11px] font-semibold text-gray-400 px-4 py-3 uppercase tracking-wider">Status</th>
              <th class="text-left text-[11px] font-semibold text-gray-400 px-4 py-3 uppercase tracking-wider hidden sm:table-cell">Alternativas</th>
              <th class="text-left text-[11px] font-semibold text-gray-400 px-4 py-3 uppercase tracking-wider hidden md:table-cell">Gabarito</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-if="listaFiltrada.length === 0">
              <td colspan="5" class="text-center py-12 text-sm text-gray-400">Nenhum simulado encontrado</td>
            </tr>
            <tr v-for="exam in listaFiltrada" :key="exam.id"
              class="hover:bg-gray-50/50 transition-colors">
              <td class="px-5 py-3.5">
                <p class="text-sm font-semibold text-gray-900">{{ exam.title }}</p>
              </td>
              <td class="px-4 py-3.5">
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full" :class="statusBadge(exam.status)">
                  {{ statusLabel(exam.status) }}
                </span>
              </td>
              <td class="px-4 py-3.5 hidden sm:table-cell">
                <span class="text-sm text-gray-500">{{ exam.options_count }}</span>
              </td>
              <td class="px-4 py-3.5 hidden md:table-cell">
                <span class="text-xs text-gray-400">{{ exam.answer_source === 'teachers' ? 'Professores' : 'OMR' }}</span>
              </td>
              <td class="px-4 py-3.5 text-right">
                <span class="text-xs text-blue-500 font-medium">Ver detalhes →</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const exams = ref<any[]>([])
const loading = ref(true)
const filtroAtivo = ref('todos')

const filtros = [
  { value: 'todos', label: 'Todos' },
  { value: 'collecting', label: 'Em coleta' },
  { value: 'locked', label: 'Travados' },
  { value: 'published', label: 'Publicados' },
]

const statsCards = computed(() => [
  { label: 'Total', value: exams.value.length, color: 'bg-gray-300' },
  { label: 'Em coleta', value: exams.value.filter(e => e.status === 'collecting').length, color: 'bg-amber-400' },
  { label: 'Travados', value: exams.value.filter(e => e.status === 'locked').length, color: 'bg-blue-400' },
  { label: 'Publicados', value: exams.value.filter(e => e.status === 'published').length, color: 'bg-emerald-400' },
])

const listaFiltrada = computed(() =>
  filtroAtivo.value === 'todos' ? exams.value : exams.value.filter(e => e.status === filtroAtivo.value)
)
function contarFiltro(v: string) {
  return v === 'todos' ? exams.value.length : exams.value.filter(e => e.status === v).length
}
function statusLabel(s: string) {
  return { collecting: 'Coletando', locked: 'Travado', published: 'Publicado', draft: 'Rascunho' }[s] ?? s
}
function statusBadge(s: string) {
  return { collecting: 'bg-amber-50 text-amber-700', locked: 'bg-blue-50 text-blue-700', published: 'bg-emerald-50 text-emerald-700' }[s] ?? 'bg-gray-50 text-gray-500'
}

onMounted(async () => {
  try { exams.value = await get<any[]>('/exams/') }
  catch { exams.value = [] }
  finally { loading.value = false }
})
</script>