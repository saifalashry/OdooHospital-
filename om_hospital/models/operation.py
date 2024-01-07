from odoo import api, fields, models

class HospitalOperation(models.Model):
    _name = "hospital.operation"
    _description = "Hospital Operation"
    _log_access = False
    _order = "sequence,id"

    name = fields.Char(string='Name')
    doctor_id = fields.Many2one('res.users', string='Doctor')
    reference_record = fields.Reference(selection=[('hospital.patient', 'Patient'),
                                                   ('hospital.appointment', 'Appointment')], string='Record')
    sequence = fields.Integer(string="Sequence", default=10)

    # @api.model
    # def name_create(self, name):
    #     print(name)
    #     return self.create({'name': name}).name_get()[0]