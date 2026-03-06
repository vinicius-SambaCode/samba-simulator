# =============================================================================
# tests/conftest.py
# =============================================================================
#
# RESPONSABILIDADE DESTE ARQUIVO:
#   Configurar fixtures e mocks compartilhados por todos os testes.
#
# O QUE MUDOU NO PASSO 4:
#   FakeSession._disciplines agora começa com dados pré-populados.
#
#   ANTES: self._disciplines = {}  ← dicionário vazio
#          db.get(Discipline, 7) retornava None → handler lançava 404
#          → testes de GET /disciplines/{id} ficavam em XFAIL
#
#   AGORA: self._disciplines = {7: DisciplineStub(id=7, name="Física"), ...}
#          db.get(Discipline, 7) retorna o stub → handler retorna 200
#          → testes passam como PASSED
#
#   IMPORTANTE: o id 999 NÃO foi adicionado — isso é proposital.
#          O teste test_get_discipline_not_found precisa que 999 retorne
#          None para que o handler lance o 404 correto (recurso inexistente).
# =============================================================================

from __future__ import annotations

# === 0) Garantir que 'backend/' está no sys.path ===
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# === 1) Imports padrão dos testes ===
import contextlib
import os
from dataclasses import dataclass, field
from typing import AsyncGenerator, Generator, Any, List

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.exam import ExamStatus


# ==== 2) Alembic (migrations) =====================================================

from alembic.config import Config

@pytest.fixture(scope="session")
def alembic_config() -> Config:
    """
    Config do Alembic para o pytest-alembic:
      - aponto script_location e URL
      - limito o downgrade até a revisão segura (legado com FK sem nome)
    """
    from app.core.settings import settings  # import tardio, após sys.path ajustado

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", getattr(settings, "SQLALCHEMY_URL", settings.DATABASE_URL))
    # evitar trecho problemático no downgrade total
    cfg.attributes["minimum_downgrade_revision"] = "f27c5666bd61"
    return cfg


def pytest_collection_modifyitems(config, items):
    """
    - Fora do Docker/CI (sem DB_TESTS), pula testes 'alembic'.
    - Dentro do Docker/CI (com DB_TESTS=1), roda alembic,
      mas pula apenas 'test_up_down_consistency' (downgrade total legado).
    """
    db_tests = bool(os.getenv("DB_TESTS"))
    for item in items:
        if "alembic" in item.keywords:
            if not db_tests:
                item.add_marker(pytest.mark.skip(
                    reason="DB tests (alembic) pulados fora do Docker. Use DB_TESTS=1 para habilitar."
                ))
            else:
                if item.name == "test_up_down_consistency":
                    item.add_marker(pytest.mark.skip(
                        reason="Downgrade total desabilitado por constraints sem nome no histórico legado."
                    ))


# ==== 3) Stubs de domínio (sem tocar DB) =========================================

@dataclass
class RoleStub:
    name: str


@dataclass
class UserStub:
    id: int = 1
    username: str = "coordinator"
    email: str = "john.doe"
    password_hash: str = "fake-hash"
    hashed_password: str = "fake-hash"
    roles: list = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = [RoleStub("COORDINATOR")]


@dataclass
class ExamStub:
    id: int
    status: ExamStatus


@dataclass
class ClassStub:
    id: int


@dataclass
class StudentStub:
    id: int


@dataclass
class DisciplineStub:
    """
    Stub de Discipline para testes.
    Deve ter os mesmos campos que o Pydantic DisciplineOut espera:
      id   → int
      name → str
    """
    id: int | None = None
    name: str = ""


