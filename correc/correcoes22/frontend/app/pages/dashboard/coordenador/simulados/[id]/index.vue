<!-- pages/dashboard/coordenador/simulados/[id].vue -->
<template>
  <div class="space-y-6">

    <!-- ── BREADCRUMB ── -->
    <!-- OVERLAY: Gerando PDFs -->
  <Transition name="pop">
    <div v-if="batchOverlay" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-8 flex flex-col items-center gap-6">
        <!-- Ícone animado -->
        <div class="relative w-20 h-20">
          <svg class="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
            <circle cx="40" cy="40" r="34" fill="none" stroke="#e5e7eb" stroke-width="6"/>
            <circle cx="40" cy="40" r="34" fill="none" stroke="#6366f1" stroke-width="6"
              stroke-linecap="round"
              :stroke-dasharray="`${(batchElapsed % 20) * 10.7} 214`"
              class="transition-all duration-1000"/>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <Icon name="lucide:book-open" class="w-8 h-8 text-indigo-500" />
          </div>
        </div>
        <!-- Título -->
        <div class="text-center">
          <p class="text-lg font-bold text-gray-900">Gerando cadernos</p>
          <p class="text-sm text-gray-400 mt-1">{{ batchOverlayMsg }}</p>
        </div>
        <!-- Timer -->
        <div class="w-full bg-gray-50 rounded-xl px-6 py-4 flex items-center justify-center gap-2">
          <Icon name="lucide:timer" class="w-4 h-4 text-gray-400" />
          <span class="text-2xl font-mono font-bold text-gray-700">{{ fmtTime(batchElapsed) }}</span>
          <span class="text-xs text-gray-400 ml-1">decorrido</span>
        </div>
        <p class="text-xs text-gray-400">Aguarde, não feche esta janela…</p>
      </div>
    </div>
  </Transition>

  <div class="animate-fade-in">
      <NuxtLink to="/dashboard/coordenador/simulados"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-gray-600 transition-colors">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" />
        Todos os simulados
      </NuxtLink>
    </div>

    <!-- ── HEADER CARD ── -->
    <div class="animate-fade-in" style="animation-delay:30ms">
      <!-- Skeleton -->
      <div v-if="loading" class="h-24 bg-white rounded-2xl border border-gray-100 animate-pulse" />

      <div v-else class="bg-white rounded-2xl border border-gray-100 px-6 py-5">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <!-- Ícone + título + meta -->
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="statusBg(exam?.status)">
              <Icon :name="statusIcon(exam?.status)" class="w-5 h-5" :class="statusIconColor(exam?.status)" />
            </div>
            <div>
              <div class="flex items-center gap-2.5 mb-1 flex-wrap">
                <h2 class="text-xl font-black text-gray-900 tracking-tight leading-tight">{{ exam?.title }}</h2>
                <span class="text-[11px] font-bold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
                  :class="statusBadge(exam?.status)">
                  <span class="w-1.5 h-1.5 rounded-full" :class="statusDot(exam?.status)" />
                  {{ statusLabel(exam?.status) }}
                </span>
              </div>
              <p class="text-xs text-gray-400 flex items-center gap-1.5">
                <span>{{ exam?.area || 'Sem área definida' }}</span>
                <span class="text-gray-200">·</span>
                <span>{{ exam?.options_count }} alternativas</span>
                <span class="text-gray-200">·</span>
                <span>{{ answerSourceLabel(exam?.answer_source) }}</span>
              </p>
            </div>
          </div>

          <!-- Ações -->
          <div class="flex items-center gap-2 flex-wrap">
            <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/editar`"
              class="flex items-center gap-1.5 px-3 py-2 border border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600 text-xs font-bold rounded-xl transition-all">
              <Icon name="lucide:settings-2" class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">Configurar</span>
            </NuxtLink>
            <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/gabarito`"
              class="flex items-center gap-1.5 px-3 py-2 border border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600 text-xs font-bold rounded-xl transition-all">
              <Icon name="lucide:check-square" class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">Gabarito</span>
            </NuxtLink>
            <button v-if="exam?.status === 'collecting'"
              class="flex items-center gap-1.5 px-3 py-2 bg-gray-900 hover:bg-gray-700 text-white text-xs font-bold rounded-xl transition-all active:scale-95"
              @click="showLockModal = true">
              <Icon name="lucide:lock" class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">Travar simulado</span>
            </button>
            <button v-if="exam?.status === 'locked'"
              class="flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition-all active:scale-95"
              @click="showGenerateModal = true">
              <Icon name="lucide:book-open" class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">Gerar cadernos</span>
            </button>
            <span v-if="exam?.status === 'generated' || exam?.status === 'published'"
              class="flex items-center gap-1.5 px-3 py-2 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-xl">
              <Icon name="lucide:check-circle-2" class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">{{ exam?.status === 'published' ? 'Publicado' : 'Cadernos gerados' }}</span>
            </span>
          </div>
        </div>

        <!-- Stat strip dentro do header -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-px mt-5 pt-4 border-t border-gray-50">
          <div v-for="s in statCards" :key="s.label" class="flex items-center gap-2.5 px-1">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :class="s.iconBg">
              <Icon :name="s.icon" class="w-3.5 h-3.5" :class="s.iconColor" />
            </div>
            <div>
              <p class="text-base font-black text-gray-900 tabular-nums leading-none">
                <span v-if="loading" class="inline-block w-5 h-4 bg-gray-100 rounded animate-pulse" />
                <span v-else>{{ s.value }}</span>
              </p>
              <p class="text-[10px] text-gray-400 font-medium mt-0.5 leading-tight">{{ s.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── GRID PRINCIPAL: progresso (esq) + turmas (dir) ── -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4 animate-fade-up" style="animation-delay:80ms">

      <!-- Progresso disciplinas -->
      <div class="lg:col-span-3 bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:bar-chart-2" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Progresso por disciplina</h3>
          </div>
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/editar`"
            class="text-[11px] font-bold text-blue-500 hover:text-blue-600 flex items-center gap-1 transition-colors">
            <Icon name="lucide:settings-2" class="w-3 h-3" />
            Configurar cotas
          </NuxtLink>
        </div>
        <div v-if="loadingProgress" class="p-4 space-y-3">
          <div v-for="i in 3" :key="i" class="h-14 bg-gray-50 rounded-xl animate-pulse" />
        </div>
        <div v-else-if="!progress?.disciplines?.length" class="flex flex-col items-center justify-center py-12">
          <Icon name="lucide:inbox" class="w-8 h-8 text-gray-200 mb-2" />
          <p class="text-xs text-gray-400 font-medium">Nenhuma cota definida</p>
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/editar`"
            class="text-xs font-bold text-blue-500 hover:text-blue-600 mt-1">Configurar agora →</NuxtLink>
        </div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="disc in progress.disciplines" :key="disc.discipline_id" class="px-5 py-4">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm font-bold text-gray-800">{{ disciplineName(disc.discipline_id) }}</p>
              <div class="flex items-center gap-2">
                <span class="text-xs font-black text-gray-900 tabular-nums">
                  {{ disc.submitted }}/{{ disc.quota }}
                </span>
                <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full"
                  :class="disc.remaining === 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
                  {{ disc.remaining === 0 ? 'Completo' : `${disc.remaining} restantes` }}
                </span>
              </div>
            </div>
            <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                :class="disc.remaining === 0 ? 'bg-emerald-400' : 'bg-blue-400'"
                :style="`width:${Math.min(100, disc.quota > 0 ? (disc.submitted / disc.quota) * 100 : 0)}%`" />
            </div>
          </div>
        </div>
      </div>

      <!-- Turmas -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:users" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Turmas</h3>
            <span class="text-[11px] font-bold px-1.5 py-0.5 rounded-md bg-gray-50 text-gray-500">
              {{ examClasses.length }}
            </span>
          </div>
          <button v-if="exam?.status === 'collecting'"
            class="text-[11px] font-bold text-blue-500 hover:text-blue-600 flex items-center gap-1 transition-colors"
            @click="showAssignModal = true">
            <Icon name="lucide:plus" class="w-3 h-3" />
            Vincular
          </button>
        </div>
        <div v-if="loadingClasses" class="p-4 space-y-2">
          <div v-for="i in 3" :key="i" class="h-10 bg-gray-50 rounded-xl animate-pulse" />
        </div>
        <div v-else-if="!examClasses.length" class="flex flex-col items-center justify-center py-12 px-4 text-center">
          <Icon name="lucide:users" class="w-8 h-8 text-gray-200 mb-2" />
          <p class="text-xs text-gray-400 font-medium">Nenhuma turma vinculada</p>
          <button v-if="exam?.status === 'collecting'"
            class="text-xs font-bold text-blue-500 hover:text-blue-600 mt-1"
            @click="showAssignModal = true">Vincular turmas →</button>
        </div>
        <div v-else class="divide-y divide-gray-50 max-h-80 overflow-y-auto">
          <div v-for="cls in examClasses" :key="cls.class_id"
            class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50/60 transition-colors">
            <div class="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:users" class="w-3 h-3 text-blue-400" />
            </div>
            <p class="text-sm font-semibold text-gray-700 truncate">{{ cls.class_name }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── CADERNOS (só quando generated/published) ── -->
    <Transition name="slide-up">
      <div v-if="exam?.status === 'generated' || exam?.status === 'published'"
        class="bg-white rounded-2xl border border-indigo-100 overflow-hidden animate-fade-up"
        style="animation-delay:110ms">

        <!-- Header da seção -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-indigo-50 bg-gradient-to-r from-indigo-50/60 to-transparent">
          <div class="flex items-center gap-2">
            <Icon name="lucide:book-open" class="w-4 h-4 text-indigo-500" />
            <h3 class="text-sm font-bold text-gray-900">Cadernos de questões</h3>
          </div>
          <Transition name="slide-up">
            <span v-if="bookletError"
              class="flex items-center gap-1.5 text-[11px] font-bold text-red-600 bg-red-50 border border-red-100 px-3 py-1.5 rounded-xl">
              <Icon name="lucide:alert-circle" class="w-3 h-3" />
              {{ bookletError }}
            </span>
          </Transition>
        </div>

        <div v-if="!examClasses.length" class="flex flex-col items-center py-10">
          <Icon name="lucide:users" class="w-7 h-7 text-gray-200 mb-2" />
          <p class="text-xs text-gray-400">Nenhuma turma vinculada</p>
        </div>

        <div v-else>
          <!-- Seletor de turma + botões de lote na mesma barra -->
          <div class="flex items-center justify-between gap-3 flex-wrap px-5 py-3 border-b border-gray-50 bg-gray-50/30">
            <div class="flex gap-2 flex-wrap">
              <button v-for="cls in examClasses" :key="cls.class_id"
                class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all border"
                :class="bookletClassId === cls.class_id
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                  : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-700'"
                @click="selectBookletClass(cls.class_id)">
                {{ cls.class_name }}
              </button>
            </div>
            <!-- Botões lote (só aparecem quando turma selecionada e alunos carregados) -->
            <div v-if="bookletClassId && students.length" class="flex gap-2">
              <button
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border"
                :class="batchLoading.booklets
                  ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                  : 'bg-white border-indigo-200 text-indigo-700 hover:bg-indigo-50'"
                :disabled="batchLoading.booklets"
                @click="downloadBatch('booklets')">
                <Icon :name="batchLoading.booklets ? 'lucide:loader-2' : 'lucide:download'"
                  class="w-3 h-3" :class="batchLoading.booklets ? 'animate-spin' : ''" />
                {{ batchLoading.booklets ? 'Gerando…' : 'Todos os cadernos' }}
              </button>
              <button
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border"
                :class="batchLoading.answers
                  ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                  : 'bg-white border-emerald-200 text-emerald-700 hover:bg-emerald-50'"
                :disabled="batchLoading.answers"
                @click="downloadBatch('answers')">
                <Icon :name="batchLoading.answers ? 'lucide:loader-2' : 'lucide:download'"
                  class="w-3 h-3" :class="batchLoading.answers ? 'animate-spin' : ''" />
                {{ batchLoading.answers ? 'Gerando…' : 'Todas as folhas' }}
              </button>
            </div>
          </div>

          <div v-if="!bookletClassId" class="flex flex-col items-center py-10">
            <Icon name="lucide:mouse-pointer-click" class="w-7 h-7 text-gray-200 mb-2" />
            <p class="text-xs text-gray-400 font-medium">Selecione uma turma acima</p>
          </div>
          <div v-else-if="loadingBooklets" class="p-4 space-y-2">
            <div v-for="i in 4" :key="i" class="h-12 bg-gray-50 rounded-xl animate-pulse" />
          </div>
          <div v-else-if="students.length">
            <!-- Cabeçalho da lista -->
            <div class="grid grid-cols-[1fr_auto] px-5 py-2 bg-gray-50/50 border-b border-gray-50">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Aluno</span>
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Downloads</span>
            </div>
            <div class="divide-y divide-gray-50">
              <div v-for="s in students" :key="s.id"
                class="flex items-center justify-between px-5 py-3 hover:bg-gray-50/50 transition-colors group">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-black flex-shrink-0"
                    :style="`background-color:${avatarColor(s.name)}18; color:${avatarColor(s.name)}`">
                    {{ s.name.trim()[0] }}
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-800 truncate">{{ s.name }}</p>
                    <p class="text-[11px] font-mono text-gray-400">{{ s.ra }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-1.5 flex-shrink-0">
                  <button
                    class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition-all border"
                    :class="pdfLoading[`b_${s.id}`]
                      ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                      : 'bg-white border-indigo-200 text-indigo-700 hover:bg-indigo-50'"
                    :disabled="!!pdfLoading[`b_${s.id}`]"
                    :title="`Caderno — ${s.name}`"
                    @click="downloadStudentBooklet(s.id, s.name, 'booklet')">
                    <Icon :name="pdfLoading[`b_${s.id}`] ? 'lucide:loader-2' : 'lucide:book-open'"
                      class="w-3 h-3" :class="pdfLoading[`b_${s.id}`] ? 'animate-spin' : ''" />
                    Caderno
                  </button>
                  <button
                    class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition-all border"
                    :class="pdfLoading[`a_${s.id}`]
                      ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-wait'
                      : 'bg-white border-emerald-200 text-emerald-700 hover:bg-emerald-50'"
                    :disabled="!!pdfLoading[`a_${s.id}`]"
                    :title="`Folha de resposta — ${s.name}`"
                    @click="downloadStudentBooklet(s.id, s.name, 'answer')">
                    <Icon :name="pdfLoading[`a_${s.id}`] ? 'lucide:loader-2' : 'lucide:clipboard-list'"
                      class="w-3 h-3" :class="pdfLoading[`a_${s.id}`] ? 'animate-spin' : ''" />
                    Folha
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-10">
            <Icon name="lucide:users" class="w-7 h-7 text-gray-200 mb-2" />
            <p class="text-xs text-gray-400">Nenhum aluno nesta turma</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── QUESTÕES ENVIADAS ── -->
    <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up"
      style="animation-delay:140ms">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
        <div class="flex items-center gap-2">
          <Icon name="lucide:file-text" class="w-4 h-4 text-gray-400" />
          <h3 class="text-sm font-bold text-gray-900">Questões enviadas</h3>
          <span class="text-[11px] font-bold px-1.5 py-0.5 rounded-md bg-gray-50 text-gray-500">
            {{ questions.length }}
          </span>
        </div>
        <select v-if="questions.length" v-model="filterDisc"
          class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600">
          <option value="">Todas disciplinas</option>
          <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
      <div v-if="loadingQuestions" class="p-4 space-y-3">
        <div v-for="i in 3" :key="i" class="h-24 bg-gray-50 rounded-xl animate-pulse" />
      </div>
      <div v-else-if="!questionsFiltradas.length" class="flex flex-col items-center justify-center py-14">
        <Icon name="lucide:file-x" class="w-8 h-8 text-gray-200 mb-2" />
        <p class="text-xs text-gray-400 font-medium">
          {{ filterDisc ? 'Nenhuma questão nesta disciplina' : 'Nenhuma questão enviada ainda' }}
        </p>
      </div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="(q, idx) in questionsFiltradas" :key="q.id"
          class="px-5 py-4 hover:bg-gray-50/40 transition-colors group">
          <div class="flex items-start justify-between gap-3 mb-2.5">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-[11px] font-black text-gray-300 tabular-nums w-5">#{{ idx + 1 }}</span>
              <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
                {{ disciplineName(q.discipline_id) }}
              </span>
              <span class="text-[11px] font-bold px-2 py-0.5 rounded-full"
                :class="q.state === 'approved' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
                {{ q.state === 'approved' ? 'Aprovada' : 'Enviada' }}
              </span>
              <span v-if="q.correct_label"
                class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">
                Gabarito: {{ q.correct_label }}
              </span>
              <span v-if="q.has_images || q.images?.length"
                class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-violet-50 text-violet-600 border border-violet-100 inline-flex items-center gap-1">
                <Icon name="lucide:image" class="w-2.5 h-2.5" />
                com imagem
              </span>
            </div>
            <button
              class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1.5 text-[11px] font-bold text-gray-400 hover:text-gray-700 px-2.5 py-1.5 rounded-lg hover:bg-gray-100 flex-shrink-0"
              @click="openEditQuestion(q)">
              <Icon name="lucide:pencil" class="w-3 h-3" />
              Editar
            </button>
          </div>
          <div class="text-sm text-gray-800 font-medium mb-3 leading-relaxed pl-7 question-content" v-html="renderStem(q.stem, q.images)" />
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pl-7">
            <div v-for="opt in q.options" :key="opt.label"
              class="flex items-start gap-2 px-3 py-2 rounded-lg text-xs"
              :class="q.correct_label === opt.label
                ? 'bg-emerald-50 border border-emerald-100'
                : 'bg-gray-50 border border-gray-100'">
              <span class="font-black flex-shrink-0"
                :class="q.correct_label === opt.label ? 'text-emerald-600' : 'text-gray-400'">
                {{ opt.label }})
              </span>
              <div class="question-content" :class="q.correct_label === opt.label ? 'text-emerald-700' : 'text-gray-600'"
                v-html="renderOption(opt.text, opt.label, q.images)" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: GERAR CADERNOS ===== -->
    <Transition name="modal">
      <div v-if="showGenerateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showGenerateModal = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center">
              <Icon name="lucide:book-open" class="w-5 h-5 text-indigo-500" />
            </div>
            <div>
              <h3 class="text-base font-black text-gray-900">Gerar cadernos</h3>
              <p class="text-xs text-gray-400 mt-0.5">Gera PDFs para todos os alunos</p>
            </div>
          </div>
          <p class="text-sm text-gray-600 mb-5">
            Serão gerados cadernos de questões e folhas de resposta individualizados para cada aluno das turmas vinculadas.
            Após gerado, o simulado não poderá mais ser editado.
          </p>
          <div v-if="generateError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl mb-4">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500 font-medium">{{ generateError }}</p>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600"
              @click="showGenerateModal = false">Cancelar</button>
            <button :disabled="generating"
              class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="generating ? 'bg-indigo-200 text-indigo-300 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white active:scale-95'"
              @click="generateBooklets">
              <svg v-if="generating" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ generating ? 'Gerando…' : 'Sim, gerar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal editar questão -->
    <Transition name="modal">
      <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showEditModal = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 animate-modal-in">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-base font-black text-gray-900">Editar questão #{{ editingQuestion?.id }}</h3>
            <button class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors"
              @click="showEditModal = false">
              <Icon name="lucide:x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>
          <div class="space-y-4">
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Enunciado</label>
              <textarea v-model="editForm.stem" rows="4"
                class="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all resize-none" />
            </div>
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-2">Alternativas</label>
              <div class="space-y-2">
                <div v-for="opt in editForm.options" :key="opt.label" class="flex items-center gap-2">
                  <button
                    class="w-8 h-8 rounded-lg border-2 text-xs font-black flex-shrink-0 transition-all"
                    :class="editForm.correct_label === opt.label
                      ? 'border-emerald-500 bg-emerald-500 text-white'
                      : 'border-gray-200 text-gray-400 hover:border-gray-300'"
                    @click="editForm.correct_label = editForm.correct_label === opt.label ? '' : opt.label">
                    {{ opt.label }}
                  </button>
                  <input v-model="opt.text"
                    class="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all" />
                </div>
              </div>
              <p class="text-[11px] text-gray-400 mt-2">Clique na letra para marcar como gabarito</p>
            </div>
            <div v-if="editError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
              <p class="text-xs text-red-500 font-medium">{{ editError }}</p>
            </div>
            <div class="flex gap-2 pt-1">
              <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600 transition-all"
                @click="showEditModal = false">Cancelar</button>
              <button :disabled="savingEdit"
                class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
                :class="savingEdit ? 'bg-gray-100 text-gray-300 cursor-not-allowed' : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
                @click="saveEdit">
                <svg v-if="savingEdit" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                </svg>
                {{ savingEdit ? 'Salvando...' : 'Salvar alterações' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal travar -->
    <Transition name="modal">
      <div v-if="showLockModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showLockModal = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <Icon name="lucide:lock" class="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h3 class="text-base font-black text-gray-900">Travar simulado</h3>
              <p class="text-xs text-gray-400 mt-0.5">Encerra a coleta de questões</p>
            </div>
          </div>
          <p class="text-sm text-gray-600 mb-5">
            Após travado, professores não poderão mais enviar questões. Todas as cotas precisam estar completas.
          </p>
          <div v-if="lockError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl mb-4">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500 font-medium">{{ lockError }}</p>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600"
              @click="showLockModal = false">Cancelar</button>
            <button :disabled="locking"
              class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="locking ? 'bg-blue-200 text-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white active:scale-95'"
              @click="lockExam">
              <svg v-if="locking" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ locking ? 'Travando...' : 'Sim, travar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal vincular turmas -->
    <Transition name="modal">
      <div v-if="showAssignModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showAssignModal = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-modal-in">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="text-base font-black text-gray-900">Vincular turmas</h3>
              <p class="text-xs text-gray-400 mt-0.5">Selecione as turmas que farão este simulado</p>
            </div>
            <button class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center"
              @click="showAssignModal = false">
              <Icon name="lucide:x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>
          <div class="relative mb-3">
            <Icon name="lucide:search" class="w-3.5 h-3.5 text-gray-300 absolute left-3 top-1/2 -translate-y-1/2" />
            <input v-model="buscaTurma"
              class="w-full pl-8 pr-3 py-2 text-xs border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 transition-all"
              placeholder="Filtrar turmas..." />
          </div>
          <div class="max-h-64 overflow-y-auto space-y-1 mb-4">
            <div v-for="cls in turmasFiltradas" :key="cls.id"
              class="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-gray-50 cursor-pointer transition-colors"
              @click="toggleTurma(cls.id)">
              <div class="w-5 h-5 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition-all"
                :class="selectedClasses.includes(cls.id) ? 'border-gray-900 bg-gray-900' : 'border-gray-200'">
                <Icon v-if="selectedClasses.includes(cls.id)" name="lucide:check" class="w-3 h-3 text-white" />
              </div>
              <span class="text-sm font-semibold text-gray-700">{{ cls.name }}</span>
              <span class="text-[10px] text-gray-400 ml-auto">
                {{ cls.grade?.level === 'fundamental' ? 'Fund.' : 'Médio' }}
              </span>
            </div>
          </div>
          <div v-if="assignError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl mb-3">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500 font-medium">{{ assignError }}</p>
          </div>
          <button :disabled="!selectedClasses.length || assigning"
            class="w-full py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
            :class="!selectedClasses.length || assigning
              ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
              : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
            @click="assignClasses">
            <svg v-if="assigning" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            {{ assigning ? 'Vinculando...' : `Vincular ${selectedClasses.length} turma${selectedClasses.length !== 1 ? 's' : ''}` }}
          </button>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

useHead({
  link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }],
})

const route = useRoute()
const { get, post, patch, accessToken } = useApi()
const { renderStem, renderOption } = useQuestionRenderer()
const examId = computed(() => Number(route.params.id))

// Data
const exam        = ref<any>(null)
const progress    = ref<any>(null)
const examClasses = ref<any[]>([])
const disciplines = ref<any[]>([])
const allClasses  = ref<any[]>([])
const questions   = ref<any[]>([])
const filterDisc  = ref<number | ''>('')

// Loading
const loading          = ref(true)
const loadingProgress  = ref(true)
const loadingClasses   = ref(true)
const loadingQuestions = ref(true)

// Lock modal
const showLockModal = ref(false)
const locking       = ref(false)
const lockError     = ref('')

// Assign modal
const showAssignModal = ref(false)
const selectedClasses = ref<number[]>([])
const buscaTurma      = ref('')
const assigning       = ref(false)
const assignError     = ref('')

// Edit question modal
const showEditModal   = ref(false)
const editingQuestion = ref<any>(null)
const savingEdit      = ref(false)
const editError       = ref('')
const editForm = reactive<{
  stem: string
  options: { label: string; text: string }[]
  correct_label: string
}>({ stem: '', options: [], correct_label: '' })

// ===== CADERNOS =====
const showGenerateModal = ref(false)
const generating        = ref(false)
const generateError     = ref('')

const bookletClassId  = ref<number | null>(null)
const students        = ref<any[]>([])
const loadingBooklets = ref(false)
const bookletError    = ref('')

// loading individual por aluno: chave `b_{id}` (booklet) ou `a_{id}` (answer sheet)
const pdfLoading = ref<Record<string, boolean>>({})

// loading em lote
const batchLoading   = ref({ booklets: false, answers: false })
const batchOverlay   = ref(false)
const batchOverlayMsg = ref('')
const batchElapsed   = ref(0)
const batchTimer     = ref<any>(null)

function startBatchTimer(msg: string) {
  batchOverlay.value   = true
  batchOverlayMsg.value = msg
  batchElapsed.value   = 0
  clearInterval(batchTimer.value)
  batchTimer.value = setInterval(() => { batchElapsed.value++ }, 1000)
}
function stopBatchTimer() {
  clearInterval(batchTimer.value)
  batchTimer.value = null
  batchOverlay.value = false
}
function fmtTime(s: number) {
  const m = Math.floor(s / 60), sec = s % 60
  return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
}

// Computed
const statCards = computed(() => [
  {
    label: 'Questões enviadas',
    value: questions.value.length,
    icon: 'lucide:file-text', iconBg: 'bg-blue-50', iconColor: 'text-blue-500',
  },
  {
    label: 'Total esperado',
    value: progress.value?.disciplines?.reduce((s: number, d: any) => s + d.quota, 0) ?? 0,
    icon: 'lucide:target', iconBg: 'bg-violet-50', iconColor: 'text-violet-500',
  },
  {
    label: 'Turmas',
    value: examClasses.value.length,
    icon: 'lucide:users', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-500',
  },
  {
    label: 'Alternativas',
    value: exam.value?.options_count ?? '—',
    icon: 'lucide:list-ordered', iconBg: 'bg-gray-50', iconColor: 'text-gray-400',
  },
])

const questionsFiltradas = computed(() =>
  filterDisc.value
    ? questions.value.filter(q => q.discipline_id === filterDisc.value)
    : questions.value
)

const turmasFiltradas = computed(() => {
  const q = buscaTurma.value.toLowerCase()
  const vinculadas = new Set(examClasses.value.map(c => c.class_id))
  const lista = allClasses.value.filter(c => !vinculadas.has(c.id))
  return q ? lista.filter(c => c.name.toLowerCase().includes(q)) : lista
})

// Status helpers
function statusLabel(s?: string) {
  return ({ collecting: 'Em coleta', locked: 'Travado', published: 'Publicado', draft: 'Rascunho', review: 'Em revisão', generated: 'Gerado' } as any)[s ?? ''] ?? s
}
function statusBadge(s?: string) {
  return ({ collecting: 'bg-amber-50 text-amber-700', locked: 'bg-blue-50 text-blue-700', published: 'bg-emerald-50 text-emerald-700', generated: 'bg-indigo-50 text-indigo-700', review: 'bg-purple-50 text-purple-700' } as any)[s ?? ''] ?? 'bg-gray-50 text-gray-500'
}
function statusDot(s?: string) {
  return ({ collecting: 'bg-amber-400', locked: 'bg-blue-400', published: 'bg-emerald-400', generated: 'bg-indigo-400', review: 'bg-purple-400' } as any)[s ?? ''] ?? 'bg-gray-300'
}
function statusBg(s?: string) {
  return ({ collecting: 'bg-amber-50', locked: 'bg-blue-50', published: 'bg-emerald-50', generated: 'bg-indigo-50' } as any)[s ?? ''] ?? 'bg-gray-50'
}
function statusIcon(s?: string) {
  return ({ collecting: 'lucide:pencil', locked: 'lucide:lock', published: 'lucide:check-circle-2', generated: 'lucide:book-open', review: 'lucide:eye' } as any)[s ?? ''] ?? 'lucide:file'
}
function statusIconColor(s?: string) {
  return ({ collecting: 'text-amber-500', locked: 'text-blue-500', published: 'text-emerald-500', generated: 'text-indigo-500', review: 'text-purple-500' } as any)[s ?? ''] ?? 'text-gray-400'
}
function answerSourceLabel(s: string) {
  return ({ teachers: 'Gabarito pelos professores', coordinator: 'Gabarito pelo coordenador' } as any)[s] ?? s
}
function disciplineName(id: number) {
  return disciplines.value.find(d => d.id === id)?.name ?? `Disciplina #${id}`
}
function toggleTurma(id: number) {
  const idx = selectedClasses.value.indexOf(id)
  if (idx === -1) selectedClasses.value.push(id)
  else selectedClasses.value.splice(idx, 1)
}

const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4','#ec4899']
function avatarColor(name: string) {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) & 0xffff
  return COLORS[h % COLORS.length]
}

// Edit question
function openEditQuestion(q: any) {
  editingQuestion.value = q
  editForm.stem = q.stem
  editForm.options = q.options.map((o: any) => ({ label: o.label, text: o.text }))
  editForm.correct_label = q.correct_label ?? ''
  editError.value = ''
  showEditModal.value = true
}

async function saveEdit() {
  if (!editingQuestion.value) return
  savingEdit.value = true
  editError.value = ''
  try {
    const updated = await patch<any>(`/exams/${examId.value}/questions/${editingQuestion.value.id}`, {
      stem: editForm.stem,
      options: editForm.options,
      correct_label: editForm.correct_label || null,
    })
    const idx = questions.value.findIndex(q => q.id === editingQuestion.value.id)
    if (idx !== -1) questions.value[idx] = updated
    showEditModal.value = false
  } catch (e: any) {
    editError.value = e.message ?? 'Erro ao salvar questão.'
  } finally {
    savingEdit.value = false
  }
}

async function lockExam() {
  locking.value = true
  lockError.value = ''
  try {
    await post(`/exams/${examId.value}/lock`, {})
    exam.value.status = 'locked'
    showLockModal.value = false
  } catch (e: any) {
    lockError.value = e.message ?? 'Erro ao travar simulado.'
  } finally {
    locking.value = false
  }
}

async function assignClasses() {
  if (!selectedClasses.value.length) return
  assigning.value = true
  assignError.value = ''
  try {
    await post(`/exams/${examId.value}/assign-classes`, { class_ids: selectedClasses.value })
    examClasses.value = await get<any[]>(`/exams/${examId.value}/classes`)
    showAssignModal.value = false
    selectedClasses.value = []
    buscaTurma.value = ''
  } catch (e: any) {
    assignError.value = e.message ?? 'Erro ao vincular turmas.'
  } finally {
    assigning.value = false
  }
}

// ===== CADERNOS — LÓGICA =====

async function generateBooklets() {
  generating.value = true
  generateError.value = ''
  try {
    const classIds = examClasses.value.map((c: any) => c.class_id)
    if (!classIds.length) throw new Error('Nenhuma turma vinculada ao simulado.')
    const token = accessToken.value ?? (import.meta.client ? localStorage.getItem('samba_token') : null)
    for (const classId of classIds) {
      const res = await fetch(`http://localhost:8000/exams/${examId.value}/pdf/generate?class_id=${classId}`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include',
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `Erro ${res.status}` }))
        throw new Error(err.detail ?? `Erro ${res.status}`)
      }
    }
    exam.value.status = 'generated'
    showGenerateModal.value = false
    if (bookletClassId.value) await loadStudents(bookletClassId.value)
  } catch (e: any) {
    generateError.value = e.message ?? 'Erro ao gerar cadernos.'
  } finally {
    generating.value = false
  }
}

async function selectBookletClass(classId: number) {
  bookletClassId.value = classId
  await loadStudents(classId)
}

async function loadStudents(classId: number) {
  loadingBooklets.value = true
  bookletError.value = ''
  try {
    const data = await get<any[]>(`/school/students?class_id=${classId}`)
    students.value = data ?? []
  } catch (e: any) {
    students.value = []
    bookletError.value = 'Não foi possível carregar os alunos.'
  } finally {
    loadingBooklets.value = false
  }
}

// ---------------------------------------------------------------------------
// Download helpers
// ---------------------------------------------------------------------------
function _triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

async function _fetchBlob(path: string): Promise<Blob> {
  const token = accessToken.value ?? (import.meta.client ? localStorage.getItem('samba_token') : null)
  const res = await fetch(`http://localhost:8000${path}`, {
    headers:     token ? { Authorization: `Bearer ${token}` } : {},
    credentials: 'include',
  })
  if (!res.ok) throw new Error(`Erro ${res.status}`)
  return res.blob()
}

async function downloadStudentBooklet(studentId: number, studentName: string, type: 'booklet' | 'answer') {
  const key = `${type === 'booklet' ? 'b' : 'a'}_${studentId}`
  pdfLoading.value[key] = true
  bookletError.value = ''
  const safe = studentName.split(' ')[0].toLowerCase()
  try {
    if (type === 'booklet') {
      const blob = await _fetchBlob(`/exams/${examId.value}/pdf/download?student_id=${studentId}&type=booklet`)
      _triggerDownload(blob, `caderno_${safe}_exam${examId.value}.pdf`)
    } else {
      const blob = await _fetchBlob(`/exams/${examId.value}/pdf/download?student_id=${studentId}&type=answer_sheet`)
      _triggerDownload(blob, `resposta_${safe}_exam${examId.value}.pdf`)
    }
  } catch (e: any) {
    bookletError.value = `Erro ao gerar PDF: ${e?.message ?? 'tente novamente'}`
    setTimeout(() => { bookletError.value = '' }, 4000)
  } finally {
    pdfLoading.value[key] = false
  }
}

