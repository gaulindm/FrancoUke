from django.contrib import admin
from .models import Cube, Mosaic, MosaicCube
from django.contrib import admin
from django.utils.html import format_html
from .models import Cube
# ----------------------
# Cube Admin
# ----------------------
@admin.register(Cube)


class CubeAdmin(admin.ModelAdmin):
    list_display = ('name', 'colored_grid')
    readonly_fields = ('colored_grid',)
    search_fields = ('name',)  # ✅ add this line for autocomplete to work


    def colored_grid(self, obj):
        """
        Return an HTML representation of the cube.
        """
        try:
            colors = obj.colors  # assume JSON string
            import json
            grid = json.loads(colors)
        except:
            grid = [["W"]*3 for _ in range(3)]

        color_map = {
            "R": "red",
            "B": "blue",
            "Y": "yellow",
            "G": "green",
            "O": "orange",
            "W": "white"
        }

        html = '<div style="display:inline-block;">'
        for row in grid:
            html += '<div style="display:flex;">'
            for cell in row:
                html += f'<div style="width:20px;height:20px;background:{color_map.get(cell,"white")};border:1px solid #000;"></div>'
            html += '</div>'
        html += '</div>'
        return format_html(html)

    colored_grid.short_description = "Cube Preview"

# ----------------------
# MosaicCube Inline
# ----------------------
class MosaicCubeInline(admin.TabularInline):
    model = MosaicCube
    autocomplete_fields = ["cube"]
    fields = ("row", "col", "cube")  # ✅ correct


# ----------------------
# Mosaic Admin
# ----------------------
@admin.register(Mosaic)
class MosaicAdmin(admin.ModelAdmin):
    inlines = [MosaicCubeInline]
    list_display = ['name', 'cube_rows', 'cube_cols', 'created_at']
    search_fields = ['name']

