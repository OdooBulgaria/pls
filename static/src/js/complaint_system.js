openerp.pls.quickadd = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.pls = instance.web.pls || {}
    
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
    
    // Attendance Dashboard
    instance.web.views.add('tree_attendance_dashboard', 'instance.web.pls.filter_view_attendance');
    instance.web.pls.filter_view_attendance = instance.web.ListView.extend({
    	init:function(){
            this._super.apply(this, arguments);
            var self = this;
            self.date = null;
            self.current_project= null
            self.project = null;
		},
    	start:function(){
    		var self = this;
    		var defs = []
            self.date = (new Date()).format("Y-m-d");
    		self.d = $.Deferred();
            return this._super.apply(this, arguments).then(function(){
            	self.$el.parent().prepend(QWeb.render("attendance_dashboard", {widget: this}));
                self.$el.parent().find('.oe_select').change(function() {
                		self.current_project = this.value === '' ? null : parseInt(this.value);
    	                self.do_search(self.last_domain, self.last_context, self.last_group_by);
    	            });            	
            	
                self.$el.parent().find("input#from").change(function(){
                	if (this.value !== "") 
                		self.date = this.value;
            		else self.date = null
                	self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });               
                
            	var mod = new instance.web.Model("telecom.project", self.dataset.context, self.dataset.domain);
                defs.push(mod.call("list_project", []).then(function(result) {
                	self.project = result
                	self.d.resolve();
                }));
                return $.when(defs)
            });  		
    	},
    	
    	do_search:function(domain, context, group_by){
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            self.project_list_sorted = []
            var o;
            self.$el.parent().find('.oe_select').children().remove().end();
            self.$el.parent().find('.oe_select').append(new Option('', ''));
            $.when(self.d).then(function(){
                if (self.project){
                    for (var i = 0;i < self.project.length;i++){
                    	self.project_list_sorted.push(self.project[i][0]);
                    	o = new Option(self.project[i][1], self.project[i][0]);
                        self.$el.parent().find('.oe_select').append(o);
                    }            	
                    self.$el.parent().find('.oe_select')[0].value = self.current_project;
                }                        	
            });
            return self.search_by_project_id();    		
    	},
    	
    	search_by_project_id: function() {
            var self = this;
            var domain = [];
            
            /*
             * Check if the user is a Project Manager,Circle Head of Corporate
             *  - If Project Manager then show all attendances for the project in which the project manager is 
             *  - Corporate Head is able to see attendance of all his projects and the project managers under him 
             *  - Corporate is able to see all
             */
            
            if (self.current_project!== null) domain.push(["line_id.project_id", "=", self.current_project]);
            else{
            	domain.push(["line_id.project_id", "in", self.project_list_sorted]);
            }
            if (self.date ) {
            	domain.push(['date','=',self.date])
            }
            self.last_context["project_id"] = self.current_project === null ? false : self.current_project;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);            	
        },            	
    });
}