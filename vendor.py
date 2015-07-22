from openerp.osv import fields, osv

class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        res = {}
        for id in ids:
            cr.execute('''
                select project_filter_id from res_partner where id = %s
            ''' %(id))
            project_id = cr.fetchone()[0]
            if project_id:
                cr.execute('''
                    select id from activity_line where vendor_id=%s and project_id=%s
                '''%(id,project_id))
                activity_ids = cr.fetchall()
                list = []
                for activity in activity_ids:
                     list.append(activity[0])
                res.update({id:list})
            else:
                res_val = super(one2many_mod2,self).get(cr, obj, [id], name, user, offset, context, values)
                res.update(res_val)
        return res

class res_partner(osv.osv):
    _inherit='res.partner'

    def apply_project_filter(self,cr,uid,id,context=None):
        return True
    
    _columns={
              'project_filter_id':fields.many2one('telecom.project',"Project Filter"),
              'activity_ids':one2many_mod2('activity.line','vendor_id',string='Activity Cost')
              }
    
