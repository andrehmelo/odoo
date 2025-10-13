from datetime import datetime, time as datetime_time

from odoo import api, fields, models


class GasCardLine(models.Model):
    _name = "gas.card.line"
    _description = "Gas Card Transaction"
    _order = "transaction_datetime desc, id desc"

    sheet_id = fields.Many2one(
        "gas.card.sheet",
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
    driver_id = fields.Many2one("res.partner", string="Driver", domain="['|', ('is_company', '=', False), ('parent_id', '!=', False)]")
    card_number = fields.Char(string="Card Number")
    card_description = fields.Char(string="Card Label")
    client_name = fields.Char(string="Client")
    station_name = fields.Char(string="Station")
    network_type = fields.Char(string="Network Type")
    transaction_date = fields.Date(string="Date")
    transaction_time = fields.Char(string="Time")
    transaction_datetime = fields.Datetime(
        string="Date & Time",
        compute="_compute_transaction_datetime",
        inverse="_inverse_transaction_datetime",
        store=True,
    )
    fuel_type = fields.Char(string="Fuel Type")
    liters = fields.Float(string="Liters")
    unit_of_measure = fields.Char(string="Unit")
    unit_price_excl_vat = fields.Monetary(string="Unit Price (excl. VAT)", currency_field="currency_id")
    receipt_number = fields.Char(string="Receipt")
    invoice_number = fields.Char(string="Invoice")
    net_amount = fields.Monetary(string="Net Amount", currency_field="currency_id")
    vat_amount = fields.Monetary(string="VAT Amount", currency_field="currency_id")
    total_amount = fields.Monetary(string="Total Amount", currency_field="currency_id")
    reference_amount = fields.Monetary(string="Reference Amount (incl. VAT)", currency_field="currency_id")
    discount_amount = fields.Monetary(string="Discount (incl. VAT)", currency_field="currency_id")
    kilometers = fields.Float(string="Odometer (km)")
    driver_identifier = fields.Char(string="Driver Reference")
    is_paid = fields.Boolean(string="Is Paid")
    payment_date = fields.Date(string="Payment Date")
    notes = fields.Text(string="Notes")
    amount_due = fields.Monetary(
        string="Outstanding",
        compute="_compute_amount_due",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("is_paid", "total_amount")
    def _compute_amount_due(self):
        for line in self:
            line.amount_due = 0.0 if line.is_paid else (line.total_amount or 0.0)

    @api.depends("transaction_date", "transaction_time")
    def _compute_transaction_datetime(self):
        for line in self:
            dt_value = False
            if line.transaction_date:
                date_value = line.transaction_date
                if isinstance(date_value, str):
                    date_value = fields.Date.to_date(date_value)
                time_value = datetime_time(0, 0)
                if line.transaction_time:
                    try:
                        hours, minutes = line.transaction_time.split(":", 1)
                        time_value = datetime_time(int(hours), int(minutes[:2]))
                    except (ValueError, TypeError):
                        time_value = datetime_time(0, 0)
                dt_value = datetime.combine(date_value, time_value)
                dt_value = fields.Datetime.to_string(dt_value)
            line.transaction_datetime = dt_value

    def _inverse_transaction_datetime(self):
        for line in self:
            if line.transaction_datetime:
                dt = fields.Datetime.to_datetime(line.transaction_datetime)
                line.transaction_date = dt.date()
                line.transaction_time = dt.strftime("%H:%M")

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        for line in self:
            if line.vehicle_id:
                line.license_plate = line.vehicle_id.license_plate
                if not line.driver_id:
                    line.driver_id = line.vehicle_id.driver_id

    def action_view_details(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.display_name,
            "res_model": "gas.card.line",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }
