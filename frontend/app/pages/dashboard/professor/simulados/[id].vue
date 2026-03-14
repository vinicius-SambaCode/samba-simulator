<template>
  <div class="page">

    <!-- Modal: selecionar turma (múltiplas) -->
    <Transition name="pop">
      <div v-if="showClassSelector" class="modal-overlay">
        <div class="modal-box">
          <div class="flex items-center gap-3 mb-1">
            <div class="modal-icon-wrap bg-blue-50"><Icon name="lucide:school" class="w-5 h-5 text-blue-600" /></div>
            <div>
              <h3 class="modal-title">Para qual turma enviar?</h3>
              <p class="modal-sub">Você está vinculado a múltiplas turmas neste simulado</p>
            </div>
          </div>
          <div class="class-options">
            <button v-if="turmasDoMesmoAno.length>1" class="class-opt class-opt--all" @click="selecionarTodasDoAno">
              <Icon name="lucide:layers" class="w-4 h-4 flex-shrink-0" />
              <div>
                <p class="opt-label">Todas do mesmo ano</p>
                <p class="opt-sub">{{ turmasDoMesmoAno.map(t=>t.class_name).join(', ') }}</p>
              </div>
            </button>
            <button v-for="a in myAssignments" :key="a.class_id" class="class-opt" @click="selecionarTurma(a)">
              <Icon name="lucide:door-open" class="w-4 h-4 flex-shrink-0 text-gray-400" />
              <div>
                <p class="opt-label">{{ a.class_name }}</p>
                <p class="opt-sub">{{ a.discipline_name }}</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show" class="toast" :class="`toast-${toast.type}`">
        <Icon :name="toast.type==='success'?'lucide:check-circle-2':toast.type==='error'?'lucide:alert-circle':'lucide:info'" class="w-4 h-4 flex-shrink-0" />
        {{ toast.message }}
      </div>
    </Transition>

    <!-- Header -->
    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/professor/simulados" class="back-btn">
          <Icon name="lucide:arrow-left" class="w-4 h-4" />
        </NuxtLink>
        <div>
          <div v-if="loadingExam" class="skel-line" />
          <h1 v-else class="page-title">{{ exam?.title }}</h1>
          <p v-if="exam && !loadingExam" class="page-sub">
            {{ progressInfo?.discipline_name ?? '—' }} · {{ progressInfo?.class_name ?? '—' }} · alternativas A–{{ exam?.options_count===4?'D':'E' }}
          </p>
        </div>
      </div>
      <!-- Progresso no header -->
      <div v-if="exam && !loadingExam" class="header-prog">
        <div class="header-prog-info">
          <span class="text-xs text-gray-400">Progresso</span>
          <span class="header-prog-count" :class="progresso===100?'text-emerald-600':'text-gray-900'">
            {{ progressInfo?.submitted??0 }}/{{ progressInfo?.quota??0 }}
          </span>
        </div>
        <div class="header-prog-bar">
          <div class="prog-fill" :class="progresso===100?'bg-emerald-500':'bg-blue-500'" :style="`width:${progresso}%`" />
        </div>
        <Icon v-if="progresso===100" name="lucide:check-circle-2" class="w-5 h-5 text-emerald-500 flex-shrink-0" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingExam" class="loading-state fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <Icon name="lucide:loader-2" class="w-5 h-5 animate-spin text-gray-400" />
      <span>Carregando simulado...</span>
    </div>

    <!-- Simulado não encontrado -->
    <div v-else-if="!exam" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <Icon name="lucide:file-x" class="w-10 h-10 text-gray-200" />
      <p>Simulado não encontrado ou sem acesso.</p>
    </div>

    <!-- Simulado travado -->
    <div v-else-if="exam?.status !== 'collecting'" class="locked-state fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <div class="locked-icon"><Icon name="lucide:lock" class="w-6 h-6 text-blue-400" /></div>
      <p class="locked-title">{{ exam.status==='locked'?'Simulado travado pelo coordenador':exam.status==='generated'?'Cadernos já gerados':'Simulado publicado' }}</p>
      <p class="locked-sub">Não é mais possível enviar questões.</p>
      <NuxtLink to="/dashboard/professor/resultados" class="btn-primary mt-4">
        <Icon name="lucide:bar-chart-2" class="w-4 h-4" /> Ver resultados
      </NuxtLink>
    </div>

    <!-- Layout principal -->
    <template v-else>

      <!-- Banner cota completa -->
      <Transition name="slide-down">
        <div v-if="progresso===100 && !enviado" class="completion-banner fade-in" :class="{ ready: mounted }" style="--d:.06s">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:check-circle-2" class="w-5 h-5 text-white" />
            </div>
            <div>
              <p class="text-sm font-bold text-white">Todas as questões cadastradas!</p>
              <p class="text-xs text-emerald-100">Cota completa — o coordenador pode prosseguir.</p>
            </div>
          </div>
          <button class="btn-completion" @click="concluirEnvio">
            <Icon name="lucide:send" class="w-4 h-4" /> Concluir
          </button>
        </div>
      </Transition>

      <!-- Pós-envio -->
      <Transition name="pop">
        <div v-if="enviado" class="sent-banner fade-in" :class="{ ready: mounted }">
          <Icon name="lucide:check-circle-2" class="w-8 h-8 animate-bounce" />
          <p class="font-bold">Questões enviadas com sucesso!</p>
          <p class="text-sm text-emerald-100">Redirecionando...</p>
        </div>
      </Transition>

      <div class="main-grid fade-in" :class="{ ready: mounted }" style="--d:.08s">

        <!-- COLUNA ESQUERDA: upload + formulário -->
        <div class="left-col">

          <!-- Upload -->
          <div class="card">
            <div class="card-header">
              <div class="card-title"><Icon name="lucide:file-up" class="w-4 h-4 text-blue-500" /> Importar arquivo</div>
              <span class="text-xs text-gray-400">.docx · .txt · .pdf</span>
            </div>
            <div class="p-4">
              <div class="drop-zone"
                :class="isDragging?'drop--drag':uploadStatus==='success'?'drop--ok':uploadStatus==='error'?'drop--err':uploadStatus==='loading'?'drop--loading':''"
                @dragover.prevent="isDragging=true" @dragleave="isDragging=false" @drop.prevent="handleDrop"
                @click="triggerFileInput">
                <input ref="fileInput" type="file" accept=".docx,.txt,.pdf" class="hidden" @change="handleFileChange" />

                <template v-if="uploadStatus==='idle'">
                  <Icon name="lucide:upload-cloud" class="w-8 h-8 text-gray-300" />
                  <p class="drop-label">Arraste ou clique para enviar</p>
                  <p class="drop-hint">Suporta imagens e fórmulas</p>
                </template>
                <template v-else-if="uploadStatus==='loading'">
                  <svg class="animate-spin w-7 h-7 text-blue-500" fill="none" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
                    <path fill="currentColor" d="M4 12a8 8 0 018-8v8z" class="opacity-75"/>
                  </svg>
                  <p class="drop-label text-blue-700">Processando...</p>
                  <p class="drop-hint truncate max-w-full">{{ uploadedFileName }}</p>
                </template>
                <template v-else-if="uploadStatus==='success'">
                  <Icon name="lucide:check-circle-2" class="w-8 h-8 text-emerald-400" />
                  <p class="drop-label text-emerald-700 truncate max-w-full">{{ uploadedFileName }}</p>
                  <button class="drop-reset" @click.stop="resetUpload">Novo arquivo</button>
                </template>
                <template v-else-if="uploadStatus==='error'">
                  <Icon name="lucide:alert-circle" class="w-8 h-8 text-red-400" />
                  <p class="drop-label text-red-600">Erro ao processar</p>
                  <p class="drop-hint text-red-400 truncate max-w-full">{{ uploadError }}</p>
                  <button class="drop-reset" @click.stop="resetUpload">Tentar novamente</button>
                </template>
              </div>
            </div>
          </div>

          <!-- Formulário questão manual -->
          <div class="card" :class="editandoId!==null?'card--editing':''">
            <div class="card-header" :class="editandoId!==null?'card-header--editing':''">
              <div class="card-title">
                <Icon :name="editandoId!==null?'lucide:pencil':'lucide:plus-circle'" class="w-4 h-4" :class="editandoId!==null?'text-blue-600':'text-gray-500'" />
                {{ editandoId!==null?`Editando questão #${editandoIndex+1}`:'Nova questão' }}
              </div>
              <button v-if="editandoId!==null" class="cancel-edit" @click="cancelarEdicao">
                <Icon name="lucide:x" class="w-3.5 h-3.5" /> Cancelar
              </button>
            </div>
            <div class="p-4 flex flex-col gap-4">

              <!-- Enunciado -->
              <div class="field">
                <label class="field-label">Enunciado <span class="req">*</span></label>
                <textarea v-model="novaQuestao.stem" rows="4"
                  placeholder="Digite o enunciado. Use $fórmula$ para LaTeX."
                  class="field-textarea" :class="editandoId!==null?'bg-blue-50/30':''" />
                <Transition name="slide-down">
                  <div v-if="stemPreview" class="preview-box">
                    <p class="preview-label"><Icon name="lucide:eye" class="w-3 h-3" /> Preview</p>
                    <div class="text-sm text-gray-800 question-content" v-html="stemPreview" />
                  </div>
                </Transition>
              </div>

              <!-- Alternativas -->
              <div class="field">
                <label class="field-label">Alternativas <span class="req">*</span></label>
                <div class="opts-list">
                  <div v-for="(_, i) in novaQuestao.options.slice(0, exam.options_count)" :key="i" class="opt-row">
                    <button class="opt-sel" :class="novaQuestao.correct_label===letras[i]?'opt-sel--on':''" @click="novaQuestao.correct_label=letras[i]">
                      {{ letras[i] }}
                    </button>
                    <input v-model="novaQuestao.options[i].text" type="text" :placeholder="`Alternativa ${letras[i]}`"
                      class="field-input" :class="novaQuestao.correct_label===letras[i]?'field-input--correct':''" />
                  </div>
                </div>
                <p class="field-hint">Clique na letra para marcar o gabarito</p>
              </div>

              <Transition name="slide-down">
                <div v-if="manualError" class="error-box">
                  <Icon name="lucide:alert-circle" class="w-4 h-4 flex-shrink-0" />
                  {{ manualError }}
                </div>
              </Transition>

              <button class="btn-submit" :class="[!questaoValida||savingManual?'btn-submit--disabled':'', editandoId!==null?'btn-submit--edit':'']"
                :disabled="!questaoValida||savingManual" @click="salvarQuestao">
                <Icon v-if="savingManual" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
                <Icon v-else :name="editandoId!==null?'lucide:check':'lucide:plus'" class="w-4 h-4" />
                {{ savingManual?'Salvando...':editandoId!==null?'Salvar alterações':'Adicionar questão' }}
              </button>
            </div>
          </div>
        </div>

        <!-- COLUNA DIREITA: lista de questões -->
        <div class="right-col">
          <div class="list-header">
            <h3 class="list-title">Questões <span class="count-badge">{{ questoes.length }}</span></h3>
            <div class="list-actions">
              <span v-if="progresso<100 && (progressInfo?.quota??0)>0" class="faltam-tag">
                faltam {{ Math.max(0,(progressInfo?.quota??0)-(progressInfo?.submitted??0)) }}
              </span>
              <span v-else-if="progresso===100" class="completa-tag">
                <Icon name="lucide:check" class="w-3 h-3" /> Cota completa
              </span>
              <div v-if="questoes.length>0" class="flex items-center gap-1">
                <button v-if="!confirmandoLimpar" class="btn-danger-sm" @click="confirmandoLimpar=true">
                  <Icon name="lucide:trash-2" class="w-3 h-3" /> Excluir todas
                </button>
                <template v-else>
                  <span class="text-xs text-red-600 font-semibold">Confirmar?</span>
                  <button class="btn-danger-sm" @click="excluirTodasQuestoes">Sim</button>
                  <button class="btn-cancel-sm" @click="confirmandoLimpar=false">Não</button>
                </template>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-if="!questoes.length" class="empty-q">
            <Icon name="lucide:file-question" class="w-8 h-8 text-gray-200" />
            <p>Nenhuma questão ainda</p>
            <p class="text-xs text-gray-300">Use o formulário ou importe um arquivo</p>
          </div>

          <!-- Cards de questão -->
          <TransitionGroup name="list-item" tag="div" class="q-list">
            <div v-for="(q, i) in questoes" :key="q.id" class="q-card group" :class="editandoId===q.id?'q-card--editing':''">
              <div class="q-card-header">
                <span class="q-num" :class="editandoId===q.id?'q-num--editing':''">{{ i+1 }}</span>
                <span v-if="q.has_images||q.images?.length" class="img-tag">
                  <Icon name="lucide:image" class="w-2.5 h-2.5" /> imagem
                </span>
                <span v-if="q.source&&q.source!=='manual'" class="source-tag">{{ q.source }}</span>
                <div class="q-actions">
                  <button class="q-action" :class="editandoId===q.id?'q-action--on':''" @click="editarQuestao(q)">
                    <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
                  </button>
                  <button class="q-action" :class="confirmandoDelecaoId===q.id?'q-action--del-on':''" @click="clicarRemover(q.id)">
                    <Icon name="lucide:trash-2" class="w-3.5 h-3.5" />
                  </button>
                  <button v-if="confirmandoDelecaoId===q.id" class="q-action" @click.stop="confirmandoDelecaoId=null">
                    <Icon name="lucide:x" class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              <Transition name="slide-down">
                <div v-if="confirmandoDelecaoId===q.id" class="del-confirm">
                  <span>Remover esta questão?</span>
                  <button class="del-yes" @click="removerQuestao(q.id)">Remover</button>
                  <button class="del-no" @click="confirmandoDelecaoId=null">Cancelar</button>
                </div>
              </Transition>
              <div class="q-stem question-content" v-html="renderStem(q.stem, q.images??[])" />
              <div class="q-opts">
                <div v-for="opt in q.options" :key="opt.label" class="q-opt" :class="q.correct_label===opt.label?'q-opt--correct':''">
                  <span class="opt-letter" :class="q.correct_label===opt.label?'opt-letter--correct':''">{{ opt.label }}</span>
                  <div class="question-content flex-1 min-w-0" v-html="renderOption(opt.text, opt.label, q.images??[])" />
                  <Icon v-if="q.correct_label===opt.label" name="lucide:check" class="w-3 h-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                </div>
              </div>
            </div>
          </TransitionGroup>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })
