openerp.pls = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.complaint_system.filter_view_message.include({
    	start:function(){
    		var self = this;
    		var defs = [];
			var tmp = this._super.apply(self, arguments); 
    		if ('render_javascript' in self.dataset.context){
    			if ('subtype' in self.dataset.context){
    				if (self.dataset.context['subtype'] == 'attendance_override'){
                		var view_id = new openerp.Model('ir.model.data');
                        defs.push(view_id.call("get_object_reference", ['pls','mt_comment_attendance_override']).then(function(result) {
                        		self.subtype = result[1]
                        }));                        	                    		    					
    				}
    			}
    		}
    		return $.when(tmp,defs);
		},
    });
}