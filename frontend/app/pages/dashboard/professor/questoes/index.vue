<!-- pages/dashboard/professor/questoes.vue -->
<template>
  <div class="space-y-6">

    <div>
      <h2 class="text-xl font-bold text-gray-900">Minhas questões</h2>
      <p class="text-sm text-gray-500 mt-0.5">Todas as questões que você criou ou importou</p>
    </div>

    <!-- Filtros -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
        <input v-model="busca" type="text" placeholder="Buscar no enunciado ou alternativas..."
          class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
      </div>
      <select v-model="examFiltro"
        class="px-3 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[180px]">
        <option value="">Todos os simulados</option>
        <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.title }}</option>
      </select>
      <div class="flex gap-1.5">
        <button v-for="f in fonteFiltros" :key="f.value"
          class="px-3 py-2 rounded-xl text-xs font-medium transition-all"
          :class="fonteFiltro === f.value ? 'bg-gray-900 text-white' : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300'"
          @click="fonteFiltro = f.value">
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div v-if="!loading" class="flex items-center gap-4 flex-wrap text-sm text-gray-500">
      <div class="flex items-center gap-1.5">
        <Icon name="lucide:layers" class="w-4 h-4 text-gray-400" />
        <span class="font-semibold text-gray-900">{{ questoesFiltradas.length }}</span> questão(ões)
      </div>
      <div class="flex items-center gap-1.5">
        <Icon name="lucide:file-text" class="w-4 h-4 text-blue-400" />
        <span class="font-semibold text-blue-700">{{ contarFonte('upload') }}</span> importadas
      </div>
      <div class="flex items-center gap-1.5">
        <Icon name="lucide:pencil" class="w-4 h-4 text-purple-400" />
        <span class="font-semibold text-purple-700">{{ contarFonte('manual') }}</span> manuais
      </div>
      <div v-if="mediaAcerto !== null" class="flex items-center gap-1.5">
        <Icon name="lucide:target" class="w-4 h-4 text-emerald-400" />
        <span class="font-semibold" :class="taxaCor(mediaAcerto, true)">{{ mediaAcerto }}%</span> acerto médio
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-28 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="{ animationDelay: `${i * 70}ms` }" />
    </div>

    <!-- Empty -->
    <div v-else-if="questoesFiltradas.length === 0"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
      <div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
        <Icon name="lucide:file-question" class="w-6 h-6 text-gray-300" />
      </div>
      <p class="text-sm font-medium text-gray-400">
        {{ busca || examFiltro || fonteFiltro !== 'todos' ? 'Nenhuma questão encontrada' : 'Você ainda não criou nenhuma questão' }}
      </p>
    </div>

    <!-- Lista -->
    <TransitionGroup v-else name="list" tag="div" class="space-y-3">
      <div v-for="q in questoesFiltradas" :key="q._uid"
        class="bg-white rounded-2xl border border-gray-100 hover:border-gray-200 hover:shadow-sm transition-all duration-200 overflow-hidden group">

        <!-- Header do card -->
        <div class="flex items-center justify-between px-5 pt-4 pb-2">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100">
              {{ examNome(q.exam_id) }}
            </span>
            <span v-if="q.discipline_name || q.discipline_id"
              class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
              {{ q.discipline_name ?? `Disc. #${q.discipline_id}` }}
            </span>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1"
              :class="(!q.source || q.source === 'manual') ? 'bg-violet-50 text-violet-600 border-violet-100' : 'bg-gray-50 text-gray-500 border-gray-100'">
              <Icon :name="(!q.source || q.source === 'manual') ? 'lucide:pencil' : 'lucide:file-text'" class="w-2.5 h-2.5" />
              {{ (!q.source || q.source === 'manual') ? 'manual' : 'importada' }}
            </span>
            <span v-if="q.images?.length"
              class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 border border-orange-100 flex items-center gap-1">
              <Icon name="lucide:image" class="w-2.5 h-2.5" />
              imagem
            </span>
          </div>
          <NuxtLink :to="`/dashboard/professor/simulados/${q.exam_id}`"
            class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500">
            <Icon name="lucide:external-link" class="w-3.5 h-3.5" />
          </NuxtLink>
        </div>

        <!-- Enunciado -->
        <div class="px-5 pb-3">
          <p class="text-sm text-gray-800 leading-relaxed line-clamp-2">{{ q.stem }}</p>
        </div>

        <!-- Alternativas -->
        <div class="px-5 pb-3 grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          <div v-for="opt in q.options" :key="opt.label"
            class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-colors"
            :class="q.correct_label === opt.label
              ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
              : 'bg-gray-50 border border-gray-100 text-gray-500'">
            <span class="font-bold w-4 flex-shrink-0" :class="q.correct_label === opt.label ? 'text-emerald-600' : 'text-gray-400'">
              {{ opt.label }}
            </span>
            <span class="truncate flex-1">{{ opt.text }}</span>
            <Icon v-if="q.correct_label === opt.label" name="lucide:check" class="w-3 h-3 text-emerald-500 flex-shrink-0 ml-auto" />
          </div>
        </div>

        <!-- Estatísticas de acerto (se disponível) -->
        <div v-if="q._stats" class="mx-5 mb-4 p-3 bg-gray-50 rounded-xl border border-gray-100">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Taxa de acerto</span>
            <span class="text-xs font-bold tabular-nums" :class="taxaCor(q._stats.taxa_acerto, true)">
              {{ q._stats.taxa_acerto != null ? q._stats.taxa_acerto + '%' : '—' }}
              <span class="font-normal text-gray-400 ml-1">({{ q._stats.acertos }}/{{ q._stats.total_respostas }})</span>
            </span>
          </div>
          <!-- Barra de taxa -->
          <div class="h-1.5 bg-white rounded-full overflow-hidden mb-2.5">
            <div class="h-full rounded-full transition-all duration-700"
              :class="taxaCor(q._stats.taxa_acerto)"
              :style="{ width: (q._stats.taxa_acerto ?? 0) + '%' }" />
          </div>
          <!-- Distribuição por letra -->
          <div v-if="q._stats.total_respostas > 0" class="flex items-center gap-1.5">
            <div v-for="letra in letras.slice(0, q.options?.length ?? 5)" :key="letra"
              class="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
              :class="letra === q.correct_label ? 'bg-emerald-100 text-emerald-700' : 'bg-white text-gray-500 border border-gray-100'">
              {{ letra }}
              <span class="tabular-nums">{{ pctMarcacao(q._stats, letra) }}%</span>
              <Icon v-if="letra === q.correct_label" name="lucide:check" class="w-2.5 h-2.5" />
            </div>
          </div>
        </div>

        <!-- Botão carregar stats (lazy por simulado) -->
        <div v-else-if="!statsCarregadas.has(q.exam_id)" class="px-5 pb-4">
          <button
            class="text-xs text-gray-400 hover:text-blue-500 flex items-center gap-1.5 transition-colors"
            :class="loadingStats.has(q.exam_id) ? 'pointer-events-none' : ''"
            @click="carregarStats(q.exam_id)">
            <Icon :name="loadingStats.has(q.exam_id) ? 'lucide:loader-2' : 'lucide:bar-chart-2'"
              class="w-3.5 h-3.5" :class="loadingStats.has(q.exam_id) ? 'animate-spin' : ''" />
            {{ loadingStats.has(q.exam_id) ? 'Carregando...' : 'Ver estatísticas de acerto' }}
          </button>
        </div>

      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()

