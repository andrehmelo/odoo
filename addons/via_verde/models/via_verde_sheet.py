from odoo import api, fields, models


class ViaVerdeSheet(models.Model):
    _name = "via.verde.sheet"
    _description = "Via Verde Statement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(tracking=True)
    date = fields.Date(default=fields.Date.context_today, tracking=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
        store=True,
    )
    line_ids = fields.One2many("via.verde.line", "sheet_id", string="Lines")
    total_gross_amount = fields.Monetary(
        compute="_compute_totals",
        currency_field="currency_id",
        store=True,
        string="Total Value",
    )
    total_liquid_amount = fields.Monetary(
        compute="_compute_totals",
        currency_field="currency_id",
        store=True,
        string="Total Liquid",
    )
    total_outstanding_amount = fields.Monetary(
        compute="_compute_totals",
        currency_field="currency_id",
        store=True,
        string="Outstanding",
    )

    @api.depends("line_ids.amount", "line_ids.liquid_amount", "line_ids.amount_due")
    def _compute_totals(self):
        for sheet in self:
            sheet.total_gross_amount = sum(sheet.line_ids.mapped("amount"))
            sheet.total_liquid_amount = sum(sheet.line_ids.mapped("liquid_amount"))
            sheet.total_outstanding_amount = sum(sheet.line_ids.mapped("amount_due"))
    def action_mark_paid(self):
        today = fields.Date.context_today(self)
        for sheet in self:
            sheet.line_ids.filtered(lambda l: not l.is_paid).write({
                "is_paid": True,
                "payment_date": today,
            })
        return True
