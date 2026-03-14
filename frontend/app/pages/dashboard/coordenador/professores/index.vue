<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Professores</h1>
        <p class="page-sub">{{ teachers.length }} professor{{ teachers.length!==1?'es':'' }} cadastrado{{ teachers.length!==1?'s':'' }}</p>
      </div>
      <NuxtLink to="/dashboard/coordenador/professores/gerenciar" class="btn-primary">
        <Icon name="lucide:settings-2" class="w-4 h-4" /> Gerenciar
      </NuxtLink>
    </div>

    <div class="search-bar fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <Icon name="lucide:search" class="search-icon" />
      <input v-model="busca" placeholder="Buscar professor..." class="search-input" />
      <button v-if="busca" class="search-clear" @click="busca = ''">
        <Icon name="lucide:x" class="w-3.5 h-3.5" />
      </button>
    </div>

    <div v-if="loading" class="prof-list fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="i in 4" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <div v-else-if="!teachersFiltrados.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:users" class="w-10 h-10 text-gray-200" />
      <p>{{ busca ? 'Nenhum professor encontrado' : 'Nenhum professor cadastrado' }}</p>
    </div>

    <div v-else class="prof-list fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="(prof, idx) in teachersFiltrados" :key="prof.id" class="prof-card" :style="`--i:${idx}`">
        <div class="prof-header" @click="toggleProf(prof.id)">
          <div class="prof-avatar" :style="`background:${avatarBg(idx)}20;color:${avatarBg(idx)}`">
            {{ initials(prof.name) }}
          </div>
          <div class="prof-info">
            <span class="prof-name">{{ prof.name }}</span>
            <span class="prof-email">{{ prof.email }}</span>
          </div>
          <div class="prof-right">
            <span class="subj-count">{{ subjectCount(prof.id) }} vínculo{{ subjectCount(prof.id)!==1?'s':'' }}</span>
            <Icon :name="expanded.has(prof.id) ? 'lucide:chevron-up' : 'lucide:chevron-down'" class="w-4 h-4 text-gray-300" />
          </div>
        </div>
        <Transition name="expand">
          <div v-if="expanded.has(prof.id)" class="prof-subjects">
            <p v-if="!subjectsOf(prof.id).length" class="empty-note">Sem turmas vinculadas</p>
            <div v-for="s in subjectsOf(prof.id)" :key="s.id" class="subject-row">
              <div class="subj-dot bg-indigo-400" />
              <span class="subj-disc">{{ s.discipline_name }}</span>
              <span class="subj-sep">·</span>
              <span class="subj-class">{{ s.class_name }}</span>
            </div>
          </div>
        </Transition>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const mounted = ref(false)
const teachers        = ref<any[]>([])
const teacherSubjects = ref<any[]>([])
const loading         = ref(true)
const busca           = ref('')
const expanded        = ref(new Set<number>())

const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4','#ec4899']
function avatarBg(idx: number) { return COLORS[idx % COLORS.length] }
function initials(name: string) { return name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0]?.toUpperCase()).join('') }
function toggleProf(id: number) { if (expanded.value.has(id)) expanded.value.delete(id); else expanded.value.add(id) }
function subjectsOf(id: number) { return teacherSubjects.value.filter(s => s.teacher_user_id === id) }
function subjectCount(id: number) { return subjectsOf(id).length }
const teachersFiltrados = computed(() => {
  if (!busca.value) return teachers.value
  const q = busca.value.toLowerCase()
  return teachers.value.filter(t => t.name.toLowerCase().includes(q) || t.email.toLowerCase().includes(q))
})

onMounted(async () => {
  await nextTick(); setTimeout(() => { mounted.value = true }, 30)
  const [tRes, sRes] = await Promise.allSettled([get<any[]>('/school/teachers'), get<any[]>('/school/teacher-subjects')])
  if (tRes.status === 'fulfilled') teachers.value        = tRes.value
  if (sRes.status === 'fulfilled') teacherSubjects.value = sRes.value
  loading.value = false
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.search-bar  { position:relative; }
.search-icon { position:absolute; left:.875rem; top:50%; transform:translateY(-50%); width:.875rem; height:.875rem; color:#d1d5db; }
.search-input { width:100%; padding:.625rem .875rem .625rem 2.5rem; border:1px solid #e5e7eb; border-radius:.875rem; font-size:.8rem; background:white; outline:none; transition:border-color .13s; }
.search-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.search-clear { position:absolute; right:.875rem; top:50%; transform:translateY(-50%); color:#d1d5db; }
.search-clear:hover { color:#6b7280; }
.prof-list  { display:flex; flex-direction:column; gap:.625rem; }
.skel-card  { height:5rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*70ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.prof-card  { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*45ms); transition:border-color .15s; }
.prof-card:hover { border-color:#e5e7eb; }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.prof-header { display:flex; align-items:center; gap:1rem; padding:1rem 1.25rem; cursor:pointer; }
.prof-avatar { width:2.5rem; height:2.5rem; border-radius:9999px; font-size:.75rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.prof-info   { flex:1; min-width:0; }
.prof-name   { display:block; font-size:.875rem; font-weight:700; color:#111827; }
.prof-email  { display:block; font-size:.7rem; color:#9ca3af; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.prof-right  { display:flex; align-items:center; gap:.75rem; flex-shrink:0; }
.subj-count  { font-size:.7rem; font-weight:600; color:#6b7280; }
.prof-subjects { border-top:1px solid #f9fafb; padding:.75rem 1.25rem; display:flex; flex-direction:column; gap:.375rem; background:#fafafa; }
.empty-note  { font-size:.75rem; color:#9ca3af; }
.subject-row { display:flex; align-items:center; gap:.5rem; }
.subj-dot    { width:.4rem; height:.4rem; border-radius:50%; flex-shrink:0; }
.subj-disc   { font-size:.75rem; font-weight:600; color:#374151; }
.subj-sep    { font-size:.75rem; color:#d1d5db; }
.subj-class  { font-size:.75rem; color:#9ca3af; }
.btn-primary { display:inline-flex; align-items:center; gap:.4rem; padding:.6rem 1.1rem; background:#111827; color:white; font-size:.8rem; font-weight:700; border-radius:.75rem; text-decoration:none; transition:background .13s; white-space:nowrap; }
.btn-primary:hover { background:#1f2937; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.expand-enter-active { transition:all .22s ease; overflow:hidden; }
.expand-leave-active { transition:all .18s ease; overflow:hidden; }
.expand-enter-from, .expand-leave-to { opacity:0; max-height:0; }
.expand-enter-to, .expand-leave-from { opacity:1; max-height:20rem; }
</style>