<!-- pages/dashboard/professor/simulados/[id].vue -->
<template>
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- ===================================================== -->
    <!-- MODAL: Seleção de disciplina + turmas                  -->
    <!-- ===================================================== -->
    <Transition name="pop">
      <div v-if="showClassSelector"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">

          <div class="flex items-center gap-3 px-6 py-5 border-b border-gray-100">
            <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:school" class="w-5 h-5 text-blue-600" />
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-gray-900">Configurar disciplina e turmas</h3>
              <p class="text-xs text-gray-400 mt-0.5">Escolha a disciplina e para quais turmas enviar questões</p>
            </div>
            <button class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              @click="fecharModalTurmas">
              <Icon name="lucide:x" class="w-4 h-4" />
            </button>
          </div>

          <div class="px-6 py-5 space-y-5 max-h-[70vh] overflow-y-auto">

            <!-- Step 1: Disciplina -->
            <div v-if="myDisciplines.length > 1">
              <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
                <Icon name="lucide:book-open" class="w-3 h-3 inline mr-1" />
                Disciplina
              </p>
              <div class="grid grid-cols-1 gap-2">
                <button v-for="disc in myDisciplines" :key="disc.discipline_id"
                  class="flex items-center gap-3 px-4 py-3 rounded-xl border-2 text-left transition-all"
                  :class="activeDisciplineId === disc.discipline_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-200 hover:bg-blue-50/30'"
                  @click="selectDiscipline(disc.discipline_id)">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 font-black text-xs"
                    :class="activeDisciplineId === disc.discipline_id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'">
                    {{ disc.discipline_name.substring(0,2).toUpperCase() }}
                  </div>
                  <div class="flex-1">
                    <p class="text-sm font-semibold" :class="activeDisciplineId === disc.discipline_id ? 'text-blue-900' : 'text-gray-700'">
                      {{ disc.discipline_name }}
                    </p>
                    <p class="text-xs text-gray-400">{{ disc.classes.length }} turma{{ disc.classes.length > 1 ? 's' : '' }}</p>
                  </div>
                  <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                    :class="activeDisciplineId === disc.discipline_id ? 'border-blue-500 bg-blue-500' : 'border-gray-300'">
                    <Icon v-if="activeDisciplineId === disc.discipline_id" name="lucide:check" class="w-3 h-3 text-white" />
                  </div>
                </button>
              </div>
              <div class="border-t border-gray-100 mt-4" />
            </div>

            <!-- Step 2: Turmas da disciplina selecionada -->
            <div v-if="activeDisciplineClasses.length > 0">
              <div class="flex items-center justify-between mb-3">
                <p class="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  <Icon name="lucide:door-open" class="w-3 h-3 inline mr-1" />
                  Turmas
                </p>
                <button v-if="activeDisciplineClasses.length > 1"
                  class="text-xs font-semibold text-blue-500 hover:text-blue-700 transition-colors"
                  @click="toggleTodasTurmasDisciplina">
                  {{ todasTurmasSelecionadas ? 'Desmarcar todas' : 'Selecionar todas' }}
                </button>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <button v-for="cls in activeDisciplineClasses" :key="cls.class_id"
                  class="flex items-center gap-2.5 px-3 py-2.5 rounded-xl border-2 text-left transition-all"
                  :class="selectedClassIds.includes(cls.class_id)
                    ? 'border-emerald-400 bg-emerald-50'
                    : 'border-gray-200 hover:border-emerald-200 hover:bg-emerald-50/30'"
                  @click="toggleTurma(cls.class_id)">
                  <div class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all"
                    :class="selectedClassIds.includes(cls.class_id) ? 'border-emerald-500 bg-emerald-500' : 'border-gray-300'">
                    <Icon v-if="selectedClassIds.includes(cls.class_id)" name="lucide:check" class="w-3 h-3 text-white" />
                  </div>
                  <span class="text-sm font-semibold"
                    :class="selectedClassIds.includes(cls.class_id) ? 'text-emerald-900' : 'text-gray-700'">
                    {{ cls.class_name }}
                  </span>
                </button>
              </div>
            </div>
          </div>

          <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between gap-3">
            <p class="text-xs text-gray-400">
              {{ selectedClassIds.length }} turma{{ selectedClassIds.length !== 1 ? 's' : '' }} selecionada{{ selectedClassIds.length !== 1 ? 's' : '' }}
            </p>
            <button
              :disabled="selectedClassIds.length === 0 || !activeDisciplineId"
              class="px-5 py-2.5 rounded-xl text-sm font-bold transition-all active:scale-95"
              :class="selectedClassIds.length > 0 && activeDisciplineId
                ? 'bg-gray-900 text-white hover:bg-gray-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
              @click="confirmarSelecaoTurmas">
              Confirmar
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Cabeçalho -->
    <div class="flex items-center gap-4">
      <NuxtLink to="/dashboard/professor"
        class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
        <Icon name="lucide:arrow-left" class="w-5 h-5" />
      </NuxtLink>

      <div class="flex-1">
        <div v-if="loadingExam" class="space-y-1">
          <div class="h-7 w-72 bg-gray-100 rounded-lg animate-pulse" />
          <div class="h-4 w-48 bg-gray-50 rounded animate-pulse" />
        </div>
        <template v-else-if="exam">
          <h2 class="text-2xl font-bold text-gray-900">{{ exam.title }}</h2>
          <p class="text-gray-500 text-sm mt-0.5 flex items-center gap-2 flex-wrap">
            <span>{{ progressInfo?.discipline_name ?? '—' }}</span>
            <span class="text-gray-300">·</span>
            <span class="flex items-center gap-1">
              <Icon name="lucide:door-open" class="w-3 h-3" />
              {{ turmasLabel }}
            </span>
            <span class="text-gray-300">·</span>
            <span>alt. A–{{ exam.options_count === 4 ? 'D' : 'E' }}</span>
            <button v-if="myDisciplines.length > 1 || myDisciplines.some((d: any) => d.classes.length > 1)"
              class="text-xs text-blue-500 hover:text-blue-700 underline"
              @click="showClassSelector = true">
              trocar disciplina/turmas
            </button>
          </p>
        </template>
      </div>

      <!-- Progresso -->
      <div v-if="exam && !loadingExam" class="hidden sm:flex items-center gap-3">
        <div class="text-right">
          <p class="text-xs text-gray-400">Progresso</p>
          <p class="text-sm font-bold tabular-nums transition-colors duration-500"
            :class="progresso === 100 ? 'text-emerald-600' : 'text-gray-900'">
            {{ progressInfo?.submitted ?? 0 }}/{{ progressInfo?.quota ?? 0 }}
          </p>
        </div>
        <div class="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-700 ease-out"
            :class="progresso === 100 ? 'bg-emerald-500' : 'bg-blue-500'"
            :style="{ width: `${progresso}%` }" />
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingExam" class="flex items-center gap-2 text-sm text-gray-400 py-8 justify-center">
      <Icon name="lucide:loader-2" class="w-5 h-5 animate-spin" />
      Carregando simulado...
    </div>

    <div v-else-if="!exam" class="text-center py-20 text-gray-300">
      <Icon name="lucide:file-x" class="w-16 h-16 mx-auto mb-4" />
      <p class="text-gray-400 font-medium">Simulado não encontrado ou sem acesso.</p>
    </div>

    <!-- Layout principal -->
    <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6 items-start">

      <!-- ======================================== -->
      <!-- COLUNA ESQUERDA                          -->
      <!-- ======================================== -->
      <div class="space-y-4 xl:sticky xl:top-6">

        <!-- Banner conclusão -->
        <Transition name="slide-down">
          <div v-if="progresso === 100 && !enviado"
            class="bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-2xl p-4 flex items-center justify-between gap-4 shadow-sm shadow-emerald-200">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                <Icon name="lucide:check-circle-2" class="w-5 h-5 text-white" />
              </div>
              <div>
                <p class="text-sm font-semibold text-white">Todas as questões cadastradas!</p>
                <p class="text-xs text-emerald-100 mt-0.5">Confirme o envio ao coordenador</p>
              </div>
            </div>
            <button
              class="flex items-center gap-2 px-4 py-2 bg-white text-emerald-700 text-sm font-semibold rounded-xl transition-all hover:bg-emerald-50 flex-shrink-0 shadow-sm"
              @click="concluirEnvio">
              <Icon name="lucide:send" class="w-4 h-4" />
              Concluir envio
            </button>
          </div>
        </Transition>

        <Transition name="pop">
          <div v-if="enviado" class="bg-emerald-600 rounded-2xl p-6 text-center text-white">
            <Icon name="lucide:check-circle-2" class="w-8 h-8 mx-auto mb-2 animate-bounce" />
            <p class="font-semibold">Questões enviadas com sucesso!</p>
            <p class="text-sm text-emerald-100 mt-1">Redirecionando...</p>
          </div>
        </Transition>

        <!-- Upload de arquivo -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="px-6 pt-5 pb-4 border-b border-gray-50 flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center">
              <Icon name="lucide:file-up" class="w-4 h-4 text-blue-600" />
            </div>
            <h3 class="font-semibold text-gray-900 text-sm">Importar arquivo</h3>
            <span class="ml-auto text-xs text-gray-400">.docx · .txt · .pdf</span>
          </div>
          <div class="p-4">
            <div
              class="relative border-2 border-dashed rounded-xl transition-all duration-200 cursor-pointer"
              :class="isDragging
                ? 'border-blue-400 bg-blue-50 scale-[1.01]'
                : uploadStatus === 'success' ? 'border-emerald-300 bg-emerald-50/50'
                : uploadStatus === 'error'   ? 'border-red-300 bg-red-50/50'
                : uploadStatus === 'loading' ? 'border-blue-200 bg-blue-50/30'
                : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/20'"
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop.prevent="handleDrop"
              @click="triggerFileInput">
              <input ref="fileInput" type="file" accept=".docx,.txt,.pdf" class="hidden" @change="handleFileChange" />

              <div v-if="uploadStatus === 'idle'" class="flex items-center gap-4 p-4">
                <div class="w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:upload-cloud" class="w-5 h-5 text-gray-400" />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-700">Arraste ou clique para enviar</p>
                  <p class="text-xs text-gray-400 mt-0.5">Questões extraídas automaticamente — suporta imagens e fórmulas</p>
                </div>
              </div>
              <div v-else-if="uploadStatus === 'loading'" class="flex items-center gap-4 p-4">
                <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                  <svg class="animate-spin w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                </div>
                <div><p class="text-sm font-medium text-blue-700">Processando...</p></div>
              </div>
              <div v-else-if="uploadStatus === 'success'" class="flex items-center gap-4 p-4">
                <div class="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:check-circle-2" class="w-5 h-5 text-emerald-500" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-emerald-700 truncate">{{ uploadedFileName }}</p>
                  <p class="text-xs text-emerald-500">Questões importadas com sucesso</p>
                </div>
                <button class="text-xs text-gray-400 hover:text-gray-600 underline" @click.stop="resetUpload">Novo</button>
              </div>
              <div v-else-if="uploadStatus === 'error'" class="flex items-center gap-4 p-4">
                <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:alert-circle" class="w-5 h-5 text-red-500" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-red-700">Erro ao processar</p>
                  <p class="text-xs text-red-400 truncate">{{ uploadError }}</p>
                </div>
                <button class="text-xs text-gray-400 hover:text-gray-600 underline" @click.stop="resetUpload">Tentar novamente</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Formulário de questão manual -->
        <div class="bg-white rounded-2xl border shadow-sm overflow-hidden transition-all duration-200"
          :class="editandoId !== null ? 'border-blue-200 ring-2 ring-blue-100' : 'border-gray-100'">

          <div class="px-6 pt-5 pb-4 border-b flex items-center gap-2"
            :class="editandoId !== null ? 'border-blue-100 bg-blue-50/40' : 'border-gray-50'">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center"
              :class="editandoId !== null ? 'bg-blue-100' : 'bg-gray-50'">
              <Icon :name="editandoId !== null ? 'lucide:pencil' : 'lucide:plus-circle'"
                class="w-4 h-4" :class="editandoId !== null ? 'text-blue-600' : 'text-gray-500'" />
            </div>
            <h3 class="font-semibold text-sm" :class="editandoId !== null ? 'text-blue-900' : 'text-gray-900'">
              {{ editandoId !== null ? `Editando questão #${editandoIndex + 1}` : 'Nova questão' }}
            </h3>
            <button v-if="editandoId !== null"
              class="ml-auto text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
              @click="cancelarEdicao">
              <Icon name="lucide:x" class="w-3 h-3" /> Cancelar
            </button>
          </div>

          <div class="p-5 space-y-5">

            <!-- Enunciado -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                Enunciado <span class="text-red-400">*</span>
              </label>
              <textarea v-model="novaQuestao.stem" rows="4"
                placeholder="Digite o enunciado da questão..."
                class="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
                :class="editandoId !== null ? 'bg-blue-50/30' : 'bg-white'" />
            </div>

            <!-- ===== FÓRMULAS ===== -->
            <div class="border border-gray-100 rounded-xl overflow-hidden">
              <button
                class="w-full flex items-center gap-2 px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                @click="showFormulaPanel = !showFormulaPanel">
                <div class="w-6 h-6 rounded-lg bg-violet-100 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:sigma" class="w-3.5 h-3.5 text-violet-600" />
                </div>
                <span class="text-sm font-semibold text-gray-700">Inserir fórmula matemática</span>
                <Icon :name="showFormulaPanel ? 'lucide:chevron-up' : 'lucide:chevron-down'"
                  class="w-4 h-4 text-gray-400 ml-auto" />
              </button>

              <Transition name="slide-down">
                <div v-if="showFormulaPanel" class="p-4 space-y-3 border-t border-gray-100">
                  <!-- Atalhos de fórmulas comuns -->
                  <div>
                    <p class="text-xs text-gray-400 mb-2">Atalhos rápidos:</p>
                    <div class="flex flex-wrap gap-2">
                      <button v-for="f in formulaAtalhos" :key="f.label"
                        class="px-2.5 py-1.5 rounded-lg bg-violet-50 border border-violet-100 text-xs font-mono text-violet-700 hover:bg-violet-100 transition-colors"
                        @click="inserirFormula(f.latex)">
                        {{ f.label }}
                      </button>
                    </div>
                  </div>

                  <!-- Modo: inline ou bloco -->
                  <div class="flex gap-2">
                    <button
                      class="flex-1 py-2 rounded-lg text-xs font-semibold border transition-all"
                      :class="formulaMode === 'inline'
                        ? 'bg-violet-600 text-white border-violet-600'
                        : 'border-gray-200 text-gray-600 hover:border-violet-300'"
                      @click="formulaMode = 'inline'">
                      Inline $f(x)$
                    </button>
                    <button
                      class="flex-1 py-2 rounded-lg text-xs font-semibold border transition-all"
                      :class="formulaMode === 'block'
                        ? 'bg-violet-600 text-white border-violet-600'
                        : 'border-gray-200 text-gray-600 hover:border-violet-300'"
                      @click="formulaMode = 'block'">
                      Bloco $$f(x)$$
                    </button>
                  </div>

                  <!-- Campo da fórmula -->
                  <div>
                    <input v-model="formulaInput" type="text"
                      placeholder="Ex: \frac{a}{b}, \sqrt{x^2+y^2}, x^2+y^2=r^2"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-violet-400"
                      @input="atualizarPreviewFormula" />
                  </div>

                  <!-- Preview da fórmula -->
                  <div v-if="formulaPreview"
                    class="p-3 bg-violet-50 border border-violet-100 rounded-xl">
                    <p class="text-[10px] font-semibold text-violet-400 uppercase tracking-wide mb-2">Preview</p>
                    <div class="text-center question-content" v-html="formulaPreview" />
                  </div>
                  <div v-else-if="formulaInput"
                    class="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-500 text-center">
                    Fórmula inválida — verifique a sintaxe LaTeX
                  </div>

                  <!-- Destino da fórmula -->
                  <div>
                    <p class="text-xs text-gray-500 mb-1.5">Inserir no:</p>
                    <div class="flex flex-wrap gap-2">
                      <button
                        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all"
                        :class="formulaDestino === 'stem'
                          ? 'bg-gray-800 text-white border-gray-800'
                          : 'border-gray-200 text-gray-600 hover:border-gray-400'"
                        @click="formulaDestino = 'stem'">
                        Enunciado
                      </button>
                      <button v-for="l in letras.slice(0, exam?.options_count ?? 4)" :key="l"
                        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all"
                        :class="formulaDestino === `option_${l}`
                          ? 'bg-gray-800 text-white border-gray-800'
                          : 'border-gray-200 text-gray-600 hover:border-gray-400'"
                        @click="formulaDestino = `option_${l}`">
                        Alt. {{ l }}
                      </button>
                    </div>
                  </div>

                  <button
                    :disabled="!formulaInput.trim() || !formulaPreview"
                    class="w-full py-2.5 rounded-xl text-sm font-semibold transition-all"
                    :class="formulaInput.trim() && formulaPreview
                      ? 'bg-violet-600 hover:bg-violet-700 text-white'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
                    @click="confirmarInsercaoFormula">
                    <Icon name="lucide:plus" class="w-4 h-4 inline mr-1" />
                    Inserir fórmula
                  </button>
                </div>
              </Transition>
            </div>

            <!-- ===== IMAGENS ===== -->
            <div class="border border-gray-100 rounded-xl overflow-hidden">
              <button
                class="w-full flex items-center gap-2 px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                @click="showImagePanel = !showImagePanel">
                <div class="w-6 h-6 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:image-plus" class="w-3.5 h-3.5 text-amber-600" />
                </div>
                <span class="text-sm font-semibold text-gray-700">Inserir imagem</span>
                <Icon :name="showImagePanel ? 'lucide:chevron-up' : 'lucide:chevron-down'"
                  class="w-4 h-4 text-gray-400 ml-auto" />
              </button>

              <Transition name="slide-down">
                <div v-if="showImagePanel" class="p-4 space-y-3 border-t border-gray-100">
                  <!-- Destino da imagem -->
                  <div>
                    <p class="text-xs text-gray-500 mb-1.5">Inserir no:</p>
                    <div class="flex flex-wrap gap-2">
                      <button
                        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all"
                        :class="imageDestino === 'stem'
                          ? 'bg-gray-800 text-white border-gray-800'
                          : 'border-gray-200 text-gray-600 hover:border-gray-400'"
                        @click="imageDestino = 'stem'">
                        Enunciado
                      </button>
                      <button v-for="l in letras.slice(0, exam?.options_count ?? 4)" :key="l"
                        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all"
                        :class="imageDestino === `option_${l}`
                          ? 'bg-gray-800 text-white border-gray-800'
                          : 'border-gray-200 text-gray-600 hover:border-gray-400'"
                        @click="imageDestino = `option_${l}`">
                        Alt. {{ l }}
                      </button>
                    </div>
                  </div>

                  <!-- Nota: só disponível após salvar questão -->
                  <div v-if="editandoId === null"
                    class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-700 flex items-start gap-2">
                    <Icon name="lucide:info" class="w-4 h-4 flex-shrink-0 mt-0.5" />
                    Salve a questão primeiro para adicionar imagens.
                  </div>

                  <template v-else>
                    <!-- Upload de imagem -->
                    <div
                      class="border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all"
                      :class="imageDragging
                        ? 'border-amber-400 bg-amber-50'
                        : 'border-gray-200 hover:border-amber-300 hover:bg-amber-50/30'"
                      @dragover.prevent="imageDragging = true"
                      @dragleave="imageDragging = false"
                      @drop.prevent="handleImageDrop"
                      @click="triggerImageInput">
                      <input ref="imageFileInput" type="file"
                        accept="image/png,image/jpeg,image/gif,image/webp"
                        class="hidden" @change="handleImageFileChange" />
                      <div v-if="uploadingImage" class="flex items-center justify-center gap-2">
                        <svg class="animate-spin w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                        </svg>
                        <span class="text-sm text-amber-600">Enviando...</span>
                      </div>
                      <div v-else>
                        <Icon name="lucide:image-plus" class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                        <p class="text-sm text-gray-500">Arraste ou clique para enviar imagem</p>
                        <p class="text-xs text-gray-400 mt-1">PNG, JPG, GIF, WEBP · máx. 10 MB</p>
                      </div>
                    </div>

                    <!-- Imagens já anexadas na questão sendo editada -->
                    <div v-if="imagensQuestaoAtual.length > 0" class="space-y-2">
                      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Imagens anexadas</p>
                      <div class="grid grid-cols-2 gap-2">
                        <div v-for="img in imagensQuestaoAtual" :key="img.id"
                          class="relative rounded-xl overflow-hidden border border-gray-100 group">
                          <img :src="resolveImageUrl(img.url)" :alt="img.context"
                            class="w-full h-28 object-cover" />
                          <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center">
                            <button
                              class="opacity-0 group-hover:opacity-100 transition-all p-2 rounded-full bg-red-500 text-white"
                              @click="removerImagem(img)">
                              <Icon name="lucide:trash-2" class="w-4 h-4" />
                            </button>
                          </div>
                          <div class="absolute bottom-0 left-0 right-0 bg-black/50 px-2 py-1">
                            <p class="text-[10px] text-white">{{ img.context }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>
              </Transition>
            </div>

            <!-- Preview do enunciado com fórmulas -->
            <Transition name="slide-down">
              <div v-if="stemPreview"
                class="p-3 bg-gray-50 border border-gray-100 rounded-xl">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5 flex items-center gap-1">
                  <Icon name="lucide:eye" class="w-3 h-3" /> Preview do enunciado
                </p>
                <div class="text-sm text-gray-800 leading-relaxed question-content" v-html="stemPreview" />
              </div>
            </Transition>

            <!-- Alternativas -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                Alternativas <span class="text-red-400">*</span>
              </label>
              <div class="space-y-2">
                <div v-for="(_, i) in novaQuestao.options.slice(0, exam.options_count)" :key="i"
                  class="flex items-center gap-2.5">
                  <button
                    class="w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold flex-shrink-0 transition-all duration-150"
                    :class="novaQuestao.correct_label === letras[i]
                      ? 'border-emerald-500 bg-emerald-500 text-white shadow-sm shadow-emerald-200 scale-110'
                      : 'border-gray-200 text-gray-400 hover:border-emerald-400 hover:text-emerald-500'"
                    :title="`Marcar ${letras[i]} como correta`"
                    @click="novaQuestao.correct_label = letras[i]">
                    {{ letras[i] }}
                  </button>
                  <input v-model="novaQuestao.options[i].text" type="text"
                    :placeholder="`Alternativa ${letras[i]}`"
                    class="flex-1 px-3.5 py-2 border rounded-xl text-sm focus:outline-none focus:ring-2 transition-all"
                    :class="novaQuestao.correct_label === letras[i]
                      ? 'border-emerald-300 focus:ring-emerald-400 bg-emerald-50/50'
                      : 'border-gray-200 focus:ring-blue-500 bg-white'" />
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-2 flex items-center gap-1">
                <Icon name="lucide:info" class="w-3 h-3" />
                Clique na letra para marcar o gabarito · use os painéis acima para fórmulas e imagens
              </p>
            </div>

            <!-- Erro -->
            <Transition name="slide-down">
              <div v-if="manualError"
                class="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
                <Icon name="lucide:alert-circle" class="w-4 h-4 flex-shrink-0" />
                {{ manualError }}
              </div>
            </Transition>

            <button :disabled="!questaoValida || savingManual"
              class="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 active:scale-[0.98]"
              :class="questaoValida && !savingManual
                ? editandoId !== null
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                  : 'bg-gray-900 hover:bg-gray-800 text-white shadow-sm'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
              @click="salvarQuestao">
              <Icon v-if="savingManual" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
              <Icon v-else :name="editandoId !== null ? 'lucide:check' : 'lucide:plus'" class="w-4 h-4" />
              {{ savingManual ? 'Salvando...' : editandoId !== null ? 'Salvar alterações' : 'Adicionar questão' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ======================================== -->
      <!-- COLUNA DIREITA: lista de questões        -->
      <!-- ======================================== -->
      <div class="space-y-3">
        <div class="flex items-center justify-between px-1">
          <h3 class="font-semibold text-gray-900">
            Questões
            <span class="ml-1.5 text-sm font-normal text-gray-400 tabular-nums">({{ questoes.length }})</span>
          </h3>
          <span v-if="progresso < 100 && (progressInfo?.quota ?? 0) > 0"
            class="text-xs text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full font-medium">
            faltam {{ Math.max(0, (progressInfo?.quota ?? 0) - (progressInfo?.submitted ?? 0)) }}
          </span>
          <span v-else-if="progresso === 100"
            class="text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
            <Icon name="lucide:check" class="w-3 h-3" /> Cota completa
          </span>
        </div>

        <div v-if="questoes.length === 0"
          class="bg-white rounded-2xl border border-dashed border-gray-200 p-12 text-center">
          <div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-3">
            <Icon name="lucide:file-question" class="w-6 h-6 text-gray-300" />
          </div>
          <p class="text-sm font-medium text-gray-400">Nenhuma questão ainda</p>
          <p class="text-xs text-gray-300 mt-1">Use o formulário ao lado ou importe um arquivo</p>
        </div>

        <TransitionGroup name="list" tag="div" class="space-y-3">
          <div v-for="(q, i) in questoes" :key="q.id"
            class="bg-white rounded-2xl border shadow-sm overflow-hidden transition-all duration-200 group"
            :class="editandoId === q.id
              ? 'border-blue-200 ring-2 ring-blue-100'
              : 'border-gray-100 hover:border-gray-200 hover:shadow-md'">

            <div class="flex items-center justify-between px-4 pt-3.5 pb-2">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center flex-shrink-0"
                  :class="editandoId === q.id ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'">
                  {{ i + 1 }}
                </span>
                <span v-if="q.has_images || q.images?.length"
                  class="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-violet-50 text-violet-600 border border-violet-100">
                  <Icon name="lucide:image" class="w-2.5 h-2.5" /> com imagem
                </span>
                <span v-if="q.source && q.source !== 'manual'"
                  class="text-xs text-gray-400 flex items-center gap-1">
                  <Icon name="lucide:file-text" class="w-3 h-3" /> {{ q.source }}
                </span>
              </div>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                <button
                  class="p-1.5 rounded-lg text-gray-300 hover:text-blue-500 hover:bg-blue-50 transition-colors"
                  :class="{ 'text-blue-500 !bg-blue-50 opacity-100': editandoId === q.id }"
                  title="Editar"
                  @click="editarQuestao(q)">
                  <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
                </button>
                <button
                  class="p-1.5 rounded-lg transition-colors"
                  :class="confirmandoDelecaoId === q.id
                    ? 'text-red-600 bg-red-50'
                    : 'text-gray-300 hover:text-red-500 hover:bg-red-50'"
                  :title="confirmandoDelecaoId === q.id ? 'Clique novamente para confirmar' : 'Remover'"
                  @click="clicarRemover(q.id)">
                  <Icon name="lucide:trash-2" class="w-3.5 h-3.5" />
                </button>
                <button v-if="confirmandoDelecaoId === q.id"
                  class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  title="Cancelar"
                  @click.stop="confirmandoDelecaoId = null">
                  <Icon name="lucide:x" class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <Transition name="slide-down">
              <div v-if="confirmandoDelecaoId === q.id"
                class="mx-4 mb-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
                <span class="text-xs text-red-700 font-medium">Confirmar remoção?</span>
                <div class="flex items-center gap-2">
                  <button class="text-xs font-semibold text-red-600 hover:text-red-700"
                    @click="removerQuestao(q.id)">Remover</button>
                  <button class="text-xs text-gray-400 hover:text-gray-600"
                    @click="confirmandoDelecaoId = null">Cancelar</button>
                </div>
              </div>
            </Transition>

            <div class="px-4 pb-3">
              <div class="text-sm text-gray-800 leading-relaxed question-content"
                v-html="renderStem(q.stem, q.images)" />
            </div>

            <div class="px-4 pb-4 space-y-1.5">
              <div v-for="opt in q.options" :key="opt.label"
                class="flex items-start gap-2 px-2.5 py-2 rounded-lg text-xs transition-colors"
                :class="q.correct_label === opt.label
                  ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
                  : 'bg-gray-50 border border-gray-100 text-gray-600'">
                <span class="font-bold flex-shrink-0 mt-0.5 w-4"
                  :class="q.correct_label === opt.label ? 'text-emerald-600' : 'text-gray-400'">
                  {{ opt.label }}
                </span>
                <div class="flex-1 min-w-0 question-content"
                  v-html="renderOption(opt.text, opt.label, q.images)" />
                <Icon v-if="q.correct_label === opt.label"
                  name="lucide:check" class="w-3 h-3 text-emerald-500 flex-shrink-0 mt-0.5 ml-auto" />
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <Transition name="toast">
    <div v-if="toast.show"
      class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-lg text-sm font-medium min-w-[220px]"
      :class="toast.type === 'success' ? 'bg-gray-900 text-white'
        : toast.type === 'error' ? 'bg-red-600 text-white'
        : 'bg-blue-600 text-white'">
      <Icon :name="toast.type === 'success' ? 'lucide:check-circle-2'
        : toast.type === 'error' ? 'lucide:alert-circle' : 'lucide:info'"
        class="w-4 h-4 flex-shrink-0" />
      {{ toast.message }}
    </div>
  </Transition>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

useHead({
  link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }],
})

const route = useRoute()
const { get, post, patch, delete: deleteReq, upload } = useApi()
const { renderStem, renderOption } = useQuestionRenderer()

const examId = Number(route.params.id)
const letras = ['A', 'B', 'C', 'D', 'E']
const BASE_URL = 'http://localhost:8000'

// ── Estado principal ──
const exam         = ref<any>(null)
const progressInfo = ref<any>(null)
const questoes     = ref<any[]>([])
const loadingExam  = ref(true)

// ── Múltiplas disciplinas e turmas ──
const myAssignments     = ref<any[]>([])          // flat — legado
const myDisciplines     = ref<any[]>([])          // [{ discipline_id, discipline_name, classes: [...] }]
const activeDisciplineId = ref<number | null>(null)
const selectedClassIds  = ref<number[]>([])
const showClassSelector = ref(false)

// Turmas da disciplina atualmente selecionada no modal
const activeDisciplineClasses = computed(() => {
  const disc = myDisciplines.value.find(d => d.discipline_id === activeDisciplineId.value)
  return disc?.classes ?? []
})

const todasTurmasSelecionadas = computed(() =>
  activeDisciplineClasses.value.length > 0 &&
  activeDisciplineClasses.value.every((c: any) => selectedClassIds.value.includes(c.class_id))
)

const turmasLabel = computed(() => {
  if (!progressInfo.value) return '—'
  const ids = progressInfo.value.targetClassIds ?? [progressInfo.value.class_id]
  const allClasses = myDisciplines.value.flatMap((d: any) => d.classes)
  const nomes = allClasses
    .filter((c: any) => ids.includes(c.class_id))
    .map((c: any) => c.class_name)
  return nomes.length ? nomes.join(', ') : progressInfo.value.class_name ?? '—'
})

function selectDiscipline(discId: number) {
  if (activeDisciplineId.value === discId) return
  activeDisciplineId.value = discId
  // Reset turmas ao trocar disciplina — não faz sentido manter seleção de outra disciplina
  selectedClassIds.value = []
}

function toggleTurma(classId: number) {
  const idx = selectedClassIds.value.indexOf(classId)
  if (idx >= 0) selectedClassIds.value.splice(idx, 1)
  else selectedClassIds.value.push(classId)
}

function toggleTodasTurmasDisciplina() {
  if (todasTurmasSelecionadas.value) {
    selectedClassIds.value = []
  } else {
    selectedClassIds.value = activeDisciplineClasses.value.map((c: any) => c.class_id)
  }
}

function fecharModalTurmas() {
  // Se nenhuma configurada ainda, aplica primeira disciplina + primeira turma
  if (!progressInfo.value?.discipline_id && myDisciplines.value.length > 0) {
    const firstDisc = myDisciplines.value[0]
    const firstClass = firstDisc.classes[0]
    if (firstClass) {
      progressInfo.value = {
        ...progressInfo.value,
        discipline_id:   firstDisc.discipline_id,
        discipline_name: firstDisc.discipline_name,
        class_id:        firstClass.class_id,
        class_name:      firstClass.class_name,
        targetClassIds:  [firstClass.class_id],
      }
    }
  }
  showClassSelector.value = false
}

function confirmarSelecaoTurmas() {
  if (!activeDisciplineId.value || selectedClassIds.value.length === 0) return
  const disc = myDisciplines.value.find(d => d.discipline_id === activeDisciplineId.value)
  if (!disc) return
  const firstClass = disc.classes.find((c: any) => selectedClassIds.value.includes(c.class_id))
  progressInfo.value = {
    ...progressInfo.value,
    discipline_id:   disc.discipline_id,
    discipline_name: disc.discipline_name,
    class_id:        firstClass?.class_id ?? selectedClassIds.value[0],
    class_name:      firstClass?.class_name ?? null,
    targetClassIds:  [...selectedClassIds.value],
  }
  showClassSelector.value = false
}

// ── Upload de arquivo ──
const fileInput        = ref<HTMLInputElement | null>(null)
const uploadStatus     = ref<'idle'|'loading'|'success'|'error'>('idle')
const uploadedFileName = ref('')
const uploadError      = ref('')
const isDragging       = ref(false)

// ── Formulário manual ──
const savingManual         = ref(false)
const manualError          = ref('')
const editandoId           = ref<number | null>(null)
const enviado              = ref(false)
const confirmandoDelecaoId = ref<number | null>(null)

// ── Painel de fórmulas ──
const showFormulaPanel  = ref(false)
const formulaInput      = ref('')
const formulaMode       = ref<'inline'|'block'>('inline')
const formulaPreview    = ref('')
const formulaDestino    = ref('stem')

const formulaAtalhos = [
  { label: 'x²',        latex: 'x^{2}' },
  { label: '√x',        latex: '\\sqrt{x}' },
  { label: 'a/b',       latex: '\\frac{a}{b}' },
  { label: 'Σ',         latex: '\\sum_{i=1}^{n}' },
  { label: 'π',         latex: '\\pi' },
  { label: '≥',         latex: '\\geq' },
  { label: '≤',         latex: '\\leq' },
  { label: '±',         latex: '\\pm' },
  { label: 'log',       latex: '\\log_{b}(x)' },
  { label: 'sen/cos',   latex: '\\sin(x) + \\cos(x)' },
  { label: 'Δ',         latex: '\\Delta = b^{2} - 4ac' },
  { label: 'bhaskara',  latex: 'x = \\frac{-b \\pm \\sqrt{b^{2}-4ac}}{2a}' },
]

function inserirFormula(latex: string) {
  formulaInput.value = latex
  atualizarPreviewFormula()
}

function atualizarPreviewFormula() {
  if (!formulaInput.value.trim()) { formulaPreview.value = ''; return }
  try {
    const katex = (window as any).katex
    if (!katex) {
      // fallback: usa renderStem
      const wrapped = formulaMode.value === 'block'
        ? `$$${formulaInput.value}$$`
        : `$${formulaInput.value}$`
      formulaPreview.value = renderStem(wrapped, [])
      return
    }
    formulaPreview.value = katex.renderToString(formulaInput.value, {
      displayMode: formulaMode.value === 'block',
      throwOnError: true,
      strict: false,
    })
  } catch {
    formulaPreview.value = ''
  }
}

watch(formulaMode, atualizarPreviewFormula)

function confirmarInsercaoFormula() {
  if (!formulaInput.value.trim() || !formulaPreview.value) return
  const wrapped = formulaMode.value === 'block'
    ? `$$${formulaInput.value}$$`
    : `$${formulaInput.value}$`

  if (formulaDestino.value === 'stem') {
    novaQuestao.stem += (novaQuestao.stem ? ' ' : '') + wrapped
  } else {
    const letra = formulaDestino.value.replace('option_', '')
    const opt = novaQuestao.options.find(o => o.label === letra)
    if (opt) opt.text += (opt.text ? ' ' : '') + wrapped
  }
  formulaInput.value = ''
  formulaPreview.value = ''
  showFormulaPanel.value = false
  showToast('Fórmula inserida!', 'success')
}

// ── Painel de imagens ──
const showImagePanel    = ref(false)
const imageDestino      = ref('stem')
const imageDragging     = ref(false)
const uploadingImage    = ref(false)
const imageFileInput    = ref<HTMLInputElement | null>(null)
const imagensQuestaoAtual = ref<any[]>([])

function resolveImageUrl(url: string): string {
  return url.startsWith('http') ? url : `${BASE_URL}${url}`
}

function triggerImageInput() {
  if (uploadingImage.value) return
  imageFileInput.value?.click()
}

function handleImageDrop(e: DragEvent) {
  imageDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) uploadImage(file)
}

function handleImageFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) uploadImage(file)
}

async function uploadImage(file: File) {
  if (!editandoId.value) return
  uploadingImage.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('context', imageDestino.value)
    const result = await upload<any>(
      `/exams/${examId}/questions/${editandoId.value}/images`,
      formData
    )
    imagensQuestaoAtual.value.push(result)
    // Atualiza questão na lista
    const q = questoes.value.find(q => q.id === editandoId.value)
    if (q) {
      q.has_images = true
      q.images = [...(q.images ?? []), result]
    }
    showToast('Imagem adicionada!', 'success')
  } catch (e: any) {
    showToast(e.message ?? 'Erro ao enviar imagem', 'error')
  } finally {
    uploadingImage.value = false
    if (imageFileInput.value) imageFileInput.value.value = ''
  }
}

async function removerImagem(img: any) {
  try {
    await deleteReq(`/exams/${examId}/questions/${editandoId.value}/images/${img.id}`)
    imagensQuestaoAtual.value = imagensQuestaoAtual.value.filter(i => i.id !== img.id)
    const q = questoes.value.find(q => q.id === editandoId.value)
    if (q) q.images = (q.images ?? []).filter((i: any) => i.id !== img.id)
    showToast('Imagem removida.', 'success')
  } catch (e: any) {
    showToast(e.message ?? 'Erro ao remover imagem', 'error')
  }
}