class _QueryStub:
    """
    Implementa cadeia mínima de query ORM para testes:
      .filter(*clauses).order_by(...).first() / .all()

    DESIGN DELIBERADO — sem filtro real:
      O .filter() ignora as cláusulas e retorna os próprios registros.
      Isso é intencional e suficiente para os testes atuais porque:

      1. Verificação de duplicata (POST /disciplines):
           db.query(Discipline).filter(name == X).first()
         → FakeSession.query(Discipline) retorna lista VAZIA
         → .filter() não muda nada → .first() retorna None
         → handler entende "não existe" → cria normalmente ✅

      2. Listagem (GET /disciplines):
           db.query(Discipline).all()
         → FakeSession.query(Discipline) retorna lista VAZIA
         → handler retorna [] ✅
         (os dados reais ficam em _disciplines, acessados via .get())

      3. Busca por ID (GET /disciplines/{id}):
           db.get(Discipline, id)
         → FakeSession.get() acessa _disciplines diretamente ✅
         (não passa pelo _QueryStub)

    RESUMO: .query() + .filter() são usados para verificações de existência
    e listagens. .get() é usado para busca por PK. Mantemos os dois caminhos
    separados e simples.
    """
    def __init__(self, model: Any, records: List[Any]):
        self.model = model
        self._records = list(records)

    def filter(self, *args, **kwargs):
        # Sem filtro real — retorna os mesmos registros.
        # FakeSession.query(Discipline) já entrega lista vazia,
        # então .filter().first() → None → handler não vê duplicata.
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._records[0] if self._records else None

    def all(self):
        return list(self._records)


