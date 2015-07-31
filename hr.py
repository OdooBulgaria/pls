from openerp.osv import fields, osv
from openerp import tools
from openerp import SUPERUSER_ID

class hr_job(osv.osv):
    _inherit = "hr.job"
    
    def name_get(self, cr, user, ids, context=None):
        return super(hr_job,self).name_get(cr, SUPERUSER_ID, ids, context=None)
    
class hr_employee(osv.osv):
    
    _inherit='hr.employee'
    
    
    # read_access is basically passed from javascript wwhile calling the attendance.line wizard
    # This is because by this we are giving project manager the access to other employees too whereas they only have a record rule to access their own employees
    # So for this time we are just overriding the record rule in name_get,name_search,read method
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if context == None:
            context = {}
        if context.get('read_access',False):
            user = SUPERUSER_ID
        return super(hr_employee,self).name_search(cr, user, name, args=args, operator=operator, context=context, limit=limit)
        
    def name_get(self, cr, user, ids, context=None):
        return super(hr_employee,self).name_get(cr, SUPERUSER_ID, ids, context=None)
    
    def read(self, cr, uid,ids,fields=None, context=None, load='_classic_read'):
        if context.get('read_access',False):
            uid = SUPERUSER_ID
        return super(hr_employee,self).read(cr, uid,ids,fields, context, load)
    
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