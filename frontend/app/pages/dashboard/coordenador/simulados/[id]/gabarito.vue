<!-- pages/dashboard/coordenador/simulados/[id]/gabarito.vue -->
<template>
  <div class="max-w-3xl mx-auto space-y-5">

    <!-- Voltar -->
    <div class="animate-fade-in">
      <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-gray-400 hover:text-gray-700 transition-colors mb-4">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" />
        Voltar para o simulado
      </NuxtLink>
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-black text-gray-900 tracking-tight">Gabarito</h2>
          <p class="text-sm text-gray-400 mt-0.5">
            <span v-if="!loading">{{ exam?.title }} · {{ questions.length }} questões</span>
            <span v-else class="inline-block w-40 h-4 bg-gray-100 rounded animate-pulse" />
          </p>
        </div>
        <div class="flex items-center gap-2">
          <!-- Progresso -->
          <div class="flex items-center gap-2 px-3.5 py-2 bg-gray-50 rounded-xl border border-gray-100">
            <span class="text-xs font-bold text-gray-500">Com gabarito:</span>
            <span class="text-sm font-black" :class="allAnswered ? 'text-emerald-600' : 'text-amber-600'">
              {{ answeredCount }}/{{ questions.length }}
            </span>
          </div>
          <!-- Salvar todos -->
          <button
            :disabled="savingAll || !pendingChanges.size"
            class="flex items-center gap-2 px-4 py-2.5 text-sm font-bold rounded-xl transition-all"
            :class="savingAll || !pendingChanges.size
              ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
              : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
            @click="saveAll">
            <svg v-if="savingAll" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            <Icon v-else name="lucide:save" class="w-4 h-4" />
            {{ savingAll ? 'Salvando...' : `Salvar${pendingChanges.size ? ` (${pendingChanges.size})` : ''}` }}
          </button>
        </div>
      </div>
    </div>

    <!-- Status card -->
    <div v-if="!loading && allAnswered"
      class="flex items-center gap-3 px-4 py-3 bg-emerald-50 border border-emerald-100 rounded-2xl animate-fade-up">
      <Icon name="lucide:check-circle-2" class="w-5 h-5 text-emerald-500 flex-shrink-0" />
      <p class="text-sm font-bold text-emerald-700">Todas as questões têm gabarito definido.</p>
    </div>
    <div v-else-if="!loading && questions.length && !allAnswered"
      class="flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-100 rounded-2xl animate-fade-up">
      <Icon name="lucide:alert-triangle" class="w-5 h-5 text-amber-500 flex-shrink-0" />
      <p class="text-sm font-bold text-amber-700">
        {{ questions.length - answeredCount }} questão(ões) ainda sem gabarito.
        O simulado só pode ser travado quando todas estiverem preenchidas.
      </p>
    </div>

    <!-- Filtros -->
    <div v-if="!loading && questions.length" class="flex items-center gap-2 flex-wrap animate-fade-up" style="animation-delay:40ms">
      <button v-for="f in filtros" :key="f.value"
        class="px-3 py-1.5 rounded-xl text-xs font-bold border-2 transition-all"
        :class="filtroAtivo === f.value
          ? 'border-gray-900 bg-gray-900 text-white'
          : 'border-gray-100 bg-white text-gray-500 hover:border-gray-300'"
        @click="filtroAtivo = filtroAtivo === f.value ? 'all' : f.value">
        {{ f.label }}
        <span class="ml-1 px-1.5 py-0.5 rounded-full text-[10px]"
          :class="filtroAtivo === f.value ? 'bg-white/20' : 'bg-gray-100'">
          {{ f.count }}
        </span>
      </button>

      <!-- Filtro disciplina -->
      <select v-model="filterDisc"
        class="ml-auto text-xs border border-gray-200 rounded-xl px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600">
        <option value="">Todas disciplinas</option>
        <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-36 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`animation-delay:${i*40}ms`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!questions.length"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-100">
      <Icon name="lucide:file-x" class="w-8 h-8 text-gray-200 mb-2" />
      <p class="text-sm font-bold text-gray-400">Nenhuma questão encontrada</p>
    </div>

    <!-- Lista de questões -->
    <div v-else class="space-y-3">
      <div v-for="(q, idx) in questoesFiltradas" :key="q.id"
        class="bg-white rounded-2xl border transition-all duration-200 overflow-hidden animate-fade-up"
        :class="[
          pendingChanges.has(q.id) ? 'border-amber-200 shadow-sm shadow-amber-50' : 'border-gray-100',
          savedIds.has(q.id) ? 'border-emerald-200' : '',
        ]"
        :style="`animation-delay:${idx*30}ms`">

        <!-- Header questão -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-gray-50">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-black text-gray-400 tabular-nums">Q{{ idx + 1 }}</span>
            <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
              {{ disciplineName(q.discipline_id) }}
            </span>
            <!-- Estado do gabarito -->
            <span v-if="savedIds.has(q.id)"
              class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 flex items-center gap-1">
              <Icon name="lucide:check" class="w-2.5 h-2.5" /> Salvo
            </span>
            <span v-else-if="pendingChanges.has(q.id)"
              class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-600">
              Alterado
            </span>
            <span v-else-if="localAnswers[q.id]"
              class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">
              Gabarito: {{ localAnswers[q.id] }}
            </span>
            <span v-else
              class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-gray-50 text-gray-400">
              Sem gabarito
            </span>
          </div>
          <!-- Salvar individual -->
          <button
            v-if="pendingChanges.has(q.id)"
            class="text-[11px] font-bold px-2.5 py-1.5 bg-gray-900 hover:bg-gray-700 text-white rounded-lg transition-all flex items-center gap-1 active:scale-95"
            @click="saveOne(q.id)">
            <Icon name="lucide:save" class="w-3 h-3" />
            Salvar
          </button>
        </div>

        <!-- Enunciado -->
        <div class="px-5 py-3">
          <div class="text-sm text-gray-800 leading-relaxed mb-4 question-content" v-html="renderStem(q.stem, q.images)" />

          <!-- Alternativas clicáveis -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              v-for="opt in q.options" :key="opt.label"
              class="flex items-start gap-2.5 px-3.5 py-2.5 rounded-xl border-2 text-left transition-all duration-150 group"
              :class="localAnswers[q.id] === opt.label
                ? 'border-emerald-400 bg-emerald-50'
                : 'border-gray-100 bg-gray-50 hover:border-gray-300 hover:bg-white'"
              @click="setAnswer(q.id, opt.label)">
              <span class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-black flex-shrink-0 transition-all"
                :class="localAnswers[q.id] === opt.label
                  ? 'bg-emerald-500 text-white'
                  : 'bg-white border border-gray-200 text-gray-400 group-hover:border-gray-300'">
                {{ opt.label }}
              </span>
              <div class="text-sm leading-snug mt-0.5 question-content"
                :class="localAnswers[q.id] === opt.label ? 'text-emerald-800 font-semibold' : 'text-gray-600'"
                v-html="renderOption(opt.text, opt.label, q.images)" />
            </button>
          </div>

          <!-- Limpar gabarito -->
          <button v-if="localAnswers[q.id]"
            class="mt-2 text-[11px] text-gray-400 hover:text-red-500 font-medium transition-colors flex items-center gap-1"
            @click="clearAnswer(q.id)">
            <Icon name="lucide:x" class="w-3 h-3" />
            Limpar gabarito
          </button>
        </div>
      </div>
    </div>

    <!-- Sucesso global -->
    <Transition name="toast">
      <div v-if="showSuccess"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 bg-emerald-600 text-white rounded-2xl shadow-xl">
        <Icon name="lucide:check-circle-2" class="w-5 h-5" />
        <p class="text-sm font-bold">Gabarito salvo com sucesso!</p>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