async function downloadBatch(type: 'booklets' | 'answers') {
  batchLoading.value[type] = true
  bookletError.value = ''
  const cls = examClasses.value.find(c => c.class_id === bookletClassId.value)
  const className = cls?.class_name?.replace(/\s/g, '') ?? bookletClassId.value
  const label = cls?.class_name ?? String(bookletClassId.value)
  startBatchTimer(type === 'booklets' ? `Gerando PDFs — ${label}` : `Gerando folhas — ${label}`)
  try {
    if (type === 'booklets') {
      const blob = await _fetchBlob(`/exams/${examId.value}/pdf/batch/?class_id=${bookletClassId.value}&type=booklets`)
      _triggerDownload(blob, `cadernos_${className}_exam${examId.value}.pdf`)
    } else {
      const blob = await _fetchBlob(`/exams/${examId.value}/pdf/batch/?class_id=${bookletClassId.value}&type=omr`)
      _triggerDownload(blob, `respostas_${className}_exam${examId.value}.pdf`)
    }
  } catch (e: any) {
    bookletError.value = `Erro ao gerar arquivo: ${e?.message ?? 'tente novamente'}`
    setTimeout(() => { bookletError.value = '' }, 4000)
  } finally {
    batchLoading.value[type] = false
    stopBatchTimer()
  }
}

