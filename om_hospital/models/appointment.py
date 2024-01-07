# -*- coding: utf-8 -*-
import random
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):  # AppointmentPharmacyLines,
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Chatter
    _description = "Hospital Appointment"
    _rec_name = 'name'  # name or 'patient_id'
    _order = 'id desc'

    name = fields.Char(string='Sequence', default='new', tracking=True)
    #                                                                  ondelete='restrict'
    patient_id = fields.Many2one('hospital.patient', string="Patient", ondelete='cascade', tracking=True,
                                 required=True)  # we can do it comodel_name='hospital.patient'
    gender = fields.Selection(related='patient_id.gender', readonly=False, tracking=True)
    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now)
    booking_date = fields.Date(string="Booking Time", default=fields.Date.context_today)
    ref = fields.Char(string="Reference")
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')],
        string='Priority')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Canceled')], default='draft', string='Status', required=True)
    doctor_id = fields.Many2one('res.users', string='Doctor', tracking=3)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string="Pharmacy Lines")
    hide_sales_price = fields.Boolean(string="Hide Sales Price")
    operation_id = fields.Many2one('hospital.operation', string='Operation')
    progress = fields.Integer(string='Progress', compute='_compute_progress')
    duration = fields.Float(string='Duration', tracking=4)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', currency_field='currency_id')
    # total = fields.Float(string='Total')

    def name_get(self):
        return [(record.id, "%s" % (record.ref)) for record in self]

    def set_line_number(self):
        sl_no = 0
        for line in self.pharmacy_line_ids:
            sl_no += 1
            line.sl_no = sl_no
        return

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        res = super(HospitalAppointment, self).create(vals)
        res.set_line_number()
        return res

    def write(self, values):
        res = super(HospitalAppointment, self).write(values)
        self.set_line_number()
        return res

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(_('You cannot delete appointment with "Done" status !'))
        return super(HospitalAppointment, self).unlink()

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_notification(self):
        action = self.env.ref('om_hospital.action_hospital_patient')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Click to open the patient record'),
                'message': '%s',
                'type': 'success',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient',
                }],
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window', # ir.actions.act_window_close
                    'res_model': 'hospital.patient',
                    'res_id': self.patient_id.id,
                    'views': [(False, 'form')]
                }
            }
        }

    def action_test(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://www.odoo.com'
        }

    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_consultation'

    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(_('Missing phone number in patient record'))
        message = 'Hi %s, your appointment number is: %s , Thank you' % (self.patient_id.name, self.ref)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, message)
        self.message_post(body=message, subject='Whatsapp Message')
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    def action_send_mail(self):
        template = self.env.ref('om_hospital.appointment_mail_template')
        for rec in self:
            if rec.patient_id.email:
                email_values = {
                    'email_cc': False,
                    'auto_delete': True,
                    'recipient_ids': [],
                    'partner_ids': [],
                    'scheduled_date': False,
                }
                template.send_mail(rec.id, force_send=True, email_values=email_values)

    def action_done(self):
        for rec in self:
            rec.state = 'done'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Done",
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        action = self.env.ref('om_hospital.action_cancel_appointment').read()[0]
        return action

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = random.randrange(0, 25)
            elif rec.state == 'in_consultation':
                progress = random.randrange(25, 99)
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress


class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    sl_no = fields.Integer(string="SNO.")
    product_id = fields.Many2one('product.product', required=True)
    price_unit = fields.Float(related='product_id.list_price', readonly=False, digits='Product Price')
    qty = fields.Integer(string='Quantity', default=1)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")

    currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal',
                                     currency_field='currency_id')

    @api.depends('price_unit', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.qty
