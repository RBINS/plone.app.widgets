// tabs pattern.
//
// Author: Rok Garbas
// Contact: rok@garbas.si
// Version: 1.0
// Depends: jquery.js patterns.js bootstrap-transition.js bootstrap-tab.js
//
// Description:
//
// License:
//
// Copyright (C) 2010 Plone Foundation
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation; either version 2 of the License.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
// more details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc., 51
// Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//

/*jshint bitwise:true, curly:true, eqeqeq:true, immed:true, latedef:true,
  newcap:true, noarg:true, noempty:true, nonew:true, plusplus:true,
  undef:true, strict:true, trailing:true, browser:true, evil:true */
/*global jQuery:false */


(function($, Patterns, undefined) {
"use strict";

var Toggle = Patterns.Base.extend({
  name: 'toggle',
  jqueryPlugin: 'patternToggle',
  defaults: {
    name: 'class',
    event: 'click'
  },
  init: function() {
    var self = this;

    self.options = $.extend({}, self.defaults, self.options);

    if (!self.options.target) {
      self.$target = self.$el;
    } else {
      self.$target = self.$el.closest(self.options.target);
    }

    self.$el.on(self.options.event, function(e) {
      e.preventDefault();
      e.stopPropagation();
      self.toggle();
    });
  },
  isMarked: function() {
    var self = this;
    if (self.options.name === 'class') {
      return this.$target.hasClass(this.options.value);
    } else {
      return this.$target.attr(this.options.name) !== this.options.value;
    }
  },
  toggle: function() {
    var self = this;
    if (self.isMarked()) {
      self.remove();
    } else {
      self.add();
    }
  },
  remove: function() {
    var self = this;
    self.$el.trigger('patterns.toggle.remove');
    if (self.options.name === 'class') {
      self.$target.removeClass(self.options.value);
    } else {
      self.$target.removeAttr(self.options.name);
    }
    self.$el.trigger('patterns.toggle.removed');
  },
  add: function() {
    var self = this;
    self.$el.trigger('patterns.toggle.add');
    if (self.options.name === 'class') {
      self.$target.addClass(self.options.value);
    } else {
      self.$target.attr(self.options.name, self.options.value);
    }
    self.$el.trigger('patterns.toggle.added');
  }
});


Patterns.register(Toggle);

}(window.jQuery, window.Patterns));