const loading     = ref(true)
const todasQuestoes = ref<any[]>([])
const exams       = ref<any[]>([])
const busca       = ref('')
const examFiltro  = ref<number | ''>('')
const fonteFiltro = ref('todos')
const letras      = ['A', 'B', 'C', 'D', 'E']

// Stats por exam (carregadas lazy)
const statsMap       = ref<Record<number, any[]>>({})   // examId → questions stats
const statsCarregadas = ref(new Set<number>())
const loadingStats   = ref(new Set<number>())

const fonteFiltros = [
  { value: 'todos',   label: 'Todas' },
  { value: 'manual',  label: 'Manuais' },
  { value: 'upload',  label: 'Importadas' },
]

// Questões com stats injetadas
const questoesEnriquecidas = computed(() =>
  todasQuestoes.value.map(q => {
    const examStats = statsMap.value[q.exam_id]
    const stat = examStats?.find((s: any) => s.question_id === q.id)
    return { ...q, _stats: stat ?? null }
  })
)

const questoesFiltradas = computed(() => {
  let lista = questoesEnriquecidas.value
  if (examFiltro.value !== '') lista = lista.filter(q => q.exam_id === examFiltro.value)
  if (fonteFiltro.value !== 'todos') {
    lista = fonteFiltro.value === 'manual'
      ? lista.filter(q => !q.source || q.source === 'manual')
      : lista.filter(q => q.source && q.source !== 'manual')
  }
  if (busca.value.trim()) {
    const s = busca.value.toLowerCase()
    lista = lista.filter(q =>
      q.stem?.toLowerCase().includes(s) ||
      q.options?.some((o: any) => o.text?.toLowerCase().includes(s))
    )
  }
  return lista
})

