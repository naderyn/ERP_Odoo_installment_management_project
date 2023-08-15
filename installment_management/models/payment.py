from odoo import models, fields, api

class PaymentWizard(models.TransientModel):
    _name = 'installment.payment.wizard'
    _description = 'Installment Payment Wizard'

    amount = fields.Float(string='Payment Amount', required=True)
    installment_id = fields.Many2one('installment.installment', string='Installment')


    def action_make_payment(self):
        # Create a payment record and update installment state
        payment_vals = {
            'partner_id': self.installment_id.customer.id,
            'journal_id': self.installment_id.journal.id,
            'amount': self.amount,
            'payment_type': 'inbound',  # or 'outbound' depending on your use case
        }
        payment = self.env['account.payment'].create(payment_vals)
        
        # Update installment state to paid
        self.installment_id.write({'state': 'paid'})
    def action_payment(self):
        # Open the payment wizard
        view_id = self.env.ref('installment_management.installment_payment_wizard_form').id
        if self.amount <= self.installment.amount:
            # Create a payment record
            payment_vals = {
                'installment_id': self.installment.id,
                'amount': self.amount,
                # Add other payment-related fields here
            }
            payment = self.env['installment.payment'].create(payment_vals)

            # Update installment state and perform necessary actions
            self.installment.write({'state': 'paid'})

            return {
                'name': 'Make Payment',
                'type': 'ir.actions.act_window',
                'res_model': 'installment.payment.wizard',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'default_payment_id': payment.id},
            }
        else:
            return {
                'warning': {'title': 'Invalid Amount', 'message': 'Payment amount cannot exceed installment amount.'}
            }

