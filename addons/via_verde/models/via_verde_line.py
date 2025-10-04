from odoo import api, fields, models


class ViaVerdeLine(models.Model):
    _name = "via.verde.line"
    _description = "Via Verde Statement Line"
    _order = "entry_datetime desc, id desc"

    sheet_id = fields.Many2one(
        "via.verde.sheet",
        string="Statement",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        related="sheet_id.company_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        related="sheet_id.currency_id",
        store=True,
        readonly=True,
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    license_plate = fields.Char(string="License Plate")
    iai = fields.Char(string="IAI")
    obu = fields.Char(string="OBU")
    service = fields.Char(string="Service")
    service_description = fields.Char(string="Service Description")
    market = fields.Char(string="Market")
    market_description = fields.Char(string="Market Description")
    entry_datetime = fields.Datetime(string="Entry Date")
    exit_datetime = fields.Datetime(string="Exit Date")
    entry_point = fields.Char(string="Entry Point")
    exit_point = fields.Char(string="Exit Point")
    amount = fields.Monetary(string="Value")
    liquid_amount = fields.Monetary(string="Liquid Value")
    discount_amount = fields.Monetary(string="Discount")
    discount_percentage = fields.Float(string="Discount %")
    discount_balance = fields.Monetary(string="Discount Balance")
    is_paid = fields.Boolean(string="Is Paid")
    payment_date = fields.Date(string="Payment Date")
    payment_method = fields.Char(string="Payment Method")
    contract_number = fields.Char(string="Contract Number")
    mobility_account = fields.Char(string="Mobility Account")
    amount_due = fields.Monetary(
        string="Outstanding",
        compute="_compute_amount_due",
        store=True,
    )
    notes = fields.Text(string="Notes")

    @api.depends("is_paid", "liquid_amount")
    def _compute_amount_due(self):
        for line in self:
            line.amount_due = 0.0 if line.is_paid else line.liquid_amount

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        for line in self:
            if line.vehicle_id and not line.license_plate:
                line.license_plate = line.vehicle_id.license_plate
    def action_view_details(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.display_name,
            "res_model": "via.verde.line",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }
