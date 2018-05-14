openerp.med_dms_client_refresh_channel = function (instance) {

var WebClient = instance.web.WebClient;
WebClient.include({
    refresh: function(message) {
    	this._super(message);
    	var widget = this.action_manager.inner_widget;
    	if((message === 'muk_dms.file' || message === 'muk_dms.directory') &&
    			widget && widget.name === "Documents") {
    		widget.refresh();
    	}
    }
});
    
};
