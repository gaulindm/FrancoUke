from django import forms
import json


class CubeStateWidget(forms.Widget):
    template_name = "cube/widgets/cube_state_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if value:
            try:
                data = json.loads(value) if isinstance(value, str) else value
            except Exception:
                data = self.default_data()
        else:
            data = self.default_data()

        context["cube_data_json"] = json.dumps(data)
        return context

    def default_data(self):
        return {
            "cube": self.default_state(),
            "highlight": {
                "stickers": []
            }
        }
