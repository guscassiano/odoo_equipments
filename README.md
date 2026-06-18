# SGE Equipamentos

Módulo Odoo 17 para controle de empréstimo de equipamentos de TI. Desenvolvido como case de estudo pessoal para demonstrar domínio prático da plataforma Odoo (modelos, views, constraints, chatter e tracking).

---

## Contexto

Este módulo nasceu como exercício prático de aprendizado da plataforma Odoo. Desenvolvi enquanto estudava para uma entrevista técnica (PD&I Software, Inatel), onde identifiquei uma lacuna entre meu conhecimento conceitual da plataforma e a experiência prática esperada.

O objetivo duplo foi:
- Aprofundar o conhecimento em Odoo indo além da teoria (modelos, herança de mixins, constraints, chatter, tracking)
- Produzir um módulo funcional com regras de negócio reais que pudesse ser usado em qualquer empresa que precisasse de controle de empréstimo de equipamentos

    Embora o gatilho tenha sido a vaga específica, o projeto se sustenta como caso de uso real e como item de portfólio aberto.

---

## Stack

| Componente | Versão/Detalhe |
|---|---|
| Odoo | 17.0 (LTS) |
| PostgreSQL | 15 |
| Containerização | Docker + Docker Compose |
| Linguagem do módulo | Python 3.10 |
| UI | XML (Odoo views) com chatter `mail.thread` + `mail.activity.mixin` |

---

## Funcionalidades

- Cadastro de categorias e equipamentos com constraints (Python + SQL)
- Controle de empréstimo com botão "Devolver" (posta no chatter)
- Chatter completo: seguidores, atividades e mensagens (`mail.thread` + `mail.activity.mixin`)
- Relatório PDF de equipamentos via QWeb (menu Print/Imprimir na lista de equipamentos)

---

## Como rodar

### Pré-requisitos

- Docker e Docker Compose instalados
- Porta 8069 disponível

### Subir o ambiente

```bash
docker compose up -d
```

A primeira execução baixa as imagens e cria o banco. Leva ~3 minutos.

### Acessar o Odoo

Abra `http://localhost:8069` no navegador.

| Campo | Valor |
|---|---|
| Database | `odoo_db` |
| Usuário | `admin` |
| Senha | `admin` |
| Idioma | Português (Brasil) |

### Instalar/atualizar o módulo

```bash
# Instalar (primeira vez)
docker compose exec odoo odoo -d odoo_db -i sge_equipamentos --db_host=db --db_user=odoo --db_password=odoo --stop-after-init

# Atualizar (após mudanças nos arquivos)
docker compose exec odoo odoo -d odoo_db -u sge_equipamentos --db_host=db --db_user=odoo --db_password=odoo --stop-after-init
```

---

## Funcionalidades

### Modelos

#### `sge.equipamento.categoria` — categoria de equipamento (ex: Notebook, Roteador, Switch)

| Campo | Tipo | Detalhe |
|---|---|---|
| `name` | Char | Obrigatório |
| `descricao` | Text | Opcional |
| `equipamento_ids` | One2many | → `sge.equipamento` |

#### `sge.equipamento` — equipamento físico (ex: "Notebook Dell Latitude 01", SN-001)

| Campo | Tipo | Detalhe |
|---|---|---|
| `name` | Char | Obrigatório |
| `serial_number` | Char | Obrigatório, único via SQL constraint |
| `categoria_id` | Many2one | → categoria, `ondelete=restrict` |
| `estado` | Selection | `disponivel`, `emprestado`, `manutencao`; default `disponivel` |
| `data_aquisicao` | Date | Default hoje |
| `responsavel_atual_id` | Many2one | → `res.partner` |
| `data_emprestimo` | Date | — |

### Regras de negócio (constraints)

| Regra | Tipo | Mensagem |
|---|---|---|
| `serial_number` único | SQL | `duplicate key value violates unique constraint` |
| Se `estado == 'emprestado'`, então `responsavel_atual_id` é obrigatório | Python | "Um equipamento emprestado precisa ter um responsável atribuído." |
| `data_aquisicao` não pode ser futura | Python | "A data de aquisição não pode ser no futuro." |
| `data_emprestimo` não pode ser futura | Python | "A data de empréstimo não pode ser no futuro." |
| `data_emprestimo` ≥ `data_aquisicao` | Python | "A data de empréstimo não pode ser anterior à data de aquisição do equipamento." |

