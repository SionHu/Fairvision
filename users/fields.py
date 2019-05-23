from django import forms
from csgame.storage_backends import MediaStorage

#https://stackoverflow.com/a/32791625
class ListTextInput(forms.TextInput):
    def __init__(self, choices, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._list = choices
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super().render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            if isinstance(item, tuple) and len(item) == 2:
                data_list += '<option value="%s">%s</option>' % item
            else:
                data_list += '<option>%s</option>' % (item,)
        data_list += '</datalist>'

        return (text_html + data_list)
