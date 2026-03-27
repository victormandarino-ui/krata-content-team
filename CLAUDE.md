# КЯАТА. Content Team — Pipeline de Conteúdo

## Contexto
Este repositório contém o pipeline automatizado de produção de conteúdo da КЯАТА.

## Skills disponíveis
As instruções de cada agente estão em `.claude/skills/`:
- `content-team/SKILL.md` — Entry point do pipeline
- `head-de-conteudo/SKILL.md` — Yago (Head), orquestrador principal
- `trends-hunter/SKILL.md` — Davi, garimpador de tendências
- `social-media/SKILL.md` — Ana, filtro editorial
- `copywriter/SKILL.md` — Joyce, redatora
- `designer/SKILL.md` — Kauã, designer (só em contexto local com Playwright)

## Como executar o pipeline
1. Leia `.claude/skills/head-de-conteudo/SKILL.md` para as instruções completas do Yago
2. Leia `./config.json` para configurações (board ID, email, limites)
3. Execute o MODO 1 (Pipeline Diário) conforme descrito na skill do Yago

## Contexto remoto (trigger)
- Sem Playwright — o pipeline para após a Etapa 3.5 (copy + email ao CEO)
- Para emails, use o n8n MCP: `mcp__n8n-manager__run_webhook` com `workflowName: "krata-email"` e `data: {"to": "...", "subject": "...", "html": "..."}`. NÃO use curl (bloqueado pelo proxy). NÃO use Gmail MCP (só cria rascunho).
- Salve estado em `./state/YYYY-MM-DD.json`
- Ao concluir: `git add state/ historico/ && git commit -m "state: YYYY-MM-DD" && git push`

## Regras
- Monday board ID: ler de `config.json` → `notificacoes.monday_board_id`
- Email CEO: ler de `config.json` → `notificacoes.email`
- Headlines diagnosticam (provocam desconforto), nunca prometem
- Tom consultivo, direto, sem jargão corporativo
