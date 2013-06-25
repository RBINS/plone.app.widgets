# -*- coding: utf-8 -*-

from DateTime import DateTime
from datetime import datetime
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from zope.component import queryMultiAdapter
from plone.app.widgets import base
from Products.CMFCore.utils import getToolByName


class BaseWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "patterns_widget",
        'pattern': None,
    })

    _widget = base.BaseWidget

    def _widget_args(self, context, field, request):
        options = {}
        for name in self._properties.keys():
            if name in ['blurrable', 'condition', 'description', 'helper_css',
                        'helper_js', 'label', 'macro', 'modes', 'populate',
                        'postback', 'show_content_type', 'visible', 'pattern',
                        'ajax_vocabulary']:
                continue
            options[name] = getattr(self, name)
        return {
            'name': field.getName(),
            'pattern': self.pattern,
            'pattern_options': options,
        }

    def view(self, context, field, request):
        return field.getAccessor(context)()

    def edit(self, context, field, request):
        args = self._widget_args(context, field, request)
        return self._widget(**args).render()


class InputWidget(BaseWidget):
    _properties = BaseWidget._properties.copy()
    _widget = base.InputWidget

    def _widget_args(self, context, field, request):
        args = super(InputWidget, self)._widget_args(context, field, request)
        # XXX: we might need to decode the value and encoding shouldn't be
        # hardcoded (value.decode('utf-8'))
        args['value'] = request.get(field.getName(),
                                    field.getAccessor(context)())
        return args


class DateWidget(InputWidget):
    _properties = InputWidget._properties.copy()
    _properties.update({
        'pattern': 'pickadate'
    })
    _widget = base.DateWidget

    def _widget_args(self, context, field, request):
        args = super(DateWidget, self)._widget_args(context, field, request)
        args['request'] = request
        value = request.get(field.getName(), field.getAccessor(context)())
        if value:
            if isinstance(value, DateTime):
                args['value'] = '%s-%s-%s' % (value.year(),
                                              value.month(),
                                              value.day())
            else:
                args['value'] = '%s-%s-%s' % (value.year,
                                              value.month,
                                              value.day)

        return args

    security = ClassSecurityInfo()
    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None):
        """Basic impl for form processing in a widget"""

        value = form.get(field.getName(), empty_marker)
        if value is empty_marker or value == '':
            return empty_marker

        if ' ' in value:
            tmp = value.split(' ')
            value = tmp[0].split('-')
            value += tmp[1].split(':')
        else:
            value = value.split('-')

        # TODO: timezone is not handled

        try:
            value = DateTime(datetime(*map(int, value)))
        except:
            value = ''

        form[field.getName()] = value  # stick it back in request.form
        return value, {}


registerWidget(
    DateWidget,
    title='Date widget',
    description=('Date widget'),
    used_for=('Products.Archetypes.Field.DateTimeField',)
)


class DatetimeWidget(DateWidget):
    _properties = DateWidget._properties.copy()
    _widget = base.DatetimeWidget

    def _widget_args(self, context, field, request):
        args = super(DatetimeWidget, self)._widget_args(context, field,
                                                        request)
        value = request.get(field.getName(), field.getAccessor(context)())
        if value:
            if isinstance(value, DateTime):
                args['value'] = '%s-%s-%s %s:%s' % (value.year(),
                                                    value.month(),
                                                    value.day(),
                                                    value.hour(),
                                                    value.minute())
            else:
                args['value'] = '%s-%s-%s %s:%s' % (value.year,
                                                    value.month,
                                                    value.day,
                                                    value.hour,
                                                    value.minute)
        return args


registerWidget(
    DateWidget,
    title='Datetime widget',
    description=('Datetime widget'),
    used_for=('Products.Archetypes.Field.DateTimeField',)
)


class SelectWidget(BaseWidget):
    _properties = InputWidget._properties.copy()
    _widget = base.SelectWidget

    def _widget_args(self, context, field, request):
        args = super(SelectWidget, self)._widget_args(context, field, request)
        args['options'] = field.Vocabulary(context).items()
        return args


class Select2Widget(InputWidget):
    _properties = InputWidget._properties.copy()
    _properties.update({
        'pattern': 'select2',
        'separator': ';',
    })
    _widget = base.Select2Widget

    def _widget_args(self, context, field, request):
        args = super(Select2Widget, self)._widget_args(context, field, request)
        if hasattr(self, 'ajax_vocabulary'):

            portal_state = queryMultiAdapter((context, request),
                                             name=u'plone_portal_state')
            url = ''
            if portal_state:
                url += portal_state.portal_url()
            url += '/@@getVocabulary?name=' + self.ajax_vocabulary
            if 'pattern_options' not in args:
                args['pattern_options'] = {}
            args['pattern_options']['ajaxvocabulary'] = url
        return args

    def process_form(self, instance, field, form, empty_marker=None):
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        value = value.strip().split(self.separator)
        return value, {}


registerWidget(
    Select2Widget,
    title='Select2 widget',
    description=('Select2 widget'),
    used_for=('Products.Archetypes.Field.LinesField',)
)


class RelatedItems(Select2Widget):
    _properties = Select2Widget._properties.copy()
    _properties.update({
        'pattern': 'relateditems',
        'ajax_vocabulary': 'plone.app.vocabularies.Catalog',
        'width': '50em'
    })

    def _widget_args(self, context, field, request):
        args = super(RelatedItems, self)._widget_args(context, field, request)
        options = args['pattern_options']
        pprops = getToolByName(context, 'portal_properties', None)
        folder_types = ['Folder']
        if pprops:
            site_props = pprops.site_properties
            folder_types = site_props.getProperty(
                'typesLinkToFolderContentsInFC',
                ['Folder'])
        options['folderTypes'] = folder_types
        return args


registerWidget(
    RelatedItems,
    title='Related items widget',
    description=('Related items widget'),
    used_for='Products.Archetypes.Field.ReferenceField')

