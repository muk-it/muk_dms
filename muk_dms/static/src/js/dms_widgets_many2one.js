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

odoo.define('muk_dms_widgets.many2one', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var form_relational = require('web.form_relational');
var list_widgets = require('web.ListView');

var PreviewHelper = require('muk_dms_preview_file.PreviewHelper');

var _t = core._t;
var QWeb = core.qweb;

var DocumentMany2OneFormWidget = core.form_widget_registry.get("many2one").extend({
	template: "FieldDocumentMany2One",
	display_string: function (str) {
        var self = this;
        if (!this.get("effective_readonly")) {
            this._super(str);
        } else {
        	if (this.options.no_open) {
				this._super(str);
        	} else {
        		var display = (str === null) ? 
        				"" : (_.escape(str.trim()).split("\n").join("<br/>") || data.noDisplayContent);
        		var $link = this.$el.find('.o_form_uri');
        		$link.html(display);
        		$link.off('click');
                $link.click(function (e) {
                    e.preventDefault();
                    _.once(self.execute_formview_action.bind(self))();
                });
                this.$el.find('.muk_form_document_preview').click(function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    PreviewHelper.createFilePreviewDialog(self.get('value'));
                });
        	}

        }
    },
});

var DocumentMany2OneColumnWidget = list_widgets.Column.extend({
    _format: function (row_data, options) {
        var value = row_data[this.id].value;
        return value ? value[1] : "";
    }
});

core.form_widget_registry.add('dms_many2one', DocumentMany2OneFormWidget);
core.list_widget_registry.add('field.dms_many2one', DocumentMany2OneColumnWidget);


});
