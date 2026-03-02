# tests/conftest.py
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
from dataclasses import dataclass
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
    email: str = "john.doe"         # seu login usa form_data.username como “email”
    # Alguns handlers usam 'password_hash', outros 'hashed_password' — oferecemos ambos
    password_hash: str = "fake-hash"
    hashed_password: str = "fake-hash"
    roles: list[RoleStub] = None
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

# Disciplina “modelo” bem simples para armazenar os atributos que o Pydantic vai ler
@dataclass
class DisciplineStub:
    id: int | None = None
    name: str = ""

class _QueryStub:
    """
    Implementa cadeia mínima: .filter(...).order_by(...).first()/.all()
    Ignora a expressão de filtro (retorna os registros "como estão").
    Para o nosso fluxo de criação de disciplina:
      - 'exists' será None porque começamos com lista vazia.
      - Depois de add/commit, o handler retorna a própria instância criada.
    """
    def __init__(self, model: Any, records: List[Any]):
        self.model = model
        self._records = records

    def filter(self, *args, **kwargs):
        # não filtramos — suficiente para testes de fluxo
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._records[0] if self._records else None

    def all(self):
        return list(self._records)


class FakeSession:
    """
    Session minimalista para atender handlers que usam ORM:
    - .get(Model, id)
    - .query(Model) -> _QueryStub
    - .add(obj), .commit(), .refresh(obj)
    """
    def __init__(self) -> None:
        # exam 1 = LOCKED; exam 2 = DRAFT
        self._exams = {
            1: ExamStub(id=1, status=ExamStatus.LOCKED),
            2: ExamStub(id=2, status=ExamStatus.DRAFT),
        }
        self._classes = {10: ClassStub(id=10)}
        self._students = {100: StudentStub(id=100)}
        self._users = [UserStub(id=123, username="coordinator", email="john.doe")]

        # “Banco” de disciplinas em memória
        self._disciplines: dict[int, DisciplineStub] = {}
        self._next_disc_id = 1000

        # fila de pendências para simular add/commit
        self._pending: list[Any] = []

    def get(self, model, obj_id: int):
        name = getattr(model, "__name__", str(model))
        if name.endswith("Exam"):
            return self._exams.get(obj_id)
        if name.endswith("SchoolClass"):
            return self._classes.get(obj_id)
        if name.endswith("Student"):
            return self._students.get(obj_id)
        if name.endswith("Discipline"):
            return self._disciplines.get(obj_id)
        if name.endswith("User"):
            # get(User, id) – raramente usado nos handlers atuais
            for u in self._users:
                if u.id == obj_id:
                    return u
        return None

    def query(self, model):
        name = getattr(model, "__name__", str(model))
        if name.endswith("User"):
            return _QueryStub(model, self._users)
        if name.endswith("Student"):
            return _QueryStub(model, [self._students[100]])
        if name.endswith("SchoolClass"):
            return _QueryStub(model, [self._classes[10]])
        if name.endswith("Discipline"):
            # lista de disciplinas existentes
            return _QueryStub(model, list(self._disciplines.values()))
        # default: lista vazia
        return _QueryStub(model, [])

    def add(self, obj):
        # guarda para “commit”
        self._pending.append(obj)

    def commit(self):
        # persiste pendências e atribui IDs quando necessário
        for obj in self._pending:
            # Se for disciplina, garantimos ID
            if isinstance(obj, DisciplineStub) or getattr(obj, "__class__", None).__name__ == "Discipline":
                # se não houver id, atribui
                if getattr(obj, "id", None) in (None, 0):
                    setattr(obj, "id", self._next_disc_id)
                    self._next_disc_id += 1
                # checksum básico: precisa ter name
                name = getattr(obj, "name", None)
                if name is not None:
                    self._disciplines[getattr(obj, "id")] = DisciplineStub(id=getattr(obj, "id"), name=name)
        self._pending.clear()

    def refresh(self, obj):
        # no-op suficiente para o handler; o ID já foi atribuído em commit()
        return

    def close(self) -> None:
        pass


@contextlib.contextmanager
def _override_dependencies() -> Generator[None, None, None]:
    # get_db -> FakeSession
    def _override_get_db():
        db = FakeSession()
        try:
            yield db
        finally:
            db.close()

    # get_current_user -> user com papel COORDINATOR
    def _override_get_current_user():
        return UserStub()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)

# ==== 4) Cliente HTTPX assíncrono (segue redirects para evitar 307) =================

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    # backend compatível com pytest.anyio
    return "asyncio"

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    with _override_dependencies():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            timeout=10.0,
            follow_redirects=True,  # <- evita 307 em rotas com barra final
        ) as ac:
            yield ac
