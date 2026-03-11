<!-- pages/dashboard/coordenador/professores.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between animate-fade-in">
      <div>
        <h2 class="text-xl font-black text-gray-900 tracking-tight">Professores</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ teachers.length }} professor{{ teachers.length !== 1 ? 'es' : '' }} cadastrado{{ teachers.length !== 1 ? 's' : '' }}</p>
      </div>
      <NuxtLink to="/dashboard/coordenador/professores/gerenciar"
        class="flex items-center gap-2 px-4 py-2 bg-gray-900 hover:bg-gray-700 text-white text-sm font-bold rounded-xl transition-all active:scale-95">
        <Icon name="lucide:settings-2" class="w-4 h-4" />
        Gerenciar
      </NuxtLink>
    </div>

    <!-- Busca -->
    <div class="relative animate-fade-up" style="animation-delay:40ms">
      <Icon name="lucide:search" class="w-4 h-4 text-gray-300 absolute left-3.5 top-1/2 -translate-y-1/2" />
      <input v-model="busca"
        class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all bg-white"
        placeholder="Buscar professor..." />
      <button v-if="busca" class="absolute right-3 top-1/2 -translate-y-1/2" @click="busca = ''">
        <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-300 hover:text-gray-500 transition-colors" />
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i"
        class="h-40 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`animation-delay:${i*50}ms`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!teachersFiltrados.length"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:users" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">
        {{ busca ? 'Nenhum professor encontrado' : 'Nenhum professor cadastrado' }}
      </p>
    </div>

    <!-- Lista -->
    <div v-else class="space-y-4">
      <div v-for="(prof, idx) in teachersFiltrados" :key="prof.id"
        class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up hover:border-gray-200 hover:shadow-sm transition-all duration-200"
        :style="`animation-delay:${idx*50}ms`">

        <!-- Header do professor -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50 cursor-pointer"
          @click="toggleProf(prof.id)">
          <div class="flex items-center gap-4">
            <!-- Avatar -->
            <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 font-black text-sm"
              :style="`background-color:${avatarBg(idx)}20; color:${avatarBg(idx)}`">
              {{ initials(prof.name) }}
            </div>
            <div>
              <p class="text-sm font-black text-gray-900">{{ prof.name }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ prof.email }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Badges resumo -->
            <div class="hidden sm:flex items-center gap-2">
              <span class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
                {{ turmasDoProf(prof.id).length }} turma{{ turmasDoProf(prof.id).length !== 1 ? 's' : '' }}
              </span>
              <span class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-violet-50 text-violet-700">
                {{ simuladosDoProf(prof.id).length }} simulado{{ simuladosDoProf(prof.id).length !== 1 ? 's' : '' }}
              </span>
            </div>
            <Icon
              :name="expanded.has(prof.id) ? 'lucide:chevron-up' : 'lucide:chevron-down'"
              class="w-4 h-4 text-gray-300 transition-transform" />
          </div>
        </div>

        <!-- Conteúdo expandido -->
        <div v-if="expanded.has(prof.id)" class="divide-y divide-gray-50">

          <!-- Turmas e disciplinas -->
          <div class="px-5 py-4">
            <p class="text-[11px] font-black text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Icon name="lucide:users" class="w-3.5 h-3.5" />
              Turmas e disciplinas
            </p>

            <div v-if="!turmasDoProf(prof.id).length"
              class="text-xs text-gray-400 italic">Nenhuma turma atribuída.</div>

            <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              <div v-for="slot in turmasDoProf(prof.id)" :key="`${slot.class_id}_${slot.discipline_id}`"
                class="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-gray-50 border border-gray-100">
                <div class="w-7 h-7 rounded-lg bg-white border border-gray-200 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:book-open" class="w-3 h-3 text-gray-400" />
                </div>
                <div class="min-w-0">
                  <p class="text-xs font-bold text-gray-800 truncate">{{ className(slot.class_id) }}</p>
                  <p class="text-[11px] text-gray-400 truncate">{{ disciplineName(slot.discipline_id) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Simulados atribuídos -->
          <div class="px-5 py-4">
            <p class="text-[11px] font-black text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Icon name="lucide:file-text" class="w-3.5 h-3.5" />
              Simulados atribuídos
            </p>

            <div v-if="!simuladosDoProf(prof.id).length"
              class="text-xs text-gray-400 italic">Nenhum simulado atribuído.</div>

            <div v-else class="flex flex-wrap gap-2">
              <div v-for="exam in simuladosDoProf(prof.id)" :key="exam.id"
                class="flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-semibold transition-colors"
                :class="statusBadge(exam.status)">
                <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="statusDot(exam.status)" />
                <span class="font-bold">{{ exam.title }}</span>
                <span class="opacity-60">· {{ statusLabel(exam.status) }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()

const teachers       = ref<any[]>([])
const teacherSubjects = ref<any[]>([])
const allClasses     = ref<any[]>([])
const disciplines    = ref<any[]>([])
const exams          = ref<any[]>([])
const examTeacherAssignments = ref<any[]>([])
const loading = ref(true)
const busca   = ref('')
const expanded = ref(new Set<number>())

// Computed
const teachersFiltrados = computed(() => {
  if (!busca.value) return teachers.value
  const q = busca.value.toLowerCase()
  return teachers.value.filter(t =>
    t.name.toLowerCase().includes(q) || t.email.toLowerCase().includes(q)
  )
})

// Helpers de dados
function turmasDoProf(profId: number) {
  return teacherSubjects.value.filter(ts => ts.teacher_user_id === profId)
}

function simuladosDoProf(profId: number) {
  // Pega exam_ids únicos onde o prof foi atribuído
  const examIds = new Set(
    examTeacherAssignments.value
      .filter(a => a.teacher_user_id === profId)
      .map(a => a.exam_id)
  )
  return exams.value.filter(e => examIds.has(e.id))
}

function className(id: number) {
  return allClasses.value.find(c => c.id === id)?.name ?? `Turma #${id}`
}

function disciplineName(id: number) {
  return disciplines.value.find(d => d.id === id)?.name ?? `Disc. #${id}`
}

function toggleProf(id: number) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
}

function initials(name: string) {
  return name.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase()
}

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']
function avatarBg(idx: number) {
  return COLORS[idx % COLORS.length]
}

function statusLabel(s: string) {
  return ({ collecting: 'Em coleta', locked: 'Travado', published: 'Publicado', draft: 'Rascunho' } as any)[s] ?? s
}
function statusBadge(s: string) {
  return ({
    collecting: 'bg-amber-50 border-amber-100 text-amber-700',
    locked:     'bg-blue-50 border-blue-100 text-blue-700',
    published:  'bg-emerald-50 border-emerald-100 text-emerald-700',
    draft:      'bg-gray-50 border-gray-100 text-gray-500',
  } as any)[s] ?? 'bg-gray-50 border-gray-100 text-gray-500'
}
function statusDot(s: string) {
  return ({
    collecting: 'bg-amber-400',
    locked:     'bg-blue-400',
    published:  'bg-emerald-400',
    draft:      'bg-gray-300',
  } as any)[s] ?? 'bg-gray-300'
}

onMounted(async () => {
  const [teachersRes, subjectsRes, classesRes, discRes, examsRes] = await Promise.allSettled([
    get<any[]>('/school/teachers'),
    get<any[]>('/school/teacher-subjects'),
    get<any[]>('/school/classes'),
    get<any[]>('/disciplines/'),
    get<any[]>('/exams/'),
  ])

  if (teachersRes.status === 'fulfilled') teachers.value        = teachersRes.value
  if (subjectsRes.status === 'fulfilled') teacherSubjects.value = subjectsRes.value
  if (classesRes.status === 'fulfilled')  allClasses.value      = classesRes.value
  if (discRes.status === 'fulfilled')     disciplines.value     = discRes.value
  if (examsRes.status === 'fulfilled')    exams.value           = examsRes.value

  // Para cada simulado, busca assignments via endpoint dedicado
  if (examsRes.status === 'fulfilled') {
    const allAssignments: any[] = []
    await Promise.allSettled(
      examsRes.value.map(async (exam: any) => {
        try {
          const items = await get<any[]>(`/exams/${exam.id}/teacher-assignments`)
          for (const a of items) allAssignments.push(a)
        } catch {}
      })
    )
    examTeacherAssignments.value = allAssignments
  }

  // Expande o primeiro professor por padrão
  if (teachers.value.length > 0) {
    expanded.value.add(teachers.value[0].id)
  }

  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
</style>