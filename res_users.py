from openerp.osv import fields, osv

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Adding employee field"
    
    
    
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
    
    _columns = {
                "emp_id":fields.function(_find_user_employee, 
                                         string='Related Employee', type='many2one',relation = "hr.employee",method=True,
            store={
                'hr.employee': (_get_hr_employee, [], 1),
            }),
                }
    