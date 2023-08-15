from odoo import models, fields, api

class InstallmentInstallment(models.Model):
    _name = 'installment.installment'
    _description = 'Customer Installments'

    name = fields.Char(string='Name', readonly=True, default='New')
    reference = fields.Char(string='Reference')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('paid', 'Paid')], string='State', default='draft')
    date = fields.Date(string='Date', default=fields.Date.today())
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    journal = fields.Many2one('account.journal', string='Journal', required=True)
    account = fields.Many2one('account.account', string='Account', required=True)
    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tags = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    amount = fields.Float(string='Amount', required=True, digits=(16, 2))
    notes = fields.Text(string='Notes')
    invoice_count = fields.Integer(compute='_compute_invoice_count', string='Invoice Count')

    def action_open(self):
        # Create a customer invoice and set the state to open
        for installment in self:
            invoice_vals = {
                'partner_id': installment.customer.id,
                'journal_id': installment.journal.id,
                'account_id': installment.account.id,
                'amount_total': installment.amount,
                'date_invoice': installment.date,
                'type': 'out_invoice',
            }
            invoice = self.env['account.move'].create(invoice_vals)
            installment.write({'state': 'open', 'name': invoice.name})

    def action_payment(self):
        # Open the payment wizard
        view_id = self.env.ref('installment_management.installment_payment_wizard_form').id
        return {
            'name': 'Make Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'installment.payment.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_amount': self.amount, 'default_installment_id': self.id},
        }

    def action_settlement(self):
        # Settle the installment and set the state to paid
        for installment in self:
            installment.write({'state': 'paid'})

    @api.depends('customer')
    def _compute_invoice_count(self):
        for installment in self:
            invoice_count = self.env['account.move'].search_count([
                ('partner_id', '=', installment.customer.id),
                ('state', '=', 'posted'),  # Consider only posted invoices
            ])
            installment.invoice_count = invoice_count

    def action_open_invoices(self):
        # Open related invoices for the selected installment's customer
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('partner_id', '=', self.customer.id),
            ('state', '=', 'posted'),  # Consider only posted invoices
        ])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if invoices:
            action['domain'] = [('id', 'in', invoices.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
