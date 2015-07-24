openerp.pls = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    /*
     * 
     * There will be a main widget that will call two widgets
     * -The many2one field widget
     * -The project for which attendance is taken rendering widget
     * Both these widgets will be called into the main widget
     *  
     */
    
    
    local.attendance_base = instance.Widget.extend({
        start: function() {
        	console.log("Shivam");
        },
    });

    instance.web.client_actions.add(
        'local.attendance_base', 'instance.pls.attendance_base');
}