// ── Toast ──
const toast = reactive({ show: false, message: '', type: 'success' as 'success'|'error'|'info' })
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(message: string, type: 'success'|'error'|'info' = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.message = message
  toast.type    = type
  toast.show    = true
  toastTimer = setTimeout(() => { toast.show = false }, 3000)
}

const editandoIndex = computed(() =>
  questoes.value.findIndex(q => q.id === editandoId.value)
)

const novaQuestao = reactive({
  stem: '',
  options: letras.map(l => ({ label: l, text: '' })),
  correct_label: 'A',
})

// Preview LaTeX do enunciado (debounced)
const stemPreview = ref('')
let previewTimer: ReturnType<typeof setTimeout> | null = null
watch(() => novaQuestao.stem, (val) => {
  if (previewTimer) clearTimeout(previewTimer)
  if (!val.trim() || !val.includes('$')) { stemPreview.value = ''; return }
  previewTimer = setTimeout(() => {
    stemPreview.value = renderStem(val, [])
  }, 400)
})

const progresso = computed(() => {
  const quota     = progressInfo.value?.quota ?? 0
  const submitted = progressInfo.value?.submitted ?? 0
  if (!quota) return 0
  return Math.min(100, Math.round((submitted / quota) * 100))
})

const questaoValida = computed(() => {
  const count = exam.value?.options_count ?? 4
  return (
    novaQuestao.stem.trim() !== '' &&
    novaQuestao.options.slice(0, count).every(o => o.text.trim() !== '')
  )
})

