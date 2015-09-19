from openerp import models, fields, api, _

class activity_line_line(models.Model):
    _name='activity.line.line'
    _description = "Activity Line Line telcome module"    
    _rec_name = "line_id"
    
    def read(self,cr,uid,ids,fields=None, context=None, load='_classic_read'):
        return super(activity_line_line,self).read(cr,uid,ids,fields=fields, context=context, load='_classic_read')
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        return super(activity_line_line,self).name_search(cr, user, name=name, args=args, operator=operator, context=context, limit=100)
    
    
    
    @api.multi
    @api.depends()
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
