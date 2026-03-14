<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/coordenador/professores" class="back-btn">
          <Icon name="lucide:arrow-left" class="w-4 h-4" />
        </NuxtLink>
        <div>
          <h1 class="page-title">Gerenciar professores</h1>
          <p class="page-sub">Cadastrar, editar e vincular turmas/disciplinas</p>
        </div>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Icon name="lucide:plus" class="w-4 h-4" /> Novo professor
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <button class="tab" :class="tab==='professores'?'tab-active':''" @click="tab='professores'">Professores</button>
      <button class="tab" :class="tab==='vinculos'?'tab-active':''" @click="tab='vinculos'">Vínculos turma/disciplina</button>
    </div>

    <!-- Tab: Professores -->
    <div v-if="tab==='professores'" class="fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-if="loading" class="list-col">
        <div v-for="i in 4" :key="i" class="skel-row-lg" :style="`--i:${i}`" />
      </div>
      <div v-else-if="!teachers.length" class="empty-state">
        <Icon name="lucide:briefcase" class="w-10 h-10 text-gray-200" />
        <p>Nenhum professor cadastrado</p>
      </div>
      <div v-else class="list-col">
        <div v-for="(prof, idx) in teachers" :key="prof.id" class="list-card" :style="`--i:${idx}`">
          <div class="prof-avatar" :style="`background:${avatarBg(idx)}20;color:${avatarBg(idx)}`">
            {{ initials(prof.name) }}
          </div>
          <div class="list-info">
            <span class="list-name">{{ prof.name }}</span>
            <span class="list-sub">{{ prof.email }}</span>
          </div>
          <div class="list-actions">
            <button class="icon-btn" title="Editar" @click="openEdit(prof)">
              <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
            </button>
            <button class="icon-btn icon-btn--del" title="Excluir" @click="openDelete(prof)">
              <Icon name="lucide:trash-2" class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Vínculos -->
    <div v-if="tab==='vinculos'" class="fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div class="link-form-card">
        <div class="link-form-title">Novo vínculo</div>
        <div class="link-form-grid">
          <div class="field">
            <label class="field-label">Professor</label>
            <select v-model="linkForm.teacher_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">Turma</label>
            <select v-model="linkForm.class_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">Disciplina</label>
            <select v-model="linkForm.discipline_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <button class="btn-primary link-btn-add"
            :disabled="!linkForm.teacher_id||!linkForm.class_id||!linkForm.discipline_id||savingLink"
            @click="saveLink">
            {{ savingLink ? 'Salvando...' : 'Vincular' }}
          </button>
        </div>
        <p v-if="linkError" class="error-msg mt-1">{{ linkError }}</p>
      </div>

      <div v-if="loading" class="list-col mt-4">
        <div v-for="i in 4" :key="i" class="skel-row-sm" :style="`--i:${i}`" />
      </div>
      <div v-else-if="!teacherSubjects.length" class="empty-state mt-4">
        <Icon name="lucide:link" class="w-10 h-10 text-gray-200" />
        <p>Nenhum vínculo cadastrado</p>
      </div>
      <div v-else class="list-col mt-4">
        <div v-for="(s, idx) in teacherSubjects" :key="s.id" class="list-card" :style="`--i:${idx}`">
          <div class="link-labels">
            <span class="list-name">{{ s.teacher_name }}</span>
            <span class="link-meta">{{ s.class_name }} · {{ s.discipline_name }}</span>
          </div>
          <button class="icon-btn icon-btn--del" @click="deleteLink(s.id)">
            <Icon name="lucide:x" class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: criar/editar professor -->
    <Transition name="modal">
      <div v-if="showProfModal" class="modal-overlay" @click.self="closeProfModal">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingProf ? 'Editar professor' : 'Novo professor' }}</h3>
          <div class="field">
            <label class="field-label">Nome</label>
            <input v-model="profForm.name" placeholder="Nome completo" class="field-input" />
          </div>
          <div class="field">
            <label class="field-label">E-mail</label>
            <input v-model="profForm.email" type="email" placeholder="email@escola.edu.br" class="field-input" />
          </div>
          <div v-if="!editingProf" class="field">
            <label class="field-label">Senha inicial</label>
            <input v-model="profForm.password" type="password" placeholder="Mínimo 6 caracteres" class="field-input" />
          </div>
          <p v-if="profError" class="error-msg">{{ profError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeProfModal">Cancelar</button>
            <button class="btn-primary" :disabled="savingProf" @click="saveProf">
              {{ savingProf ? 'Salvando...' : editingProf ? 'Salvar' : 'Criar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: excluir professor -->
    <Transition name="modal">
      <div v-if="showDelete" class="modal-overlay" @click.self="showDelete=false">
        <div class="modal-box">
          <div class="modal-icon-wrap bg-red-50">
            <Icon name="lucide:trash-2" class="w-5 h-5 text-red-500" />
          </div>
          <h3 class="modal-title">Excluir {{ deletingProf?.name }}?</h3>
          <p class="modal-body">Esta ação não pode ser desfeita.</p>
          <p v-if="deleteError" class="error-msg">{{ deleteError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showDelete=false">Cancelar</button>
            <button class="btn-danger" :disabled="deleting" @click="confirmDelete">
              {{ deleting ? 'Excluindo...' : 'Excluir' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get, post, patch, delete: del } = useApi()
const mounted = ref(false)
const tab     = ref('professores')

const teachers        = ref<any[]>([])
const teacherSubjects = ref<any[]>([])
const classes         = ref<any[]>([])
const disciplines     = ref<any[]>([])
const loading         = ref(true)

const showProfModal = ref(false); const profError   = ref(''); const savingProf = ref(false)
const showDelete    = ref(false); const deleteError = ref(''); const deleting   = ref(false)
const savingLink    = ref(false); const linkError   = ref('')
const editingProf   = ref<any>(null); const deletingProf = ref<any>(null)
const profForm = reactive({ name:'', email:'', password:'' })
const linkForm = reactive({ teacher_id:'', class_id:'', discipline_id:'' })

const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4']
function avatarBg(idx: number) { return COLORS[idx % COLORS.length] }
function initials(name: string) { return name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0]?.toUpperCase()).join('') }

function openCreate() { editingProf.value=null; profForm.name=''; profForm.email=''; profForm.password=''; profError.value=''; showProfModal.value=true }
function openEdit(prof: any) { editingProf.value=prof; profForm.name=prof.name; profForm.email=prof.email; profForm.password=''; profError.value=''; showProfModal.value=true }
function openDelete(prof: any) { deletingProf.value=prof; deleteError.value=''; showDelete.value=true }
function closeProfModal() { showProfModal.value=false; editingProf.value=null }

async function saveProf() {
  savingProf.value=true; profError.value=''
  try {
    if (editingProf.value) {
      const updated = await patch<any>(`/auth/users/${editingProf.value.id}`, { name:profForm.name, email:profForm.email })
      const idx = teachers.value.findIndex(t=>t.id===editingProf.value.id)
      if (idx!==-1) teachers.value[idx]={ ...teachers.value[idx], ...updated }
    } else {
      const created = await post<any>('/auth/users', { name:profForm.name, email:profForm.email, password:profForm.password, role:'TEACHER' })
      teachers.value.push(created)
    }
    closeProfModal()
  } catch (e:any) { profError.value=e?.data?.detail??e?.message??'Erro ao salvar.' } finally { savingProf.value=false }
}

async function confirmDelete() {
  if (!deletingProf.value) return
  deleting.value=true; deleteError.value=''
  try {
    await del(`/auth/users/${deletingProf.value.id}`)
    teachers.value=teachers.value.filter(t=>t.id!==deletingProf.value.id)
    showDelete.value=false
  } catch (e:any) { deleteError.value=e?.data?.detail??'Erro ao excluir.' } finally { deleting.value=false }
}

async function saveLink() {
  savingLink.value=true; linkError.value=''
  try {
    const created = await post<any>('/school/teacher-subjects', {
      teacher_user_id:Number(linkForm.teacher_id), class_id:Number(linkForm.class_id), discipline_id:Number(linkForm.discipline_id)
    })
    const t = teachers.value.find(t=>t.id===created.teacher_user_id)
    const c = classes.value.find(c=>c.id===created.class_id)
    const d = disciplines.value.find(d=>d.id===created.discipline_id)
    teacherSubjects.value.push({ ...created, teacher_name:t?.name, class_name:c?.name, discipline_name:d?.name })
    linkForm.teacher_id=''; linkForm.class_id=''; linkForm.discipline_id=''
  } catch (e:any) { linkError.value=e?.data?.detail??e?.message??'Erro ao vincular.' } finally { savingLink.value=false }
}

async function deleteLink(id: number) {
  try { await del(`/school/teacher-subjects/${id}`); teacherSubjects.value=teacherSubjects.value.filter(s=>s.id!==id) } catch {}
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [tRes,sRes,cRes,dRes] = await Promise.allSettled([
    get<any[]>('/school/teachers'), get<any[]>('/school/teacher-subjects'),
    get<any[]>('/school/classes'), get<any[]>('/disciplines/'),
  ])
  if (tRes.status==='fulfilled') teachers.value        = tRes.value
  if (cRes.status==='fulfilled') classes.value         = cRes.value
  if (dRes.status==='fulfilled') disciplines.value     = dRes.value
  if (sRes.status==='fulfilled') {
    // Enrich with names
    const subjects = sRes.value
    for (const s of subjects) {
      const t = teachers.value.find(t=>t.id===s.teacher_user_id)
      const c = classes.value.find(c=>c.id===s.class_id)
      const d = disciplines.value.find(d=>d.id===s.discipline_id)
      s.teacher_name=t?.name??`Prof #${s.teacher_user_id}`
      s.class_name=c?.name??`Turma #${s.class_id}`
      s.discipline_name=d?.name??`Disc. #${s.discipline_id}`
    }
    teacherSubjects.value = subjects
  }
  loading.value=false
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.back-btn    { width:2rem; height:2rem; border-radius:.625rem; display:flex; align-items:center; justify-content:center; background:white; border:1px solid #e5e7eb; color:#6b7280; cursor:pointer; text-decoration:none; transition:background .13s; flex-shrink:0; }
.back-btn:hover { background:#f9fafb; }

.tabs { display:flex; gap:.25rem; background:#f3f4f6; padding:.25rem; border-radius:.875rem; width:fit-content; }
.tab { padding:.4rem 1rem; border-radius:.625rem; font-size:.78rem; font-weight:700; border:none; background:none; cursor:pointer; color:#6b7280; transition:all .13s; }
.tab-active { background:white; color:#111827; box-shadow:0 1px 4px rgba(0,0,0,.06); }

.list-col { display:flex; flex-direction:column; gap:.5rem; }
.skel-row-lg { height:4.5rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*70ms); }
.skel-row-sm { height:3.25rem; background:white; border:1px solid #f3f4f6; border-radius:.875rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*60ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:3rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.mt-4 { margin-top:1rem; }

.list-card { display:flex; align-items:center; gap:1rem; padding:.875rem 1.25rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*45ms); transition:border-color .13s; }
.list-card:hover { border-color:#e5e7eb; }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.prof-avatar { width:2.5rem; height:2.5rem; border-radius:9999px; font-size:.75rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.list-info   { flex:1; min-width:0; display:flex; flex-direction:column; gap:.1rem; }
.list-name   { font-size:.875rem; font-weight:700; color:#111827; }
.list-sub    { font-size:.7rem; color:#9ca3af; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.list-actions { display:flex; gap:.375rem; }
.icon-btn    { width:2rem; height:2rem; border-radius:.5rem; border:1px solid #e5e7eb; background:white; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#9ca3af; transition:all .13s; }
.icon-btn:hover      { background:#f9fafb; color:#374151; border-color:#d1d5db; }
.icon-btn--del:hover { background:#fef2f2; color:#ef4444; border-color:#fecaca; }

.link-form-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1.25rem; display:flex; flex-direction:column; gap:.875rem; }
.link-form-title { font-size:.8rem; font-weight:700; color:#111827; }
.link-form-grid  { display:grid; grid-template-columns:1fr; gap:.75rem; }
@media(min-width:640px) { .link-form-grid { grid-template-columns:1fr 1fr 1fr auto; align-items:end; } }
.link-btn-add { padding:.55rem 1.25rem; align-self:end; }
.link-labels { flex:1; min-width:0; }
.link-meta   { display:block; font-size:.7rem; color:#9ca3af; margin-top:.1rem; }

/* Buttons */
.btn-primary,.btn-cancel,.btn-danger { display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1rem; font-size:.78rem; font-weight:700; border-radius:.75rem; cursor:pointer; white-space:nowrap; transition:all .13s; border:none; text-decoration:none; }
.btn-primary  { background:#111827; color:white; } .btn-primary:hover:not(:disabled) { background:#1f2937; } .btn-primary:disabled { opacity:.5; cursor:not-allowed; }
.btn-cancel   { background:white; color:#6b7280; border:1px solid #e5e7eb; } .btn-cancel:hover { background:#f9fafb; }
.btn-danger   { background:#ef4444; color:white; } .btn-danger:hover:not(:disabled) { background:#dc2626; }

/* Field */
.field       { display:flex; flex-direction:column; gap:.375rem; }
.field-label { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.field-input { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; }
.field-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.field-select { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; background:white; }
.error-msg  { font-size:.72rem; color:#ef4444; font-weight:600; }

/* Modal */
.modal-overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; padding:1rem; background:rgba(0,0,0,.25); backdrop-filter:blur(2px); }
.modal-box { background:white; border-radius:1rem; padding:1.5rem; width:100%; max-width:22rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-title { font-size:1rem; font-weight:800; color:#111827; margin:0; }
.modal-body  { font-size:.8rem; color:#6b7280; margin:0; line-height:1.5; }
.modal-actions { display:flex; gap:.5rem; }
.modal-icon-wrap { width:2.5rem; height:2.5rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.modal-enter-active { transition:opacity .18s ease; } .modal-leave-active { transition:opacity .15s ease; }
.modal-enter-from, .modal-leave-to { opacity:0; }
</style>