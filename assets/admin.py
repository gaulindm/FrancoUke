# assets/admin.py
from django.contrib import admin

from django.utils.text import slugify
from .forms import AssetBulkUploadForm
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("title", "file", "created_at")
    search_fields = ("title",)
    change_list_template = "admin/assets_changelist.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                "bulk-upload/",
                self.admin_site.admin_view(self.bulk_upload_view),
                name="assets_bulk_upload",
            ),
        ]
        return custom_urls + urls

    def bulk_upload_view(self, request):
        from django.contrib import messages
        from django.shortcuts import render, redirect

        if request.method == "POST":
            form = AssetBulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                files = request.FILES.getlist("files")
                event = form.cleaned_data.get("event")
                tags_raw = form.cleaned_data.get("tags")
                tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

                created_assets = []
                for f in files:
                    asset = Asset.objects.create(file=f, title=f.name)
                    # ✅ Apply tags
                    if tags:
                        asset.tags.add(*tags)
                    created_assets.append(asset)

                # ✅ Assign to event gallery
                if event:
                    event.gallery_assets.add(*created_assets)

                messages.success(
                    request,
                    f"✅ Uploaded {len(created_assets)} assets. "
                    + (f"Linked to event '{event}'." if event else "")
                    + (f" Tags: {', '.join(tags)}" if tags else "")
                )
                return redirect("..")
        else:
            form = AssetBulkUploadForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            opts=self.model._meta,
        )
        return render(request, "admin/assets_bulk_upload.html", context)
