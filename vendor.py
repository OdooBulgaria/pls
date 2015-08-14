from openerp.osv import fields, osv

class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
#         res = {}
#         for id in ids:
#             cr.execute('''
#                 select project_filter_id from res_partner where id = %s
#             ''' %(id))
#             project_id = cr.fetchone()[0]
#             if project_id:
#                 cr.execute('''
#                     select id from activity_line where vendor_id=%s and project_id=%s
#                 '''%(id,project_id))
#                 activity_ids = cr.fetchall()
#                 list = []
#                 for activity in activity_ids:
#                      list.append(activity[0])
#                 res.update({id:list})
#             else:
#                 res_val = super(one2many_mod2,self).get(cr, obj, [id], name, user, offset, context, values)
#                 res.update(res_val)
#         res_val = super(one2many_mod2,self).get(cr, obj, [id], name, user, offset, context, values)
#         res.update(res_val)
#         print "================================res_val",res_val
#         return res
        print "-------------------ids",ids
        res = {}
        for id in ids:
            cr.execute("select project_filter_id from res_partner where id = %s", (id,)) 
            ids_cr=cr.fetchall()
            if ids_cr[0][0]:
                print "ids_cr--------------------------------------",ids_cr
                cr.execute("select id from activity_line_line where project_id = %s and vendor_id = %s",(ids_cr[0][0],id,))
                activity_line_cr=[i[0] for i in cr.fetchall()]
                print "---------------_get_sorted_planned_intervals----machine workcenter ids-",activity_line_cr
                res.update({id:activity_line_cr})
            else :
                cr.execute("select id from activity_line_line where vendor_id = %s",(id,))
                activity_line_cr=[i[0] for i in cr.fetchall()]
                print "---------------_get_sorted_planned_intervals----machine workcenter ids-",activity_line_cr
                res.update({id:activity_line_cr})
        return res

class res_partner(osv.osv):
    _inherit='res.partner'

    def apply_project_filter(self,cr,uid,id,context=None):
        return True
    
    _columns={
              'project_filter_id':fields.many2one('telecom.project',"Project Filter"),
              'activity_ids':one2many_mod2('activity.line.line','vendor_id',string='Activity Cost')
              }
