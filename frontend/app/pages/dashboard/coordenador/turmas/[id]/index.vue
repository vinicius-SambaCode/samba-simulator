<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/coordenador/turmas" class="back-btn">
          <Icon name="lucide:arrow-left" class="w-4 h-4" />
        </NuxtLink>
        <div>
          <h1 class="page-title">
            <span v-if="loading" class="skel-line" />
            <span v-else>Turma {{ turma?.name }}</span>
          </h1>
          <p class="page-sub">
            <span v-if="!loading">{{ students.length }} aluno{{ students.length!==1?'s':'' }} · {{ disciplines.length }} disciplina{{ disciplines.length!==1?'s':'' }}</span>
            <span v-else class="skel-line skel-line--sm" />
          </p>
        </div>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button class="btn-secondary" @click="showImportModal = true">
          <Icon name="lucide:upload" class="w-4 h-4" /> CSV
        </button>
        <button class="btn-secondary" @click="showAddStudent = true">
          <Icon name="lucide:user-plus" class="w-4 h-4" /> Aluno
        </button>
        <button class="btn-primary" @click="showAddDisc = true">
          <Icon name="lucide:plus" class="w-4 h-4" /> Disciplina
        </button>
      </div>
    </div>

    <div class="main-grid fade-in" :class="{ ready: mounted }" style="--d:.06s">

      <!-- Disciplinas -->
      <div class="card">
        <div class="card-header">
          <div class="card-title"><Icon name="lucide:book-open" class="w-4 h-4 text-gray-400" /> Disciplinas</div>
          <span class="count-badge">{{ disciplines.length }}</span>
        </div>
        <div v-if="loading" class="card-loading">
          <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="!disciplines.length" class="card-empty">
          <Icon name="lucide:book-open" class="w-7 h-7 text-gray-200" />
          <p>Nenhuma disciplina vinculada</p>
          <button class="link-btn" @click="showAddDisc = true">Adicionar disciplina →</button>
        </div>
        <ul v-else class="item-list">
          <li v-for="d in disciplines" :key="d.id" class="item-row">
            <div class="item-icon bg-indigo-50">
              <Icon name="lucide:book-open" class="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <span class="item-label">{{ d.name }}</span>
            <button class="del-btn" @click="removeDisc(d.id)" title="Remover">
              <Icon name="lucide:x" class="w-3.5 h-3.5" />
            </button>
          </li>
        </ul>
      </div>

      <!-- Alunos -->
      <div class="card">
        <div class="card-header">
          <div class="card-title"><Icon name="lucide:users" class="w-4 h-4 text-gray-400" /> Alunos</div>
          <span class="count-badge">{{ students.length }}</span>
        </div>

        <div class="card-search">
          <Icon name="lucide:search" class="search-icon" />
          <input v-model="busca" placeholder="Buscar por nome ou RA..." class="search-input" />
          <button v-if="busca" class="search-clear" @click="busca = ''">
            <Icon name="lucide:x" class="w-3.5 h-3.5" />
          </button>
        </div>

        <div v-if="loading" class="card-loading">
          <div v-for="i in 4" :key="i" class="skel-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="!alunosFiltrados.length" class="card-empty">
          <Icon name="lucide:users" class="w-7 h-7 text-gray-200" />
          <p>{{ busca ? 'Nenhum aluno encontrado' : 'Nenhum aluno cadastrado' }}</p>
          <button v-if="!busca" class="link-btn" @click="showAddStudent = true">Adicionar aluno →</button>
        </div>
        <ul v-else class="item-list student-list">
          <li v-for="s in alunosFiltrados" :key="s.id" class="item-row">
            <div class="student-avatar">{{ initials(s.name) }}</div>
            <div class="student-info">
              <span class="item-label">{{ s.name }}</span>
              <span class="student-ra">RA {{ s.ra }}</span>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Modal adicionar disciplina -->
    <Transition name="modal">
      <div v-if="showAddDisc" class="modal-overlay" @click.self="showAddDisc = false">
        <div class="modal-box">
          <h3 class="modal-title">Adicionar disciplina</h3>
          <div class="field">
            <label class="field-label">Disciplina</label>
            <select v-model="discForm.discipline_id" class="field-select">
              <option value="">Selecione...</option>
              <option v-for="d in discOptions" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <p v-if="discError" class="error-msg">{{ discError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showAddDisc = false">Cancelar</button>
            <button class="btn-primary" :disabled="!discForm.discipline_id || savingDisc" @click="addDisc">
              {{ savingDisc ? 'Adicionando...' : 'Adicionar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal adicionar aluno -->
    <Transition name="modal">
      <div v-if="showAddStudent" class="modal-overlay" @click.self="showAddStudent = false">
        <div class="modal-box">
          <h3 class="modal-title">Adicionar aluno</h3>
          <div class="field">
            <label class="field-label">Nome completo</label>
            <input v-model="studentForm.name" placeholder="Nome do aluno" class="field-input" />
          </div>
          <div class="field">
            <label class="field-label">RA</label>
            <input v-model="studentForm.ra" placeholder="Registro do Aluno" class="field-input" />
          </div>
          <p v-if="studentError" class="error-msg">{{ studentError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showAddStudent = false">Cancelar</button>
            <button class="btn-primary" :disabled="!studentForm.name || !studentForm.ra || savingStudent" @click="addStudent">
              {{ savingStudent ? 'Salvando...' : 'Adicionar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal importar CSV -->
    <Transition name="modal">
      <div v-if="showImportModal" class="modal-overlay" @click.self="closeImport">
        <div class="modal-box">
          <h3 class="modal-title">Importar alunos via CSV</h3>
          <div class="drop-zone"
            :class="isDragging ? 'drop-zone--drag' : csvFile ? 'drop-zone--ok' : ''"
            @dragover.prevent="isDragging=true" @dragleave="isDragging=false" @drop.prevent="onDrop"
            @click="($refs.csvInput as HTMLInputElement).click()">
            <input ref="csvInput" type="file" accept=".csv" class="hidden" @change="onFileChange" />
            <Icon :name="csvFile ? 'lucide:file-check' : 'lucide:upload-cloud'" class="w-8 h-8"
              :class="csvFile ? 'text-emerald-400' : 'text-gray-300'" />
            <span class="drop-label">{{ csvFile ? csvFile.name : 'Arraste ou clique para selecionar' }}</span>
          </div>
          <div v-if="importResult" class="result-box" :class="importResult.error ? 'result-box--err' : 'result-box--ok'">
            {{ importResult.message }}
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeImport">Fechar</button>
            <button class="btn-primary" :disabled="!csvFile || importing" @click="importCsv">
              {{ importing ? 'Importando...' : 'Importar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route   = useRoute()
const { get, post, delete: del } = useApi()
const classId = computed(() => Number(route.params.id))
const mounted = ref(false)

const turma       = ref<any>(null)
const students    = ref<any[]>([])
const disciplines = ref<any[]>([])
const allDiscs    = ref<any[]>([])
const loading     = ref(true)
const busca       = ref('')

const showAddDisc     = ref(false); const discError    = ref(''); const savingDisc    = ref(false)
const showAddStudent  = ref(false); const studentError = ref(''); const savingStudent = ref(false)
const showImportModal = ref(false); const importResult = ref<any>(null); const importing = ref(false)

const discForm    = reactive({ discipline_id: '' })
const studentForm = reactive({ name: '', ra: '' })
const csvFile     = ref<File | null>(null)
const isDragging  = ref(false)

const alunosFiltrados = computed(() => {
  if (!busca.value) return students.value
  const q = busca.value.toLowerCase()
  return students.value.filter(s => s.name.toLowerCase().includes(q) || s.ra.toLowerCase().includes(q))
})
const discOptions = computed(() => {
  const ids = new Set(disciplines.value.map(d => d.id))
  return allDiscs.value.filter(d => !ids.has(d.id))
})

function initials(name: string) {
  return name.split(' ').filter(Boolean).slice(0, 2).map(w => w[0]?.toUpperCase()).join('')
}
function closeImport() { showImportModal.value = false; csvFile.value = null; importResult.value = null; isDragging.value = false }
function onFileChange(e: Event) { const f = (e.target as HTMLInputElement).files?.[0]; if (f) { csvFile.value = f; importResult.value = null } }
function onDrop(e: DragEvent) { isDragging.value = false; const f = e.dataTransfer?.files?.[0]; if (f?.name.endsWith('.csv')) { csvFile.value = f; importResult.value = null } }

async function addDisc() {
  savingDisc.value = true; discError.value = ''
  try {
    await post(`/school/classes/${classId.value}/disciplines`, { discipline_id: Number(discForm.discipline_id) })
    disciplines.value = await get<any[]>(`/school/classes/${classId.value}/disciplines`)
    showAddDisc.value = false; discForm.discipline_id = ''
  } catch (e: any) { discError.value = e.message ?? 'Erro ao adicionar.' } finally { savingDisc.value = false }
}
async function removeDisc(discId: number) {
  try {
    await del(`/school/classes/${classId.value}/disciplines/${discId}`)
    disciplines.value = disciplines.value.filter(d => d.id !== discId)
  } catch {}
}
async function addStudent() {
  savingStudent.value = true; studentError.value = ''
  try {
    const st = await post<any>('/school/students/', { name: studentForm.name, ra: studentForm.ra, class_id: classId.value })
    students.value.push(st)
    showAddStudent.value = false; studentForm.name = ''; studentForm.ra = ''
  } catch (e: any) { studentError.value = e.message ?? 'Erro ao adicionar aluno.' } finally { savingStudent.value = false }
}
async function importCsv() {
  if (!csvFile.value) return
  importing.value = true; importResult.value = null
  try {
    const fd = new FormData(); fd.append('file', csvFile.value)
    const { upload } = useApi()
    const res = await upload<any>(`/school/students/import?class_id=${classId.value}&dry_run=false`, fd)
    importResult.value = { error: false, message: `${res.created} criado(s), ${res.updated} atualizado(s).` }
    students.value = await get<any[]>(`/school/students/?class_id=${classId.value}`)
    csvFile.value = null
  } catch (e: any) { importResult.value = { error: true, message: e.message ?? 'Erro ao importar.' } } finally { importing.value = false }
}

onMounted(async () => {
  await nextTick(); setTimeout(() => { mounted.value = true }, 30)
  const [turmaRes, studentsRes, discRes, allDiscRes] = await Promise.allSettled([
    get<any>(`/school/classes/${classId.value}`),
    get<any[]>(`/school/students/?class_id=${classId.value}`),
    get<any[]>(`/school/classes/${classId.value}/disciplines`),
    get<any[]>('/disciplines/'),
  ])
  if (turmaRes.status    === 'fulfilled') turma.value       = turmaRes.value
  if (studentsRes.status === 'fulfilled') students.value    = studentsRes.value
  if (discRes.status     === 'fulfilled') disciplines.value = discRes.value
  if (allDiscRes.status  === 'fulfilled') allDiscs.value    = allDiscRes.value
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
.back-btn    { width:2rem; height:2rem; border-radius:.625rem; display:flex; align-items:center; justify-content:center; background:white; border:1px solid #e5e7eb; color:#6b7280; cursor:pointer; text-decoration:none; transition:background .13s; flex-shrink:0; }
.back-btn:hover { background:#f9fafb; }
.skel-line   { display:inline-block; width:10rem; height:.875rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }
.skel-line--sm { width:7rem; height:.75rem; }

.main-grid { display:grid; grid-template-columns:1fr; gap:.75rem; }
@media(min-width:768px) { .main-grid { grid-template-columns:280px 1fr; align-items:start; } }

.card { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; }
.card-header { display:flex; align-items:center; justify-content:space-between; padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; }
.card-title  { display:flex; align-items:center; gap:.5rem; font-size:.8rem; font-weight:700; color:#111827; }
.count-badge { font-size:.65rem; font-weight:700; padding:.1rem .4rem; border-radius:9999px; background:#f3f4f6; color:#6b7280; }
.card-loading { padding:.75rem 1rem; display:flex; flex-direction:column; gap:.5rem; }
.skel-row { height:2.75rem; background:#f9fafb; border-radius:.625rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*100ms); }
.card-empty { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:2.5rem 1rem; text-align:center; }
.card-empty p { font-size:.78rem; color:#9ca3af; margin:0; }
.card-search { padding:.625rem 1rem; border-bottom:1px solid #f9fafb; position:relative; }
.search-icon  { position:absolute; left:1.75rem; top:50%; transform:translateY(-50%); width:.875rem; height:.875rem; color:#d1d5db; }
.search-input { width:100%; padding:.5rem .75rem .5rem 2.25rem; border:1px solid #f3f4f6; border-radius:.625rem; font-size:.78rem; background:#fafafa; outline:none; transition:border-color .13s; }
.search-input:focus { border-color:#93c5fd; background:white; }
.search-clear { position:absolute; right:1.5rem; top:50%; transform:translateY(-50%); color:#d1d5db; }
.search-clear:hover { color:#6b7280; }

.item-list  { list-style:none; margin:0; padding:0; }
.item-row   { display:flex; align-items:center; gap:.75rem; padding:.7rem 1.25rem; border-bottom:1px solid #f9fafb; }
.item-row:last-child { border-bottom:none; }
.item-icon  { width:1.875rem; height:1.875rem; border-radius:.5rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.item-label { flex:1; font-size:.8rem; font-weight:600; color:#374151; }
.del-btn    { width:1.5rem; height:1.5rem; border-radius:.375rem; background:none; border:none; cursor:pointer; color:#d1d5db; display:flex; align-items:center; justify-content:center; transition:all .13s; }
.del-btn:hover { color:#ef4444; background:#fef2f2; }
.link-btn   { font-size:.72rem; font-weight:600; color:#3b82f6; background:none; border:none; cursor:pointer; }
.link-btn:hover { color:#2563eb; }

.student-list { max-height:32rem; overflow-y:auto; }
.student-avatar { width:2rem; height:2rem; border-radius:9999px; background:#e0e7ff; color:#3730a3; font-size:.65rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.student-info { flex:1; min-width:0; display:flex; flex-direction:column; gap:.1rem; }
.student-ra { font-size:.65rem; color:#9ca3af; }

/* Buttons */
.btn-primary,.btn-secondary,.btn-cancel {
  display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1rem;
  font-size:.78rem; font-weight:700; border-radius:.75rem; cursor:pointer;
  white-space:nowrap; transition:all .13s; border:none; text-decoration:none;
}
.btn-primary  { background:#111827; color:white; } .btn-primary:hover:not(:disabled) { background:#1f2937; } .btn-primary:disabled { opacity:.5; cursor:not-allowed; }
.btn-secondary{ background:white; color:#374151; border:1px solid #e5e7eb; } .btn-secondary:hover { background:#f9fafb; }
.btn-cancel   { background:white; color:#6b7280; border:1px solid #e5e7eb; } .btn-cancel:hover { background:#f9fafb; }

/* Modal */
.modal-overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; padding:1rem; background:rgba(0,0,0,.25); backdrop-filter:blur(2px); }
.modal-box { background:white; border-radius:1rem; padding:1.5rem; width:100%; max-width:22rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-title  { font-size:1rem; font-weight:800; color:#111827; margin:0; }
.modal-actions { display:flex; gap:.5rem; }
.field        { display:flex; flex-direction:column; gap:.375rem; }
.field-label  { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.field-input  { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; }
.field-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.field-select { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; background:white; }
.error-msg    { font-size:.72rem; color:#ef4444; font-weight:600; }
.drop-zone    { border:2px dashed #e5e7eb; border-radius:.875rem; padding:2rem 1rem; display:flex; flex-direction:column; align-items:center; gap:.625rem; cursor:pointer; transition:all .15s; }
.drop-zone:hover,.drop-zone--drag { border-color:#60a5fa; background:#eff6ff; }
.drop-zone--ok { border-color:#34d399; background:#f0fdf4; }
.drop-label   { font-size:.78rem; color:#6b7280; text-align:center; }
.result-box   { padding:.625rem .875rem; border-radius:.625rem; font-size:.78rem; font-weight:600; }
.result-box--ok  { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; }
.result-box--err { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.modal-enter-active { transition:opacity .18s ease; } .modal-leave-active { transition:opacity .15s ease; }
.modal-enter-from, .modal-leave-to { opacity:0; }
</style>