from openerp.osv import fields, osv

class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        res = {}
        for id in ids:
            cr.execute("select project_filter_id from res_partner where id = %s", (id,)) 
            ids_cr=cr.fetchall()
            if ids_cr[0][0]:
                cr.execute("select id from activity_line_line where project_id = %s and vendor_id = %s",(ids_cr[0][0],id,))
                activity_line_cr=[i[0] for i in cr.fetchall()]
                res.update({id:activity_line_cr})
            else :
                cr.execute("select id from activity_line_line where vendor_id = %s",(id,))
                activity_line_cr=[i[0] for i in cr.fetchall()]
                res.update({id:activity_line_cr})
        return res

class res_partner(osv.osv):
    _inherit='res.partner'

    def apply_project_filter(self,cr,uid,id,context=None):
        return True
    
    _columns={
              'project_filter_id':fields.many2one('telecom.project',"Project Filter"),
              'activity_ids':one2many_mod2('activity.line.line','vendor_id',string='Activity Cost'),
              'contracts':fields.one2many('customer.contract','res_partner_id',string="Contracts"),
              }
    
class customer_contract(osv.osv):
    _name="customer.contract"
    
    _columns = {
                'activity_id':fields.many2one('activity.activity',string="Activities"),
                'cost':fields.float(string="Cost"),
                'res_partner_id':fields.many2one('res.partner',string='Customer')
                }