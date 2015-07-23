from openerp.osv import fields, osv
from openerp import tools
from openerp import SUPERUSER_ID

class hr_employee(osv.osv):
    
    _inherit='hr.employee'
    
    def reset_company_name(self,cr,uid,ids,emp_type,context=None):
        return {'value':{'company_name':False}
                }
        
    _columns={
              'doj':fields.date(string='Date of Joining'),
              'emp_type':fields.selection(string="Employee Type",selection=[('Inhouse','Inhouse'),('Vendor','Vendor')]),
              'company_name':fields.many2one('res.partner',string='Vendor Company'),
              'current_project':fields.many2one('telecom.project',string='Current Project'),
              }
    
class resource_resource(osv.osv):
    _inherit = "resource.resource"
    _sql_constraints = [
        ('user_id_unique', 'unique(user_id)', 'The Related User must be unique per Employee!'),
    ]