class FakeSession:
    """
    Session ORM minimalista para testes unitários sem banco de dados.

    Implementa a interface usada pelos handlers:
      .get(Model, id)         → busca por PK
      .query(Model)           → retorna _QueryStub com dados mockados
      .add(obj)               → enfileira para commit
      .commit()               → persiste pendências, atribui IDs
      .refresh(obj)           → no-op (ID já foi atribuído no commit)
      .rollback()             → descarta pendências
      .close()                → no-op
    """

    def __init__(self) -> None:
        # --- Simulados ---
        self._exams = {
            1: ExamStub(id=1, status=ExamStatus.LOCKED),
            2: ExamStub(id=2, status=ExamStatus.DRAFT),
        }

        # --- Estrutura escolar ---
        self._classes  = {10: ClassStub(id=10)}
        self._students = {100: StudentStub(id=100)}

        # --- Usuários ---
        self._users = [UserStub(id=123, username="coordinator", email="john.doe")]

        # -------------------------------------------------------------------------
        # PASSO 4: disciplinas pré-populadas
        # -------------------------------------------------------------------------
        # Adicionamos registros reais para que db.get(Discipline, id) funcione
        # nos testes de GET /disciplines/{id}.
        #
        # IDs incluídos: 7 e alguns extras (realistas para um sistema escolar).
        # ID 999 NÃO está aqui — propositalmente, para que o teste
        # test_get_discipline_not_found receba None e o handler lance 404.
        # -------------------------------------------------------------------------
        self._disciplines: dict[int, DisciplineStub] = {
            1:  DisciplineStub(id=1,  name="Língua Portuguesa"),
            2:  DisciplineStub(id=2,  name="Matemática"),
            3:  DisciplineStub(id=3,  name="Ciências"),
            4:  DisciplineStub(id=4,  name="História"),
            5:  DisciplineStub(id=5,  name="Geografia"),
            6:  DisciplineStub(id=6,  name="Arte"),
            7:  DisciplineStub(id=7,  name="Física"),      # ← usado em test_get_discipline_found
            8:  DisciplineStub(id=8,  name="Química"),
            9:  DisciplineStub(id=9,  name="Biologia"),
            10: DisciplineStub(id=10, name="Educação Física"),
        }

        # Contador para novos IDs criados via add/commit
        self._next_disc_id = 1000

        # Fila de objetos pendentes de commit
        self._pending: list[Any] = []

    # -------------------------------------------------------------------------
    # get — busca por PK
    # -------------------------------------------------------------------------
    def get(self, model, obj_id: int):
        """
        Simula db.get(Model, id).
        Cada model é roteado para o dicionário correspondente.
        Retorna None se o id não existir — comportamento idêntico ao SQLAlchemy.
        """
        name = getattr(model, "__name__", str(model))

        if name.endswith("Exam"):
            return self._exams.get(obj_id)

        if name.endswith("SchoolClass"):
            return self._classes.get(obj_id)

        if name.endswith("Student"):
            return self._students.get(obj_id)

        if name.endswith("Discipline"):
            # Retorna o stub se existir, None se não existir (ex.: id=999)
            return self._disciplines.get(obj_id)

        if name.endswith("User"):
            for u in self._users:
                if u.id == obj_id:
                    return u

        return None

    # -------------------------------------------------------------------------
    # query — listagem / filtro simples
    # -------------------------------------------------------------------------
    def query(self, model):
        """
        Simula db.query(Model).
        Retorna um _QueryStub com a lista de registros do model.
        """
        name = getattr(model, "__name__", str(model))

        if name.endswith("User"):
            return _QueryStub(model, self._users)

        if name.endswith("Student"):
            return _QueryStub(model, list(self._students.values()))

        if name.endswith("SchoolClass"):
            return _QueryStub(model, list(self._classes.values()))

        if name.endswith("Discipline"):
            # Retorna lista VAZIA intencionalmente.
            # Motivo: .query(Discipline) é usado pelo handler para verificar
            # duplicatas (filter+first) e listagens (all).
            # → filter().first() → None → handler não vê duplicata → cria ✅
            # → all() → [] → listagem vazia ✅
            # Busca por PK real usa db.get() que acessa _disciplines diretamente.
            return _QueryStub(model, [])

        # default: lista vazia (model desconhecido)
        return _QueryStub(model, [])

    # -------------------------------------------------------------------------
    # add / commit / refresh / rollback / close
    # -------------------------------------------------------------------------
    def add(self, obj):
        """Enfileira objeto para persistência no próximo commit."""
        self._pending.append(obj)

    def commit(self):
        """
        Simula a persistência: atribui IDs a novos objetos e salva no dicionário.
        Apenas Discipline é tratada explicitamente (outros models não precisam).
        """
        for obj in self._pending:
            class_name = getattr(obj.__class__, "__name__", "")

            if class_name == "Discipline" or isinstance(obj, DisciplineStub):
                # Atribui ID se ainda não tiver
                if getattr(obj, "id", None) in (None, 0):
                    setattr(obj, "id", self._next_disc_id)
                    self._next_disc_id += 1

                # Persiste no dicionário interno
                disc_id = getattr(obj, "id")
                disc_name = getattr(obj, "name", None)
                if disc_name is not None:
                    self._disciplines[disc_id] = DisciplineStub(
                        id=disc_id, name=disc_name
                    )

        self._pending.clear()

    def refresh(self, obj):
        """
        No-op: o ID já foi atribuído em commit().
        O handler pode continuar usando obj.id normalmente após o refresh.
        """
        pass

    def rollback(self):
        """Descarta pendências sem persistir (usado em dry_run)."""
        self._pending.clear()

    def close(self) -> None:
        """No-op: não há conexão real para fechar."""
        pass


# ==== 4) Override de dependências ================================================

@contextlib.contextmanager
def _override_dependencies() -> Generator[None, None, None]:
    """
    Context manager que substitui as dependências reais pelas versões mock:
      get_db           → FakeSession (sem banco de dados)
      get_current_user → UserStub   (sem JWT)
    """

    def _override_get_db():
        db = FakeSession()
        try:
            yield db
        finally:
            db.close()

    def _override_get_current_user():
        return UserStub()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


# ==== 5) Cliente HTTPX assíncrono ================================================

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP assíncrono para testes de integração.

    follow_redirects=True: evita que redirecionamentos 307 causem falsos negativos.
    Os overrides de dependência são aplicados apenas durante o teste.
    """
    with _override_dependencies():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            timeout=10.0,
            follow_redirects=True,
        ) as ac:
            yield ac
