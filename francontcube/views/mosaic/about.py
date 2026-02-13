from django.shortcuts import render

def about(request):
    return render(request, "francontcube/mosaic/about.html")