useHead({
  link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }],
})

const route  = useRoute()
const { get, patch } = useApi()
const { renderStem, renderOption } = useQuestionRenderer()
const examId = computed(() => Number(route.params.id))

const exam        = ref<any>(null)
const questions   = ref<any[]>([])
const disciplines = ref<any[]>([])
const loading     = ref(true)

// Estado local do gabarito (question_id → label)
const localAnswers  = reactive<Record<number, string>>({})
const pendingChanges = ref(new Set<number>())  // ids com mudança não salva
const savedIds       = ref(new Set<number>())  // ids recém-salvos

const savingAll   = ref(false)
const showSuccess = ref(false)
const filterDisc  = ref<number | ''>('')
const filtroAtivo = ref<'all' | 'answered' | 'missing'>('all')

const answeredCount = computed(() => questions.value.filter(q => localAnswers[q.id]).length)
const allAnswered   = computed(() => questions.value.length > 0 && answeredCount.value === questions.value.length)

const filtros = computed(() => [
  { value: 'all',      label: 'Todas',         count: questions.value.length },
  { value: 'answered', label: 'Com gabarito',   count: answeredCount.value },
  { value: 'missing',  label: 'Sem gabarito',   count: questions.value.length - answeredCount.value },
])

const questoesFiltradas = computed(() => {
  let list = questions.value
  if (filterDisc.value)        list = list.filter(q => q.discipline_id === filterDisc.value)
  if (filtroAtivo.value === 'answered') list = list.filter(q => localAnswers[q.id])
  if (filtroAtivo.value === 'missing')  list = list.filter(q => !localAnswers[q.id])
  return list
})

