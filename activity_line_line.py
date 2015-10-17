from openerp import models, fields, api, _
from openerp import SUPERUSER_ID

class activity_line_line(models.Model):
    _name='activity.line.line'
    _description = "Activity Line Line telcom module"    
    _rec_name = "line_id"
    
    @api.multi
    @api.depends('cost','advance_paid_to_vendor')
    def _get_balance_payment(self):
        res = {}
        for info in self:
            info.balance_payment = info.cost - info.advance_paid_to_vendor
            
    line_id = fields.Many2one('activity.line',string ="Activity Line",required=True, ondelete='cascade', select=True, readonly=True)
    work_description = fields.Many2one(related = "line_id.activity_line.description_id",relation = "work.description",string = "Work description",store=True)
    site_id = fields.Many2one('project.site',string = "Site",required=True)
    site_code = fields.Char(related = 'site_id.site_id',string="Site Code",readonly=True)
    vendor_id = fields.Many2one('res.partner',string = "Sub Vendor",domain = [('supplier','=',True)])
    type = fields.Selection(selection=[
                                       ('inhouse','Inhouse'),('vendor','Vendor')
                                       ],required = True,string = "Activity Type")
    cost = fields.Float(string = "Sub Vendor Rate")
    project_id = fields.Many2one(related = "line_id.activity_line.project_id",relation = "telecom.project",string = "Project",store=True)
    balance_payment = fields.Float(compute=_get_balance_payment,string = "Balance Payment")    
    advance_paid_to_vendor = fields.Float("Advance Paid to vendor")