onMounted(async () => {
  const [examRes, progressRes, classesRes, discRes, allClassesRes, questionsRes] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any>(`/exams/${examId.value}/progress`),
    get<any[]>(`/exams/${examId.value}/classes`),
    get<any[]>('/disciplines/'),
    get<any[]>('/school/classes'),
    get<any[]>(`/exams/${examId.value}/questions`),
  ])

  if (examRes.status === 'fulfilled')       exam.value        = examRes.value
  if (progressRes.status === 'fulfilled')   progress.value    = progressRes.value
  if (classesRes.status === 'fulfilled')    examClasses.value = classesRes.value
  if (discRes.status === 'fulfilled')       disciplines.value = discRes.value
  if (allClassesRes.status === 'fulfilled') allClasses.value  = allClassesRes.value
  if (questionsRes.status === 'fulfilled')  questions.value   = questionsRes.value

  loading.value          = false
  loadingProgress.value  = false
  loadingClasses.value   = false
  loadingQuestions.value = false
})
</script>

<style scoped>
@keyframes fade-in  { from { opacity:0; transform:translateY(6px)  } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up  { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
@keyframes modal-in { from { opacity:0; transform:scale(0.94) translateY(10px) } to { opacity:1; transform:scale(1) translateY(0) } }

.animate-fade-in  { animation: fade-in  0.3s  ease both }
.animate-fade-up  { animation: fade-up  0.38s ease both }
.animate-modal-in { animation: modal-in 0.22s cubic-bezier(0.34,1.56,0.64,1) both }

.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease }
.modal-enter-from, .modal-leave-to { opacity: 0 }

.slide-up-enter-active { transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.34,1.56,0.64,1) }
.slide-up-leave-active { transition: opacity 0.15s ease, transform 0.15s ease }
.slide-up-enter-from   { opacity:0; transform:translateY(10px) }
.slide-up-leave-to     { opacity:0; transform:translateY(6px) }
.question-content :deep(img.question-img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 6px 0;
  display: block;
}
.question-content :deep(.katex-display) {
  margin: 8px 0;
  overflow-x: auto;
}
.question-content :deep(.katex) {
  font-size: 1em;
}
.question-content :deep(.math-error) {
  color: #dc3545;
  font-family: monospace;
  font-size: 0.8em;
}
</style>