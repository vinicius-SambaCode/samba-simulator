<!-- pages/dashboard/professor/minhas-turmas.vue -->
<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Minhas turmas</h2>
        <p class="text-sm text-gray-500 mt-0.5">Turmas em que você foi vinculado pelo coordenador</p>
      </div>
      <button
        class="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-50"
        :class="{ 'pointer-events-none': loading }"
        @click="carregarDados">
        <Icon :name="loading ? 'lucide:loader-2' : 'lucide:refresh-cw'"
          class="w-3.5 h-3.5" :class="loading ? 'animate-spin' : ''" />
        Atualizar
      </button>
    </div>

    <!-- Loading skeletons -->
    <div v-if="loading" class="grid gap-3 sm:grid-cols-2">
      <div v-for="i in 3" :key="i"
        class="h-44 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="{ animationDelay: `${i * 80}ms` }" />
    </div>

    <!-- Empty state -->
    <div v-else-if="minhasTurmas.length === 0"
      class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border-2 border-dashed border-gray-100">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:users" class="w-7 h-7 text-gray-200" />
      </div>
      <p class="text-sm font-medium text-gray-400">Você ainda não foi vinculado a nenhuma turma</p>
      <p class="text-xs text-gray-300 mt-1">O coordenador precisa criar o vínculo turma + disciplina</p>
    </div>

    <!-- Grid de turmas -->
    <TransitionGroup v-else name="list" tag="div" class="grid gap-3 sm:grid-cols-2">
      <div
        v-for="(item, idx) in minhasTurmas"
        :key="item.class_id"
        class="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:border-gray-200 hover:shadow-md transition-all duration-200">

        <!-- Faixa colorida -->
        <div class="h-1.5 w-full" :class="cores[idx % cores.length].stripe" />

        <div class="p-5">

          <!-- Header da turma -->
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0 select-none"
              :class="cores[idx % cores.length].bg">
              {{ iniciais(item.class_name) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-gray-900 truncate">{{ item.class_name }}</p>
              <p class="text-xs text-gray-400 truncate">{{ item.disciplines.join(', ') }}</p>
            </div>
            <span v-if="students[item.class_id]"
              class="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full flex-shrink-0">
              {{ students[item.class_id].length }} alunos
            </span>
          </div>

          <!-- Simulados desta turma -->
          <div class="space-y-1.5 mb-4">
            <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Simulados</p>

            <div v-if="item.exams.length === 0"
              class="flex items-center gap-2 py-2 px-2.5 text-xs text-gray-300">
              <Icon name="lucide:inbox" class="w-3.5 h-3.5" />
              Nenhum simulado atribuído ainda
            </div>

            <NuxtLink
              v-for="exam in item.exams"
              :key="exam.id"
              :to="exam.status === 'collecting' ? `/dashboard/professor/simulados/${exam.id}` : '#'"
              class="flex items-center gap-2.5 p-2.5 rounded-xl border transition-all duration-150 group"
              :class="exam.status === 'collecting'
                ? 'border-gray-100 hover:border-orange-200 hover:bg-orange-50/30 cursor-pointer'
                : 'border-gray-50 opacity-70 cursor-default'">

              <div class="w-2 h-2 rounded-full flex-shrink-0" :class="statusDot(exam.status)" />

              <p class="text-xs font-semibold text-gray-700 truncate flex-1 transition-colors"
                :class="exam.status === 'collecting' ? 'group-hover:text-orange-600' : ''">
                {{ exam.title }}
              </p>

              <div v-if="progressMap[exam.id]" class="flex items-center gap-1.5 flex-shrink-0">
                <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-700 ease-out"
                    :class="calcProgresso(exam.id, item) === 100 ? 'bg-emerald-400' : 'bg-orange-400'"
                    :style="{ width: calcProgresso(exam.id, item) + '%' }" />
                </div>
                <span class="text-[10px] tabular-nums font-medium"
                  :class="calcProgresso(exam.id, item) === 100 ? 'text-emerald-500' : 'text-gray-400'">
                  {{ calcProgresso(exam.id, item) }}%
                </span>
              </div>

              <Icon v-if="exam.status === 'collecting'"
                name="lucide:chevron-right"
                class="w-3 h-3 text-gray-300 group-hover:text-orange-400 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
            </NuxtLink>
          </div>

          <!-- Botão expandir alunos -->
          <button
            class="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors text-xs font-medium text-gray-500"
            @click="toggleAlunos(item.class_id)">
            <span class="flex items-center gap-1.5">
              <Icon name="lucide:users" class="w-3.5 h-3.5" />
              Ver alunos
              <Transition name="pop">
                <span v-if="students[item.class_id]" class="text-gray-400 tabular-nums">
                  ({{ students[item.class_id].length }})
                </span>
              </Transition>
            </span>
            <Icon
              :name="expandedAlunos[item.class_id] ? 'lucide:chevron-up' : 'lucide:chevron-down'"
              class="w-3.5 h-3.5 transition-transform duration-200" />
          </button>

          <!-- Lista de alunos (lazy) -->
          <Transition name="expand">
            <div v-if="expandedAlunos[item.class_id]" class="mt-2">
              <div v-if="loadingStudents[item.class_id]" class="space-y-1.5 py-1">
                <div v-for="i in 4" :key="i"
                  class="h-7 bg-gray-50 rounded-lg animate-pulse"
                  :style="{ animationDelay: `${i * 60}ms` }" />
              </div>
              <div v-else-if="!students[item.class_id]?.length"
                class="text-xs text-gray-300 text-center py-4">
                Nenhum aluno cadastrado
              </div>
              <div v-else class="space-y-0.5 max-h-48 overflow-y-auto pr-1 scrollbar-thin">
                <div v-for="aluno in students[item.class_id]" :key="aluno.id"
                  class="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-gray-50 transition-colors group/aluno">
                  <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0"
                    :class="cores[idx % cores.length].avatar">
                    {{ aluno.name[0].toUpperCase() }}
                  </div>
                  <p class="text-xs text-gray-600 truncate flex-1">{{ aluno.name }}</p>
                  <p class="text-[10px] text-gray-300 font-mono flex-shrink-0 group-hover/aluno:text-gray-400 transition-colors">
                    {{ aluno.ra }}
                  </p>
                </div>
              </div>
            </div>
          </Transition>

        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()

const loading         = ref(true)
const students        = ref<Record<number, any[]>>({})
const loadingStudents = ref<Record<number, boolean>>({})
const expandedAlunos  = ref<Record<number, boolean>>({})
const progressMap     = ref<Record<number, any>>({})
const myAssignments   = ref<Record<number, any>>({}) // examId → assignment

// Turmas agrupadas a partir dos vínculos do professor
// { class_id, class_name, disciplines[], exams[] }
const minhasTurmas = ref<any[]>([])

const cores = [
  { stripe: 'bg-orange-400',  bg: 'bg-orange-500',  avatar: 'bg-orange-100 text-orange-600' },
  { stripe: 'bg-blue-400',    bg: 'bg-blue-500',    avatar: 'bg-blue-100 text-blue-600' },
  { stripe: 'bg-emerald-400', bg: 'bg-emerald-500', avatar: 'bg-emerald-100 text-emerald-600' },
  { stripe: 'bg-purple-400',  bg: 'bg-purple-500',  avatar: 'bg-purple-100 text-purple-600' },
  { stripe: 'bg-pink-400',    bg: 'bg-pink-500',    avatar: 'bg-pink-100 text-pink-600' },
]

function iniciais(nome: string): string {
  const partes = nome.trim().split(/\s+/)
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase()
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
}

function statusDot(s: string): string {
  const map: Record<string, string> = {
    collecting: 'bg-amber-400',
    locked:     'bg-blue-400',
    published:  'bg-emerald-400',
    generated:  'bg-purple-400',
  }
  return map[s] ?? 'bg-gray-300'
}

// Progresso do professor neste exam, filtrado pela(s) disciplina(s) da turma
function calcProgresso(examId: number, item: any): number {
  const prog       = progressMap.value[examId]
  const assignment = myAssignments.value[examId]
  if (!prog) return 0

  // Usa discipline_id do assignment deste exam, ou das disciplinas da turma
  const discId = assignment?.discipline_id ?? item.discipline_ids?.[0]
  if (!discId) return 0

  const disc = prog.disciplines?.find((d: any) => d.discipline_id === discId)
  if (!disc?.quota) return 0
  return Math.min(100, Math.round(disc.submitted / disc.quota * 100))
}

async function toggleAlunos(classId: number) {
  expandedAlunos.value[classId] = !expandedAlunos.value[classId]
  if (expandedAlunos.value[classId] && !students.value[classId]) {
    loadingStudents.value[classId] = true
    try {
      students.value[classId] = await get<any[]>(`/school/students?class_id=${classId}`)
    } catch {
      students.value[classId] = []
    } finally {
      loadingStudents.value[classId] = false
    }
  }
}

async function carregarDados() {
  loading.value     = true
  myAssignments.value = {}
  progressMap.value   = {}

  try {
    // 1. Vínculos permanentes do professor (independe de simulado)
    const [subjects, exams] = await Promise.all([
      get<any[]>('/school/my-subjects'),
      get<any[]>('/exams/'),
    ])

    // 2. Agrupa subjects por turma
    const classMap: Record<number, any> = {}
    for (const s of subjects) {
      if (!classMap[s.class_id]) {
        classMap[s.class_id] = {
          class_id:       s.class_id,
          class_name:     s.class_name,
          disciplines:    [],
          discipline_ids: [],
          exams:          [],
        }
      }
      if (s.discipline_name && !classMap[s.class_id].disciplines.includes(s.discipline_name)) {
        classMap[s.class_id].disciplines.push(s.discipline_name)
        classMap[s.class_id].discipline_ids.push(s.discipline_id)
      }
    }

    // 3. Busca my-assignment e progress de cada exam em paralelo
    const [assignmentResults, progressResults] = await Promise.all([
      Promise.allSettled(exams.map(e => get<any>(`/exams/${e.id}/my-assignment`))),
      Promise.allSettled(exams.map(e => get<any>(`/exams/${e.id}/progress`))),
    ])

    exams.forEach((exam, i) => {
      const ar = assignmentResults[i]
      const pr = progressResults[i]

      if (pr.status === 'fulfilled') progressMap.value[exam.id] = pr.value

      // Se o professor tem assignment neste exam, vincula o exam à turma correta
      if (ar.status === 'fulfilled' && ar.value) {
        const assignment = ar.value
        myAssignments.value[exam.id] = assignment

        const classId = assignment.class_id
        if (classMap[classId]) {
          // Garante que a turma do assignment está no mapa (mesmo sem vínculo permanente)
          if (!classMap[classId].exams.find((e: any) => e.id === exam.id)) {
            classMap[classId].exams.push(exam)
          }
        } else {
          // Turma sem vínculo permanente mas com assignment — mostra mesmo assim
          classMap[classId] = {
            class_id:       classId,
            class_name:     assignment.class_name ?? `Turma #${classId}`,
            disciplines:    assignment.discipline_name ? [assignment.discipline_name] : [],
            discipline_ids: assignment.discipline_id  ? [assignment.discipline_id]  : [],
            exams:          [exam],
          }
        }
      }
    })

    // 4. Ordena exams dentro de cada turma: collecting primeiro
    for (const item of Object.values(classMap)) {
      item.exams.sort((a: any, b: any) =>
        a.status === 'collecting' && b.status !== 'collecting' ? -1 : 1
      )
    }

    minhasTurmas.value = Object.values(classMap)
  } catch (e) {
    console.error('Erro ao carregar turmas:', e)
    minhasTurmas.value = []
  } finally {
    loading.value = false
  }
}

onMounted(carregarDados)
onActivated(carregarDados)
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: max-height 0.28s ease, opacity 0.22s ease;
  overflow: hidden;
  max-height: 400px;
}
.expand-enter-from,
.expand-leave-to { max-height: 0; opacity: 0; }

.pop-enter-active { transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-leave-active { transition: all 0.12s ease; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: scale(0.8); }

.list-enter-active { transition: all 0.25s ease; }
.list-enter-from   { opacity: 0; transform: translateY(-6px); }
.list-move         { transition: transform 0.3s ease; }

.scrollbar-thin::-webkit-scrollbar { width: 4px; }
.scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
.scrollbar-thin::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 9999px; }
.scrollbar-thin::-webkit-scrollbar-thumb:hover { background: #d1d5db; }
</style>