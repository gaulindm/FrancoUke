# assets/views.py
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .models import Asset

@staff_member_required
def asset_chooser_api(request):
    """Return JSON results for asset chooser modal."""
    q = request.GET.get("q", "")
    type_filter = request.GET.get("type")
    page = int(request.GET.get("page", 1))

    qs = Asset.objects.all().order_by("-uploaded_at")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(caption__icontains=q))
    if type_filter:
        qs = qs.filter(type=type_filter)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(page)

    data = {
        "results": [
            {
                "id": str(asset.id),
                "title": asset.title,
                "thumb": asset.thumbnail.url if asset.thumbnail else (asset.file.url if asset.file else ""),
            }
            for asset in page_obj.object_list
        ],
        "pagination": {
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        },
    }
    return JsonResponse(data)

# assets/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def chooser_modal(request):
    """
    Admin-only asset chooser modal.
    Serves the empty shell HTML template,
    which loads assets via the JSON API.
    """
    return render(request, "assets/chooser.html")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from .forms import AssetBulkUploadForm
from .models import Asset


@login_required
@permission_required("assets.add_asset", raise_exception=True)
def bulk_upload_assets(request):
    """Handle bulk image uploads for the Asset model."""
    if request.method == "POST":
        form = AssetBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("files")
            created = 0
            for f in files:
                Asset.objects.create(file=f, title=f.name)
                created += 1
            messages.success(request, f"✅ Successfully uploaded {created} assets.")
            return redirect("admin:assets_asset_changelist")  # back to Asset admin
    else:
        form = AssetBulkUploadForm()

    return render(request, "assets/bulk_upload.html", {"form": form})
