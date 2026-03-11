<!-- pages/dashboard/coordenador/professores/gerenciar.vue -->
<template>
  <div class="max-w-2xl mx-auto space-y-6">

    <!-- Header -->
    <div class="animate-fade-in">
      <NuxtLink to="/dashboard/coordenador/professores"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-gray-700 transition-colors mb-4">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" />
        Voltar para professores
      </NuxtLink>
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gray-900 flex items-center justify-center flex-shrink-0">
          <Icon name="lucide:users" class="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 class="text-xl font-black text-gray-900 tracking-tight">Gerenciar professores</h2>
          <p class="text-xs text-gray-400 mt-0.5">Adicione, edite, vincule turmas e remova professores</p>
        </div>
      </div>
    </div>

    <!-- Botão novo professor -->
    <button
      class="w-full flex items-center gap-3 px-5 py-4 bg-gray-900 hover:bg-gray-700 text-white rounded-2xl transition-all active:scale-[.99] group animate-fade-up"
      style="animation-delay:40ms"
      @click="openCreate">
      <div class="w-8 h-8 rounded-xl bg-white/10 group-hover:bg-white/20 flex items-center justify-center flex-shrink-0 transition-colors">
        <Icon name="lucide:user-plus" class="w-4 h-4" />
      </div>
      <span class="font-bold text-sm">Adicionar novo professor</span>
      <Icon name="lucide:arrow-right" class="w-4 h-4 ml-auto opacity-40 group-hover:translate-x-0.5 group-hover:opacity-70 transition-all" />
    </button>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-2 animate-fade-up" style="animation-delay:80ms">
      <div v-for="i in 4" :key="i"
        class="h-16 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`animation-delay:${i*40}ms`" />
    </div>

    <!-- Lista de professores -->
    <div v-else-if="teachers.length"
      class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up"
      style="animation-delay:80ms">

      <!-- Barra busca -->
      <div class="flex items-center justify-between px-5 py-3 border-b border-gray-50">
        <span class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
          {{ teachers.length }} professor{{ teachers.length !== 1 ? 'es' : '' }}
        </span>
        <div class="relative">
          <Icon name="lucide:search" class="w-3.5 h-3.5 text-gray-300 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input v-model="busca"
            class="pl-8 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600 w-40 focus:w-52 transition-all"
            placeholder="Filtrar..." />
        </div>
      </div>

      <div v-if="!teachersFiltrados.length" class="flex flex-col items-center py-10">
        <Icon name="lucide:search-x" class="w-6 h-6 text-gray-200 mb-2" />
        <p class="text-xs text-gray-400">Nenhum professor encontrado para "{{ busca }}"</p>
      </div>

      <div v-else class="divide-y divide-gray-50">
        <div v-for="(prof, idx) in teachersFiltrados" :key="prof.id">

          <!-- Linha clicável -->
          <div
            class="flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50/60 transition-colors group cursor-pointer"
            @click="toggleExpand(prof.id)">

            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-xs font-black"
              :style="`background-color:${avatarBg(idx)}18; color:${avatarBg(idx)}`">
              {{ initials(prof.name) }}
            </div>

            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-gray-900 truncate">{{ prof.name }}</p>
              <p class="text-xs text-gray-400 truncate">{{ prof.email }}</p>
            </div>

            <span class="hidden sm:inline-flex text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 flex-shrink-0">
              {{ vinculosDoProf(prof.id).length }} vínculo{{ vinculosDoProf(prof.id).length !== 1 ? 's' : '' }}
            </span>

            <span class="hidden sm:inline-flex text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0"
              :class="prof.is_active !== false ? 'bg-emerald-50 text-emerald-600' : 'bg-gray-100 text-gray-400'">
              {{ prof.is_active !== false ? 'Ativo' : 'Inativo' }}
            </span>

            <!-- Ações (stopPropagation para não abrir painel) -->
            <div class="flex items-center gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
              @click.stop>
              <button
                class="w-8 h-8 rounded-lg hover:bg-blue-50 flex items-center justify-center transition-colors"
                title="Editar dados"
                @click="openEdit(prof)">
                <Icon name="lucide:pencil" class="w-3.5 h-3.5 text-blue-500" />
              </button>
              <button
                class="w-8 h-8 rounded-lg hover:bg-red-50 flex items-center justify-center transition-colors"
                title="Excluir professor"
                @click="openDelete(prof)">
                <Icon name="lucide:trash-2" class="w-3.5 h-3.5 text-red-400" />
              </button>
            </div>

            <Icon
              :name="expandedIds.has(prof.id) ? 'lucide:chevron-up' : 'lucide:chevron-down'"
              class="w-4 h-4 text-gray-300 flex-shrink-0 transition-transform" />
          </div>

          <!-- Painel de vínculos expandível -->
          <div v-if="expandedIds.has(prof.id)"
            class="px-5 pt-2 pb-4 bg-gray-50/50 border-t border-gray-50">

            <p class="text-[11px] font-black text-gray-400 uppercase tracking-wider mb-3 mt-1 flex items-center gap-1.5">
              <Icon name="lucide:link" class="w-3.5 h-3.5" />
              Turmas e disciplinas
            </p>

            <!-- Tags dos vínculos existentes -->
            <div v-if="vinculosDoProf(prof.id).length" class="flex flex-wrap gap-2 mb-3">
              <div v-for="v in vinculosDoProf(prof.id)" :key="v.id"
                class="flex items-center gap-1.5 px-2.5 py-1.5 bg-white border border-gray-200 rounded-xl text-xs group/tag">
                <Icon name="lucide:book-open" class="w-3 h-3 text-gray-400 flex-shrink-0" />
                <span class="font-bold text-gray-800">{{ className(v.class_id) }}</span>
                <span class="text-gray-300">·</span>
                <span class="text-gray-600">{{ disciplineName(v.discipline_id) }}</span>
                <button
                  class="ml-1 w-4 h-4 rounded-full hover:bg-red-100 flex items-center justify-center transition-colors opacity-0 group-hover/tag:opacity-100"
                  title="Remover vínculo"
                  @click="removeVinculo(v.id)">
                  <Icon name="lucide:x" class="w-2.5 h-2.5 text-red-400" />
                </button>
              </div>
            </div>
            <p v-else class="text-xs text-gray-400 italic mb-3">Nenhum vínculo cadastrado.</p>

            <!-- Adicionar vínculo -->
            <div class="flex items-end gap-2 flex-wrap">
              <div class="flex-1 min-w-[130px]">
                <label class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">Turma</label>
                <select v-model="novoVinculo[prof.id].class_id"
                  class="w-full text-xs border border-gray-200 rounded-xl px-2.5 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-700">
                  <option value="">Selecionar turma</option>
                  <option v-for="c in allClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="flex-1 min-w-[130px]">
                <label class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">Disciplina</label>
                <select v-model="novoVinculo[prof.id].discipline_id"
                  class="w-full text-xs border border-gray-200 rounded-xl px-2.5 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-700">
                  <option value="">Selecionar disciplina</option>
                  <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
              <button
                :disabled="!novoVinculo[prof.id]?.class_id || !novoVinculo[prof.id]?.discipline_id || addingVinculo === prof.id"
                class="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex-shrink-0"
                :class="!novoVinculo[prof.id]?.class_id || !novoVinculo[prof.id]?.discipline_id
                  ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                  : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
                @click="addVinculo(prof.id)">
                <svg v-if="addingVinculo === prof.id" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                </svg>
                <Icon v-else name="lucide:plus" class="w-3.5 h-3.5" />
                Vincular
              </button>
            </div>

            <p v-if="vinculoError[prof.id]" class="text-[11px] text-red-500 mt-2 flex items-center gap-1">
              <Icon name="lucide:alert-circle" class="w-3 h-3" />
              {{ vinculoError[prof.id] }}
            </p>
          </div>

        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else
      class="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-up"
      style="animation-delay:80ms">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:users" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">Nenhum professor cadastrado ainda</p>
      <button class="mt-3 text-xs font-bold text-blue-500 hover:text-blue-700 transition-colors" @click="openCreate">
        Adicionar o primeiro →
      </button>
    </div>

    <!-- ── MODAL: CRIAR / EDITAR ── -->
    <Transition name="modal">
      <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="closeForm" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-modal-in">

          <div class="flex items-center gap-3 mb-6">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="editingProf ? 'bg-blue-50' : 'bg-gray-900'">
              <Icon :name="editingProf ? 'lucide:pencil' : 'lucide:user-plus'"
                class="w-4 h-4" :class="editingProf ? 'text-blue-500' : 'text-white'" />
            </div>
            <div>
              <h3 class="text-base font-black text-gray-900">
                {{ editingProf ? 'Editar professor' : 'Novo professor' }}
              </h3>
              <p class="text-xs text-gray-400">{{ editingProf ? editingProf.name : 'Preencha os dados abaixo' }}</p>
            </div>
            <button class="ml-auto w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors"
              @click="closeForm">
              <Icon name="lucide:x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Nome completo</label>
              <input v-model="form.name" type="text" placeholder="Ex: Prof. João Silva"
                class="w-full px-3.5 py-2.5 border rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 transition-all"
                :class="errors.name ? 'border-red-300 focus:ring-red-100' : 'border-gray-200 focus:ring-blue-200 focus:border-blue-300'" />
              <p v-if="errors.name" class="text-[11px] text-red-500 mt-1 flex items-center gap-1">
                <Icon name="lucide:alert-circle" class="w-3 h-3" />{{ errors.name }}
              </p>
            </div>

            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">E-mail</label>
              <input v-model="form.email" type="email" placeholder="prof@escola.edu.br"
                class="w-full px-3.5 py-2.5 border rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 transition-all"
                :class="errors.email ? 'border-red-300 focus:ring-red-100' : 'border-gray-200 focus:ring-blue-200 focus:border-blue-300'" />
              <p v-if="errors.email" class="text-[11px] text-red-500 mt-1 flex items-center gap-1">
                <Icon name="lucide:alert-circle" class="w-3 h-3" />{{ errors.email }}
              </p>
            </div>

            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">
                {{ editingProf ? 'Nova senha (deixe em branco para manter)' : 'Senha' }}
              </label>
              <div class="relative">
                <input v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  :placeholder="editingProf ? '••••••••' : 'Mínimo 6 caracteres'"
                  class="w-full px-3.5 py-2.5 pr-10 border rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 transition-all"
                  :class="errors.password ? 'border-red-300 focus:ring-red-100' : 'border-gray-200 focus:ring-blue-200 focus:border-blue-300'" />
                <button type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500 transition-colors"
                  @click="showPassword = !showPassword">
                  <Icon :name="showPassword ? 'lucide:eye-off' : 'lucide:eye'" class="w-4 h-4" />
                </button>
              </div>
              <p v-if="errors.password" class="text-[11px] text-red-500 mt-1 flex items-center gap-1">
                <Icon name="lucide:alert-circle" class="w-3 h-3" />{{ errors.password }}
              </p>
            </div>

            <div v-if="editingProf"
              class="flex items-center justify-between px-3.5 py-3 bg-gray-50 rounded-xl border border-gray-100">
              <div>
                <p class="text-sm font-bold text-gray-700">Professor ativo</p>
                <p class="text-xs text-gray-400 mt-0.5">Inativos não conseguem acessar o sistema</p>
              </div>
              <button
                class="relative w-11 h-6 rounded-full transition-colors flex-shrink-0"
                :class="form.is_active ? 'bg-emerald-400' : 'bg-gray-200'"
                @click="form.is_active = !form.is_active">
                <span class="absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-all duration-200"
                  :class="form.is_active ? 'left-5' : 'left-0.5'" />
              </button>
            </div>

            <div v-if="formError"
              class="flex items-center gap-2 px-3.5 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
              <p class="text-xs text-red-600 font-medium">{{ formError }}</p>
            </div>

            <div class="flex gap-2 pt-1">
              <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600 transition-all"
                @click="closeForm">Cancelar</button>
              <button :disabled="saving"
                class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
                :class="saving
                  ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                  : editingProf
                    ? 'bg-blue-600 hover:bg-blue-700 text-white active:scale-95'
                    : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
                @click="submitForm">
                <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                </svg>
                <Icon v-else :name="editingProf ? 'lucide:save' : 'lucide:user-plus'" class="w-4 h-4" />
                {{ saving ? 'Salvando...' : editingProf ? 'Salvar alterações' : 'Adicionar professor' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── MODAL: EXCLUIR ── -->
    <Transition name="modal">
      <div v-if="showDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showDelete = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:trash-2" class="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h3 class="text-base font-black text-gray-900">Excluir professor</h3>
              <p class="text-xs text-gray-400 mt-0.5">Esta ação não pode ser desfeita</p>
            </div>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed mb-5">
            Tem certeza que deseja excluir
            <span class="font-bold text-gray-900">{{ deletingProf?.name }}</span>?
            Todos os vínculos com turmas e simulados serão removidos permanentemente.
          </p>
          <div v-if="deleteError"
            class="flex items-center gap-2 px-3.5 py-2.5 bg-red-50 border border-red-100 rounded-xl mb-4">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-600 font-medium">{{ deleteError }}</p>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600 transition-all"
              @click="showDelete = false">Cancelar</button>
            <button :disabled="deleting"
              class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="deleting ? 'bg-red-200 text-red-300 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700 text-white active:scale-95'"
              @click="confirmDelete">
              <svg v-if="deleting" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ deleting ? 'Excluindo...' : 'Sim, excluir' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl text-white text-sm font-bold"
        :class="toast.type === 'success' ? 'bg-emerald-600' : 'bg-red-600'">
        <Icon :name="toast.type === 'success' ? 'lucide:check-circle-2' : 'lucide:alert-circle'" class="w-5 h-5 flex-shrink-0" />
        {{ toast.message }}
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get, post, patch, delete: del } = useApi()

// ── Dados principais ──
const teachers    = ref<any[]>([])
const vinculos    = ref<any[]>([])
const allClasses  = ref<any[]>([])
const disciplines = ref<any[]>([])
const loading     = ref(true)
const busca       = ref('')

// ── Expand/collapse de vínculos ──
const expandedIds = ref(new Set<number>())

function toggleExpand(id: number) {
  if (expandedIds.value.has(id)) expandedIds.value.delete(id)
  else expandedIds.value.add(id)
}

// ── Computed ──
const teachersFiltrados = computed(() => {
  if (!busca.value) return teachers.value
  const q = busca.value.toLowerCase()
  return teachers.value.filter(t =>
    t.name.toLowerCase().includes(q) || t.email.toLowerCase().includes(q)
  )
})

function vinculosDoProf(profId: number) {
  return vinculos.value.filter(v => v.teacher_user_id === profId)
}

function className(id: number) {
  return allClasses.value.find(c => c.id === id)?.name ?? `Turma #${id}`
}
function disciplineName(id: number) {
  return disciplines.value.find(d => d.id === id)?.name ?? `Disc. #${id}`
}

// ── Estado de novo vínculo por professor ──
const novoVinculo   = reactive<Record<number, { class_id: number | ''; discipline_id: number | '' }>>({})
const addingVinculo = ref<number | null>(null)
const vinculoError  = reactive<Record<number, string>>({})

function ensureVinculo(profId: number) {
  if (!novoVinculo[profId]) {
    novoVinculo[profId] = { class_id: '', discipline_id: '' }
  }
}

// Garante estado ao expandir
watch(() => [...expandedIds.value], (ids) => {
  for (const id of ids) ensureVinculo(id)
})

async function addVinculo(profId: number) {
  const v = novoVinculo[profId]
  if (!v?.class_id || !v?.discipline_id) return
  addingVinculo.value = profId
  vinculoError[profId] = ''
  try {
    const created = await post<any>('/school/teacher-subjects', {
      teacher_user_id: profId,
      class_id: v.class_id,
      discipline_id: v.discipline_id,
    })
    vinculos.value.push(created)
    novoVinculo[profId] = { class_id: '', discipline_id: '' }
    showToast('success', 'Vínculo adicionado!')
  } catch (e: any) {
    vinculoError[profId] = e?.data?.detail ?? 'Erro ao adicionar vínculo.'
  } finally {
    addingVinculo.value = null
  }
}

async function removeVinculo(linkId: number) {
  try {
    await del(`/school/teacher-subjects/${linkId}`)
    vinculos.value = vinculos.value.filter(v => v.id !== linkId)
    showToast('success', 'Vínculo removido.')
  } catch (e: any) {
    showToast('error', e?.data?.detail ?? 'Erro ao remover vínculo.')
  }
}

// ── Form criar / editar ──
const showForm     = ref(false)
const editingProf  = ref<any>(null)
const saving       = ref(false)
const showPassword = ref(false)
const formError    = ref('')
const form   = reactive({ name: '', email: '', password: '', is_active: true })
const errors = reactive({ name: '', email: '', password: '' })

function openCreate() {
  editingProf.value = null
  Object.assign(form, { name: '', email: '', password: '', is_active: true })
  Object.assign(errors, { name: '', email: '', password: '' })
  formError.value = ''
  showPassword.value = false
  showForm.value = true
}

function openEdit(prof: any) {
  editingProf.value = prof
  Object.assign(form, { name: prof.name, email: prof.email, password: '', is_active: prof.is_active !== false })
  Object.assign(errors, { name: '', email: '', password: '' })
  formError.value = ''
  showPassword.value = false
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  setTimeout(() => { editingProf.value = null }, 200)
}

function validate(): boolean {
  let ok = true
  Object.assign(errors, { name: '', email: '', password: '' })
  if (!form.name.trim()) { errors.name = 'Nome é obrigatório.'; ok = false }
  if (!form.email.trim()) { errors.email = 'E-mail é obrigatório.'; ok = false }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'E-mail inválido.'; ok = false }
  if (!editingProf.value) {
    if (!form.password.trim()) { errors.password = 'Senha é obrigatória.'; ok = false }
    else if (form.password.length < 6) { errors.password = 'Mínimo 6 caracteres.'; ok = false }
  } else if (form.password && form.password.length < 6) {
    errors.password = 'Nova senha deve ter mínimo 6 caracteres.'; ok = false
  }
  return ok
}

