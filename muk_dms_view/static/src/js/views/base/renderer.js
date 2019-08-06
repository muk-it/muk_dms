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

odoo.define('muk_dms_view.DocumentsRenderer', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var mixins = require('web.mixins');
var config = require('web.config');
var session = require('web.session');

var mimetype = require('muk_web_utils.mimetype');
var dropzone = require('muk_web_utils.dropzone');

var Widget = require('web.Widget');

var DocumentsRenderer = Widget.extend(dropzone.FileDropzoneMixin, {
	xmlDependencies: [
		'/muk_dms_view/static/src/xml/tree.xml'
	],
	cssLibs: [
        '/muk_dms_view/static/lib/jsTree/themes/proton/style.css',
    ],
    jsLibs: [
        '/muk_dms_view/static/lib/jsTree/jstree.js',
    ],
    template: 'muk_dms.DocumentTree',
    init: function (parent, params) {
		this._super.apply(this, arguments);
		this.params = params || {};
    },
    willStart: function() {
        return $.when(ajax.loadLibs(this), 
        	this._super.apply(this, arguments)
        );
    },
    start: function() {
    	var self = this;
    	var res = this._super.apply(this, arguments);
    	if(this.params.dnd) {
    		this._startDropzone(this.$('.mk_content'));
    	}
        this.$tree = this.$('.mk_tree');
        this.$tree.jstree(this.params.config);
    	this.$tree.on('open_node.jstree', function (e, data) {
    		if(data.node.data && data.node.data.odoo_model === "muk_dms.directory") {
    			data.instance.set_icon(data.node, "fa fa-folder-open-o"); 
    		}
    	});
    	this.$tree.on('close_node.jstree', function (e, data) { 
    		if(data.node.data && data.node.data.odoo_model === "muk_dms.directory") {
        		data.instance.set_icon(data.node, "fa fa-folder-o"); 
    		}
    	});
    	this.$tree.on('ready.jstree', function (e, data) {
    		self.trigger_up('tree_ready', {
    			data: data
            });
    	});
    	this.$tree.on('changed.jstree', function (e, data) {
    		self.trigger_up('tree_changed', {
    			data: data
            });
    	});
    	this.$tree.on('move_node.jstree', function(e, data) {
    		self.trigger_up('move_node', {
    			node: data.node,
    			new_parent: data.parent,
    			old_parent: data.old_parent,
            });
    	});
    	this.$tree.on('copy_node.jstree', function(e, data) {
    		self.trigger_up('copy_node', {
    			node: data.node,
    			original: data.original,
    			parent: data.parent,
            });
    		
    	});
    	this.$tree.on('rename_node.jstree', function(e, data) {
    		self.trigger_up('rename_node', {
    			node: data.node,
    			text: data.text,
    			old: data.old,
            });
    	});
    	this.$tree.on('delete_node.jstree', function(e, data) {
    		self.trigger_up('delete_node', {
    			node: data.node,
    			parent: data.parent,
            });
    	});
    	this.$('[data-toggle="tooltip"]').tooltip();
        return res;
    },
	destroy: function () {
		var res = this._super.apply(this, arguments);
		if(this.params.dnd) {
			this._destroyDropzone(this.$('.mk_content'));
		}
        return res;
    },
    _handleDrop: function(event) {
    	var dataTransfer = event.originalEvent.dataTransfer;
    	if(this.params.dnd && dataTransfer.items && dataTransfer.items.length > 0) {
            this.trigger_up('drop_items', {
            	items: dataTransfer.items
            });
    		event.stopPropagation();
    		event.preventDefault();
    	}
	},
});

return DocumentsRenderer;

});