/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Documents View 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms_view.ActionDocumentTreeView', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var config = require('web.config');
var session = require('web.session');
var web_client = require('web.web_client');

var ControlPanelMixin = require('web.ControlPanelMixin');

var DocumentsModel = require('muk_dms_view.DocumentsModel');
var DocumentsRenderer = require('muk_dms_view.DocumentsRenderer');
var DocumentsViewController = require('muk_dms_view.DocumentsViewController');
var DocumentTreeView = require('muk_dms_view.DocumentTreeView');

var _t = core._t;
var QWeb = core.qweb;

var ActionDocumentTreeView = DocumentTreeView.extend(ControlPanelMixin, {
	custom_events: _.extend({}, DocumentTreeView.prototype.custom_events, {
		reverse_breadcrumb: '_on_reverse_breadcrumb',
    }),
	config: {
		DocumentsModel: DocumentsModel,
		DocumentsRenderer: DocumentsRenderer,
		DocumentsController: DocumentsViewController,
	},
    _update_cp: function() {
    	var self = this;
    	if (!this.$searchview) {
            this.$searchview = $(QWeb.render('muk_dms.DocumentTreeViewSearch', {
                widget: this,
            }));
            this.$searchview.find('#mk_searchview_input').keyup(this._trigger_search.bind(this));
        }
        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
    },    
    _on_reverse_breadcrumb: function() {
        web_client.do_push_state({});
        this._update_cp();
        this.controller.refresh();
    },
    _trigger_search: _.debounce(function() {
		var val = this.$searchview.find('#mk_searchview_input').val();
    	this.controller.search(val);
    }, 200),
});

return ActionDocumentTreeView;

});