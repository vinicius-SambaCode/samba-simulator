# SAMBA Simulator — Instalação nas Unidades Escolares

## Pré-requisitos (instalar uma vez por computador)

| Software | Download | Versão mínima |
|---|---|---|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop | 4.x |
| **Git** | https://git-scm.com/downloads | qualquer |

> No Windows: instale o Docker Desktop e reinicie o computador.  
> No Linux: `sudo apt install docker.io docker-compose-plugin -y`

---

## Instalação (primeira vez)

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/samba-simulator.git
cd samba-simulator

# 2. (Opcional) Copie e ajuste o .env
cp .env.example .env
# Edite o .env se quiser mudar senha do banco

# 3. Suba tudo — o Docker baixa as imagens e builda automaticamente
docker compose up -d --build
```

Aguarde ~3-5 minutos na primeira vez (baixando imagens e instalando dependências).  
Nas próximas vezes, sobe em ~20 segundos.

---

## Acesso ao sistema

Abra o navegador em: **http://localhost**

| URL | O que é |
|---|---|
| http://localhost | Sistema (frontend) |
| http://localhost/api/docs | Documentação da API (Swagger) |

---

## Comandos do dia a dia

```bash
# Ligar o sistema
docker compose up -d

# Desligar o sistema
docker compose down

# Ver logs em tempo real
docker compose logs -f

# Ver logs só da API
docker compose logs -f api

# Atualizar após git pull
docker compose up -d --build

# Reiniciar só o frontend (após mudanças)
docker compose up -d --build frontend

# Reiniciar só a API (após mudanças)
docker compose up -d --build api
```

---

## Atualizar o sistema (depois de nova versão no GitHub)

```bash
git pull
docker compose up -d --build
```

---

## Backup do banco de dados

```bash
# Exportar
docker exec samba_pg pg_dump -U postgres samba_simulator > backup_$(date +%Y%m%d).sql

# Restaurar
docker exec -i samba_pg psql -U postgres samba_simulator < backup_20250101.sql
```

---

## Solução de problemas

**Sistema não abre no navegador:**
```bash
docker compose ps          # verifica se os containers estão rodando
docker compose logs api    # vê erros da API
```

**"port 80 already in use":**  
Outro serviço está usando a porta 80. Edite `docker-compose.yml` e mude `"80:80"` para `"8080:80"`, depois acesse em `http://localhost:8080`.

**Banco corrompido / limpar tudo:**
```bash
docker compose down -v     # APAGA TODOS OS DADOS
docker compose up -d --build
```

---

## Estrutura do repositório

```
samba-simulator/
├── docker-compose.yml      ← orquestra tudo
├── .env.example            ← modelo de configuração
├── backend/                ← FastAPI + PostgreSQL
│   ├── Dockerfile
│   ├── entrypoint.sh       ← migrations + seed automáticos na subida
│   └── app/
└── frontend/               ← Nuxt SPA + Nginx
    ├── Dockerfile
    ├── nginx.conf
    └── app/
```