async function submitForm() {
  if (!validate()) return
  saving.value = true
  formError.value = ''
  try {
    if (editingProf.value) {
      const payload: any = { name: form.name, email: form.email, is_active: form.is_active }
      if (form.password.trim()) payload.password = form.password
      const updated = await patch<any>(`/auth/users/${editingProf.value.id}`, payload)
      const idx = teachers.value.findIndex(t => t.id === editingProf.value.id)
      if (idx !== -1) teachers.value[idx] = { ...teachers.value[idx], ...updated }
      showToast('success', 'Professor atualizado!')
    } else {
      const created = await post<any>('/auth/users', {
        name: form.name, email: form.email, password: form.password, role: 'TEACHER',
      })
      teachers.value.push(created)
      ensureVinculo(created.id)
      showToast('success', `${form.name} adicionado com sucesso!`)
    }
    closeForm()
  } catch (e: any) {
    formError.value = e?.data?.detail ?? e?.message ?? 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

// ── Delete professor ──
const showDelete   = ref(false)
const deletingProf = ref<any>(null)
const deleting     = ref(false)
const deleteError  = ref('')

function openDelete(prof: any) {
  deletingProf.value = prof
  deleteError.value = ''
  showDelete.value = true
}

async function confirmDelete() {
  if (!deletingProf.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await del(`/auth/users/${deletingProf.value.id}`)
    teachers.value = teachers.value.filter(t => t.id !== deletingProf.value.id)
    vinculos.value = vinculos.value.filter(v => v.teacher_user_id !== deletingProf.value.id)
    showDelete.value = false
    showToast('success', 'Professor excluído.')
  } catch (e: any) {
    deleteError.value = e?.data?.detail ?? 'Erro ao excluir.'
  } finally {
    deleting.value = false
  }
}

// ── Toast ──
const toast = ref<{ type: 'success' | 'error'; message: string } | null>(null)
function showToast(type: 'success' | 'error', message: string) {
  toast.value = { type, message }
  setTimeout(() => { toast.value = null }, 3000)
}

// ── Helpers visuais ──
const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']
function avatarBg(idx: number) { return COLORS[idx % COLORS.length] }
function initials(name: string) {
  return name.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase()
}

// ── Fetch inicial ──
onMounted(async () => {
  const [teachersRes, vinculosRes, classesRes, discRes] = await Promise.allSettled([
    get<any[]>('/school/teachers'),
    get<any[]>('/school/teacher-subjects'),
    get<any[]>('/school/classes'),
    get<any[]>('/disciplines/'),
  ])

  if (teachersRes.status === 'fulfilled') teachers.value    = teachersRes.value
  if (vinculosRes.status === 'fulfilled') vinculos.value    = vinculosRes.value
  if (classesRes.status === 'fulfilled')  allClasses.value  = classesRes.value
  if (discRes.status === 'fulfilled')     disciplines.value = discRes.value

  for (const t of teachers.value) ensureVinculo(t.id)

  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in  { from { opacity:0; transform:translateY(6px)  } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up  { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
@keyframes modal-in { from { opacity:0; transform:scale(.94) translateY(8px) } to { opacity:1; transform:scale(1) translateY(0) } }
@keyframes toast-in { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }

.animate-fade-in  { animation: fade-in  0.3s  ease both }
.animate-fade-up  { animation: fade-up  0.38s ease both }
.animate-modal-in { animation: modal-in 0.22s cubic-bezier(0.34,1.56,0.64,1) both }

.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease }
.modal-enter-from,  .modal-leave-to      { opacity: 0 }

.toast-enter-active { animation: toast-in 0.25s ease both }
.toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease }
.toast-leave-to     { opacity: 0; transform: translateY(8px) }
</style>