function normalizeQuestion(q: any): any {
  return { ...q, images: q.images ?? [] }
}

// ── Fetch inicial ──
onMounted(async () => {
  loadingExam.value = true
  try {
    const [examData, progressData, questoesData, myAssignment] = await Promise.all([
      get<any>(`/exams/${examId}`),
      get<any>(`/exams/${examId}/progress`),
      get<any[]>(`/exams/${examId}/questions`),
      get<any>(`/exams/${examId}/my-assignment`).catch(() => null),
    ])
    exam.value     = examData
    questoes.value = (questoesData ?? []).map(normalizeQuestion)

    if (myAssignment) {
      myAssignments.value  = myAssignment.assignments ?? [myAssignment]
      myDisciplines.value  = myAssignment.disciplines ?? []

      // Se o backend ainda não retorna disciplines (versão antiga), montar manualmente
      if (!myDisciplines.value.length && myAssignments.value.length) {
        const discMap: Record<number, any> = {}
        for (const a of myAssignments.value) {
          if (!discMap[a.discipline_id]) {
            discMap[a.discipline_id] = {
              discipline_id:   a.discipline_id,
              discipline_name: a.discipline_name,
              classes: [],
            }
          }
          discMap[a.discipline_id].classes.push({ class_id: a.class_id, class_name: a.class_name })
        }
        myDisciplines.value = Object.values(discMap)
      }

      // Configurar disciplina ativa inicial = primeira disciplina
      const firstDisc  = myDisciplines.value[0]
      const firstClass = firstDisc?.classes?.[0]

      if (firstDisc && firstClass) {
        activeDisciplineId.value = firstDisc.discipline_id
        selectedClassIds.value   = [firstClass.class_id]

        if (progressData?.disciplines?.length) {
          const myDisc = progressData.disciplines.find(
            (d: any) => d.discipline_id === firstDisc.discipline_id
          ) ?? progressData.disciplines[0]

          progressInfo.value = {
            ...myDisc,
            discipline_id:   firstDisc.discipline_id,
            discipline_name: firstDisc.discipline_name,
            class_id:        firstClass.class_id,
            class_name:      firstClass.class_name,
            targetClassIds:  [firstClass.class_id],
          }
        }
      }

      // Abre modal se tiver múltiplas disciplinas OU múltiplas turmas em alguma disciplina
      const hasMultiple = myDisciplines.value.length > 1 ||
        myDisciplines.value.some((d: any) => d.classes.length > 1)
      if (hasMultiple) {
        showClassSelector.value = true
      }
    } else if (progressData?.disciplines?.length) {
      progressInfo.value = {
        ...progressData.disciplines[0],
        submitted:      questoes.value.length,
        class_id:       null,
        class_name:     null,
        targetClassIds: [],
      }
    }
  } catch {
    exam.value = null
  } finally {
    loadingExam.value = false
  }
})

