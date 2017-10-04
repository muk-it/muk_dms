/**********************************************************************************
* 
*    Copyright (C) 2017 MuK IT GmbH
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms_widgets.path', function(require) {
"use strict";

var core = require('web.core');
var form_common = require('web.form_common');
var form_widgets = require('web.form_widgets');
var list_widgets = require('web.ListView');

var _t = core._t;
var QWeb = core.qweb;

$.fn.textWidth = function(text, font) {
    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);
    $.fn.textWidth.fakeEl.text(text || this.val() || this.text()).css('font', font || this.css('font'));
    return $.fn.textWidth.fakeEl.width();
};

var PathFormWidget = form_widgets.FieldChar.extend({
	render_value: function() {
        if (this.$input) {
            this._super();
        } else {
        	var show_value = this.format_value(this.get('value'), '');
        	var max_width = this.options.width || 500;
        	var text_witdh = $.fn.textWidth(show_value);
        	if(text_witdh >= max_width) {
        		var ratio_start = (1 - (max_width / text_witdh)) * show_value.length;
        		show_value = ".." +  show_value.substring(ratio_start, show_value.length);
        	}
            this.$el.text(show_value);
        }
	},
});

var RelationalPathFormWidget = core.form_widget_registry.get("text").extend({
    template: 'FieldRelationalPath',
    events : {
		'click a' : 'node_clicked',
	},
    render_value: function() {
    	var self = this;
    	var value = this.get('value');
        if (this.get("effective_readonly")) {
        	var path = JSON.parse(value || "[]");
        	var max_width = this.options.width || 500;
        	var text = "";
        	this.$el.empty();
        	$.each(_.clone(path).reverse(), function(index, element) {
        		text += element.name + "/";
        		if($.fn.textWidth(text) >= max_width) {
            		self.$el.prepend($('<span/>').text(".."));
        		} else {
	        		if (index == 0) {
	        			if(element.model == 'muk_dms.directory') {
	            			self.$el.prepend($('<span/>').text(self.options.seperator || "/"));
	        			}
	            		self.$el.prepend($('<span/>').text(element.name));
	            		self.$el.prepend($('<span/>').text(self.options.seperator || "/"));
	        		} else {
	        			var node = $('<a/>');
	            		node.addClass("oe_form_uri");
	            		node.data('model', element.model);
	            		node.data('id', element.id);
	            		node.attr('href', "javascript:void(0);");
	            		node.text(element.name);
	            		self.$el.prepend(node);
	            		self.$el.prepend($('<span/>').text(self.options.seperator || "/"));
	        		}
        		}
        		return ($.fn.textWidth(text) < max_width);
        	});
        } else {
            this._super();
        }
    },
    node_clicked : function(event) {
    	this.do_action({
			type : 'ir.actions.act_window',
			res_model : $(event.currentTarget).data('model'),
			res_id : $(event.currentTarget).data('id'),
			views : [[ false, 'form' ]],
			target : 'current',
			context : {},
		});
	}
});

var PathColumnWidget = list_widgets.Column.extend({
    _format: function (row_data, options) {
        var value = row_data[this.id].value;
        var text_witdh = $.fn.textWidth(value);
    	if(text_witdh >= 500) {
    		var ratio_start = (1 - (500 / text_witdh)) * value.length;
    		value = ".." + value.substring(ratio_start, value.length);
    	}
        return value;
    }
});

core.form_widget_registry.add('dms_path', PathFormWidget);
core.form_widget_registry.add('dms_relpath', RelationalPathFormWidget);
core.list_widget_registry.add('field.dms_path', PathColumnWidget);


});
