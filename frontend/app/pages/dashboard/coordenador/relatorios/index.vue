<!-- pages/dashboard/coordenador/relatorios.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="animate-fade-in">
      <h2 class="text-xl font-black text-gray-900 tracking-tight">Relatórios</h2>
      <p class="text-sm text-gray-400 mt-0.5">Progresso de coleta e resultados dos alunos</p>
    </div>

    <!-- Seletor de simulado -->
    <div class="animate-fade-up" style="animation-delay:40ms">
      <div v-if="loadingExams" class="flex gap-2">
        <div v-for="i in 3" :key="i" class="h-9 w-32 bg-white rounded-xl border border-gray-100 animate-pulse" />
      </div>
      <div v-else class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
        <button v-for="exam in exams" :key="exam.id"
          class="flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all"
          :class="selectedExamId === exam.id
            ? 'bg-gray-900 text-white'
            : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300'"
          @click="selectExam(exam.id)">
          <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="statusDot(exam.status)" />
          {{ exam.title }}
        </button>
      </div>
    </div>

    <!-- Placeholder inicial -->
    <div v-if="!selectedExamId"
      class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:bar-chart-2" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">Selecione um simulado para ver os relatórios</p>
    </div>

    <template v-else>

      <!-- Abas -->
      <div class="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit animate-fade-up" style="animation-delay:60ms">
        <button v-for="tab in tabs" :key="tab.id"
          class="px-4 py-2 rounded-lg text-xs font-bold transition-all"
          :class="activeTab === tab.id ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          @click="activeTab = tab.id">
          {{ tab.label }}
        </button>
      </div>

      <!-- ==================== ABA: PROGRESSO ==================== -->
      <template v-if="activeTab === 'progresso'">

        <div v-if="loadingProgress" class="space-y-3">
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div v-for="i in 3" :key="i" class="h-24 bg-white rounded-2xl border border-gray-100 animate-pulse" />
          </div>
          <div class="h-48 bg-white rounded-2xl border border-gray-100 animate-pulse" />
        </div>

        <template v-else>

          <!-- Stat cards -->
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 animate-fade-up" style="animation-delay:80ms">
            <div v-for="s in progressCards" :key="s.label"
              class="bg-white rounded-2xl border border-gray-100 p-4 flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :class="s.iconBg">
                <Icon :name="s.icon" class="w-4 h-4" :class="s.iconColor" />
              </div>
              <div>
                <p class="text-xl font-black text-gray-900 tabular-nums leading-none">{{ s.value }}</p>
                <p class="text-[11px] text-gray-400 font-medium mt-0.5">{{ s.label }}</p>
              </div>
            </div>
          </div>

          <!-- Questões vs cota -->
          <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:100ms">
            <div class="flex items-center gap-2 px-5 py-4 border-b border-gray-50">
              <Icon name="lucide:target" class="w-4 h-4 text-gray-400" />
              <h3 class="text-sm font-bold text-gray-900">Questões enviadas vs cota</h3>
            </div>
            <div v-if="!progress?.disciplines?.length" class="flex flex-col items-center py-12">
              <Icon name="lucide:inbox" class="w-7 h-7 text-gray-200 mb-2" />
              <p class="text-xs text-gray-400">Nenhuma cota definida</p>
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div v-for="d in progress.disciplines" :key="d.discipline_id" class="px-5 py-4">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-sm font-bold text-gray-800">{{ disciplineName(d.discipline_id) }}</p>
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-black text-gray-900 tabular-nums">{{ d.submitted }}/{{ d.quota }}</span>
                    <span class="text-[11px] font-bold px-2 py-0.5 rounded-full"
                      :class="d.remaining === 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
                      {{ d.remaining === 0 ? 'Completo' : `${d.remaining} restantes` }}
                    </span>
                  </div>
                </div>
                <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500"
                    :class="d.remaining === 0 ? 'bg-emerald-400' : 'bg-blue-400'"
                    :style="`width:${d.quota > 0 ? Math.min(100,(d.submitted/d.quota)*100) : 0}%`" />
                </div>
              </div>
            </div>
          </div>

          <!-- Por professor -->
          <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:120ms">
            <div class="flex items-center gap-2 px-5 py-4 border-b border-gray-50">
              <Icon name="lucide:user-check" class="w-4 h-4 text-gray-400" />
              <h3 class="text-sm font-bold text-gray-900">Progresso por professor</h3>
            </div>
            <div v-if="!byTeacher?.teachers?.length" class="flex flex-col items-center py-12">
              <Icon name="lucide:inbox" class="w-7 h-7 text-gray-200 mb-2" />
              <p class="text-xs text-gray-400">Nenhum professor atribuído</p>
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div v-for="t in byTeacher.teachers" :key="t.teacher_user_id" class="px-5 py-4">
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-[11px] font-black mt-0.5"
                    :style="`background-color:${avatarColor(t.teacher_name)}18; color:${avatarColor(t.teacher_name)}`">
                    {{ t.teacher_name.split(' ').slice(0,2).map((n: string) => n[0]).join('').toUpperCase() }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between gap-2 mb-1.5 flex-wrap">
                      <p class="text-sm font-bold text-gray-800">{{ t.teacher_name }}</p>
                      <div class="flex items-center gap-2">
                        <span class="text-xs font-black text-gray-900 tabular-nums">{{ t.total_submitted }}/{{ t.total_quota }}</span>
                        <span class="text-[11px] font-bold px-2 py-0.5 rounded-full"
                          :class="t.overall_status === 'COMPLETE' ? 'bg-emerald-50 text-emerald-700' : t.overall_status === 'PARTIAL' ? 'bg-amber-50 text-amber-700' : 'bg-gray-50 text-gray-400'">
                          {{ ({ COMPLETE: 'Completo', PARTIAL: 'Parcial', PENDING: 'Pendente' } as any)[t.overall_status] ?? t.overall_status }}
                        </span>
                      </div>
                    </div>
                    <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div class="h-full rounded-full transition-all duration-500"
                        :class="t.overall_status === 'COMPLETE' ? 'bg-emerald-400' : 'bg-blue-400'"
                        :style="`width:${t.total_quota > 0 ? Math.min(100,(t.total_submitted/t.total_quota)*100) : 0}%`" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </template>
      </template>

      <!-- ==================== ABA: RESULTADOS ==================== -->
      <template v-if="activeTab === 'resultados'">

        <!-- Sem turmas -->
        <div v-if="!examClasses.length"
          class="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border-2 border-dashed border-gray-100">
          <Icon name="lucide:users" class="w-8 h-8 text-gray-200 mb-2" />
          <p class="text-sm font-bold text-gray-400">Nenhuma turma vinculada a este simulado</p>
        </div>

        <template v-else>
          <!-- Seletor turma -->
          <div class="flex gap-2 flex-wrap animate-fade-up" style="animation-delay:60ms">
            <button v-for="cls in examClasses" :key="cls.class_id"
              class="px-3.5 py-2 rounded-xl text-xs font-bold transition-all border"
              :class="selectedClassId === cls.class_id
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'"
              @click="selectClass(cls.class_id)">
              {{ cls.class_name }}
            </button>
          </div>

          <div v-if="!selectedClassId"
            class="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border-2 border-dashed border-gray-100">
            <p class="text-sm font-bold text-gray-400">Selecione uma turma para ver o ranking</p>
          </div>

          <div v-else-if="loadingRanking"
            class="h-64 bg-white rounded-2xl border border-gray-100 animate-pulse" />

          <template v-else-if="ranking">

            <!-- Stat cards turma -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 animate-fade-up" style="animation-delay:80ms">
              <div v-for="s in rankingCards" :key="s.label"
                class="bg-white rounded-2xl border border-gray-100 p-4 flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :class="s.iconBg">
                  <Icon :name="s.icon" class="w-4 h-4" :class="s.iconColor" />
                </div>
                <div>
                  <p class="text-xl font-black text-gray-900 tabular-nums leading-none">{{ s.value }}</p>
                  <p class="text-[11px] text-gray-400 font-medium mt-0.5">{{ s.label }}</p>
                </div>
              </div>
            </div>

            <!-- Barra de exportações -->
            <div class="flex flex-wrap gap-2 animate-fade-up" style="animation-delay:95ms">
              <!-- XLSX -->
              <button
                class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all border"
                :class="exportLoading.xlsx
                  ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                  : 'bg-white border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:border-emerald-300'"
                :disabled="exportLoading.xlsx"
                @click="downloadExport('xlsx')">
                <Icon :name="exportLoading.xlsx ? 'lucide:loader-2' : 'lucide:sheet'" class="w-3.5 h-3.5" :class="exportLoading.xlsx ? 'animate-spin' : ''" />
                {{ exportLoading.xlsx ? 'Gerando…' : 'Exportar XLSX' }}
              </button>

              <!-- ZIP devolutivas -->
              <button
                class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all border"
                :class="exportLoading.zip
                  ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                  : 'bg-white border-violet-200 text-violet-700 hover:bg-violet-50 hover:border-violet-300'"
                :disabled="exportLoading.zip"
                @click="downloadExport('zip')">
                <Icon :name="exportLoading.zip ? 'lucide:loader-2' : 'lucide:archive'" class="w-3.5 h-3.5" :class="exportLoading.zip ? 'animate-spin' : ''" />
                {{ exportLoading.zip ? 'Gerando…' : 'Devolutivas ZIP' }}
              </button>

              <!-- Erro export -->
              <Transition name="slide-up">
                <span v-if="exportError"
                  class="flex items-center gap-1.5 px-3 py-2 rounded-xl text-[11px] font-bold text-red-600 bg-red-50 border border-red-100">
                  <Icon name="lucide:alert-circle" class="w-3 h-3" />
                  {{ exportError }}
                </span>
              </Transition>
            </div>

            <!-- Tabela ranking -->
            <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:100ms">
              <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
                <div class="flex items-center gap-2">
                  <Icon name="lucide:trophy" class="w-4 h-4 text-gray-400" />
                  <h3 class="text-sm font-bold text-gray-900">Ranking — {{ ranking.class_name }}</h3>
                </div>
                <span class="text-[11px] font-bold text-gray-400">{{ ranking.total_students }} alunos</span>
              </div>

              <div v-if="!ranking.results?.length" class="flex flex-col items-center py-12">
                <Icon name="lucide:inbox" class="w-7 h-7 text-gray-200 mb-2" />
                <p class="text-xs text-gray-400">Nenhuma resposta registrada nesta turma</p>
              </div>

              <div v-else>
                <div class="grid grid-cols-[40px_1fr_100px_80px_70px_32px] text-[11px] font-black text-gray-400 uppercase tracking-wider px-5 py-2.5 bg-gray-50/60 border-b border-gray-50">
                  <span>#</span><span>Aluno</span>
                  <span class="text-center hidden sm:block">RA</span>
                  <span class="text-center">Acertos</span>
                  <span class="text-right">Nota</span>
                  <span></span>
                </div>
                <div class="divide-y divide-gray-50 max-h-[520px] overflow-y-auto">
                  <div v-for="r in ranking.results" :key="r.student_id"
                    class="grid grid-cols-[40px_1fr_100px_80px_70px_32px] items-center px-5 py-2.5 hover:bg-gray-50/50 transition-colors cursor-pointer"
                    :class="selectedStudentId === r.student_id ? 'bg-blue-50/40' : ''"
                    @click="selectStudent(r.student_id)">
                    <div>
                      <span v-if="r.ranking === 1" class="w-6 h-6 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-[10px] font-black">1</span>
                      <span v-else-if="r.ranking === 2" class="w-6 h-6 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center text-[10px] font-black">2</span>
                      <span v-else-if="r.ranking === 3" class="w-6 h-6 rounded-full bg-orange-50 text-orange-500 flex items-center justify-center text-[10px] font-black">3</span>
                      <span v-else class="text-xs font-black text-gray-300 tabular-nums">{{ r.ranking }}</span>
                    </div>
                    <p class="text-sm font-semibold text-gray-800 truncate pr-2">{{ r.student_name }}</p>
                    <p class="text-[11px] font-mono text-gray-400 text-center hidden sm:block">{{ r.student_ra }}</p>
                    <p class="text-sm font-bold text-center tabular-nums"
                      :class="r.nota >= 7 ? 'text-emerald-600' : r.nota >= 5 ? 'text-amber-600' : 'text-red-500'">
                      {{ r.acertos }}/{{ r.total }}
                    </p>
                    <p class="text-sm font-black text-right tabular-nums"
                      :class="r.nota >= 7 ? 'text-emerald-600' : r.nota >= 5 ? 'text-amber-600' : 'text-red-500'">
                      {{ r.nota.toFixed(1) }}
                    </p>
                    <!-- Botão PDF devolutiva -->
                    <div class="flex justify-end" @click.stop>
                      <button
                        class="w-6 h-6 rounded-lg flex items-center justify-center transition-colors"
                        :class="pdfLoadingId === r.student_id
                          ? 'text-gray-300 cursor-wait'
                          : 'text-gray-300 hover:text-violet-600 hover:bg-violet-50'"
                        :title="`Devolutiva PDF — ${r.student_name}`"
                        :disabled="pdfLoadingId === r.student_id"
                        @click="downloadStudentPdf(r.student_id, r.student_name)">
                        <Icon :name="pdfLoadingId === r.student_id ? 'lucide:loader-2' : 'lucide:file-text'"
                          class="w-3.5 h-3.5" :class="pdfLoadingId === r.student_id ? 'animate-spin' : ''" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Detalhe individual -->
            <Transition name="slide-up">
              <div v-if="selectedStudentId" class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                <div v-if="loadingStudent" class="h-40 animate-pulse" />
                <template v-else-if="studentResult">
                  <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-xl flex items-center justify-center text-[11px] font-black flex-shrink-0"
                        :style="`background-color:${avatarColor(studentResult.student_name)}18; color:${avatarColor(studentResult.student_name)}`">
                        {{ studentResult.student_name.trim()[0] }}
                      </div>
                      <div>
                        <p class="text-sm font-bold text-gray-900">{{ studentResult.student_name }}</p>
                        <p class="text-[11px] font-mono text-gray-400">{{ studentResult.student_ra }}</p>
                      </div>
                      <span class="text-lg font-black tabular-nums ml-1"
                        :class="studentResult.nota >= 7 ? 'text-emerald-600' : studentResult.nota >= 5 ? 'text-amber-600' : 'text-red-500'">
                        {{ studentResult.nota.toFixed(1) }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2">
                      <!-- Download PDF devolutiva individual -->
                      <button
                        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border"
                        :class="pdfLoadingId === selectedStudentId
                          ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                          : 'bg-white border-violet-200 text-violet-700 hover:bg-violet-50'"
                        :disabled="pdfLoadingId === selectedStudentId"
                        @click="downloadStudentPdf(selectedStudentId!, studentResult.student_name)">
                        <Icon :name="pdfLoadingId === selectedStudentId ? 'lucide:loader-2' : 'lucide:file-text'"
                          class="w-3 h-3" :class="pdfLoadingId === selectedStudentId ? 'animate-spin' : ''" />
                        {{ pdfLoadingId === selectedStudentId ? 'Gerando…' : 'Devolutiva PDF' }}
                      </button>
                      <button class="w-7 h-7 rounded-lg hover:bg-gray-100 flex items-center justify-center"
                        @click="selectedStudentId = null; studentResult = null">
                        <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-400" />
                      </button>
                    </div>
                  </div>
                  <div class="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    <div v-for="d in studentResult.por_disciplina" :key="d.discipline_id"
                      class="p-3.5 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors">
                      <div class="flex items-center justify-between mb-1.5">
                        <p class="text-xs font-bold text-gray-700 truncate">{{ d.discipline_name }}</p>
                        <p class="text-base font-black tabular-nums ml-2 flex-shrink-0"
                          :class="d.nota >= 7 ? 'text-emerald-600' : d.nota >= 5 ? 'text-amber-600' : 'text-red-500'">
                          {{ d.nota.toFixed(1) }}
                        </p>
                      </div>
                      <p class="text-[11px] text-gray-400 mb-1.5">{{ d.acertos }} de {{ d.total }} acertos</p>
                      <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div class="h-full rounded-full transition-all"
                          :class="d.nota >= 7 ? 'bg-emerald-400' : d.nota >= 5 ? 'bg-amber-400' : 'bg-red-400'"
                          :style="`width:${d.total > 0 ? (d.acertos/d.total)*100 : 0}%`" />
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </Transition>

          </template>
        </template>
      </template>

    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get, accessToken } = useApi()

const exams         = ref<any[]>([])
const disciplines   = ref<any[]>([])
const examClasses   = ref<any[]>([])
const progress      = ref<any>(null)
const byTeacher     = ref<any>(null)
const ranking       = ref<any>(null)
const studentResult = ref<any>(null)

const loadingExams    = ref(true)
const loadingProgress = ref(false)
const loadingRanking  = ref(false)
const loadingStudent  = ref(false)

// Export state
const exportLoading = ref({ xlsx: false, zip: false })
const exportError   = ref('')
const pdfLoadingId  = ref<number | null>(null)

const selectedExamId    = ref<number | null>(null)
const selectedClassId   = ref<number | null>(null)
const selectedStudentId = ref<number | null>(null)
const activeTab = ref<'progresso' | 'resultados'>('progresso')

const tabs = [
  { id: 'progresso',  label: 'Progresso de coleta' },
  { id: 'resultados', label: 'Resultados dos alunos' },
]

const progressCards = computed(() => {
  const q              = progress.value?.disciplines ?? []
  const totalQuota     = q.reduce((s: number, d: any) => s + d.quota, 0)
  const totalSubmitted = q.reduce((s: number, d: any) => s + d.submitted, 0)
  const completas      = q.filter((d: any) => d.remaining === 0).length
  return [
    { label: 'Questões esperadas', value: totalQuota,               icon: 'lucide:target',         iconBg: 'bg-violet-50',  iconColor: 'text-violet-500' },
    { label: 'Questões enviadas',  value: totalSubmitted,           icon: 'lucide:check-circle-2', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-500' },
    { label: 'Cotas completas',    value: `${completas}/${q.length}`, icon: 'lucide:trophy',       iconBg: 'bg-amber-50',   iconColor: 'text-amber-500' },
  ]
})

const rankingCards = computed(() => {
  if (!ranking.value) return []
  return [
    { label: 'Alunos',      value: ranking.value.total_students,              icon: 'lucide:users',          iconBg: 'bg-blue-50',    iconColor: 'text-blue-500' },
    { label: 'Média turma', value: ranking.value.media_turma?.toFixed(1) ?? '—', icon: 'lucide:bar-chart-2', iconBg: 'bg-violet-50',  iconColor: 'text-violet-500' },
    { label: 'Aprovados',   value: ranking.value.aprovados,                   icon: 'lucide:check-circle-2', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-500' },
    { label: 'Reprovados',  value: ranking.value.reprovados,                  icon: 'lucide:x-circle',       iconBg: 'bg-red-50',     iconColor: 'text-red-400' },
  ]
})

function disciplineName(id: number) {
  return disciplines.value.find(d => d.id === id)?.name ?? `Disc. #${id}`
}
function statusDot(s: string) {
  return ({ collecting: 'bg-amber-400', locked: 'bg-blue-400', published: 'bg-emerald-400', draft: 'bg-gray-300' } as any)[s] ?? 'bg-gray-300'
}
const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4','#ec4899']
function avatarColor(name: string) {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) & 0xffff
  return COLORS[h % COLORS.length]
}

async function selectExam(id: number) {
  selectedExamId.value    = id
  selectedClassId.value   = null
  selectedStudentId.value = null
  ranking.value           = null
  studentResult.value     = null
  loadingProgress.value   = true

  const [pRes, btRes, classesRes] = await Promise.allSettled([
    get<any>(`/exams/${id}/progress`),
    get<any>(`/exams/${id}/dashboard/by-teacher`),
    get<any[]>(`/exams/${id}/classes`),
  ])
  if (pRes.status === 'fulfilled')       progress.value    = pRes.value
  if (btRes.status === 'fulfilled')      byTeacher.value   = btRes.value
  if (classesRes.status === 'fulfilled') examClasses.value = classesRes.value
  loadingProgress.value = false
}

async function selectClass(classId: number) {
  selectedClassId.value   = classId
  selectedStudentId.value = null
  studentResult.value     = null
  loadingRanking.value    = true
  try {
    ranking.value = await get<any>(`/exams/${selectedExamId.value}/results?class_id=${classId}`)
  } catch { ranking.value = null }
  loadingRanking.value = false
}

async function selectStudent(studentId: number) {
  if (selectedStudentId.value === studentId) {
    selectedStudentId.value = null
    studentResult.value     = null
    return
  }
  selectedStudentId.value = studentId
  loadingStudent.value    = true
  try {
    studentResult.value = await get<any>(`/exams/${selectedExamId.value}/results?student_id=${studentId}`)
  } catch { studentResult.value = null }
  loadingStudent.value = false
}

// ---------------------------------------------------------------------------
// Download helpers — usa o mesmo token do useApi (useState 'access_token')
// ---------------------------------------------------------------------------
function _triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

async function _fetchBlob(path: string): Promise<Blob> {
  const token = accessToken.value ?? (import.meta.client ? localStorage.getItem('samba_token') : null)
  const res = await fetch(`http://localhost:8000${path}`, {
    headers:     token ? { Authorization: `Bearer ${token}` } : {},
    credentials: 'include',
  })
  if (!res.ok) throw new Error(`Erro ${res.status}`)
  return res.blob()
}

async function downloadExport(type: 'xlsx' | 'zip') {
  exportError.value = ''
  exportLoading.value[type] = true
  const eid = selectedExamId.value
  const cid = selectedClassId.value
  try {
    if (type === 'xlsx') {
      const blob     = await _fetchBlob(`/exams/${eid}/results/export?class_id=${cid}`)
      const className = ranking.value?.class_name?.replace(/\s/g,'') ?? cid
      _triggerDownload(blob, `resultados_${className}_exam${eid}.xlsx`)
    } else {
      const blob     = await _fetchBlob(`/exams/${eid}/results/export/reports?class_id=${cid}`)
      const className = ranking.value?.class_name?.replace(/\s/g,'') ?? cid
      _triggerDownload(blob, `devolutivas_${className}_exam${eid}.zip`)
    }
  } catch (e: any) {
    exportError.value = e?.message ?? 'Erro ao gerar arquivo'
    setTimeout(() => { exportError.value = '' }, 4000)
  }
  exportLoading.value[type] = false
}

async function downloadStudentPdf(studentId: number, studentName: string) {
  pdfLoadingId.value = studentId
  try {
    const blob = await _fetchBlob(`/exams/${selectedExamId.value}/results/report/${studentId}`)
    const safe = studentName.split(' ')[0].toLowerCase()
    _triggerDownload(blob, `devolutiva_${safe}_exam${selectedExamId.value}.pdf`)
  } catch {
    exportError.value = 'Erro ao gerar PDF devolutiva'
    setTimeout(() => { exportError.value = '' }, 4000)
  }
  pdfLoadingId.value = null
}

onMounted(async () => {
  const [examsRes, discRes] = await Promise.allSettled([
    get<any[]>('/exams/'),
    get<any[]>('/disciplines/'),
  ])
  if (examsRes.status === 'fulfilled') exams.value       = examsRes.value
  if (discRes.status === 'fulfilled')  disciplines.value = discRes.value
  loadingExams.value = false
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) }  to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
.scrollbar-hide  { scrollbar-width:none }
.scrollbar-hide::-webkit-scrollbar { display:none }
.slide-up-enter-active { transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.34,1.56,0.64,1) }
.slide-up-leave-active { transition: opacity 0.15s ease, transform 0.15s ease }
.slide-up-enter-from   { opacity:0; transform:translateY(10px) }
.slide-up-leave-to     { opacity:0; transform:translateY(6px) }
</style>