const mediaAcerto = computed(() => {
  const comStats = questoesFiltradas.value.filter(q => q._stats?.taxa_acerto != null)
  if (!comStats.length) return null
  const media = comStats.reduce((acc, q) => acc + q._stats.taxa_acerto, 0) / comStats.length
  return Math.round(media)
})

function contarFonte(tipo: string) {
  if (tipo === 'manual') return todasQuestoes.value.filter(q => !q.source || q.source === 'manual').length
  return todasQuestoes.value.filter(q => q.source && q.source !== 'manual').length
}

function examNome(examId: number): string {
  return exams.value.find(e => e.id === examId)?.title ?? `Simulado #${examId}`
}

function pctMarcacao(stats: any, letra: string): number {
  if (!stats?.total_respostas) return 0
  return Math.round((stats.distribuicao?.[letra] ?? 0) / stats.total_respostas * 100)
}

function taxaCor(t: number | null, text = false) {
  if (t == null) return text ? 'text-gray-300' : 'bg-gray-200'
  if (t >= 70)   return text ? 'text-emerald-600' : 'bg-emerald-400'
  if (t >= 40)   return text ? 'text-amber-600'   : 'bg-amber-400'
  return text ? 'text-red-500' : 'bg-red-400'
}

async function carregarStats(examId: number) {
  if (statsCarregadas.value.has(examId) || loadingStats.value.has(examId)) return
  loadingStats.value = new Set([...loadingStats.value, examId])
  try {
    const data = await get<any>(`/exams/${examId}/results/questions`)
    statsMap.value = { ...statsMap.value, [examId]: data.questions ?? [] }
    statsCarregadas.value = new Set([...statsCarregadas.value, examId])
  } catch {
    statsCarregadas.value = new Set([...statsCarregadas.value, examId]) // não tenta de novo
  } finally {
    const s = new Set(loadingStats.value)
    s.delete(examId)
    loadingStats.value = s
  }
}

onMounted(async () => {
  try {
    const examList = await get<any[]>('/exams/')
    exams.value = examList
    const results = await Promise.allSettled(examList.map(e => get<any[]>(`/exams/${e.id}/questions`)))
    const todas: any[] = []
    examList.forEach((exam, i) => {
      const r = results[i]
      if (r.status === 'fulfilled') {
        r.value.forEach((q: any, idx: number) => {
          todas.push({ ...q, exam_id: exam.id, _uid: `${exam.id}-${q.id}` })
        })
      }
    })
    todasQuestoes.value = todas.sort((a, b) => b.exam_id - a.exam_id || b.id - a.id)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.list-enter-active { transition: all 0.2s ease; }
.list-leave-active { transition: all 0.15s ease; position: absolute; width: 100%; }
.list-enter-from   { opacity: 0; transform: translateY(-6px); }
.list-leave-to     { opacity: 0; }
.list-move         { transition: transform 0.25s ease; }
</style>