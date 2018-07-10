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

odoo.define('muk_dms.field_utils', function(require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var field_utils = require('web.field_utils');

var _t = core._t;
var QWeb = core.qweb;

function documentbinaryToBinsize(value) {
    if (!utils.is_bin_size(value)) {
        return utils.human_size(value.length);
    }
    return value;
}

function formatDocumentBinary(value, field, options) {
    if (!value) {
        return '';
    }
    return documentbinaryToBinsize(value);
}

function formatDocumentMany2one(value, field, options) {
    value = value && (_.isArray(value) ? value[1] : value.data.display_name) || '';
    if (options && options.escape) {
        value = _.escape(value);
    }
    return value;
}

function parseDocumentMany2one(value) {
    if (_.isArray(value)) {
        return {
            id: value[0],
            display_name: value[1],
        };
    }
    if (_.isNumber(value) || _.isString(value)) {
        return {
            id: parseInt(value, 10),
        };
    }
    return value;
}

field_utils.format.document_binary = formatDocumentBinary;
field_utils.parse.document_binary = _.identity; 

field_utils.format.document_many2one = formatDocumentMany2one;
field_utils.parse.document_many2one = parseDocumentMany2one; 

});
