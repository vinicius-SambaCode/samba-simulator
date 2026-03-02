# backend/tools/pyd_v2_migrate.py
"""
Migração Pydantic v1 -> v2:
- Substitui 'class Config:' por 'model_config = ConfigDict(...)'
- Converte 'orm_mode=True' -> 'from_attributes=True'
- Preserva/transforma as opções comuns: extra, populate_by_name, use_enum_values, arbitrary_types_allowed
- Deixa comentários para opções não mapeadas (ex.: json_encoders)
- Garante import 'ConfigDict' no arquivo
- Cria backup .bak (a cada arquivo)
- Suporta dry-run para visualizar as mudanças sem aplicá-las
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # .../backend
INCLUDE_DIRS = ["app"]  # ajuste se houver outras pastas

RE_CLASS_CONFIG = re.compile(r"^(\s*)class\s+Config\s*:\s*$", re.MULTILINE)

# Linhas reconhecíveis (interno do bloco Config)
RE_ORM_MODE = re.compile(r"^\s*orm_mode\s*=\s*True\s*$")
RE_EXTRA = re.compile(r'^\s*extra\s*=\s*"(ignore|forbid|allow)"\s*$')
RE_POPULATE_BY_NAME = re.compile(r"^\s*(allow_population_by_field_name|populate_by_name)\s*=\s*True\s*$")
RE_USE_ENUM_VALUES = re.compile(r"^\s*use_enum_values\s*=\s*True\s*$")
RE_ARBITRARY_TYPES = re.compile(r"^\s*arbitrary_types_allowed\s*=\s*True\s*$")
RE_JSON_ENCODERS = re.compile(r"^\s*json_encoders\s*=\s*\{.*", re.DOTALL)

def _ensure_configdict_import(code: str) -> str:
    # Já importa?
    if re.search(r"from\s+pydantic\s+import\s+.*\bConfigDict\b", code):
        return code
    # Tenta anexar a uma linha existente from pydantic import ...
    m = re.search(r"^from\s+pydantic\s+import\s+([^\n]+)", code, flags=re.MULTILINE)
    if m:
        line, imports = m.group(0), m.group(1)
        if "ConfigDict" not in imports:
            return code.replace(line, f"{line}, ConfigDict")
        return code
    # Caso contrário, injeta um novo import após o primeiro import do arquivo
    first_import = re.search(r"^import\s+|^from\s+", code, flags=re.MULTILINE)
    insert_at = 0
    if first_import:
        # após a primeira linha de import
        line_end = code.find("\n", first_import.start())
        insert_at = line_end + 1 if line_end != -1 else 0
    return code[:insert_at] + "from pydantic import ConfigDict\n" + code[insert_at:]

def _dedent_block(block_text: str) -> list[str]:
    lines = block_text.splitlines()
    # remove linhas vazias de topo/fundo
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # remove indent comum
    if not lines:
        return []
    prefix = len(lines[0]) - len(lines[0].lstrip())
    return [ln[prefix:] if len(ln) >= prefix else ln for ln in lines]

def _extract_config_block(code: str, start_idx: int) -> tuple[int, int, str]:
    """
    A partir da linha 'class Config:', encontra o bloco indentado seguinte.
    Retorna (ini_bloco, fim_bloco, texto_do_bloco).
    """
    ini = code.find("\n", start_idx) + 1
    if ini <= 0:
        return start_idx, len(code), ""
    i = ini
    n = len(code)
    while i < n:
        nl = code.find("\n", i)
        if nl == -1:
            nl = n
        line = code[i:nl]
        # fim do bloco quando a linha não tiver indentação (nem em branco)
        if line.strip() and not (line.startswith(" ") or line.startswith("\t")):
            break
        i = nl + 1
    return ini, i, code[ini:i]

def _build_model_config(indent_for_class: str, config_body: str) -> str:
    """
    Constrói 'model_config = ConfigDict(...)' usando mapeamento v1->v2.
    Produz comentários para opções não mapeadas.
    """
    options = {
        "from_attributes": False,
        "extra": None,  # ignore|forbid|allow
        "populate_by_name": False,
        "use_enum_values": False,
        "arbitrary_types_allowed": False
    }
    comments = []

    lines = [ln.strip() for ln in _dedent_block(config_body) if ln.strip()]
    for ln in lines:
        if RE_ORM_MODE.match(ln):
            options["from_attributes"] = True
            continue
        m = RE_EXTRA.match(ln)
        if m:
            options["extra"] = m.group(1)
            continue
        if RE_POPULATE_BY_NAME.match(ln):
            options["populate_by_name"] = True
            continue
        if RE_USE_ENUM_VALUES.match(ln):
            options["use_enum_values"] = True
            continue
        if RE_ARBITRARY_TYPES.match(ln):
            options["arbitrary_types_allowed"] = True
            continue
        if ln.startswith("json_encoders"):
            comments.append(f"# Pydantic v2: revisar json_encoders -> usar field_serializer/model_dump. Linha original: {ln}")
            continue
        # Deixar qualquer outro item como comentário para revisão
        comments.append(f"# Pydantic v2: revisar opção não migrada: {ln}")

    args = []
    if options["from_attributes"]:
        args.append("from_attributes=True")
    if options["extra"]:
        args.append(f'extra="{options["extra"]}"')
    if options["populate_by_name"]:
        args.append("populate_by_name=True")
    if options["use_enum_values"]:
        args.append("use_enum_values=True")
    if options["arbitrary_types_allowed"]:
        args.append("arbitrary_types_allowed=True")

    args_str = ", ".join(args)
    mc_line = f"{indent_for_class}model_config = ConfigDict({args_str})\n" if args_str else f"{indent_for_class}model_config = ConfigDict()\n"
    comment_block = "".join(indent_for_class + c + "\n" for c in comments)
    return comment_block + mc_line

def migrate_file(path: Path, dry_run: bool = False) -> bool:
    code = path.read_text(encoding="utf-8")
    changed = False
    out = code
    offset = 0

    for m in list(RE_CLASS_CONFIG.finditer(code)):
        start = m.start(0) + offset
        end = m.end(0) + offset

        # indent da própria linha 'class Config:' (nível da classe)
        indent_for_class = m.group(1)
        block_ini, block_fim, block_text = _extract_config_block(out, end)

        replacement = _build_model_config(indent_for_class, block_text)
        # substitui do INÍCIO da linha 'class Config:' até o fim do bloco
        out = out[:start] + replacement + out[block_fim:]
        delta = len(replacement) - (block_fim - start)
        offset += delta
        changed = True

    if changed:
        out = _ensure_configdict_import(out)
        if not dry_run:
            # backup
            path.with_suffix(path.suffix + ".bak").write_text(code, encoding="utf-8")
            path.write_text(out, encoding="utf-8")
    return changed

def main():
    parser = argparse.ArgumentParser(description="Migração Pydantic v1->v2 (class Config -> ConfigDict)")
    parser.add_argument("--dry-run", action="store_true", help="Não escreve os arquivos; apenas reporta o que seria alterado.")
    args = parser.parse_args()

    changed_files = 0
    checked_files = 0
    for base in INCLUDE_DIRS:
        for py in (ROOT / base).rglob("*.py"):
            checked_files += 1
            try:
                if migrate_file(py, dry_run=args.dry_run):
                    print(("[DRY] " if args.dry_run else "[UPDATED] "), py.relative_to(ROOT))
                    changed_files += 1
            except Exception as e:
                print("[ERROR] ", py.relative_to(ROOT), "->", e)

    suffix = " (dry-run)" if args.dry_run else ""
    print(f"Done{suffix}. Checked {checked_files} files; changed {changed_files}.")

if __name__ == "__main__":
    main()