function disciplineName(id: number) {
  return disciplines.value.find(d => d.id === id)?.name ?? `Disc. #${id}`
}

function setAnswer(qid: number, label: string) {
  localAnswers[qid] = label
  const q = questions.value.find((q: any) => q.id === qid)
  if (label !== (q?.correct_label ?? '')) {
    pendingChanges.value.add(qid)
  } else {
    pendingChanges.value.delete(qid)
  }
  savedIds.value.delete(qid)
}

function clearAnswer(qid: number) {
  localAnswers[qid] = ''
  const q = questions.value.find((q: any) => q.id === qid)
  if (q?.correct_label) {
    pendingChanges.value.add(qid)
  } else {
    pendingChanges.value.delete(qid)
  }
  savedIds.value.delete(qid)
}

async function saveOne(qid: number) {
  const q = questions.value.find(q => q.id === qid)
  if (!q) return
  try {
    await patch(`/exams/${examId.value}/questions/${qid}`, {
      correct_label: localAnswers[qid] || null,
    })
    // Atualiza o original
    q.correct_label = localAnswers[qid] || null
    pendingChanges.value.delete(qid)
    savedIds.value.add(qid)
    setTimeout(() => savedIds.value.delete(qid), 3000)
  } catch (e: any) {
    console.error(e)
  }
}

async function saveAll() {
  if (!pendingChanges.value.size) return
  savingAll.value = true
  try {
    const ids = [...pendingChanges.value]
    await Promise.all(ids.map(qid =>
      patch(`/exams/${examId.value}/questions/${qid}`, {
        correct_label: localAnswers[qid] || null,
      }).then(() => {
        const q = questions.value.find(q => q.id === qid)
        if (q) q.correct_label = localAnswers[qid] || null
        pendingChanges.value.delete(qid)
        savedIds.value.add(qid)
      })
    ))
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
      savedIds.value.clear()
    }, 3000)
  } catch (e: any) {
    console.error(e)
  } finally {
    savingAll.value = false
  }
}

onMounted(async () => {
  const [examRes, questionsRes, discRes] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any[]>(`/exams/${examId.value}/questions`),
    get<any[]>('/disciplines/'),
  ])

  if (examRes.status === 'fulfilled')      exam.value        = examRes.value
  if (discRes.status === 'fulfilled')      disciplines.value = discRes.value
  if (questionsRes.status === 'fulfilled') {
    questions.value = questionsRes.value.map((q: any) => ({ ...q, images: q.images ?? [] }))
    // Inicializa estado local com gabaritos existentes
    for (const q of questionsRes.value) {
      localAnswers[q.id] = q.correct_label ?? ''
    }
  }

  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in  { from { opacity:0; transform:translateY(6px)  } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up  { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
@keyframes toast-in { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:translateY(0) } }

.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }

.toast-enter-active { animation: toast-in 0.25s ease both }
.toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease }
.toast-leave-to     { opacity: 0; transform: translateY(8px) }
.question-content :deep(img.question-img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 6px 0;
  display: block;
}
.question-content :deep(.katex-display) { margin: 8px 0; overflow-x: auto; }
.question-content :deep(.katex) { font-size: 1em; }
.question-content :deep(.math-error) { color: #dc3545; font-family: monospace; font-size: 0.8em; }
</style>