// ── Upload de arquivo ──
function triggerFileInput() {
  if (uploadStatus.value === 'loading') return
  fileInput.value?.click()
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) processFile(file)
}

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) processFile(file)
}

async function processFile(file: File) {
  const allowed = ['.docx', '.txt', '.pdf']
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!allowed.includes(ext)) {
    uploadStatus.value = 'error'
    uploadError.value  = 'Formato não suportado. Use .docx, .txt ou .pdf'
    return
  }
  uploadedFileName.value = file.name
  uploadStatus.value     = 'loading'
  uploadError.value      = ''

  try {
    const targetIds = progressInfo.value?.targetClassIds ?? [progressInfo.value?.class_id]
    // Envia para cada turma selecionada
    for (const classId of targetIds) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('class_id',      String(classId))
      formData.append('discipline_id', String(progressInfo.value?.discipline_id ?? 0))
      await upload<any>(`/exams/${examId}/questions/upload`, formData)
    }
    uploadStatus.value = 'success'
    questoes.value = (await get<any[]>(`/exams/${examId}/questions`)).map(normalizeQuestion)
    await recarregarProgresso()
    showToast('Questões importadas com sucesso!')
  } catch (e: any) {
    uploadStatus.value = 'error'
    uploadError.value  = e.message ?? 'Erro ao processar o arquivo'
    showToast(uploadError.value, 'error')
  }
}

