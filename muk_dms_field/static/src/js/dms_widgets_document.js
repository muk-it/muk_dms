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

odoo.define('muk_dms_field_widgets.document', function(require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');
var document_common = require('muk_dms_field_widgets.common');

var form_common = require('web.form_common');
var list_widgets = require('web.ListView');

var Model = require("web.Model");
var Dialog = require('web.Dialog');
var PreviewHelper = require('muk_dms_preview_file.PreviewHelper');

var Data = new Model('ir.model.data', session.user_context);
var Directory = new Model('muk_dms.directory', session.user_context);
var Files = new Model('muk_dms.file', session.user_context);

var _t = core._t;
var QWeb = core.qweb;

var DocumentFormWidget = form_common.AbstractField.extend(
		document_common.FolderCompletionFieldMixin, form_common.ReinitializeFieldMixin, {
	template: "FieldDocument",
	init: function(field_manager, node) {
        this._super(field_manager, node);
        this.useFileAPI = !!window.FileReader;
        this.max_upload_size = this.options.max_upload_size || 50 * 1024 * 1024;
        if (!this.useFileAPI) {
            this.fileupload_id = _.uniqueId('o_fileupload');
            $(window).on(this.fileupload_id, function() {
                var args = [].slice.call(arguments).slice(1);
                self.on_file_uploaded.apply(self, args);
            });
        }
	},
	stop: function() {
        if (!this.useFileAPI) {
            $(window).off(this.fileupload_id);
        }
        this._super.apply(this, arguments);
    },
    initialize_content: function() {
    	var self = this;
    	if (this.get("effective_readonly")) {
    		this.$el.find('.muk_form_document_download').on('click', _.bind(this.download_file, this));
    		this.$el.find('.muk_form_document_info').on('click', _.bind(this.info_file, this));
    		this.$el.find('.muk_form_document_preview').on('click', _.bind(this.preview_file, this));
    		this.$el.find('.muk_form_document_checkout').on('click', _.bind(this.checkout_file, this));
    		this.$el.find('.muk_form_document_link').on('click', _.bind(this.link_file, this));
        } else {
        	if(this.node.attrs.directory) {
        		this.$el.find('.muk_form_document_folder_selection').prop('disabled', true);
        		this.$el.find('.muk_form_document_folder_search').prop('disabled', true);
        	} else {
	        	var $folder = this.$el.find('.muk_form_document_folder_selection');
	    		$folder.on('click', function() {
	                if ($folder.autocomplete("widget").is(":visible")) {
	                	$folder.autocomplete("close");
	                } else {
	                	$folder.autocomplete("search", "");
	                }
	            });
	    		$folder.closest(".modal .modal-content").on('scroll', function() {
	    			_.debounce(function() {
	                    if ($folder.autocomplete("widget").is(":visible")) {
	                    	$folder.autocomplete("close");
	                    }
	                }, 50);
	    		});
	    		$folder.autocomplete({
	                source: function(req, resp) {
	                	self.get_search_result(req.term).done(function(result) {
	                        resp(result);
	                    });
	                },
		            select: function(event, ui) {
		                var item = ui.item;
		                if (item.id) {
		                	self.directory_selected(item.id);
		                } else if (item.action) {
		                    item.action();
		                    self.trigger('focused');
		                }
		                return false;
		            },
		            focus: function(e, ui) {
		                e.preventDefault();
		            },
		            autoFocus: true,
		            html: true,
		            minLength: 0,
		            delay: 200,
	            });
	    		this.$el.find('.muk_form_document_folder_search').on('click', _.bind(this.open_search, this));
	        }
       }
    },
    render_value: function() {
    	var self = this;
    	var value = this.get('value');
    	if (this.get("effective_readonly")) {
    		if(value) {
    			var $folder = this.$el.find('.muk_form_document_folder');
    			var $donwload_link = this.$el.find('.muk_form_document_download');
    			$folder.empty().append($("<span/>").addClass('fa fa-folder'));
    			$folder.append($("<span/>").text(value.directory[0][1]));
    			$donwload_link.empty().append($("<span/>").addClass('fa fa-download'));
    			$donwload_link.append($("<span/>").text(value.name));
    			if(value.locked && value.locked instanceof Array) {
    				this.$el.find('.muk_form_document_checkout').prop('disabled', true);
    			}
    		} else {
    			this.do_toggle(!!value);
    		}
    	} else {
    		if(value.directory && value.directory[0]) {
    			this.$el.find('.muk_form_document_folder_selection').val(value.directory[0][1]);
    		} else if(this.node.attrs.directory) {
    			var args = this.node.attrs.directory.split(".");
    			var module, xmlid;
    			if(args.length === 1) {
    				module = this.view.dataset.model.split(".")[0];
    				xmlid = args[0];
    			} else {
    				module = args[0];
    				xmlid = args[1];
    			} 
        		Data.call('get_object_reference', [module, xmlid])
        		.then(function (directory_ref) {
        			this.directory_selected(value.directory[0]);
	        	});
        	}
    		if(value.content) {
                this.$el.find('.muk_form_document_binary_file').children().removeClass('o_hidden');
                this.$el.find('.muk_form_document_file_select').first().addClass('o_hidden');
                this.$el.find('.muk_form_document_file_filename').val(value.name);
                this.$el.find('.muk_form_document_locked').hide();
            } else if(value.locked && value.locked instanceof Array) {
            	this.$el.find('.muk_form_document_binary_file').children().prop('disabled', true);
                this.$el.find('.muk_form_document_file_select').first().addClass('o_hidden');
                this.$el.find('.muk_form_document_file_filename').val(value.name);
                this.$el.find('.muk_form_document_folder_selection').prop('disabled', true);
                this.$el.find('.muk_form_document_folder_search').prop('disabled', true);
                this.$el.find('.muk_form_document_locked').show();
            } else {
            	this.$el.find('.muk_form_document_binary_file').children().addClass('o_hidden');
                this.$el.find('.muk_form_document_file_select').first().removeClass('o_hidden');
                this.$el.find('.muk_form_document_locked').hide();
            }
    		var $input = this.$el.find('.o_form_input_file');
    		$input.on('change', _.bind(this.on_file_change, this));
    		this.$el.find('.muk_form_document_file_select, .muk_form_document_file_edit').click(function() {
    			$input.click();
            });
            this.$el.find('.muk_form_document_file_filename').on('change', _.bind(this.on_filename_change, this));
            this.$el.find('.muk_form_document_file_clear').on('click', _.bind(this.on_clear, this));
    	}
    },
    is_syntax_valid: function() {
    	var value = this.get('value');
    	if(value.content && (!value.name || 0 === value.name.length)) {
    		return false;
    	}
    	if(value.content && !value.directory) {
    		return false;
    	}
    	return this._super();
    },
    on_file_change: function(e) {
    	var self = this;
        var file_node = e.target;
        if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
            if (this.useFileAPI) {
                var file = file_node.files[0];
                if (file.size > this.max_upload_size) {
                    var msg = _t("The selected file exceed the maximum file size of %s.");
                    this.do_warn(_t("File upload"), _.str.sprintf(msg, utils.human_size(this.max_upload_size)));
                    return false;
                }
                var filereader = new FileReader();
                filereader.readAsDataURL(file);
                filereader.onloadend = function(upload) {
                    var data = upload.target.result;
                    data = data.split(',')[1];
                    self.on_file_uploaded(file.size, file.name, file.type, data);
                };
            } else {
                this.$('form.o_form_binary_form input[name=session_id]').val(this.session.session_id);
                this.$('form.o_form_binary_form').submit();
            }
            this.$el.find('.muk_form_document_file_select').hide();
            this.$el.find('.muk_form_document_file_edit').hide();
            this.$el.find('.muk_form_document_file_clear').hide();
            this.$('.o_form_binary_progress').show();
        }
    },
    on_file_uploaded: function(size, name, content_type, file_base64) {
        this.$el.find('.muk_form_document_file_select').show();
        this.$el.find('.muk_form_document_file_edit').show();
        this.$el.find('.muk_form_document_file_clear').show();
        this.$('.o_form_binary_progress').hide();
        if (size === false) {
            this.do_warn(_t("File Upload"), _t("There was a problem while uploading your file"));
            console.warn("Error while uploading file : ", name);
        } else {
        	var new_value = _.clone(this.get('value')) || {};
        	new_value.content = file_base64;
        	new_value.name = name;
        	this.set_value(new_value);
        	this.$el.find('.muk_form_document_file_filename').val(name);
        }
    },
    on_filename_change: function(e) {
    	var new_value = _.clone(this.get('value')) || {};
    	var $input = this.$el.find('.muk_form_document_file_filename');
    	new_value.name = $input.val();
    	this.set_value(new_value);
    },
    on_clear: function(e) {
    	var new_value = _.clone(this.get('value'));
    	new_value.content = false;
    	new_value.name = false;
    	this.set_value(new_value);
    	this.$el.find('.muk_form_document_file_filename').val(false);
    	
    },
    directory_selected: function(id) {
    	var self = this;
    	Directory.query(['name'])
        .filter([['id', '=', id]])
        .limit(1)
        .first().then(function (directory) {
        	var new_value = _.clone(self.get('value')) || {};
        	new_value.directory = [directory.id, directory.name];
        	self.internal_set_value(new_value);
        	self.$el.find('.muk_form_document_folder_selection').val(directory.name);
        });
    },
    open_search: function() {
    	var self = this;
    	new document_common.FolderSearchDialog(this, {}).open()
    	.on('directory_selected', self, function(result){
	    	if(result) {
	    		var id = parseInt(result[0]) || false;
	    		if(id) {
	    			self.directory_selected(id);
	    		}
    		}
        });
    },
    info_file: function(e) {
    	var self = this;
    	var value = self.get('value');
        if (!value) {
        	this.do_warn(_t("Info..."), _t("The field is empty, there's nothing to show!"));
        } else {
        	Files.query(['name', 'create_date', 'write_date', 'size', 'mimetype', 'path'])
        	.filter([['id', '=', value.id]])
        	.first()
        	.then(function(file) {
	        	file.size = utils.human_size(file.size);
        		new Dialog(this, {
	                size: 'medium',
	                title: _t("Info!"),
	                $content: $('<div>').html(QWeb.render('DMSInfoDialog', {
	                	file: file
	                }))
	            }).open();
	        });
        }
    },
    preview_file: function(e) {
   	 	var value = this.get('value');
	   	 if (!value) {
	         this.do_warn(_t("Preview..."), _t("The field is empty, there's nothing to preview!"));
	         e.stopPropagation();
	     } else {
	        PreviewHelper.createFilePreviewDialog(value.id);
	        e.stopPropagation();
	     }
    },
    link_file: function(e) {
    	var self = this;
    	var value = this.get('value');
    	var value = this.get('value');
        if (!value) {
            this.do_warn(_t("Link..."), _t("The field is empty, there's nothing to link to!"));
            e.stopPropagation();
        } else {
	    	var context = this.build_context().eval();
	        Files.call('get_formview_action', [[value.id], context]).then(function(action) {
	        	_.once(self.do_action(action));
	        });
        }
    },
    download_file: function(e) {
    	 var value = this.get('value');
         if (!value) {
             this.do_warn(_t("Download..."), _t("The field is empty, there's nothing to download!"));
             e.stopPropagation();
         } else {
             framework.blockUI();
             this.session.get_file({
                 'url': '/web/content',
                 'data': {
                     'id': value.id,
                     'download': true,
                     'field': 'content',
                     'model': 'muk_dms.file',
                     'filename_field': 'name',
                     'filename': value.name,
                     'data': utils.is_bin_size(value.content) ? null : value.content,
                 },
                 'complete': framework.unblockUI,
                 'error': crash_manager.rpc_error.bind(crash_manager)
             });
             e.stopPropagation();
         }
    },
    checkout_file: function(e) {
    	var value = this.get('value');
        if (!value) {
            this.do_warn(_t("Checkout..."), _t("The field is empty, there's nothing to download!"));
            e.stopPropagation();
        } else {
            framework.blockUI();
            this.session.get_file({
                'url': '/dms/checkout/',
                'data': {
                    'id': value.id,
                    'filename': value.name,
                    'data': utils.is_bin_size(value.content) ? null : value.content,
                },
                'complete': framework.unblockUI,
                'error': crash_manager.rpc_error.bind(crash_manager)
            });
            e.stopPropagation();
        }
    },
});

var DocumentColumnWidget = list_widgets.Column.extend({
    _format: function (row_data, options) {
    	var value = row_data[this.id].value;
    	console.log(value);
        if (!value) {
            return options.value_if_empty || '';
        } else {
		    var text = _.str.sprintf(_t("Download \"%s\""), value.name);
		    var download_url = session.url(
	    		'/web/content', {
	    			model: 'muk_dms.file',
	    			filename: value.name,
	    			filename_field: 'name',
	    			field: 'content',
	    			id: value.id,
	    			download: true
	    	});
		    var preview = _.template(
	    		'<button type="button" \
	        		  class="o_binary_preview" \
	        		  aria-hidden="true" \
					  data-link="<%-link%>" \
					  data-filename="<%-filename%>"> \
	        	  	<i class="fa fa-file-text-o"></i> \
	          	</button>')({
	        	link: download_url,
	            filename: value.name,
		    });
		    var link = _.template(
		    	'<a download="<%-download%>" href="<%-href%>"> \
		    		<%-text%> \
		    	</a> (<%-size%>)')({
		        text: text,
		        href: download_url,
		        size: utils.binary_to_binsize(value.content),
		        download: value.name,
		    });
		    return preview + link;
        }
    }
});

core.form_widget_registry.add('document', DocumentFormWidget);
core.list_widget_registry.add('field.document', DocumentColumnWidget);


});
