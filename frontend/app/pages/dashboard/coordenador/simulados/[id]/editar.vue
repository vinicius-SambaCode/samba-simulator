<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div class="flex items-center gap-3">
        <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`" class="back-btn">
          <Icon name="lucide:arrow-left" class="w-4 h-4" />
        </NuxtLink>
        <div>
          <h1 class="page-title">
            <span v-if="loading" class="skel-line" />
            <span v-else>{{ exam?.title }}</span>
          </h1>
          <p class="page-sub">Cotas por disciplina e atribuições de professores</p>
        </div>
      </div>
      <span v-if="exam?.status === 'locked'" class="status-pill pill-blue">
        <Icon name="lucide:lock" class="w-3 h-3" /> Travado
      </span>
      <span v-else-if="exam?.status === 'collecting'" class="status-pill pill-amber">
        <Icon name="lucide:pen" class="w-3 h-3" /> Em coleta
      </span>
    </div>

    <div v-if="loading" class="main-grid fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <div class="skel-panel" />
      <div class="skel-panel" />
    </div>

    <div v-else class="main-grid fade-in" :class="{ ready: mounted }" style="--d:.06s">

      <!-- COTAS -->
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title"><Icon name="lucide:target" class="w-4 h-4 text-gray-400" /> Cotas por disciplina</div>
          <div class="flex items-center gap-2">
            <Transition name="fade-msg">
              <span v-if="quotasSuccess" class="saved-msg">
                <Icon name="lucide:check" class="w-3 h-3" /> Salvo!
              </span>
            </Transition>
            <button class="btn-primary btn-sm"
              :disabled="savingQuotas || exam?.status !== 'collecting'"
              @click="saveQuotas">
              <svg v-if="savingQuotas" class="spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
                <path fill="currentColor" d="M4 12a8 8 0 018-8v8z" class="opacity-75"/>
              </svg>
              <Icon v-else name="lucide:save" class="w-3 h-3" />
              {{ savingQuotas ? 'Salvando...' : 'Salvar cotas' }}
            </button>
          </div>
        </div>

        <!-- Total -->
        <div class="total-bar">
          <span class="total-label">Total esperado</span>
          <span class="total-value">{{ Object.values(quotaForm).reduce((a:number,b:number)=>a+b,0) }}</span>
        </div>

        <!-- Aviso status -->
        <div v-if="exam?.status === 'draft'" class="status-warning">
          <Icon name="lucide:info" class="w-3.5 h-3.5 flex-shrink-0" />
          O simulado precisa estar em <strong>coleta</strong> para salvar cotas. Inicie a coleta primeiro.
        </div>

        <div class="disc-list">
          <div v-for="disc in disciplinasComCota" :key="disc.id" class="disc-row">
            <div class="disc-info">
              <span class="disc-name">{{ disc.name }}</span>
              <div class="progress-row">
                <div class="prog-bar">
                  <div class="prog-fill"
                    :class="(quotaMap[disc.id]?.submitted??0)>=quotaForm[disc.id]&&quotaForm[disc.id]>0?'bg-emerald-400':'bg-blue-300'"
                    :style="`width:${quotaForm[disc.id]>0?Math.min(100,((quotaMap[disc.id]?.submitted??0)/quotaForm[disc.id])*100):0}%`" />
                </div>
                <span class="prog-text">{{ quotaMap[disc.id]?.submitted??0 }}/{{ quotaForm[disc.id]??0 }}</span>
              </div>
            </div>
            <div class="quota-ctrl">
              <button class="quota-btn"
                :disabled="exam?.status === 'locked'"
                @click="changeQuota(disc.id,-1)">−</button>
              <input :value="quotaForm[disc.id]??0"
                :disabled="exam?.status === 'locked'"
                type="number" min="0" max="99" class="quota-input"
                @input="setQuota(disc.id, Number(($event.target as HTMLInputElement).value))" />
              <button class="quota-btn"
                :disabled="exam?.status === 'locked'"
                @click="changeQuota(disc.id,1)">+</button>
            </div>
          </div>
          <div v-if="!disciplinasComCota.length" class="empty-note">Nenhuma disciplina cadastrada</div>
        </div>
        <p v-if="quotaError" class="error-msg px-4 pb-3">{{ quotaError }}</p>
      </div>

      <!-- PROFESSORES -->
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title"><Icon name="lucide:briefcase" class="w-4 h-4 text-gray-400" /> Atribuições de professores</div>
          <button class="btn-secondary btn-sm"
            :disabled="exam?.status === 'locked'"
            @click="showAssignTeacherModal = true">
            <Icon name="lucide:plus" class="w-3 h-3" /> Atribuir
          </button>
        </div>

        <div v-if="loadingAssignments" class="card-loading">
          <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="!assignments.length" class="empty-note p-4">
          Nenhum professor atribuído ainda
        </div>
        <ul v-else class="assign-list">
          <li v-for="a in assignments" :key="a.id" class="assign-item">
            <div class="assign-avatar" :style="`background:${avatarColor(a.teacher_name??'')}20;color:${avatarColor(a.teacher_name??'')}`">
              {{ initials(a.teacher_name??'') }}
            </div>
            <div class="assign-info">
              <span class="assign-name">{{ a.teacher_name }}</span>
              <span class="assign-meta">{{ a.class_name }} · {{ a.discipline_name }}</span>
            </div>
            <button class="del-btn" title="Remover" @click="removeAssignment(a.id)">
              <Icon name="lucide:x" class="w-3.5 h-3.5" />
            </button>
          </li>
        </ul>
      </div>

    </div>

    <!-- Modal atribuir professor -->
    <Transition name="modal">
      <div v-if="showAssignTeacherModal" class="modal-overlay" @click.self="showAssignTeacherModal = false">
        <div class="modal-box">
          <h3 class="modal-title">Atribuir professor</h3>
          <div class="field">
            <label class="field-label">Professor</label>
            <select v-model="assignForm.teacher_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">Turma</label>
            <select v-model="assignForm.class_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="cls in examClasses" :key="cls.class_id" :value="cls.class_id">{{ cls.class_name }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">Disciplina</label>
            <select v-model="assignForm.discipline_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <p v-if="assignTeacherError" class="error-msg">{{ assignTeacherError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showAssignTeacherModal = false">Cancelar</button>
            <button class="btn-primary"
              :disabled="!assignForm.teacher_id || !assignForm.class_id || !assignForm.discipline_id || savingAssign"
              @click="saveAssignment">
              {{ savingAssign ? 'Salvando...' : 'Atribuir' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { get, post, delete: del } = useApi()
const examId = computed(() => Number(route.params.id))
const mounted = ref(false)

const exam        = ref<any>(null)
const disciplines = ref<any[]>([])
const teachers    = ref<any[]>([])
const examClasses = ref<any[]>([])
const assignments = ref<any[]>([])
const quotaMap    = ref<Record<number,any>>({})
const quotaForm   = reactive<Record<number,number>>({})

const loading           = ref(true)
const loadingAssignments= ref(true)
const savingQuotas      = ref(false)
const quotasSuccess     = ref(false)
const quotaError        = ref('')
const showAssignTeacherModal = ref(false)
const savingAssign      = ref(false)
const assignTeacherError= ref('')
const assignForm = reactive({ teacher_id:'', class_id:'', discipline_id:'' })

const disciplinasComCota = computed(() => disciplines.value)

function changeQuota(id: number, delta: number) {
  if (exam.value?.status !== 'collecting') return
  quotaForm[id] = Math.max(0, (quotaForm[id]??0) + delta)
}
function setQuota(id: number, val: number) {
  quotaForm[id] = isNaN(val) ? 0 : Math.max(0, Math.min(99, val))
}

async function saveQuotas() {
  savingQuotas.value=true; quotaError.value=''
  try {
    if (exam.value?.status !== 'collecting') {
      quotaError.value = 'O simulado precisa estar em coleta para definir cotas.'
      return
    }
    // Backend rejeita quota === 0 — envia apenas os que têm valor > 0
    const items = Object.entries(quotaForm)
      .map(([id, quota]) => ({ discipline_id: Number(id), quota: Number(quota) }))
      .filter(it => it.quota > 0)
    if (!items.length) {
      quotaError.value = 'Defina pelo menos uma cota maior que zero.'
      return
    }
    await post(`/exams/${examId.value}/quotas`, { items })
    quotasSuccess.value=true; setTimeout(()=>{quotasSuccess.value=false},2000)
  } catch (e:any) { quotaError.value=e?.data?.detail??e.message??'Erro ao salvar cotas.' } finally { savingQuotas.value=false }
}

async function saveAssignment() {
  savingAssign.value=true; assignTeacherError.value=''
  try {
    await post(`/exams/${examId.value}/assign-teachers`, {
      items:[{ teacher_user_id:Number(assignForm.teacher_id), class_id:Number(assignForm.class_id), discipline_id:Number(assignForm.discipline_id) }]
    })
    await loadAssignments()
    showAssignTeacherModal.value=false; assignForm.teacher_id=''; assignForm.class_id=''; assignForm.discipline_id=''
  } catch (e:any) { assignTeacherError.value=e.message??'Erro ao atribuir.' } finally { savingAssign.value=false }
}

async function removeAssignment(id: number) {
  try {
    await del(`/exams/${examId.value}/teacher-assignments/${id}`)
    assignments.value = assignments.value.filter(a => a.id !== id)
  } catch (e: any) {
    quotaError.value = e?.data?.detail ?? 'Erro ao remover atribuição.'
  }
}

async function loadAssignments() {
  loadingAssignments.value=true
  try {
    const raw = await get<any[]>(`/exams/${examId.value}/teacher-assignments`)
    // O endpoint só retorna IDs — cruzamos com os arrays já carregados
    assignments.value = raw.map(a => ({
      ...a,
      teacher_name:    teachers.value.find(t => t.id === a.teacher_user_id)?.name    ?? `Professor #${a.teacher_user_id}`,
      class_name:      examClasses.value.find(c => c.class_id === a.class_id)?.class_name ?? `Turma #${a.class_id}`,
      discipline_name: disciplines.value.find(d => d.id === a.discipline_id)?.name    ?? `Disciplina #${a.discipline_id}`,
    }))
  } catch { assignments.value=[] } finally { loadingAssignments.value=false }
}

