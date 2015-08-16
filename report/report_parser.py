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
            if employee.employee_id.id in result.keys():
                if employee.state in result.get(employee.employee_id.id).keys():
                    result[employee.employee_id.id][employee.state] = result[employee.employee_id.id][employee.state] + 1
                else :
                     result[employee.employee_id.id]['name'] = employee.employee_id.name
                     result[employee.employee_id.id][employee.state] = 1
            else:
                result.update({employee.employee_id.id:{"name":employee.employee_id.name,employee.state:1}})
        for key, value in result.iteritems():
            dictlist.append(value)
        return dictlist 