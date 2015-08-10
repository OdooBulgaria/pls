from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                    "get_employee_status":self._get_employee_status      
        })

    def _get_employee_status(self,objects):
        result = {}
        dictlist = []
        for employee in objects:
            if employee.id in result:
                if employee.state in result.get(employee.id):
                    result[employee.id][employee.state] = result[employee.id][employee.state] + 1
                else :
                     result[employee.id]['name'] = employee.employee_id.name
                     result[employee.id][employee.state] = 1
            else:
                result.update({employee.id:{"name":employee.employee_id.name,employee.state:1}})
        for key, value in result.iteritems():
            dictlist.append(value)
        return dictlist 