const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4']
function avatarColor(name: string) { let h=0; for (const c of name) h=(h*31+c.charCodeAt(0))&0xffff; return COLORS[h%COLORS.length] }
function initials(name: string) { return name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0]?.toUpperCase()).join('') }

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [examRes, discRes, teacherRes, classesRes, progressRes] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any[]>('/disciplines/'),
    get<any[]>('/school/teachers'),
    get<any[]>(`/exams/${examId.value}/classes`),
    get<any>(`/exams/${examId.value}/progress`),
  ])
  if (examRes.status==='fulfilled')    exam.value        = examRes.value
  if (discRes.status==='fulfilled')    disciplines.value = discRes.value
  if (teacherRes.status==='fulfilled') teachers.value    = teacherRes.value
  if (classesRes.status==='fulfilled') examClasses.value = classesRes.value
  if (progressRes.status==='fulfilled') {
    const prog = progressRes.value
    for (const d of prog.disciplines??[]) {
      quotaMap.value[d.discipline_id] = d
      quotaForm[d.discipline_id] = d.quota ?? 0
    }
  }
  // Init quotas for disciplines without quota yet
  for (const d of disciplines.value) {
    if (!(d.id in quotaForm)) quotaForm[d.id] = 0
  }
  loading.value=false
  await loadAssignments()
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }

