<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Turmas</h1>
        <p class="page-sub">
          <span v-if="loading" class="skel-line" />
          <span v-else>{{ classes.length }} turma{{ classes.length!==1?'s':'' }} · {{ totalAlunos }} aluno{{ totalAlunos!==1?'s':'' }}</span>
        </p>
      </div>
      <div class="flex gap-2">
        <button class="btn-secondary" @click="showImportModal = true">
          <Icon name="lucide:upload" class="w-4 h-4" /> <span class="hidden sm:inline">Importar CSV</span>
        </button>
        <button class="btn-primary" @click="showModal = true">
          <Icon name="lucide:plus" class="w-4 h-4" /> Nova turma
        </button>
      </div>
    </div>

    <!-- Resumo rápido -->
    <div v-if="!loading && classes.length" class="summary fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <div v-for="r in resumoRapido" :key="r.label" class="summary-item">
        <span class="summary-dot" :class="r.dot" />
        <span><strong>{{ r.value }}</strong> {{ r.label }}</span>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="turmas-grid fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="i in 8" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!classes.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:school" class="w-10 h-10 text-gray-200" />
      <p class="empty-title">Nenhuma turma cadastrada</p>
      <p class="empty-sub">Crie turmas para começar a organizar os alunos</p>
      <div class="flex gap-2 mt-3">
        <button class="btn-secondary" @click="showImportModal = true">
          <Icon name="lucide:upload" class="w-4 h-4" /> Importar CSV
        </button>
        <button class="btn-primary" @click="showModal = true">
          <Icon name="lucide:plus" class="w-4 h-4" /> Criar turma
        </button>
      </div>
    </div>

    <!-- Agrupado por nível -->
    <template v-else>
      <!-- Ensino Médio -->
      <section v-if="classesPorNivel.medio.length" class="fade-in" :class="{ ready: mounted }" style="--d:.08s">
        <div class="level-header">
          <span class="level-bar bg-blue-500" />
          <span class="level-label">Ensino Médio</span>
          <span class="level-count">{{ classesPorNivel.medio.length }} turmas</span>
        </div>
        <div class="turmas-grid">
          <div v-for="(cls, idx) in classesPorNivel.medio" :key="cls.id"
            class="turma-card group" :style="`--i:${idx}`">
            <div class="turma-actions">
              <button class="action-btn" title="Clonar disciplinas" @click.prevent="openClone(cls)">
                <Icon name="lucide:copy" class="w-3.5 h-3.5 text-violet-500" />
              </button>
              <button class="action-btn action-btn--del" title="Excluir" @click.prevent="askDelete(cls)">
                <Icon name="lucide:trash-2" class="w-3.5 h-3.5 text-red-400" />
              </button>
            </div>
            <NuxtLink :to="`/dashboard/coordenador/turmas/${cls.id}`" class="turma-link">
              <div class="turma-badge" :class="coresMedio[idx % coresMedio.length]">{{ cls.name }}</div>
              <div class="turma-info">
                <span class="turma-disc">{{ disciplineCount[cls.id]??0 }} disciplina{{ (disciplineCount[cls.id]??0)!==1?'s':'' }}</span>
                <span class="turma-alunos">
                  <span v-if="loadingStudents[cls.id]" class="skel-tiny" />
                  <span v-else>{{ students[cls.id]?.length??0 }} aluno{{ (students[cls.id]?.length??0)!==1?'s':'' }}</span>
                </span>
              </div>
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- Ensino Fundamental -->
      <section v-if="classesPorNivel.fundamental.length" class="fade-in" :class="{ ready: mounted }" style="--d:.12s">
        <div class="level-header">
          <span class="level-bar bg-emerald-500" />
          <span class="level-label">Ensino Fundamental</span>
          <span class="level-count">{{ classesPorNivel.fundamental.length }} turmas</span>
        </div>
        <div class="turmas-grid">
          <div v-for="(cls, idx) in classesPorNivel.fundamental" :key="cls.id"
            class="turma-card group" :style="`--i:${idx}`">
            <div class="turma-actions">
              <button class="action-btn" title="Clonar disciplinas" @click.prevent="openClone(cls)">
                <Icon name="lucide:copy" class="w-3.5 h-3.5 text-violet-500" />
              </button>
              <button class="action-btn action-btn--del" title="Excluir" @click.prevent="askDelete(cls)">
                <Icon name="lucide:trash-2" class="w-3.5 h-3.5 text-red-400" />
              </button>
            </div>
            <NuxtLink :to="`/dashboard/coordenador/turmas/${cls.id}`" class="turma-link">
              <div class="turma-badge" :class="coresFund[idx % coresFund.length]">{{ cls.name }}</div>
              <div class="turma-info">
                <span class="turma-disc">{{ disciplineCount[cls.id]??0 }} disciplina{{ (disciplineCount[cls.id]??0)!==1?'s':'' }}</span>
                <span class="turma-alunos">
                  <span v-if="loadingStudents[cls.id]" class="skel-tiny" />
                  <span v-else>{{ students[cls.id]?.length??0 }} aluno{{ (students[cls.id]?.length??0)!==1?'s':'' }}</span>
                </span>
              </div>
            </NuxtLink>
          </div>
        </div>
      </section>
    </template>

    <!-- Modal nova turma -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-box">
          <h3 class="modal-title">Nova turma</h3>
          <div class="field">
            <label class="field-label">Nível</label>
            <div class="toggle-group">
              <button class="toggle-btn" :class="novoForm.nivel==='medio'?'toggle-btn--on':'toggle-btn--off'" @click="selectNivel('medio')">Ensino Médio</button>
              <button class="toggle-btn" :class="novoForm.nivel==='fundamental'?'toggle-btn--on':'toggle-btn--off'" @click="selectNivel('fundamental')">Ens. Fundamental</button>
            </div>
          </div>
          <div v-if="novoForm.nivel" class="field">
            <label class="field-label">Série</label>
            <div class="opt-grid">
              <button v-for="g in gradesFiltradas" :key="g.id"
                class="opt-btn" :class="novoForm.grade_id===g.id?'opt-btn--on':''"
                @click="novoForm.grade_id=g.id">{{ g.label }}</button>
            </div>
          </div>
          <div v-if="novoForm.grade_id" class="field">
            <label class="field-label">Turma</label>
            <div class="opt-grid">
              <button v-for="s in sections" :key="s.id"
                class="opt-btn" :class="novoForm.section_id===s.id?'opt-btn--on':''"
                @click="novoForm.section_id=s.id">{{ s.label }}</button>
            </div>
          </div>
          <div v-if="previewNome" class="preview-box">
            Turma: <strong>{{ previewNome }}</strong>
          </div>
          <p v-if="modalError" class="error-msg">{{ modalError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeModal">Cancelar</button>
            <button class="btn-primary" :disabled="!novoForm.grade_id||!novoForm.section_id||saving" @click="createClass">
              {{ saving ? 'Criando...' : 'Criar turma' }}
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
          <div class="field">
            <label class="field-label">Turma</label>
            <select v-model="importForm.class_id" class="field-select">
              <option value="">Selecione a turma...</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">Arquivo CSV</label>
            <div class="drop-zone"
              :class="isDragging?'drop-zone--drag':csvFile?'drop-zone--ok':''"
              @dragover.prevent="isDragging=true" @dragleave="isDragging=false" @drop.prevent="onDrop"
              @click="$refs.csvInput.click()">
              <input ref="csvInput" type="file" accept=".csv" class="hidden" @change="onFileChange" />
              <Icon v-if="!csvFile" name="lucide:upload-cloud" class="w-8 h-8 text-gray-300" />
              <Icon v-else name="lucide:file-check" class="w-8 h-8 text-emerald-400" />
              <span class="drop-label">{{ csvFile ? csvFile.name : 'Arraste ou clique para selecionar' }}</span>
            </div>
          </div>
          <div v-if="importResult" class="result-box" :class="importResult.error?'result-box--err':'result-box--ok'">
            {{ importResult.message }}
          </div>
          <p v-if="importResult?.error === false" class="field-hint text-center">CSV importado com sucesso!</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeImport">Fechar</button>
            <button class="btn-primary" :disabled="!csvFile||!importForm.class_id||importing" @click="importCsv">
              {{ importing ? 'Importando...' : 'Importar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal clonar disciplinas -->
    <Transition name="modal">
      <div v-if="showCloneModal" class="modal-overlay" @click.self="closeClone">
        <div class="modal-box modal-box--wide">
          <h3 class="modal-title">Clonar disciplinas de <strong>{{ cloneSource?.name }}</strong></h3>
          <p class="modal-sub">{{ cloneSourceDiscs.length }} disciplina(s) serão copiadas para as turmas selecionadas.</p>
          <div class="clone-grid">
            <label v-for="cls in [...cloneTargetOptions.medio,...cloneTargetOptions.fundamental]" :key="cls.id"
              class="clone-item">
              <input type="checkbox" :value="cls.id" v-model="cloneTargets" class="accent-blue-600" />
              <span>{{ cls.name }}</span>
            </label>
          </div>
          <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input type="checkbox" v-model="cloneOverwrite" class="accent-blue-600" />
            Sobrescrever disciplinas existentes
          </label>
          <div v-if="cloneResult" class="result-box" :class="cloneResult.error?'result-box--err':'result-box--ok'">
            {{ cloneResult.message }}
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeClone">Fechar</button>
            <button class="btn-primary" :disabled="!cloneTargets.length||cloning" @click="executeClone">
              {{ cloning ? 'Clonando...' : `Clonar para ${cloneTargets.length} turma${cloneTargets.length!==1?'s':''}` }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal excluir -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal=false">
        <div class="modal-box">
          <div class="modal-icon-wrap bg-red-50">
            <Icon name="lucide:trash-2" class="w-5 h-5 text-red-500" />
          </div>
          <h3 class="modal-title">Excluir turma {{ deleteTarget?.name }}?</h3>
          <p class="modal-body">Esta ação não pode ser desfeita. Todos os vínculos serão removidos.</p>
          <p v-if="deleteError" class="error-msg">{{ deleteError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showDeleteModal=false">Cancelar</button>
            <button class="btn-danger" :disabled="deleting" @click="confirmDelete">
              {{ deleting ? 'Excluindo...' : 'Sim, excluir' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get, post, delete: del } = useApi()
const mounted = ref(false)

const classes         = ref<any[]>([])
const grades          = ref<any[]>([])
const sections        = ref<any[]>([])
const students        = ref<Record<number,any[]>>({})
const disciplineCount = ref<Record<number,number>>({})
const loadingStudents = ref<Record<number,boolean>>({})
const loading         = ref(true)

// Modals
const showModal       = ref(false); const modalError   = ref(''); const saving  = ref(false)
const showImportModal = ref(false); const importResult = ref<any>(null); const importing = ref(false)
const showCloneModal  = ref(false); const cloneResult  = ref<any>(null); const cloning   = ref(false)
const showDeleteModal = ref(false); const deleteError  = ref('');         const deleting  = ref(false)

const novoForm    = reactive<{ nivel:string; grade_id:number|null; section_id:number|null }>({ nivel:'', grade_id:null, section_id:null })
const importForm  = reactive({ class_id:'' })
const csvFile     = ref<File|null>(null)
const isDragging  = ref(false)
const cloneSource = ref<any>(null); const cloneSourceDiscs = ref<any[]>([]); const cloneTargets = ref<number[]>([]); const cloneOverwrite = ref(false)
const deleteTarget= ref<any>(null)

const coresMedio = ['bg-blue-500','bg-indigo-500','bg-violet-500','bg-sky-500','bg-cyan-500']
const coresFund  = ['bg-emerald-500','bg-teal-500','bg-green-500','bg-lime-600','bg-amber-500']

const classesPorNivel = computed(() => {
  const medio: any[] = [], fundamental: any[] = []
  for (const cls of classes.value) {
    const g = grades.value.find(g => g.id === cls.grade_id)
    if (g?.level === 'fundamental') fundamental.push(cls)
    else medio.push(cls)
  }
  medio.sort((a,b)=>a.name.localeCompare(b.name))
  fundamental.sort((a,b)=>a.name.localeCompare(b.name))
  return { medio, fundamental }
})

const totalAlunos = computed(() => Object.values(students.value).reduce((s,arr)=>s+(arr?.length??0),0))
const resumoRapido = computed(() => [
  { label:'Ensino Médio',     value:classesPorNivel.value.medio.length,       dot:'bg-blue-400'    },
  { label:'Ens. Fundamental', value:classesPorNivel.value.fundamental.length, dot:'bg-emerald-400' },
  { label:'alunos no total',  value:totalAlunos.value,                        dot:'bg-gray-300'    },
])
const gradesFiltradas    = computed(() => grades.value.filter(g=>g.level===novoForm.nivel).sort((a,b)=>a.year_number-b.year_number))
const cloneTargetOptions = computed(() => {
  const srcId = cloneSource.value?.id
  return { medio:classesPorNivel.value.medio.filter(c=>c.id!==srcId), fundamental:classesPorNivel.value.fundamental.filter(c=>c.id!==srcId) }
})
const previewNome = computed(() => {
  if (!novoForm.grade_id || !novoForm.section_id) return ''
  const g = grades.value.find(g=>g.id===novoForm.grade_id)
  const s = sections.value.find(s=>s.id===novoForm.section_id)
  return g&&s?`${g.label}${s.label}`:''
})

function selectNivel(nivel: string) { novoForm.nivel=nivel; novoForm.grade_id=null; novoForm.section_id=null }
function closeModal()  { showModal.value=false; novoForm.nivel=''; novoForm.grade_id=null; novoForm.section_id=null; modalError.value='' }
function closeImport() { showImportModal.value=false; csvFile.value=null; importResult.value=null; importForm.class_id=''; isDragging.value=false }
function closeClone()  { showCloneModal.value=false; cloneSource.value=null; cloneSourceDiscs.value=[]; cloneTargets.value=[]; cloneResult.value=null }
function onFileChange(e: Event) { const f=(e.target as HTMLInputElement).files?.[0]; if (f){csvFile.value=f;importResult.value=null} }
function onDrop(e: DragEvent) { isDragging.value=false; const f=e.dataTransfer?.files?.[0]; if (f?.name.endsWith('.csv')){csvFile.value=f;importResult.value=null} }
function askDelete(cls: any) { deleteTarget.value=cls; deleteError.value=''; showDeleteModal.value=true }

async function openClone(cls: any) {
  cloneSource.value=cls; cloneTargets.value=[]; cloneOverwrite.value=false; cloneResult.value=null; showCloneModal.value=true
  try { cloneSourceDiscs.value=await get<any[]>(`/school/classes/${cls.id}/disciplines`) } catch { cloneSourceDiscs.value=[] }
}
async function executeClone() {
  if (!cloneSource.value||!cloneTargets.value.length) return
  cloning.value=true; cloneResult.value=null
  try {
    const res=await post<any>(`/school/classes/${cloneSource.value.id}/clone-disciplines`,{ source_class_id:cloneSource.value.id, target_class_ids:cloneTargets.value, overwrite:cloneOverwrite.value })
    const total=Object.values(res.results as Record<string,any>).reduce((s:number,r:any)=>s+r.added,0)
    cloneResult.value={error:false,message:`${res.disciplines_count} disciplinas copiadas para ${cloneTargets.value.length} turma(s) — ${total} vínculos.`}
    cloneTargets.value=[]
  } catch (e:any) { cloneResult.value={error:true,message:e?.message??'Erro ao clonar.'} } finally { cloning.value=false }
}
async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value=true; deleteError.value=''
  try { await del(`/school/classes/${deleteTarget.value.id}`); classes.value=classes.value.filter(c=>c.id!==deleteTarget.value.id); showDeleteModal.value=false }
  catch (e:any) { deleteError.value=e?.message??'Erro ao excluir.' } finally { deleting.value=false }
}
async function createClass() {
  if (!novoForm.grade_id||!novoForm.section_id) return
  saving.value=true; modalError.value=''
  try {
    const created=await post<any>('/school/classes',{grade_id:novoForm.grade_id,section_id:novoForm.section_id})
    classes.value.push(created); disciplineCount.value[created.id]=0; students.value[created.id]=[]
    closeModal()
  } catch (e:any) { modalError.value=e.message??'Erro ao criar turma.' } finally { saving.value=false }
}
async function importCsv() {
  if (!csvFile.value||!importForm.class_id) return
  importing.value=true; importResult.value=null
  try {
    const fd=new FormData(); fd.append('file',csvFile.value)
    const { upload }=useApi()
    const res=await upload<any>(`/school/students/import?class_id=${importForm.class_id}&dry_run=false`,fd)
    importResult.value={error:false,message:`${res.created} criado(s), ${res.updated} atualizado(s), ${res.skipped_inactive} inativos ignorados.`}
    students.value[importForm.class_id]=await get<any[]>(`/school/students/?class_id=${importForm.class_id}`)
    csvFile.value=null
  } catch (e:any) { importResult.value={error:true,message:e.message??'Erro ao importar CSV.'} } finally { importing.value=false }
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [classList,gradeList,sectionList]=await Promise.allSettled([
    get<any[]>('/school/classes'), get<any[]>('/school/grades'), get<any[]>('/school/sections')
  ])
  if (classList.status==='fulfilled')   classes.value  = classList.value
  if (gradeList.status==='fulfilled')   grades.value   = gradeList.value
  if (sectionList.status==='fulfilled') sections.value = sectionList.value
  loading.value=false
  classes.value.forEach(async cls => {
    loadingStudents.value[cls.id]=true
    try { students.value[cls.id]=await get<any[]>(`/school/students/?class_id=${cls.id}`) } catch { students.value[cls.id]=[] } finally { loadingStudents.value[cls.id]=false }
    try { const d=await get<any[]>(`/school/classes/${cls.id}/disciplines`); disciplineCount.value[cls.id]=d.length } catch { disciplineCount.value[cls.id]=0 }
  })
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }

.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.skel-line   { display:inline-block; width:12rem; height:.875rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }

.summary { display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap; padding:.75rem 1.25rem; background:white; border:1px solid #f3f4f6; border-radius:.875rem; }
.summary-item { display:flex; align-items:center; gap:.5rem; font-size:.8rem; color:#6b7280; }
.summary-item strong { color:#111827; font-weight:800; }
.summary-dot  { width:.5rem; height:.5rem; border-radius:50%; }

.level-header { display:flex; align-items:center; gap:.75rem; margin-bottom:.875rem; }
.level-bar    { width:.3rem; height:1.25rem; border-radius:9999px; }
.level-label  { font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.1em; color:#374151; }
.level-count  { font-size:.72rem; color:#9ca3af; margin-left:auto; }

.turmas-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:.625rem; }

.skel-card { height:8rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*50ms); }

.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-title { font-size:.875rem; font-weight:700; color:#9ca3af; margin:.5rem 0 0; }
.empty-sub   { font-size:.75rem; color:#d1d5db; margin:0; }

.turma-card {
  position:relative; background:white; border:1px solid #f3f4f6; border-radius:1rem;
  overflow:hidden; transition:border-color .15s, box-shadow .15s, transform .15s;
  animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*40ms);
}
.turma-card:hover { border-color:#e5e7eb; box-shadow:0 2px 12px rgba(0,0,0,.06); transform:translateY(-2px); }
@keyframes card-in { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

.turma-actions { position:absolute; top:.5rem; right:.5rem; display:flex; gap:.25rem; opacity:0; transition:opacity .15s; z-index:10; }
.turma-card:hover .turma-actions { opacity:1; }
.action-btn { width:1.625rem; height:1.625rem; border-radius:.5rem; background:white; border:1px solid #e5e7eb; display:flex; align-items:center; justify-content:center; cursor:pointer; transition:all .13s; }
.action-btn:hover { border-color:#d1d5db; background:#f9fafb; }
.action-btn--del:hover { border-color:#fecaca; background:#fef2f2; }

.turma-link { display:flex; flex-direction:column; gap:.75rem; padding:1rem; text-decoration:none; }
.turma-badge { width:2.75rem; height:2.75rem; border-radius:.75rem; color:white; font-size:.75rem; font-weight:800; display:flex; align-items:center; justify-content:center; }
.turma-info  { display:flex; flex-direction:column; gap:.2rem; }
.turma-disc  { font-size:.7rem; color:#6b7280; }
.turma-alunos{ font-size:.7rem; color:#9ca3af; }
.skel-tiny   { display:inline-block; width:3rem; height:.625rem; background:#f3f4f6; border-radius:.25rem; animation:shimmer 1.5s ease-in-out infinite; }

/* Buttons */
.btn-primary,.btn-secondary,.btn-cancel,.btn-danger {
  display:inline-flex; align-items:center; gap:.4rem; padding:.6rem 1.1rem;
  font-size:.8rem; font-weight:700; border-radius:.75rem; cursor:pointer; white-space:nowrap;
  transition:all .13s; border:none; text-decoration:none;
}
.btn-primary  { background:#111827; color:white; } .btn-primary:hover:not(:disabled) { background:#1f2937; } .btn-primary:disabled { opacity:.5; cursor:not-allowed; }
.btn-secondary{ background:white; color:#374151; border:1px solid #e5e7eb; } .btn-secondary:hover { background:#f9fafb; }
.btn-cancel   { background:white; color:#6b7280; border:1px solid #e5e7eb; } .btn-cancel:hover { background:#f9fafb; }
.btn-danger   { background:#ef4444; color:white; } .btn-danger:hover:not(:disabled) { background:#dc2626; }

/* Modal */
.modal-overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; padding:1rem; background:rgba(0,0,0,.25); backdrop-filter:blur(2px); }
.modal-box { background:white; border-radius:1rem; padding:1.5rem; width:100%; max-width:22rem; display:flex; flex-direction:column; gap:1rem; }
.modal-box--wide { max-width:30rem; }
.modal-title { font-size:1rem; font-weight:800; color:#111827; margin:0; }
.modal-sub   { font-size:.8rem; color:#6b7280; margin:0; }
.modal-body  { font-size:.8rem; color:#6b7280; margin:0; line-height:1.5; }
.modal-actions { display:flex; gap:.5rem; margin-top:.25rem; }
.modal-icon-wrap { width:2.5rem; height:2.5rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; }

/* Field */
.field       { display:flex; flex-direction:column; gap:.375rem; }
.field-label { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.field-select{ padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; background:white; }
.field-hint  { font-size:.7rem; color:#9ca3af; }
.error-msg   { font-size:.72rem; color:#ef4444; font-weight:600; }

.toggle-group { display:grid; grid-template-columns:1fr 1fr; gap:.4rem; }
.toggle-btn   { padding:.5rem .75rem; border-radius:.625rem; border:1.5px solid; font-size:.78rem; font-weight:700; cursor:pointer; transition:all .13s; }
.toggle-btn--off { border-color:#e5e7eb; background:#fafafa; color:#6b7280; }
.toggle-btn--on  { border-color:#111827; background:#111827; color:white; }

.opt-grid { display:flex; flex-wrap:wrap; gap:.35rem; }
.opt-btn  { padding:.375rem .75rem; border-radius:.625rem; border:1.5px solid #e5e7eb; background:white; font-size:.78rem; font-weight:700; cursor:pointer; transition:all .13s; color:#374151; }
.opt-btn:hover   { border-color:#d1d5db; }
.opt-btn--on     { border-color:#3b82f6; background:#eff6ff; color:#1d4ed8; }

.preview-box { padding:.625rem .875rem; background:#f0f9ff; border:1px solid #bae6fd; border-radius:.625rem; font-size:.8rem; color:#0369a1; }

.drop-zone { border:2px dashed #e5e7eb; border-radius:.875rem; padding:1.5rem 1rem; display:flex; flex-direction:column; align-items:center; gap:.5rem; cursor:pointer; transition:all .15s; }
.drop-zone:hover, .drop-zone--drag { border-color:#60a5fa; background:#eff6ff; }
.drop-zone--ok   { border-color:#34d399; background:#f0fdf4; }
.drop-label { font-size:.78rem; color:#6b7280; text-align:center; }

.result-box { padding:.625rem .875rem; border-radius:.625rem; font-size:.78rem; font-weight:600; }
.result-box--ok  { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; }
.result-box--err { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; }

.clone-grid { display:flex; flex-wrap:wrap; gap:.5rem; max-height:12rem; overflow-y:auto; border:1px solid #f3f4f6; border-radius:.75rem; padding:.75rem; }
.clone-item { display:flex; align-items:center; gap:.5rem; font-size:.8rem; color:#374151; cursor:pointer; min-width:6rem; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.modal-enter-active { transition:opacity .18s ease; } .modal-leave-active { transition:opacity .15s ease; }
.modal-enter-from, .modal-leave-to { opacity:0; }
</style>