from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
              'costs':fields.one2many('cost.line','partner_id',string='Cost line')
              }
    
class cost_line(osv.osv):
    _name='cost.line'
    
    def onchange_project_id(self,cr,uid,id,project_id,context=None):
        list_ids = []
        if project_id:
            cr.execute('''
                       select line.id from activity_line as line join project_description_line as project on line.activity_line = project.id where project.project_id = %s  
                       ''' %(project_id))
            line_ids = cr.fetchall()
            for i in line_ids:
                list_ids.append(i[0])
        return {
                'value':{
                         'activity':[
                                     (6,0,list_ids)
                                     ]
                         }
                }
    _columns={
            'project_id':fields.many2one('telecom.project',string='Project'),
            'activity':fields.many2many('activity.line','vendor_cost_line_activities','activity_id','project_id',string="Activities"),
            'partner_id':fields.many2one('res.partner'),
            
              }