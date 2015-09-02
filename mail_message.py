from openerp.osv import osv, orm, fields

class mail_message(osv.Model):
    _inherit = "mail.message"
    
    def allow_override_attendance(self,cr,uid,ids,context=None):
        self.pool.get('res.users').write(cr,uid,context.get('active_ids',False),{'override_time':True},context)
        return True