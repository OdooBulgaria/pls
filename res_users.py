from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Adding employee field"
    
    def override_time_true(self,cr,uid,ids,context=None):
#         self.write(cr,uid,ids,{'override_time':True},context)
        assert len(ids) == 1 ,'This option should only be used for a single id at a time'
        dummy,view_id = self.pool.get('ir.model.data').get_object_reference(cr,uid,'pls','override_log_attendance')
        user = self.browse(cr,uid,ids[0],context)
        dummy,subtype_id = self.pool.get('ir.model.data').get_object_reference(cr,uid,'pls','mt_comment_attendance_override')
        
        return {
            'name': _('Reason For Override'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.message',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': {'default_employee_id':user.emp_id and user.emp_id.id or False,
                        'default_subtype_id':subtype_id or False
                        },
        }

    def override_time_false(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'override_time':False},context)
        
    def _find_user_employee(self, cr, uid, ids, field_name, args, context=None):
        #ids ---> these are the ids of res.users for which the employee will change send from the method _get_hr_employee
        res = {}
        if ids:
            for id in ids:
                emp_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',id)])
                if emp_id:
                    res.update({id:emp_id[0]})
                else:
                    res.update({id:False})
        return res
        
    
    def _get_hr_employee(self, cr, uid, ids, context=None):
        #ids --> they are the ids of the resource.resource for which the user_id has changed
        #return ---> list of ids of res.users for which the resource.resource will change and ultimately the emp_id
        list = []
        if ids:
            cr.execute('''
                select res.user_id from hr_employee as hr join resource_resource as res on hr.resource_id = res.id where hr.id = ANY(%s)''', (ids,))
            list = [i[0] for i in cr.fetchall()]
        return list
    
    def _check_allowed_time(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.allowed_attendance_time > 24 or obj.override_time < 0: 
            return False
        return True

    _constraints = [
        (_check_allowed_time, 'Allowed time cannot be greater than 24 Hours or less than 0', ['allowed_attendance_time']),
    ]

    _columns = {
                "emp_id":fields.function(_find_user_employee, 
                                         string='Related Employee', type='many2one',relation = "hr.employee",method=True,
            store={
                'hr.employee': (_get_hr_employee, [], 1),
            }),
                
                'allowed_attendance_time':fields.property(
             type='float',
             string ='Allowed Attendance Submission Time (24 hrs format)',
             help="Enter only for project manager. Otherwise does not have any functionality"),
                
                'override_time':fields.boolean('Allow Override Time Limit',help = "Overrides the time limit for submitting the attendance for Project Manager "),
                
            }
    