function resetUpload() {
  uploadStatus.value     = 'idle'
  uploadedFileName.value = ''
  uploadError.value      = ''
  if (fileInput.value) fileInput.value.value = ''
}

// ── Questão manual ──
async function salvarQuestao() {
  manualError.value  = ''
  savingManual.value = true

  const count   = exam.value?.options_count ?? 4
  const targetIds = progressInfo.value?.targetClassIds ?? [progressInfo.value?.class_id]

  try {
    if (editandoId.value !== null) {
      // Edição: atualiza apenas a questão original (1 turma)
      const payload = {
        stem: novaQuestao.stem.trim(),
        options: novaQuestao.options.slice(0, count).map(o => ({
          label: o.label, text: o.text.trim(),
        })),
        correct_label:  novaQuestao.correct_label || undefined,
        discipline_id:  progressInfo.value?.discipline_id,
        class_id:       progressInfo.value?.class_id,
      }
      const updated = normalizeQuestion(await patch<any>(`/exams/${examId}/questions/${editandoId.value}`, payload))
      const idx = questoes.value.findIndex(q => q.id === editandoId.value)
      if (idx !== -1) questoes.value[idx] = updated
      editandoId.value = null
      showToast('Questão atualizada!')
    } else {
      // Criação: duplica para cada turma selecionada
      for (const classId of targetIds) {
        const payload = {
          stem: novaQuestao.stem.trim(),
          options: novaQuestao.options.slice(0, count).map(o => ({
            label: o.label, text: o.text.trim(),
          })),
          correct_label:  novaQuestao.correct_label || undefined,
          discipline_id:  progressInfo.value?.discipline_id,
          class_id:       classId,
        }
        await post<any>(`/exams/${examId}/questions`, payload)
      }
      // Recarrega lista completa para garantir que todas aparecem imediatamente
      questoes.value = (await get<any[]>(`/exams/${examId}/questions`)).map(normalizeQuestion)
      showToast(targetIds.length > 1
        ? `Questão adicionada para ${targetIds.length} turmas!`
        : 'Questão adicionada!')
    }
    resetForm()
    await recarregarProgresso()
  } catch (e: any) {
    manualError.value = e.message ?? 'Erro ao salvar questão.'
    showToast(manualError.value, 'error')
  } finally {
    savingManual.value = false
  }
}

