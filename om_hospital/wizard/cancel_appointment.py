# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date

class CancelAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointmentWizard, self).default_get(fields)
        res['date_cancel'] = datetime.date.today()
        # this (if) not important because res['appointment_id'] = 1 = self.env.context.get('active_id')
        if self.env.context.get('active_id'):
            res['appointment_id'] = self.env.context.get('active_id')
        return res

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment",
                                     domain=[('state', '=', 'draft'), ('priority', 'in', ('0', '1', False))])
    reason = fields.Text(string='Reason')
    date_cancel = fields.Date(string='Cancellation Date')


    def action_cancel(self):
        cancel_day = self.env['ir.config_parameter'].get_param('om_hospital.cancel_day')
        allowed_date = self.appointment_id.booking_date - relativedelta.relativedelta(days=int(cancel_day))

        if allowed_date < date.today():
            raise ValidationError(_("sorry, cancellation is not allowed the same day of booking"))
        self.appointment_id.state = 'cancel'

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cancel.appointment.wizard',
            'target': 'new',
            'res_id': self.id
        }

        # query = """select id,name from hospital_patient"""
        # self.env.cr.execute(query)
        # patients = self.env.cr.dictfetchall()
        # print(patients)

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload'
        # }
