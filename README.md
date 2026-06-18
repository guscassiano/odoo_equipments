# SGE Equipamentos

Módulo Odoo 17 para gestão de empréstimo de equipamentos de TI. Desenvolvido como case de estudo para entrevista técnica da vaga **PDI SW - Fullstack II (JS/Python)** no **Inatel**.

## Stack

- **Odoo 17.0** (LTS)
- **PostgreSQL 15**
- **Docker / Docker Compose**

## Funcionalidades

- Cadastro de categorias de equipamentos
- Cadastro de equipamentos com serial, estado e responsável
- Controle de empréstimo com validações (`@api.constrains`)
- Histórico de alterações via chatter/tracking (`mail.thread` + `mail.activity.mixin`)
- Relatório PDF de equipamentos via QWeb

## Como rodar

```bash
# Subir os containers
docker compose up -d

# Acessar http://localhost:8069 e criar o banco "odoo_db"

# Instalar o módulo (primeira vez)
docker compose exec odoo odoo -d odoo_db -i sge_equipamentos \
  --db_host=db --db_user=odoo --db_password=odoo --stop-after-init

# Atualizar após editar código
docker compose exec odoo odoo -d odoo_db -u sge_equipamentos \
  --db_host=db --db_user=odoo --db_password=odoo --stop-after-init
```

## Estrutura de pastas

```
sge_equipamentos/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── categoria.py          # sge.equipamento.categoria
│   └── equipamento.py        # sge.equipamento (com chatter)
├── views/
│   ├── categoria_views.xml   # tree + form + menu + action
│   └── equipamento_views.xml # tree + form (statusbar, botão devolver, chatter) + menu + action
├── reports/
│   └── equipment_report_template.xml  # template QWeb + action ir.actions.report
├── security/
│   └── ir.model.access.csv
└── .gitignore
```

## Decisões técnicas

- **One2many/Many2one** entre categoria e equipamento: categoria é o lado "forte" (Many2one), equipamento referencia a categoria. One2many no categoria é só o lado reverso.
- **Chatter/tracking**: herança dupla de `mail.thread` (mensagens + seguidores) e `mail.activity.mixin` (atividades). No Odoo 17, `mail.thread` sozinho não fornece `activity_ids`.
- **Constraints em Python** (`@api.constrains`) em vez de só SQL: permite mensagens de erro contextualizadas no chatter.
- **Relatório QWeb**: template server-side processado pelo Odoo, convertido em PDF. Action registrada via `<record model="ir.actions.report">` (a tag `<report>` foi removida do schema do Odoo 17).
- **`_sql_constraints`** para unique de serial_number: validação em SQL puro, mais performática que Python.

## O que aprendi

*(a preencher após a entrevista)*

## Autor

Gustavo Cassiano — [github.com/guscassiano](https://github.com/guscassiano)
