<!-- pages/dashboard/professor/resultados.vue -->
<template>
  <div class="space-y-6">

    <div>
      <h2 class="text-xl font-bold text-gray-900">Resultados</h2>
      <p class="text-sm text-gray-500 mt-0.5">Desempenho da turma nos simulados em que você foi atribuído</p>
    </div>

    <!-- Loading inicial -->
    <div v-if="loadingExams" class="space-y-2">
      <div v-for="i in 3" :key="i" class="h-14 bg-white rounded-xl border border-gray-100 animate-pulse" :style="{ animationDelay: `${i*80}ms` }" />
    </div>

    <!-- Sem simulados -->
    <div v-else-if="examsDisponiveis.length === 0"
      class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border-2 border-dashed border-gray-100">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:bar-chart-2" class="w-7 h-7 text-gray-200" />
      </div>
      <p class="text-sm font-medium text-gray-400">Nenhum resultado disponível ainda</p>
      <p class="text-xs text-gray-300 mt-1">Os resultados aparecem após o simulado ser processado</p>
    </div>

    <div v-else class="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">

      <!-- Sidebar: seleção de simulado -->
      <div class="xl:sticky xl:top-6 space-y-2">
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider px-1 mb-3">Simulados</p>
        <button v-for="exam in examsDisponiveis" :key="exam.id"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-left transition-all duration-150"
          :class="examSelecionado?.id === exam.id
            ? 'bg-gray-900 border-gray-900 shadow-sm'
            : 'bg-white border-gray-100 hover:border-gray-200 hover:shadow-sm'"
          @click="selecionarExam(exam)">
          <div class="w-2 h-2 rounded-full flex-shrink-0"
            :class="examSelecionado?.id === exam.id ? 'bg-white/40' : statusDot(exam.status)" />
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold truncate" :class="examSelecionado?.id === exam.id ? 'text-white' : 'text-gray-800'">
              {{ exam.title }}
            </p>
            <p class="text-xs mt-0.5 truncate text-gray-400">
              {{ myAssignments[exam.id]?.class_name ?? '—' }} · {{ myAssignments[exam.id]?.discipline_name ?? '—' }}
            </p>
          </div>
          <Icon name="lucide:chevron-right" class="w-4 h-4 flex-shrink-0"
            :class="examSelecionado?.id === exam.id ? 'text-white/40' : 'text-gray-300'" />
        </button>
      </div>

      <!-- Painel principal -->
      <div class="xl:col-span-2 space-y-4">

        <!-- Loading resultados -->
        <div v-if="loadingResultados" class="space-y-3">
          <div v-for="i in 4" :key="i" class="h-16 bg-white rounded-xl border border-gray-100 animate-pulse" :style="{ animationDelay: `${i*60}ms` }" />
        </div>

        <template v-else-if="resultados">

          <!-- Tabs -->
          <div class="flex items-center gap-1 bg-gray-100 p-1 rounded-xl w-fit">
            <button v-for="tab in tabs" :key="tab.value"
              class="px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150"
              :class="tabAtiva === tab.value ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
              @click="tabAtiva = tab.value">
              {{ tab.label }}
            </button>
          </div>

          <!-- ───── ABA: RANKING ───── -->
          <template v-if="tabAtiva === 'ranking'">

            <!-- Cards de resumo -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="bg-white rounded-2xl border border-gray-100 p-4 text-center">
                <p class="text-2xl font-bold text-gray-900">{{ resultados.total_students }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Alunos</p>
              </div>
              <div class="bg-white rounded-2xl border border-gray-100 p-4 text-center">
                <p class="text-2xl font-bold" :class="notaCor(resultados.media_turma)">
                  {{ resultados.media_turma?.toFixed(1) ?? '—' }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5">Média</p>
              </div>
              <div class="bg-white rounded-2xl border border-gray-100 p-4 text-center">
                <p class="text-2xl font-bold text-emerald-600">{{ resultados.aprovados }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Aprovados</p>
              </div>
              <div class="bg-white rounded-2xl border border-gray-100 p-4 text-center">
                <p class="text-2xl font-bold text-red-500">{{ resultados.reprovados }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Reprovados</p>
              </div>
            </div>

            <!-- Distribuição de notas -->
            <div class="bg-white rounded-2xl border border-gray-100 p-5">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Distribuição de notas</p>
              <div class="space-y-2">
                <div v-for="faixa in distribuicao" :key="faixa.label" class="flex items-center gap-3">
                  <span class="text-xs text-gray-500 w-16 flex-shrink-0">{{ faixa.label }}</span>
                  <div class="flex-1 h-5 bg-gray-50 rounded-lg overflow-hidden">
                    <div class="h-full rounded-lg transition-all duration-700 ease-out flex items-center justify-end pr-2"
                      :class="faixa.color" :style="{ width: faixa.pct + '%' }">
                      <span v-if="faixa.count > 0" class="text-[10px] font-bold text-white">{{ faixa.count }}</span>
                    </div>
                  </div>
                  <span class="text-xs text-gray-400 w-8 text-right flex-shrink-0">{{ faixa.pct }}%</span>
                </div>
              </div>
            </div>

            <!-- Ranking -->
            <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              <div class="px-5 py-4 border-b border-gray-50 flex items-center justify-between">
                <h3 class="font-semibold text-gray-900 text-sm">Ranking — {{ resultados.class_name }}</h3>
                <div class="relative">
                  <Icon name="lucide:search" class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-300" />
                  <input v-model="busca" placeholder="Buscar aluno..."
                    class="pl-7 pr-3 py-1.5 text-xs bg-gray-50 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-blue-500 w-40" />
                </div>
              </div>
              <div class="divide-y divide-gray-50">
                <div v-for="row in rankingFiltrado" :key="row.student_id"
                  class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50/50 transition-colors">
                  <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                    :class="medalha(row.ranking)">{{ row.ranking }}</div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-800 truncate">{{ row.student_name }}</p>
                    <p class="text-xs text-gray-400 font-mono">{{ row.student_ra }}</p>
                  </div>
                  <span class="text-xs text-gray-400 tabular-nums flex-shrink-0">{{ row.acertos }}/{{ row.total }}</span>
                  <span class="text-sm font-bold tabular-nums flex-shrink-0 w-10 text-right" :class="notaCor(row.nota)">
                    {{ row.nota?.toFixed(1) }}
                  </span>
                  <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden flex-shrink-0">
                    <div class="h-full rounded-full transition-all duration-500"
                      :class="row.nota >= 7 ? 'bg-emerald-400' : row.nota >= 5 ? 'bg-amber-400' : 'bg-red-400'"
                      :style="{ width: (row.nota / 10 * 100) + '%' }" />
                  </div>
                </div>
                <div v-if="rankingFiltrado.length === 0" class="px-5 py-8 text-center text-xs text-gray-300">
                  Nenhum aluno encontrado
                </div>
              </div>
            </div>
          </template>

          <!-- ───── ABA: COMPARATIVO ───── -->
          <template v-else-if="tabAtiva === 'comparativo'">
            <div v-if="loadingComparativo" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-14 bg-white rounded-xl border border-gray-100 animate-pulse" />
            </div>
            <div v-else-if="comparativo?.classes?.length" class="space-y-4">
              <div class="bg-white rounded-2xl border border-gray-100 p-5">
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Média por turma</p>
                <div class="space-y-3">
                  <div v-for="cls in comparativoOrdenado" :key="cls.class_id"
                    class="flex items-center gap-3">
                    <div class="w-28 flex-shrink-0">
                      <p class="text-xs font-semibold text-gray-700 truncate">{{ cls.class_name }}</p>
                      <p class="text-[10px] text-gray-400">{{ cls.total_students }} alunos</p>
                    </div>
                    <div class="flex-1 h-7 bg-gray-50 rounded-xl overflow-hidden">
                      <div class="h-full rounded-xl transition-all duration-700 ease-out flex items-center px-3"
                        :class="[barCor(cls.media_turma), cls.class_id === myAssignments[examSelecionado?.id]?.class_id ? 'ring-2 ring-offset-1 ring-blue-400' : '']"
                        :style="{ width: Math.max(4, cls.media_turma * 10) + '%' }">
                        <span class="text-xs font-bold text-white tabular-nums">{{ cls.media_turma?.toFixed(1) }}</span>
                      </div>
                    </div>
                    <span v-if="cls.class_id === myAssignments[examSelecionado?.id]?.class_id"
                      class="text-[10px] font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded-full flex-shrink-0">
                      sua turma
                    </span>
                  </div>
                </div>
              </div>

              <!-- Tabela resumo -->
              <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                <table class="w-full text-sm">
                  <thead class="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                    <tr>
                      <th class="px-5 py-3 text-left font-semibold">Turma</th>
                      <th class="px-4 py-3 text-right font-semibold">Alunos</th>
                      <th class="px-4 py-3 text-right font-semibold">Média</th>
                      <th class="px-4 py-3 text-right font-semibold">Acertos</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-50">
                    <tr v-for="cls in comparativoOrdenado" :key="cls.class_id"
                      :class="cls.class_id === myAssignments[examSelecionado?.id]?.class_id ? 'bg-blue-50/40' : 'hover:bg-gray-50/50'">
                      <td class="px-5 py-3 font-medium text-gray-800">
                        {{ cls.class_name }}
                        <span v-if="cls.class_id === myAssignments[examSelecionado?.id]?.class_id"
                          class="ml-1.5 text-[10px] text-blue-600">★</span>
                      </td>
                      <td class="px-4 py-3 text-right text-gray-500">{{ cls.total_students }}</td>
                      <td class="px-4 py-3 text-right font-bold" :class="notaCor(cls.media_turma)">
                        {{ cls.media_turma?.toFixed(1) }}
                      </td>
                      <td class="px-4 py-3 text-right text-gray-500 text-xs">
                        {{ cls.acertos }}/{{ cls.total_respostas }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else class="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-dashed border-gray-200">
              <Icon name="lucide:bar-chart-3" class="w-10 h-10 text-gray-200 mb-3" />
              <p class="text-sm text-gray-400">Sem dados de outras turmas para comparar</p>
            </div>
          </template>

          <!-- ───── ABA: POR QUESTÃO ───── -->
          <template v-else-if="tabAtiva === 'questoes'">
            <div v-if="loadingQuestoes" class="space-y-2">
              <div v-for="i in 5" :key="i" class="h-14 bg-white rounded-xl border border-gray-100 animate-pulse" />
            </div>
            <div v-else-if="questaoStats?.questions?.length" class="space-y-2">
              <!-- Ordenação -->
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-xs text-gray-400">Ordenar por:</span>
                <button v-for="s in ordens" :key="s.value"
                  class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all"
                  :class="ordemQuestoes === s.value ? 'bg-gray-900 text-white' : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300'"
                  @click="ordemQuestoes = s.value">
                  {{ s.label }}
                </button>
              </div>

              <div v-for="q in questoesOrdernadas" :key="q.link_id"
                class="bg-white rounded-xl border border-gray-100 px-4 py-3 hover:border-gray-200 transition-colors">
                <div class="flex items-start gap-3">
                  <!-- Número -->
                  <span class="w-7 h-7 rounded-full bg-gray-100 text-xs font-bold flex items-center justify-center flex-shrink-0 text-gray-500 mt-0.5">
                    {{ q.order }}
                  </span>
                  <div class="flex-1 min-w-0">
                    <!-- Enunciado preview -->
                    <p class="text-sm text-gray-700 leading-snug mb-2">{{ q.stem_preview }}</p>

                    <!-- Taxa de acerto -->
                    <div class="flex items-center gap-3 mb-2">
                      <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div class="h-full rounded-full transition-all duration-700"
                          :class="taxaCor(q.taxa_acerto)"
                          :style="{ width: (q.taxa_acerto ?? 0) + '%' }" />
                      </div>
                      <span class="text-xs font-bold tabular-nums flex-shrink-0"
                        :class="taxaCor(q.taxa_acerto, true)">
                        {{ q.taxa_acerto != null ? q.taxa_acerto + '%' : '—' }}
                      </span>
                      <span class="text-[10px] text-gray-400 flex-shrink-0">
                        {{ q.acertos }}/{{ q.total_respostas }} acertos
                      </span>
                    </div>

                    <!-- Distribuição de marcação -->
                    <div v-if="q.total_respostas > 0" class="flex items-center gap-1.5 flex-wrap">
                      <div v-for="letra in letras.slice(0, 5)" :key="letra"
                        class="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
                        :class="letra === q.correct_label
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-gray-50 text-gray-500'">
                        {{ letra }}
                        <span class="tabular-nums">
                          {{ pctMarcacao(q, letra) }}%
                        </span>
                        <Icon v-if="letra === q.correct_label" name="lucide:check" class="w-2.5 h-2.5" />
                      </div>
                    </div>
                    <p v-else class="text-xs text-gray-300">Sem respostas registradas</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-dashed border-gray-200">
              <Icon name="lucide:help-circle" class="w-10 h-10 text-gray-200 mb-3" />
              <p class="text-sm text-gray-400">Sem dados de respostas por questão</p>
            </div>
          </template>

        </template>

        <!-- Estado inicial -->
        <div v-else-if="!loadingResultados"
          class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
          <Icon name="lucide:mouse-pointer-click" class="w-10 h-10 text-gray-200 mb-3" />
          <p class="text-sm text-gray-400">Selecione um simulado para ver os resultados</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()

const loadingExams      = ref(true)
const loadingResultados = ref(false)
const loadingComparativo = ref(false)
const loadingQuestoes   = ref(false)

const examsDisponiveis  = ref<any[]>([])
const examSelecionado   = ref<any>(null)
const resultados        = ref<any>(null)
const comparativo       = ref<any>(null)
const questaoStats      = ref<any>(null)
const myAssignments     = ref<Record<number, any>>({})
const busca             = ref('')
const tabAtiva          = ref('ranking')
const ordemQuestoes     = ref('ordem')

const letras = ['A', 'B', 'C', 'D', 'E']

const tabs = [
  { value: 'ranking',     label: 'Ranking' },
  { value: 'comparativo', label: 'Comparativo' },
  { value: 'questoes',    label: 'Por questão' },
]

const ordens = [
  { value: 'ordem',  label: 'Nº da questão' },
  { value: 'facil',  label: 'Mais fáceis' },
  { value: 'dificil',label: 'Mais difíceis' },
]

// Ao trocar de aba, carrega dados se necessário
watch(tabAtiva, async (tab) => {
  if (!examSelecionado.value) return
  const assignment = myAssignments.value[examSelecionado.value.id]
  if (tab === 'comparativo' && !comparativo.value) await carregarComparativo()
  if (tab === 'questoes'    && !questaoStats.value)  await carregarQuestoes(assignment?.class_id)
})

const distribuicao = computed(() => {
  if (!resultados.value?.results) return []
  const notas = resultados.value.results.map((r: any) => r.nota)
  const faixas = [
    { label: '9 – 10',  min: 9, max: 10.1, color: 'bg-emerald-500' },
    { label: '7 – 8.9', min: 7, max: 9,    color: 'bg-emerald-400' },
    { label: '5 – 6.9', min: 5, max: 7,    color: 'bg-amber-400'   },
    { label: '3 – 4.9', min: 3, max: 5,    color: 'bg-orange-400'  },
    { label: '0 – 2.9', min: 0, max: 3,    color: 'bg-red-400'     },
  ]
  const total = notas.length || 1
  return faixas.map(f => {
    const count = notas.filter((n: number) => n >= f.min && n < f.max).length
    return { ...f, count, pct: Math.round(count / total * 100) }
  })
})

const rankingFiltrado = computed(() => {
  if (!resultados.value?.results) return []
  const q = busca.value.toLowerCase()
  if (!q) return resultados.value.results
  return resultados.value.results.filter((r: any) =>
    r.student_name.toLowerCase().includes(q) || r.student_ra?.toLowerCase().includes(q)
  )
})

const comparativoOrdenado = computed(() =>
  [...(comparativo.value?.classes ?? [])].sort((a, b) => b.media_turma - a.media_turma)
)

const questoesOrdernadas = computed(() => {
  const qs = [...(questaoStats.value?.questions ?? [])]
  if (ordemQuestoes.value === 'facil')   return qs.sort((a, b) => (b.taxa_acerto ?? -1) - (a.taxa_acerto ?? -1))
  if (ordemQuestoes.value === 'dificil') return qs.sort((a, b) => (a.taxa_acerto ?? 101) - (b.taxa_acerto ?? 101))
  return qs.sort((a, b) => a.order - b.order)
})

function pctMarcacao(q: any, letra: string): number {
  if (!q.total_respostas) return 0
  return Math.round((q.distribuicao?.[letra] ?? 0) / q.total_respostas * 100)
}

function statusDot(s: string) {
  const m: Record<string, string> = { generated: 'bg-purple-400', published: 'bg-emerald-400', locked: 'bg-blue-400' }
  return m[s] ?? 'bg-gray-300'
}
function notaCor(n: number)  { return n >= 7 ? 'text-emerald-600' : n >= 5 ? 'text-amber-600' : 'text-red-500' }
function barCor(n: number)   { return n >= 7 ? 'bg-emerald-500'   : n >= 5 ? 'bg-amber-400'   : 'bg-red-400'  }
function taxaCor(t: number | null, text = false) {
  if (t == null) return text ? 'text-gray-300' : 'bg-gray-200'
  if (t >= 70)   return text ? 'text-emerald-600' : 'bg-emerald-400'
  if (t >= 40)   return text ? 'text-amber-600'   : 'bg-amber-400'
  return text ? 'text-red-500' : 'bg-red-400'
}
function medalha(pos: number) {
  if (pos === 1) return 'bg-amber-100 text-amber-700'
  if (pos === 2) return 'bg-gray-100 text-gray-600'
  if (pos === 3) return 'bg-orange-100 text-orange-600'
  return 'bg-gray-50 text-gray-400'
}

async function carregarComparativo() {
  if (!examSelecionado.value) return
  loadingComparativo.value = true
  try {
    comparativo.value = await get<any>(`/exams/${examSelecionado.value.id}/results/summary`)
  } catch { comparativo.value = null }
  finally { loadingComparativo.value = false }
}

async function carregarQuestoes(classId?: number) {
  if (!examSelecionado.value) return
  loadingQuestoes.value = true
  try {
    const qs = classId ? `?class_id=${classId}` : ''
    questaoStats.value = await get<any>(`/exams/${examSelecionado.value.id}/results/questions${qs}`)
  } catch { questaoStats.value = null }
  finally { loadingQuestoes.value = false }
}

async function selecionarExam(exam: any) {
  examSelecionado.value    = exam
  resultados.value         = null
  comparativo.value        = null
  questaoStats.value       = null
  tabAtiva.value           = 'ranking'
  busca.value              = ''
  loadingResultados.value  = true
  try {
    const assignment = myAssignments.value[exam.id]
    if (!assignment?.class_id) return
    resultados.value = await get<any>(`/exams/${exam.id}/results?class_id=${assignment.class_id}`)
  } catch { resultados.value = null }
  finally { loadingResultados.value = false }
}

onMounted(async () => {
  try {
    const exams = await get<any[]>('/exams/')
    const results = await Promise.allSettled(exams.map(e => get<any>(`/exams/${e.id}/my-assignment`)))
    exams.forEach((exam, i) => {
      const r = results[i]
      if (r.status === 'fulfilled' && r.value) myAssignments.value[exam.id] = r.value
    })
    examsDisponiveis.value = exams.filter(e =>
      ['generated', 'published', 'locked'].includes(e.status) && myAssignments.value[e.id]
    )
    if (examsDisponiveis.value.length > 0) await selecionarExam(examsDisponiveis.value[0])
  } finally { loadingExams.value = false }
})
</script>