### Ações (botões)

- **Devolver Equipamento** (`action_devolver`): limpa o responsável, a data de empréstimo e volta o estado para `disponivel`. Posta mensagem no chatter registrando quem devolveu. Visível apenas quando `estado == 'emprestado'`.

### Interface

- **Formulário:** com statusbar (visual), grupos de Identificação e Status, botão de devolver condicional e chatter completo (seguidores + atividades + mensagens).
- **Lista (tree):** com badges coloridos no estado (azul para disponível, amarelo para emprestado, cinza para manutenção) e decoração de linha.
- **Menu:** entrada própria "SGE Equipamentos" no menu principal, com submenus "Equipamentos" e "Categorias".

---

## Estrutura de pastas

```
sge_equipamentos/
├── __init__.py                 # Importa o subpacote models
├── __manifest__.py             # Manifesto do módulo (nome, versão, dependências)
├── README.md                   # Este arquivo
├── models/
│   ├── __init__.py             # Importa categoria e equipamento
│   ├── categoria.py            # Modelo de categoria
│   └── equipamento.py          # Modelo de equipamento (com constraints e action_devolver)
├── views/
│   ├── categoria_views.xml     # Form, tree, action, menuitem da categoria
│   └── equipamento_views.xml   # Form, tree, action, menuitem do equipamento
├── reports/
│   └── equipment_report_template.xml  # Template QWeb + action ir.actions.report
└── security/
    └── ir.model.access.csv     # Permissões de acesso (CRUD para base.group_user)
```

---

## Decisões técnicas

1. **Chatter herdado de `mail.thread` + `mail.activity.mixin`:** o equipamento precisa de histórico de mudanças (tracking) E de tarefas/lembretes (atividades). Os dois mixins juntos dão o widget completo.

2. **Statusbar + dropdown:** a statusbar (`widget="statusbar"`) é visual, e o `widget="selection"` no formulário é editável. Decisão de UX pra driblar um bug conhecido do front-end Odoo 17 onde a statusbar fica disabled em algumas condições.

3. **Constraint SQL para serial único:** é mais performático que validar em Python. O Odoo cria a constraint no `CREATE TABLE` e o Postgres rejeita duplicatas antes mesmo de chamar o ORM.

4. **Many2one para `res.partner` (responsável):** reusa o modelo nativo de contatos do Odoo em vez de criar um modelo próprio de "Funcionário". Vantagem: integra com o app Contacts do Odoo, aproveita endereços, telefones e emails já cadastrados.

5. **One2many na categoria:** facilita a navegação — ao abrir uma categoria, você vê todos os equipamentos daquela categoria direto no formulário.

6. **Inherit `mail.activity.mixin` + `_sql_constraints`:** combinação que dá comportamento completo de ERP (chatter, atividades, validações de banco) sem reinventar a roda.

7. **Relatório QWeb via `ir.actions.report`:** a tag `<report>` foi removida do schema RELAXNG do Odoo 17. A forma correta é registrar a action via `<record model="ir.actions.report">` com `binding_model_id` (faz o relatório aparecer no menu Print da lista). O template QWeb usa `t-foreach`, `t-if`, `t-field` — processado no servidor, convertido em PDF.

---

## O que aprendi com o projeto

- Estrutura de um módulo Odoo: `__manifest__.py`, `models/`, `views/`, `security/`;
- Herança de mixins: `mail.thread` (mensagens) + `mail.activity.mixin` (atividades);
- Decoradores do Odoo: `@api.constrains` (validação Python), `tracking=True` (chatter);
- `Two2many` / `One2many` / `Many2one`: ORM do Odoo mapeia pra colunas de chave estrangeira;
- XML para views: `<record>`, `<field>`, `ir.ui.view`, `ir.actions.act_window`, `ir.ui.menu`;
- `ir.model.access.csv`: segurança por padrão no Odoo (sem permissão, ninguém vê)
- Debug de erros Odoo: `docker compose logs odoo --tail 50` + psql direto no banco;
- Pitfalls comuns: CRLF nos XMLs, naming conventions de dunder files, `mail.activity.mixin` separado de `mail.thread` no Odoo 17.