<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Disciplinas</h1>
        <p class="page-sub">{{ disciplines.length }} disciplina{{ disciplines.length!==1?'s':'' }} cadastrada{{ disciplines.length!==1?'s':'' }}</p>
      </div>
      <button class="btn-primary" @click="abrirModalCriar">
        <Icon name="lucide:plus" class="w-4 h-4" /> Nova disciplina
      </button>
    </div>

    <div class="search-bar fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <Icon name="lucide:search" class="search-icon" />
      <input v-model="busca" placeholder="Buscar disciplina..." class="search-input" />
      <button v-if="busca" class="search-clear" @click="busca = ''">
        <Icon name="lucide:x" class="w-3.5 h-3.5" />
      </button>
    </div>

    <div v-if="loading" class="disc-grid fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="i in 8" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <div v-else-if="!disciplinasFiltradas.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:book-open" class="w-10 h-10 text-gray-200" />
      <p>{{ busca ? 'Nenhuma disciplina encontrada' : 'Nenhuma disciplina cadastrada' }}</p>
      <button v-if="!busca" class="btn-primary mt-3" @click="abrirModalCriar">
        <Icon name="lucide:plus" class="w-4 h-4" /> Nova disciplina
      </button>
    </div>

    <div v-else class="disc-grid fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="(d, idx) in disciplinasFiltradas" :key="d.id" class="disc-card group" :style="`--i:${idx}`">
        <div class="disc-icon" :class="discColors[idx % discColors.length]">
          <Icon name="lucide:book-open" class="w-4 h-4" />
        </div>
        <p class="disc-name">{{ d.name }}</p>
        <div class="disc-actions">
          <button class="icon-btn" title="Editar" @click="abrirModalEditar(d)">
            <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
          </button>
          <button class="icon-btn icon-btn--del" title="Excluir" @click="confirmarExclusao(d)">
            <Icon name="lucide:trash-2" class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal criar/editar -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-box">
          <h3 class="modal-title">{{ editando ? 'Editar disciplina' : 'Nova disciplina' }}</h3>
          <div class="field">
            <label class="field-label">Nome</label>
            <input v-model="form.name" placeholder="Ex: Matemática" class="field-input"
              @keydown.enter="salvar" />
          </div>
          <p v-if="formError" class="error-msg">{{ formError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeModal">Cancelar</button>
            <button class="btn-primary" :disabled="!form.name.trim() || saving" @click="salvar">
              {{ saving ? 'Salvando...' : editando ? 'Salvar' : 'Criar' }}
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
          <h3 class="modal-title">Excluir "{{ deletingDisc?.name }}"?</h3>
          <p class="modal-body">Questões vinculadas a esta disciplina podem ser afetadas.</p>
          <p v-if="deleteError" class="error-msg">{{ deleteError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showDeleteModal=false">Cancelar</button>
            <button class="btn-danger" :disabled="deleting" @click="excluir">
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
const { get, post, put, delete: deleteReq } = useApi()
const mounted = ref(false)

const disciplines     = ref<any[]>([])
const loading         = ref(true)
const busca           = ref('')
const showModal       = ref(false); const formError  = ref(''); const saving  = ref(false)
const showDeleteModal = ref(false); const deleteError = ref(''); const deleting = ref(false)
const editando        = ref<any>(null); const deletingDisc = ref<any>(null)
const form = reactive({ name: '' })

const discColors = [
  'bg-blue-100 text-blue-600', 'bg-violet-100 text-violet-600', 'bg-emerald-100 text-emerald-600',
  'bg-amber-100 text-amber-600', 'bg-rose-100 text-rose-600', 'bg-teal-100 text-teal-600',
  'bg-indigo-100 text-indigo-600', 'bg-orange-100 text-orange-600',
]

const disciplinasFiltradas = computed(() => {
  if (!busca.value) return disciplines.value
  const q = busca.value.toLowerCase()
  return disciplines.value.filter(d => d.name.toLowerCase().includes(q))
})

function abrirModalCriar() { editando.value=null; form.name=''; formError.value=''; showModal.value=true }
function abrirModalEditar(d: any) { editando.value=d; form.name=d.name; formError.value=''; showModal.value=true }
function closeModal() { showModal.value=false; editando.value=null; form.name=''; formError.value='' }
function confirmarExclusao(d: any) { deletingDisc.value=d; deleteError.value=''; showDeleteModal.value=true }

async function salvar() {
  if (!form.name.trim()) return
  saving.value=true; formError.value=''
  try {
    if (editando.value) {
      await put<any>(`/disciplines/${editando.value.id}/`, { name:form.name.trim() })
      const idx=disciplines.value.findIndex(d=>d.id===editando.value.id)
      if (idx!==-1) disciplines.value[idx]={...disciplines.value[idx],name:form.name.trim()}
    } else {
      const created=await post<any>('/disciplines/',{name:form.name.trim()})
      disciplines.value.push(created)
    }
    closeModal()
  } catch (e:any) { formError.value=e?.data?.detail??e?.message??'Erro ao salvar.' } finally { saving.value=false }
}
async function excluir() {
  if (!deletingDisc.value) return
  deleting.value=true; deleteError.value=''
  try {
    await deleteReq(`/disciplines/${deletingDisc.value.id}/`)
    disciplines.value=disciplines.value.filter(d=>d.id!==deletingDisc.value.id)
    showDeleteModal.value=false
  } catch (e:any) { deleteError.value=e?.data?.detail??'Erro ao excluir.' } finally { deleting.value=false }
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  try { disciplines.value=await get<any[]>('/disciplines/') } catch { disciplines.value=[] } finally { loading.value=false }
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
.disc-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:.625rem; }
.skel-card { height:6rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*50ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.mt-3 { margin-top:.75rem; }
.disc-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; flex-direction:column; gap:.625rem; position:relative; transition:border-color .15s, box-shadow .15s; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*40ms); }
.disc-card:hover { border-color:#e5e7eb; box-shadow:0 2px 10px rgba(0,0,0,.05); }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.disc-icon { width:2.5rem; height:2.5rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.disc-name { font-size:.8rem; font-weight:700; color:#111827; line-height:1.3; flex:1; }
.disc-actions { display:flex; gap:.3rem; opacity:0; transition:opacity .15s; }
.disc-card:hover .disc-actions { opacity:1; }
.icon-btn    { width:1.75rem; height:1.75rem; border-radius:.5rem; border:1px solid #e5e7eb; background:white; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#9ca3af; transition:all .13s; }
.icon-btn:hover      { background:#f9fafb; color:#374151; border-color:#d1d5db; }
.icon-btn--del:hover { background:#fef2f2; color:#ef4444; border-color:#fecaca; }
.btn-primary,.btn-cancel,.btn-danger { display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1rem; font-size:.78rem; font-weight:700; border-radius:.75rem; cursor:pointer; white-space:nowrap; transition:all .13s; border:none; }
.btn-primary  { background:#111827; color:white; } .btn-primary:hover:not(:disabled) { background:#1f2937; } .btn-primary:disabled { opacity:.5; cursor:not-allowed; }
.btn-cancel   { background:white; color:#6b7280; border:1px solid #e5e7eb; } .btn-cancel:hover { background:#f9fafb; }
.btn-danger   { background:#ef4444; color:white; } .btn-danger:hover:not(:disabled) { background:#dc2626; }
.field       { display:flex; flex-direction:column; gap:.375rem; }
.field-label { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.field-input { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; }
.field-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.error-msg  { font-size:.72rem; color:#ef4444; font-weight:600; }
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