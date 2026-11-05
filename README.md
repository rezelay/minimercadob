# DevOps Market Python

Mini mercado web para a disciplina de Integração DevOps, feito em Python para facilitar execução em laboratório.

O frontend usa Flask + Jinja. O backend usa Flask API. O banco é SQLite com SQLAlchemy.

## Primeira execução

```bash
python -m pip install -r requirements-dev.txt
python tasks.py db-seed
python tasks.py dev
```

Acesse `http://localhost:3000`.

## Comandos base para CI dos alunos

```bash
python -m pip install -r requirements-dev.txt
python tasks.py lint
python tasks.py test
python tasks.py build
python tasks.py docker-build
python tasks.py smoke
```

O comando `build` em Python faz uma construção/validação com `compileall`, garantindo que o código importa e compila para bytecode. O Dockerfile também tem um stage `builder`.

## Docker

```bash
docker compose up --build
```

Para preview em outra porta:

```bash
PORT=3101 docker compose up --build
```

## Features

```bash
python tasks.py feature-create product-search
python tasks.py feature-check product-search
```

Cada feature fica em um pacote Python. Slugs com hífen viram pasta com underscore.

```text
app/features/product_search/
  manifest.py
  routes.py
  service.py
  templates/
  tests/
  README.md
```

## Core protegido

Não altere `app/core/*` para implementar uma feature comum. O aluno deve trabalhar em `app/features/<slug>`.

## CI/CD (DevSecOps)

O repositório tem dois workflows no GitHub Actions. Todo PR para a `main` passa por lint, testes e varreduras de segurança, e só a `main` é publicada no Azure Container Apps, depois de aprovação manual.

```text
PR ou push na main
  └─ DevSecOps CI (.github/workflows/ci.yml)
       ├─ lint-test ──────┐
       ├─ secret-scan ────┴─ build-scan-push ─ (push na main) imagem no GHCR
       │
  push na main com CI verde
  └─ Deploy (.github/workflows/deploy.yml)
       └─ deploy ─ aprovação no environment production ─ Azure Container Apps
```

| Job | Workflow | O que faz | Quando roda |
| --- | --- | --- | --- |
| `lint-test` | `ci.yml` | `python tasks.py lint` (ruff) e `python tasks.py test` (pytest), com Python 3.12 | PR e push na `main` |
| `secret-scan` | `ci.yml` | [gitleaks](https://github.com/gitleaks/gitleaks) procura senhas, tokens e chaves em todo o histórico | PR e push na `main` |
| `build-scan-push` | `ci.yml` | Faz o build da imagem e roda o [Trivy](https://github.com/aquasecurity/trivy); falha se houver vulnerabilidade HIGH ou CRITICAL com correção. No push na `main`, publica `ghcr.io/rezelay/minimercadob:<sha>` | Depois de `lint-test` e `secret-scan` |
| `deploy` | `deploy.yml` | Faz login no Azure por OIDC e atualiza o Container App `app-seminario` com a imagem do commit | Quando o CI termina com sucesso em um push na `main`; nunca em PR |

### Segurança

- **Sem senhas no GitHub:** o login no Azure usa OIDC (token de curta duração). Os secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` e `AZURE_SUBSCRIPTION_ID` são só identificadores.
- **Menor privilégio:** a identidade do GitHub Actions só tem `Contributor` no resource group `rg-seminario-devsecops`, e só o environment `production` deste repositório pode usá-la.
- **Aprovação manual:** o deploy espera aprovação no environment `production` (Settings → Environments).
- **Actions fixadas por SHA:** cada action usa o SHA de um commit, não uma tag, para evitar ataques à cadeia de suprimentos.
- **Imagem no GHCR (pública):** a assinatura Azure for Students só cria ambientes Container Apps "express", que não aceitam pull do ACR com identidade gerenciada.

### Rodar as verificações localmente

```bash
python tasks.py lint
python tasks.py test
docker build -t devops-market-python .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity CRITICAL,HIGH --ignore-unfixed devops-market-python
docker run --rm -v "$PWD":/repo zricethezav/gitleaks detect --source /repo
```

Novas pipelines de alunos continuam em `.github/workflows/<nome-do-aluno-ou-feature>.yml`, usando os comandos base acima.
