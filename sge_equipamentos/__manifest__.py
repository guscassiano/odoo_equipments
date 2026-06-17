{
    "name": "SGE Equipamentos",
    "version": "17.0.1.0.0",
    "summary": "Controle de empréstimo de equipamentos de TI",
    "description": """
    SGE Equipamentos
    ================

    Módulo para gestão de empréstimo de equipamentos de TI.
    Desenvolvido como case de estudo da plataforma Odoo.

    Funcionalidades:
    - Cadastro de categorias de equipamentos
    - Cadastro de equipamentos com serial, estado e responsável
    - Controle de empréstimo com validações (constraints)
    - Histórico de alterações (chatter/tracking)
        """,
    "author": "Gustavo Cassiano",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/categoria_views.xml",
        "views/equipamento_views.xml",
    ],
    "installable": True,
    "application": True,
}
