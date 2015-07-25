openerp.pls = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    /*
     * 
     * There will be a main widget that will call two widgets
     * -The many2one field widget
     * -The project for which attendance is taken rendering widget
     *  Both these widgets will be called into the main widget
     *  Display the project for which attendance is taken in a table form with two columns ---> project,attendance taken by 
     *  also display another table for projects for which attendance is not taken\
     *  
     */
    
    // This is the select project widget containing many2one field and the button
    
    local.select_project = instance.Widget.extend({
    	template:"select_project",
        events : {
			"click #select_project":"pop_up_wizard",
        },
    	init:function(parent){
    		this._super(parent);
    		this.create_form_fields = {
                    project_id: {
                        id: "project_id",
                        index: 0,
                        corresponding_property: "project_id", // a account.move field name
                        label: _t("Select Project"),
                        required: true,
                        tabindex: 10,
                        constructor: instance.web.form.FieldMany2One,
                        field_properties: {
                            relation: "telecom.project",
                            string: _t("Select Project"),
                            type: "many2one",
                            //domain: [], //[['type','not in',['view', 'closed', 'consolidation']]]
                        },
    		
                    },
              };
    	},
    	
    	pop_up_wizard:function(){
    		var self = this
    		project_selected = self.project_m2o.get_value() 
    			
    	},
    	
    	start:function(){
    		var self = this;
    		def = self.render_view();
    		return def
    	},

    	render_view:function(){
    		var self=this;
    		return self.createFormWidget();
    	},
    	
    	createFormWidget: function() { //working
    		var self = this;
    		if (self.dfm)
    			return;
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                project_id: {
                    relation: "telecom.project",
                },
            });
            self.project_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    name: "project_id",
                    type: "many2one",
                    domain: [
                    ],
                    context: {
                    },
                    modifiers: '{"required": true}',
                },
            });
            var $button = $(QWeb.render("button_select_project", {}));
            self.project_m2o.prependTo(self.$el);
            console.log(self.$el.children().find('span.oe_form_field'));
            self.$el.first().find('span.oe_form_field').prepend($button);
    	},    	
    });
    
    
    local.attendance_base = instance.Widget.extend({
    	template:"attendance_base",
    	init:function(parent){
    		this._super(parent)
    	},
    	
    	start: function() {
    		var self =this;
        	// Initializing the select project widget
        	var select_project_widget  = new local.select_project(this);
        	select_project_widget.appendTo(self.$el)
        },
        
    });

    instance.web.client_actions.add(
        'local.attendance_base', 'instance.pls.attendance_base');
}