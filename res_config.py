from openerp.osv import fields, osv

class pls_configuration(osv.TransientModel):
    _name = "pls.config.settings"
    _inherit = 'res.config.settings'

    def get_default_permitted_attendance_time(self,cr,uid,ids,context=None):
        model,property_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'pls', 'default_time_attendances')
        allowed_time = self.pool.get(model).read(cr,uid,property_id,['value_float'],context)
        return {'permitted_attendance_time':allowed_time.get('value_float',0)}

    def set_default_permitted_attendance_time(self, cr, uid, ids, context=None):
        obj = self.read(cr,uid,ids[0],['permitted_attendance_time'],context)
        model,property_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'pls', 'default_time_attendances')
        if obj.get('permitted_attendance_time',False):
            cr.execute('''
                update ir_property set value_float = %s where id = %s ;
                ''' %(obj.get('permitted_attendance_time',0),property_id))
     
    _columns = {
            'permitted_attendance_time': fields.float('Permitted time to submit attendance', digits=(16, 2)),
    }