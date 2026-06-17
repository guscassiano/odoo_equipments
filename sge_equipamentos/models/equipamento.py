from odoo import api, fields, models  # type: ignore
from odoo.exceptions import UserError, ValidationError  # type: ignore


class SgeEquipamento(models.Model):
    _name = "sge.equipamento"
    _description = "Equipamento"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "name asc"

    name = fields.Char(string="Nome", required=True, tracking=True)
    serial_number = fields.Char(string="Número de Série", required=True, tracking=True)
    categoria_id = fields.Many2one(
        "sge.equipamento.categoria",
        string="Categoria",
        ondelete="restrict",
        tracking=True,
    )
    estado = fields.Selection(
        [
            ("disponivel", "Disponível"),
            ("emprestado", "Emprestado"),
            ("manutencao", "Em Manutenção"),
        ],
        string="Estado",
        default="disponivel",
        required=True,
        tracking=True,
    )
    data_aquisicao = fields.Date(
        string="Data de Aquisição",
        default=fields.Date.today,
        tracking=True,
    )
    responsavel_atual_id = fields.Many2one(
        "res.partner",
        string="Responsável Atual",
        tracking=True,
    )
    data_emprestimo = fields.Date(string="Data do Empréstimo", tracking=True)

    _sql_constraints = [
        (
            "serial_number_uniq",
            "UNIQUE(serial_number)",
            "Número de série deve ser único.",
        ),
    ]

    @api.constrains("estado", "responsavel_atual_id")
    def _check_responsavel_se_emprestado(self):
        """Se o equipamento está emprestado, precisa ter um responsável."""
        for record in self:
            if record.estado == "emprestado" and not record.responsavel_atual_id:
                raise ValidationError(
                    "Um equipamento emprestado precisa ter um responsável atribuído."
                )

    @api.constrains("data_aquisicao")
    def _check_data_aquisicao(self):
        """Data de aquisição não pode ser no futuro."""
        for record in self:
            if record.data_aquisicao and record.data_aquisicao > fields.Date.today():
                raise ValidationError("A data de aquisição não pode ser no futuro.")

    def action_devolver(self):
        """Devolve o equipamento: limpa responsável e volta para disponível."""
        for record in self:
            if record.estado != "emprestado":
                raise UserError(
                    "Só é possível devolver equipamentos que estão emprestados."
                )
            responsavel_anterior = record.responsavel_atual_id.name
            record.write(
                {
                    "estado": "disponivel",
                    "responsavel_atual_id": False,
                    "data_emprestimo": False,
                }
            )
            record.message_post(
                body=f"Equipamento devolvido por {responsavel_anterior}."
            )
        return True

    @api.constrains("data_emprestimo")
    def _check_data_emprestimo(self):
        """Data de aquisição não pode ser no futuro e nem antes da data de aquisição."""
        for record in self:
            if record.data_emprestimo:
                if record.data_emprestimo > fields.Date.today():
                    raise ValidationError(
                        "A data de empréstimo não pode ser no futuro."
                    )
                if (
                    record.data_aquisicao
                    and record.data_emprestimo < record.data_aquisicao
                ):
                    raise ValidationError(
                        "A data de empréstimo não pode ser anterior à data de aquisição do equipamento."
                    )