function editarQuestao(q: any) {
  editandoId.value           = q.id
  novaQuestao.stem           = q.stem
  novaQuestao.correct_label  = q.correct_label ?? 'A'
  novaQuestao.options = letras.map(l => ({
    label: l,
    text:  q.options.find((o: any) => o.label === l)?.text ?? '',
  }))
  manualError.value         = ''
  imagensQuestaoAtual.value = [...(q.images ?? [])]
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelarEdicao() {
  editandoId.value          = null
  imagensQuestaoAtual.value = []
  resetForm()
}

function clicarRemover(id: number) {
  const numId = Number(id)
  if (!numId || isNaN(numId)) return
  if (confirmandoDelecaoId.value === numId) {
    removerQuestao(numId)
  } else {
    confirmandoDelecaoId.value = numId
    setTimeout(() => {
      if (confirmandoDelecaoId.value === numId) confirmandoDelecaoId.value = null
    }, 3000)
  }
}

async function removerQuestao(id: number) {
  confirmandoDelecaoId.value = null
  const numId = Number(id)
  if (!numId || isNaN(numId)) {
    showToast('ID de questão inválido.', 'error')
    return
  }
  try {
    await deleteReq(`/exams/${examId}/questions/${numId}`)
    questoes.value = questoes.value.filter(q => Number(q.id) !== numId)
    if (editandoId.value === numId) cancelarEdicao()
    await recarregarProgresso()
    showToast('Questão removida.')
  } catch (e: any) {
    showToast(e.message ?? 'Erro ao remover questão.', 'error')
  }
}

function resetForm() {
  novaQuestao.stem          = ''
  novaQuestao.options       = letras.map(l => ({ label: l, text: '' }))
  novaQuestao.correct_label = 'A'
  manualError.value         = ''
  stemPreview.value         = ''
  formulaInput.value        = ''
  formulaPreview.value      = ''
}

function concluirEnvio() {
  enviado.value = true
  setTimeout(() => navigateTo('/dashboard/professor'), 1800)
}

async function recarregarProgresso() {
  try {
    const [data, myAssignment] = await Promise.all([
      get<any>(`/exams/${examId}/progress`),
      get<any>(`/exams/${examId}/my-assignment`).catch(() => null),
    ])
    if (data?.disciplines?.length) {
      const discId = myAssignment?.discipline_id ?? progressInfo.value?.discipline_id
      const myDisc = data.disciplines.find((d: any) => d.discipline_id === discId)
        ?? data.disciplines[0]
      const mySubmitted = questoes.value.filter(
        (q: any) => q.discipline_id === discId
      ).length
      progressInfo.value = {
        ...myDisc,
        submitted:       mySubmitted,
        class_id:        progressInfo.value?.class_id,
        discipline_id:   discId,
        class_name:      progressInfo.value?.class_name,
        discipline_name: progressInfo.value?.discipline_name,
        targetClassIds:  progressInfo.value?.targetClassIds,
      }
    }
  } catch {}
}
</script>

<style>
.question-content img.question-img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 6px 0;
  display: block;
}
.question-content .katex-display { margin: 8px 0; overflow-x: auto; }
.question-content .katex { font-size: 1em; }
.question-content .math-block {
  display: block; font-family: monospace; background: #f8f9fa;
  border: 1px solid #e9ecef; border-radius: 4px; padding: 4px 8px;
  margin: 4px 0; font-size: 0.85em; color: #495057;
}
.question-content .math-inline {
  font-family: monospace; background: #f8f9fa;
  border-radius: 3px; padding: 1px 4px; font-size: 0.85em; color: #495057;
}
.question-content .math-error { color: #dc3545; font-family: monospace; font-size: 0.8em; }
</style>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0; max-height: 0; transform: translateY(-4px);
}
.slide-down-enter-to, .slide-down-leave-from { max-height: 600px; }

.pop-enter-active { transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-leave-active { transition: all 0.15s ease; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: scale(0.8); }

.toast-enter-active { transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateY(16px) scale(0.95); }
.toast-leave-to   { opacity: 0; transform: translateY(8px); }

.list-enter-active { transition: all 0.25s ease; }
.list-leave-active { transition: all 0.2s ease; position: absolute; width: 100%; }
.list-enter-from   { opacity: 0; transform: translateY(-8px); }
.list-leave-to     { opacity: 0; transform: translateX(16px); }
.list-move         { transition: transform 0.3s ease; }
</style>
