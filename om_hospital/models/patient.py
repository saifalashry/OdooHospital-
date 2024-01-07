# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Chatter
    _description = "Hospital Patient"


    name = fields.Char(string='Name', tracking=True, required=True)
    date_of_birth = fields.Date(string='Date of Birth')
    ref = fields.Char(string="Reference")
    age = fields.Integer(string="Age", compute='_compute_age', search='_search_age', tracking=True, store=True) # inverse='_inverse_compute_age'
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True,
                              default='female')
    active = fields.Boolean(string='Active', default=True, copy=False)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    image = fields.Image(string="Image")
    tag_ids = fields.Many2many('patient.tag', string="Tags")
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointments")
    marital_status = fields.Selection([('married', 'Married'), ('single', 'Single')],
                                      string="Marital Status", tracking=True)
    partner_name = fields.Char(string='Partner Name')
    is_birthday = fields.Boolean(string='Birthday', compute='_compute_is_birthday')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    appointment_count = fields.Integer(string="Appointment Count", compute='_compute_appointment_count')

    @api.model
    def test_cron_job(self):
        print("==========")
        self.env['hospital.appointment'].search([]).action_send_mail()

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        appointment_group = self.env['hospital.appointment'].read_group(domain=[], fields=['patient_id'], groupby=['patient_id'])
        for appointment in appointment_group:
            patient_id = appointment['patient_id'][0]
            patient_rec = self.browse(patient_id)
            patient_rec.appointment_count = appointment['patient_id_count']
            self -= patient_rec # Not Understand
        self.appointment_count = 0 # Not Understand


    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            if not rec.date_of_birth or rec.date_of_birth > fields.Date.today():
                raise ValidationError(_('The entered date of birth is not acceptable !'))

    @api.ondelete(at_uninstall=False)
    def _check_appointments(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_('You cannot delete a patient with appointment !'))

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(vals)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0

    # @api.depends('age') # If You Want The date_of_birth equal the same of select year
    # def _inverse_compute_age(self):
    #     for rec in self:
    #         today = date.today()
    #         if rec.date_of_birth:
    #             rec.date_of_birth = today - relativedelta.relativedelta(years=rec.age)

    def _search_age(self, operator, value):
        date_of_birth = date.today() - relativedelta.relativedelta(years=value)
        start_of_year = date_of_birth.replace(day=1, month=1)
        end_of_year = date_of_birth.replace(day=31, month=12)
        return [('date_of_birth', '>=', start_of_year), ('date_of_birth', '<=', end_of_year)]


    def name_get(self):
        return [(record.id, "%s" % (record.name)) for record in self]

    def action_test(self):
        return

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_birth:
                today = date.today()
                if today.day == rec.date_of_birth.day and today.month == rec.date_of_birth.month:
                    is_birthday = True
            rec.is_birthday = is_birthday

    def action_view_appointments(self):
        return {
            'name': _('Appointments'),
            'view_mode': 'list,form',
            'res_model': 'hospital.appointment',
            'type': 'ir.actions.act_window',
            'context': {'default_patient_id': self.id},
            'target': 'current',
            'domain': [('patient_id', '=', self.id)]
        }
