from odoo import fields, models  # type: ignore


class SgeEquipamentoCategoria(models.Model):
    _name = "sge.equipamento.categoria"
    _description = "Categoria de Equipamento"
    _rec_name = "name"
    _order = "name asc"

    name = fields.Char(string="Nome", required=True)
    descricao = fields.Text(string="Descrição")

    equipamento_ids = fields.One2many(
        "sge.equipamento",
        "categoria_id",
        string="Equipamentos",
    )