useHead({ link: [{ rel:'stylesheet', href:'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }] })

const route   = useRoute()
const { get, post, patch, delete: deleteReq, upload } = useApi()
const { renderStem, renderOption } = useQuestionRenderer()
const examId = Number(route.params.id)
const letras = ['A','B','C','D','E']
const mounted = ref(false)

const exam         = ref<any>(null)
const progressInfo = ref<any>(null)
const questoes     = ref<any[]>([])
const loadingExam  = ref(true)
const myAssignments    = ref<any[]>([])
const showClassSelector= ref(false)
const turmasDoMesmoAno = computed(() => {
  if (!myAssignments.value.length) return []
  const ano = extrairAno(myAssignments.value[0]?.class_name??'')
  return myAssignments.value.filter(a=>extrairAno(a.class_name??'')===ano)
})
function extrairAno(nome: string) { const m=nome.match(/^(\d+)/); return m?m[1]:nome.substring(0,2) }
function selecionarTurma(a: any) {
  progressInfo.value={ ...progressInfo.value, class_id:a.class_id, discipline_id:a.discipline_id, class_name:a.class_name, discipline_name:a.discipline_name, targetClassIds:[a.class_id] }
  showClassSelector.value=false
}
function selecionarTodasDoAno() {
  const first=turmasDoMesmoAno.value[0]
  progressInfo.value={ ...progressInfo.value, class_id:first.class_id, discipline_id:first.discipline_id, class_name:turmasDoMesmoAno.value.map(t=>t.class_name).join(', '), discipline_name:first.discipline_name, targetClassIds:turmasDoMesmoAno.value.map(t=>t.class_id) }
  showClassSelector.value=false
}

const fileInput        = ref<HTMLInputElement|null>(null)
const uploadStatus     = ref<'idle'|'loading'|'success'|'error'>('idle')
const uploadedFileName = ref('')
const uploadError      = ref('')
const isDragging       = ref(false)
const savingManual         = ref(false)
const manualError          = ref('')
const editandoId           = ref<number|null>(null)
const enviado              = ref(false)
const confirmandoDelecaoId = ref<number|null>(null)
const confirmandoLimpar    = ref(false)
const toast = reactive({ show:false, message:'', type:'success' as 'success'|'error'|'info' })
let toastTimer: any = null
function showToast(message: string, type: 'success'|'error'|'info'='success') {
  if (toastTimer) clearTimeout(toastTimer); toast.message=message; toast.type=type; toast.show=true
  toastTimer=setTimeout(()=>{toast.show=false},3000)
}
const editandoIndex = computed(()=>questoes.value.findIndex(q=>q.id===editandoId.value))
const novaQuestao = reactive({ stem:'', options:letras.map(l=>({label:l,text:''})), correct_label:'A' })
const stemPreview = ref('')
let previewTimer: any = null
watch(()=>novaQuestao.stem, val=>{
  if (previewTimer) clearTimeout(previewTimer)
  if (!val.trim()||!val.includes('$')) { stemPreview.value=''; return }
  previewTimer=setTimeout(()=>{ stemPreview.value=renderStem(val,[]) },400)
})
const progresso = computed(()=>{
  const quota=progressInfo.value?.quota??0, submitted=progressInfo.value?.submitted??0
  if (!quota) return 0
  return Math.min(100,Math.round(submitted/quota*100))
})
const questaoValida = computed(()=>{
  const count=exam.value?.options_count??4
  return novaQuestao.stem.trim()!=='' && novaQuestao.options.slice(0,count).every(o=>o.text.trim()!=='')
})
function normalizeQuestion(q: any) { return {...q, images:q.images??[]} }

onMounted(async ()=>{
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  loadingExam.value=true
  try {
    const [examData,progressData,questoesData,myAssignment]=await Promise.all([
      get<any>(`/exams/${examId}`),
      get<any>(`/exams/${examId}/progress`),
      get<any[]>(`/exams/${examId}/questions`),
      get<any>(`/exams/${examId}/my-assignment`).catch(()=>null),
    ])
    exam.value=examData
    questoes.value=(questoesData??[]).map(normalizeQuestion)
    if (myAssignment) {
      myAssignments.value=myAssignment.assignments??[myAssignment]
      if (progressData?.disciplines?.length) {
        const myDisc=progressData.disciplines.find((d:any)=>d.discipline_id===myAssignment.discipline_id)??progressData.disciplines[0]
        const mySubmitted=questoes.value.filter((q:any)=>q.discipline_id===myAssignment.discipline_id&&q.class_id===myAssignment.class_id).length
        progressInfo.value={...myDisc,submitted:mySubmitted,class_id:myAssignment.class_id,discipline_id:myAssignment.discipline_id,class_name:myAssignment.class_name??null,discipline_name:myAssignment.discipline_name??null,targetClassIds:[myAssignment.class_id]}
      }
      const quotaCompleta=progressInfo.value&&progressInfo.value.quota>0&&progressInfo.value.submitted>=progressInfo.value.quota
      if (myAssignments.value.length>1&&!quotaCompleta) showClassSelector.value=true
    } else if (progressData?.disciplines?.length) {
      progressInfo.value={...progressData.disciplines[0],submitted:questoes.value.length,class_id:null,class_name:null,targetClassIds:[]}
    }
  } catch { exam.value=null } finally { loadingExam.value=false }
})

function triggerFileInput() { if (uploadStatus.value==='loading') return; fileInput.value?.click() }
function handleDrop(e: DragEvent) { isDragging.value=false; const f=e.dataTransfer?.files[0]; if (f) processFile(f) }
function handleFileChange(e: Event) { const f=(e.target as HTMLInputElement).files?.[0]; if (f) processFile(f) }
async function processFile(file: File) {
  const allowed=['.docx','.txt','.pdf']
  const ext='.'+file.name.split('.').pop()?.toLowerCase()
  if (!allowed.includes(ext)) { uploadStatus.value='error'; uploadError.value='Formato não suportado. Use .docx, .txt ou .pdf'; return }
  uploadedFileName.value=file.name; uploadStatus.value='loading'; uploadError.value=''
  try {
    const fd=new FormData(); fd.append('file',file)
    fd.append('class_id',String(progressInfo.value?.class_id??0))
    fd.append('discipline_id',String(progressInfo.value?.discipline_id??0))
    await upload<any>(`/exams/${examId}/questions/upload`,fd)
    uploadStatus.value='success'
    questoes.value=(await get<any[]>(`/exams/${examId}/questions`)).map(normalizeQuestion)
    await recarregarProgresso(); showToast('Questões importadas com sucesso!')
  } catch (e:any) { uploadStatus.value='error'; uploadError.value=e.message??'Erro ao processar'; showToast(uploadError.value,'error') }
}
function resetUpload() { uploadStatus.value='idle'; uploadedFileName.value=''; uploadError.value=''; if (fileInput.value) fileInput.value.value='' }

async function salvarQuestao() {
  manualError.value=''; savingManual.value=true
  const count=exam.value?.options_count??4
  const payload={ stem:novaQuestao.stem.trim(), options:novaQuestao.options.slice(0,count).map(o=>({label:o.label,text:o.text.trim()})), correct_label:novaQuestao.correct_label||undefined, discipline_id:progressInfo.value?.discipline_id, class_id:progressInfo.value?.class_id }
  try {
    if (editandoId.value!==null) {
      const updated=normalizeQuestion(await patch<any>(`/exams/${examId}/questions/${editandoId.value}`,payload))
      const idx=questoes.value.findIndex(q=>q.id===editandoId.value); if (idx!==-1) questoes.value[idx]=updated
      editandoId.value=null; showToast('Questão atualizada!')
    } else {
      const created=normalizeQuestion(await post<any>(`/exams/${examId}/questions`,payload))
      questoes.value.push(created); showToast('Questão adicionada!')
    }
    resetForm(); await recarregarProgresso()
  } catch (e:any) { manualError.value=e.message??'Erro ao salvar questão.'; showToast(manualError.value,'error') } finally { savingManual.value=false }
}
function editarQuestao(q: any) {
  editandoId.value=q.id; novaQuestao.stem=q.stem; novaQuestao.correct_label=q.correct_label??'A'
  novaQuestao.options=letras.map(l=>({label:l,text:q.options.find((o:any)=>o.label===l)?.text??''}))
  manualError.value=''; window.scrollTo({top:0,behavior:'smooth'})
}
function cancelarEdicao() { editandoId.value=null; resetForm() }
function clicarRemover(id: number) {
  if (confirmandoDelecaoId.value===id) { removerQuestao(id) }
  else { confirmandoDelecaoId.value=id; setTimeout(()=>{ if (confirmandoDelecaoId.value===id) confirmandoDelecaoId.value=null },3000) }
}
async function removerQuestao(id: number) {
  confirmandoDelecaoId.value=null
  try { await deleteReq(`/exams/${examId}/questions/${id}`); questoes.value=questoes.value.filter(q=>q.id!==id); if (editandoId.value===id) cancelarEdicao(); await recarregarProgresso(); showToast('Questão removida.') }
  catch (e:any) { showToast(e.message??'Erro ao remover.','error') }
}
async function excluirTodasQuestoes() {
  confirmandoLimpar.value=false
  let removidas=0
  for (const id of questoes.value.map((q:any)=>q.id)) {
    try { await deleteReq(`/exams/${examId}/questions/${id}`); questoes.value=questoes.value.filter((q:any)=>q.id!==id); removidas++ } catch {}
  }
  await recarregarProgresso(); showToast(`${removidas} questão(ões) removida(s).`)
}
function resetForm() { novaQuestao.stem=''; novaQuestao.options=letras.map(l=>({label:l,text:''})); novaQuestao.correct_label='A'; manualError.value=''; stemPreview.value='' }
function concluirEnvio() { enviado.value=true; setTimeout(()=>navigateTo('/dashboard/professor'),1800) }
async function recarregarProgresso() {
  try {
    const [data,myAssignment]=await Promise.all([get<any>(`/exams/${examId}/progress`),get<any>(`/exams/${examId}/my-assignment`).catch(()=>null)])
    if (data?.disciplines?.length) {
      const discId=myAssignment?.discipline_id??progressInfo.value?.discipline_id
      const myDisc=data.disciplines.find((d:any)=>d.discipline_id===discId)??data.disciplines[0]
      const classId=myAssignment?.class_id??progressInfo.value?.class_id
      const mySubmitted=questoes.value.filter((q:any)=>q.discipline_id===discId&&q.class_id===classId).length
      progressInfo.value={...myDisc,submitted:mySubmitted,class_id:classId,discipline_id:discId,class_name:myAssignment?.class_name??progressInfo.value?.class_name,discipline_name:myAssignment?.discipline_name??progressInfo.value?.discipline_name,targetClassIds:progressInfo.value?.targetClassIds??[classId]}
    }
  } catch {}
}
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; max-width:80rem; margin:0 auto; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.back-btn    { width:2rem; height:2rem; border-radius:.625rem; display:flex; align-items:center; justify-content:center; background:white; border:1px solid #e5e7eb; color:#6b7280; cursor:pointer; text-decoration:none; flex-shrink:0; }
.back-btn:hover { background:#f9fafb; }
.skel-line   { display:inline-block; width:14rem; height:1.25rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s infinite; }
.header-prog { display:flex; align-items:center; gap:.75rem; flex-shrink:0; }
.header-prog-info { text-align:right; }
.header-prog-count { display:block; font-size:.875rem; font-weight:800; line-height:1; }
.header-prog-bar { width:8rem; height:.5rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.prog-fill { height:100%; border-radius:9999px; transition:width .6s ease; }
.loading-state { display:flex; align-items:center; gap:.75rem; justify-content:center; padding:4rem; color:#9ca3af; font-size:.875rem; }
.empty-state  { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.locked-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:3.5rem 1rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; text-align:center; }
.locked-icon  { width:3rem; height:3rem; border-radius:.875rem; background:#eff6ff; display:flex; align-items:center; justify-content:center; }
.locked-title { font-size:.875rem; font-weight:700; color:#374151; margin:.5rem 0 0; }
.locked-sub   { font-size:.78rem; color:#9ca3af; margin:0; }
.completion-banner { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:1rem 1.25rem; background:linear-gradient(135deg,#10b981,#059669); border-radius:1rem; flex-wrap:wrap; }
.btn-completion { display:inline-flex; align-items:center; gap:.4rem; padding:.5rem 1rem; background:white; color:#059669; font-size:.78rem; font-weight:700; border-radius:.75rem; border:none; cursor:pointer; flex-shrink:0; transition:background .13s; }
.btn-completion:hover { background:#f0fdf4; }
.sent-banner { background:#059669; border-radius:1rem; padding:2rem; text-align:center; color:white; display:flex; flex-direction:column; align-items:center; gap:.5rem; }
.main-grid { display:grid; grid-template-columns:1fr; gap:1rem; }
@media(min-width:1024px) { .main-grid { grid-template-columns:1fr 1fr; align-items:start; } }
.left-col  { display:flex; flex-direction:column; gap:.75rem; }
.right-col { display:flex; flex-direction:column; gap:.75rem; }
@media(min-width:1024px) { .left-col { position:sticky; top:1.5rem; } }
.card { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; }
.card--editing { border-color:#bfdbfe; box-shadow:0 0 0 3px #eff6ff; }
.card-header { display:flex; align-items:center; justify-content:space-between; padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; }
.card-header--editing { background:#f0f9ff; border-bottom-color:#bfdbfe; }
.card-title { display:flex; align-items:center; gap:.5rem; font-size:.8rem; font-weight:700; color:#111827; }
.cancel-edit { display:inline-flex; align-items:center; gap:.3rem; font-size:.72rem; font-weight:600; color:#6b7280; background:none; border:none; cursor:pointer; }
.cancel-edit:hover { color:#374151; }
.drop-zone { border:2px dashed #e5e7eb; border-radius:.875rem; padding:1.5rem 1rem; display:flex; flex-direction:column; align-items:center; gap:.4rem; cursor:pointer; text-align:center; transition:all .15s; }
.drop-zone:hover, .drop--drag { border-color:#60a5fa; background:#eff6ff; }
.drop--ok    { border-color:#34d399; background:#f0fdf4; }
.drop--err   { border-color:#f87171; background:#fef2f2; }
.drop--loading { border-color:#60a5fa; background:#eff6ff; pointer-events:none; }
.drop-label { font-size:.8rem; font-weight:600; }
.drop-hint  { font-size:.7rem; color:#9ca3af; }
.drop-reset { font-size:.7rem; font-weight:600; color:#3b82f6; text-decoration:underline; background:none; border:none; cursor:pointer; }
.field       { display:flex; flex-direction:column; gap:.375rem; }
.field-label { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.req { color:#f87171; }
.field-textarea { padding:.625rem .875rem; border:1px solid #e5e7eb; border-radius:.75rem; font-size:.8rem; outline:none; resize:none; line-height:1.6; transition:border-color .15s; }
.field-textarea:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.field-input { flex:1; padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; outline:none; transition:border-color .15s; }
.field-input:focus { border-color:#93c5fd; }
.field-input--correct { border-color:#6ee7b7; background:#f0fdf4; }
.field-hint { font-size:.68rem; color:#9ca3af; }
.preview-box { padding:.75rem; background:#f9fafb; border:1px solid #f3f4f6; border-radius:.75rem; }
.preview-label { font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#9ca3af; display:flex; align-items:center; gap:.25rem; margin-bottom:.5rem; }
.opts-list { display:flex; flex-direction:column; gap:.5rem; }
.opt-row { display:flex; align-items:center; gap:.5rem; }
.opt-sel { width:2rem; height:2rem; border-radius:9999px; border:2px solid #e5e7eb; font-size:.72rem; font-weight:800; cursor:pointer; display:flex; align-items:center; justify-content:center; flex-shrink:0; background:white; color:#6b7280; transition:all .13s; }
.opt-sel--on { border-color:#10b981; background:#10b981; color:white; }
.error-box { display:flex; align-items:center; gap:.5rem; padding:.625rem .875rem; background:#fef2f2; border:1px solid #fecaca; border-radius:.75rem; font-size:.75rem; color:#dc2626; font-weight:500; }
.btn-submit { width:100%; padding:.625rem; border-radius:.75rem; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:.5rem; font-size:.8rem; font-weight:700; background:#111827; color:white; transition:all .13s; }
.btn-submit:hover:not(.btn-submit--disabled) { background:#1f2937; }
.btn-submit--disabled { background:#e5e7eb; color:#9ca3af; cursor:not-allowed; }
.btn-submit--edit { background:#2563eb; }
.btn-submit--edit:hover:not(.btn-submit--disabled) { background:#1d4ed8; }
.list-header { display:flex; align-items:center; justify-content:space-between; gap:.5rem; flex-wrap:wrap; padding-bottom:.375rem; }
.list-title  { font-size:.875rem; font-weight:700; color:#111827; display:flex; align-items:center; gap:.5rem; }
.list-actions{ display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }
.count-badge { font-size:.65rem; font-weight:700; padding:.1rem .4rem; border-radius:9999px; background:#f3f4f6; color:#6b7280; }
.faltam-tag  { font-size:.65rem; font-weight:700; padding:.15rem .5rem; border-radius:9999px; background:#fef3c7; color:#92400e; }
.completa-tag{ font-size:.65rem; font-weight:700; padding:.15rem .5rem; border-radius:9999px; background:#d1fae5; color:#065f46; display:flex; align-items:center; gap:.2rem; }
.btn-danger-sm{ display:inline-flex; align-items:center; gap:.25rem; padding:.3rem .625rem; font-size:.68rem; font-weight:700; color:#ef4444; background:#fef2f2; border:none; border-radius:.5rem; cursor:pointer; transition:all .13s; }
.btn-danger-sm:hover { background:#fee2e2; }
.btn-cancel-sm{ display:inline-flex; align-items:center; gap:.25rem; padding:.3rem .625rem; font-size:.68rem; font-weight:700; color:#6b7280; background:#f3f4f6; border:none; border-radius:.5rem; cursor:pointer; }
.empty-q { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:3rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-q p { font-size:.8rem; color:#9ca3af; margin:0; }
.q-list { display:flex; flex-direction:column; gap:.625rem; }
.q-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; flex-direction:column; gap:.625rem; transition:border-color .13s; }
.q-card--editing { border-color:#bfdbfe; box-shadow:0 0 0 3px #eff6ff; }
.q-card:hover { border-color:#e5e7eb; }
.q-card-header { display:flex; align-items:center; gap:.5rem; }
.q-num { width:1.5rem; height:1.5rem; border-radius:9999px; background:#f3f4f6; font-size:.68rem; font-weight:700; color:#6b7280; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.q-num--editing { background:#dbeafe; color:#1e40af; }
.img-tag, .source-tag { font-size:.62rem; font-weight:700; padding:.1rem .4rem; border-radius:9999px; }
.img-tag    { background:#ede9fe; color:#5b21b6; display:inline-flex; align-items:center; gap:.2rem; }
.source-tag { background:#f3f4f6; color:#6b7280; }
.q-actions { margin-left:auto; display:flex; gap:.2rem; opacity:0; transition:opacity .13s; }
.q-card:hover .q-actions { opacity:1; }
.q-action { width:1.75rem; height:1.75rem; border-radius:.5rem; background:none; border:none; cursor:pointer; color:#9ca3af; display:flex; align-items:center; justify-content:center; transition:all .13s; }
.q-action:hover { color:#374151; background:#f3f4f6; }
.q-action--on   { color:#3b82f6; background:#eff6ff; opacity:1 !important; }
.q-action--del-on { color:#ef4444; background:#fef2f2; opacity:1 !important; }
.del-confirm { display:flex; align-items:center; gap:.5rem; padding:.5rem .625rem; background:#fef2f2; border:1px solid #fecaca; border-radius:.625rem; font-size:.72rem; color:#dc2626; font-weight:600; }
.del-yes { font-size:.7rem; font-weight:700; color:#ef4444; background:none; border:none; cursor:pointer; text-decoration:underline; }
.del-no  { font-size:.7rem; font-weight:700; color:#6b7280; background:none; border:none; cursor:pointer; }
.q-stem { font-size:.8rem; color:#374151; line-height:1.6; }
.q-opts  { display:flex; flex-direction:column; gap:.3rem; }
.q-opt   { display:flex; align-items:flex-start; gap:.5rem; padding:.35rem .625rem; border-radius:.5rem; background:#f9fafb; font-size:.75rem; color:#6b7280; }
.q-opt--correct { background:#f0fdf4; border:1px solid #bbf7d0; }
.opt-letter { font-weight:700; flex-shrink:0; width:.875rem; }
.opt-letter--correct { color:#059669; }
.btn-primary { display:inline-flex; align-items:center; gap:.4rem; padding:.6rem 1.1rem; background:#111827; color:white; font-size:.8rem; font-weight:700; border-radius:.75rem; border:none; cursor:pointer; text-decoration:none; transition:background .13s; }
.btn-primary:hover { background:#1f2937; }

/* Modal seletor de turma */
.modal-overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; padding:1rem; background:rgba(0,0,0,.4); backdrop-filter:blur(4px); }
.modal-box { background:white; border-radius:1rem; padding:1.5rem; width:100%; max-width:26rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-icon-wrap { width:2.5rem; height:2.5rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.modal-title { font-size:.9rem; font-weight:800; color:#111827; margin:0; }
.modal-sub   { font-size:.72rem; color:#9ca3af; margin:.1rem 0 0; }
.class-options { display:flex; flex-direction:column; gap:.5rem; }
.class-opt { display:flex; align-items:flex-start; gap:.75rem; padding:.75rem 1rem; border:1.5px solid #e5e7eb; border-radius:.875rem; cursor:pointer; background:white; text-align:left; transition:all .13s; }
.class-opt:hover { border-color:#93c5fd; background:#eff6ff; }
.class-opt--all { border-color:#bfdbfe; background:#eff6ff; }
.opt-label { font-size:.8rem; font-weight:700; color:#111827; }
.opt-sub   { font-size:.7rem; color:#6b7280; margin-top:.15rem; }

/* Toast */
.toast { position:fixed; bottom:1.5rem; right:1.5rem; z-index:60; display:flex; align-items:center; gap:.75rem; padding:.75rem 1.125rem; border-radius:.875rem; font-size:.8rem; font-weight:600; min-width:14rem; box-shadow:0 8px 24px rgba(0,0,0,.12); }
.toast-success { background:#111827; color:white; }
.toast-error   { background:#dc2626; color:white; }
.toast-info    { background:#2563eb; color:white; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.pop-enter-active { transition:all .25s cubic-bezier(.175,.885,.32,1.275); }
.pop-leave-active { transition:all .15s ease; }
.pop-enter-from, .pop-leave-to { opacity:0; transform:scale(.9); }
.slide-down-enter-active, .slide-down-leave-active { transition:all .2s ease; overflow:hidden; }
.slide-down-enter-from, .slide-down-leave-to { opacity:0; max-height:0; transform:translateY(-4px); }
.slide-down-enter-to, .slide-down-leave-from { max-height:12rem; }
.list-item-enter-active { transition:all .22s ease; }
.list-item-leave-active { transition:all .18s ease; position:absolute; width:100%; }
.list-item-enter-from   { opacity:0; transform:translateY(-6px); }
.list-item-leave-to     { opacity:0; transform:translateX(12px); }
.list-item-move         { transition:transform .25s ease; }
.toast-enter-active { transition:all .3s cubic-bezier(.175,.885,.32,1.275); }
.toast-leave-active { transition:all .2s ease; }
.toast-enter-from { opacity:0; transform:translateY(12px) scale(.95); }
.toast-leave-to   { opacity:0; transform:translateY(6px); }

.question-content :deep(img) { max-width:100%; border-radius:.5rem; margin:.25rem 0; display:block; }
.question-content :deep(.katex) { font-size:.9em; }
.question-content :deep(.katex-display) { margin:.5rem 0; overflow-x:auto; }
</style>