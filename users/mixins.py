# users/mixins.py
class BootstrapFormMixin:
    def apply_bootstrap_classes(self):
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