.page-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.15rem; font-weight:800; color:#111827; margin:0 0 .15rem; }
.page-sub    { font-size:.75rem; color:#9ca3af; margin:0; }
.back-btn    { width:2rem; height:2rem; border-radius:.625rem; display:flex; align-items:center; justify-content:center; background:white; border:1px solid #e5e7eb; color:#6b7280; cursor:pointer; transition:background .13s; text-decoration:none; }
.back-btn:hover { background:#f9fafb; }
.status-pill { display:inline-flex; align-items:center; gap:.35rem; font-size:.72rem; font-weight:700; padding:.35rem .75rem; border-radius:9999px; }
.pill-blue   { background:#dbeafe; color:#1e40af; }
.pill-amber  { background:#fef3c7; color:#92400e; }

.main-grid { display:grid; grid-template-columns:1fr; gap:.75rem; }
@media(min-width:1024px) { .main-grid { grid-template-columns:1fr 1fr; align-items:start; } }

.skel-panel { height:28rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; }

.panel { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; display:flex; flex-direction:column; }
.panel-header { display:flex; align-items:center; justify-content:space-between; padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; flex-shrink:0; }
.panel-title  { display:flex; align-items:center; gap:.5rem; font-size:.8rem; font-weight:700; color:#111827; }

.total-bar { display:flex; align-items:center; justify-content:space-between; margin:.75rem 1rem; padding:.625rem 1rem; background:#f9fafb; border-radius:.75rem; }
.total-label { font-size:.75rem; font-weight:700; color:#6b7280; }
.total-value { font-size:1.5rem; font-weight:800; color:#111827; }

.disc-list { flex:1; overflow-y:auto; padding:.25rem 0; }
.disc-row  { display:flex; align-items:center; gap:1rem; padding:.625rem 1.25rem; }
.disc-info { flex:1; min-width:0; display:flex; flex-direction:column; gap:.3rem; }
.disc-name { font-size:.78rem; font-weight:700; color:#374151; }
.progress-row { display:flex; align-items:center; gap:.5rem; }
.prog-bar  { flex:1; height:.2rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.prog-fill { height:100%; border-radius:9999px; transition:width .5s ease; }
.prog-text { font-size:.65rem; color:#9ca3af; flex-shrink:0; }

.quota-ctrl  { display:flex; align-items:center; gap:.25rem; flex-shrink:0; }
.quota-btn   { width:1.75rem; height:1.75rem; border-radius:.5rem; border:1px solid #e5e7eb; background:white; font-size:.875rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .13s; }
.quota-btn:hover:not(:disabled) { background:#f3f4f6; border-color:#d1d5db; }
.quota-btn:disabled { opacity:.4; cursor:not-allowed; }
.quota-input { width:2.5rem; text-align:center; border:1px solid #e5e7eb; border-radius:.5rem; padding:.25rem; font-size:.8rem; font-weight:700; color:#111827; outline:none; }
.quota-input:focus { border-color:#93c5fd; }
.quota-input::-webkit-inner-spin-button, .quota-input::-webkit-outer-spin-button { -webkit-appearance:none; }

.empty-note { font-size:.75rem; color:#9ca3af; text-align:center; padding:2rem 1rem; }

.assign-list { list-style:none; margin:0; padding:0; }
.assign-item { display:flex; align-items:center; gap:.75rem; padding:.75rem 1.25rem; border-bottom:1px solid #f9fafb; }
.assign-item:last-child { border-bottom:none; }
.assign-avatar { width:2rem; height:2rem; border-radius:9999px; font-size:.7rem; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.assign-info { flex:1; min-width:0; }
.assign-name { display:block; font-size:.8rem; font-weight:700; color:#374151; }
.assign-meta { display:block; font-size:.68rem; color:#9ca3af; margin-top:.1rem; }
.del-btn { width:1.5rem; height:1.5rem; border-radius:.375rem; background:none; border:none; cursor:pointer; color:#d1d5db; display:flex; align-items:center; justify-content:center; transition:all .13s; }
.del-btn:hover { color:#ef4444; background:#fef2f2; }

.status-warning { display:flex; align-items:center; gap:.5rem; margin:.5rem 1rem; padding:.625rem .875rem; background:#fefce8; border:1px solid #fde68a; border-radius:.625rem; font-size:.72rem; color:#92400e; line-height:1.4; }
.status-warning strong { font-weight:700; }

/* Buttons */
.btn-primary, .btn-secondary, .btn-cancel {
  display:inline-flex; align-items:center; gap:.4rem;
  border-radius:.625rem; font-size:.75rem; font-weight:700;
  cursor:pointer; white-space:nowrap; transition:all .13s; border:none;
}
.btn-sm { padding:.4rem .875rem; }
.btn-primary  { background:#111827; color:white; padding:.5rem 1rem; } .btn-primary:hover:not(:disabled) { background:#1f2937; } .btn-primary:disabled { opacity:.5; cursor:not-allowed; }
.btn-secondary{ background:white; color:#374151; border:1px solid #e5e7eb; padding:.5rem 1rem; } .btn-secondary:hover:not(:disabled) { background:#f9fafb; } .btn-secondary:disabled { opacity:.5; cursor:not-allowed; }
.btn-cancel   { background:white; color:#6b7280; border:1px solid #e5e7eb; padding:.5rem 1rem; } .btn-cancel:hover { background:#f9fafb; }

/* Field */
.field       { display:flex; flex-direction:column; gap:.375rem; }
.field-label { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.field-select{ padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; background:white; }
.field-select:focus { border-color:#93c5fd; }
.error-msg  { font-size:.72rem; color:#ef4444; font-weight:600; }

/* Modal */
.modal-overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; padding:1rem; background:rgba(0,0,0,.25); backdrop-filter:blur(2px); }
.modal-box { background:white; border-radius:1rem; padding:1.5rem; width:100%; max-width:24rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-title { font-size:1rem; font-weight:800; color:#111827; margin:0; }
.modal-actions { display:flex; gap:.5rem; margin-top:.25rem; }
.card-loading { padding:.75rem 1rem; display:flex; flex-direction:column; gap:.5rem; }
.skel-row { height:2.75rem; background:#f9fafb; border-radius:.625rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*120ms); }
.skel-line { display:inline-block; width:55%; height:.875rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
@keyframes spin { to { transform:rotate(360deg); } }
.spin { animation:spin .8s linear infinite; }
.modal-enter-active { transition:opacity .18s ease; }
.modal-leave-active { transition:opacity .15s ease; }
.modal-enter-from, .modal-leave-to { opacity:0; }
.fade-msg-enter-active, .fade-msg-leave-active { transition:opacity .2s ease; }
.fade-msg-enter-from, .fade-msg-leave-to { opacity:0; }
</style>