from django.shortcuts import render

def home(request):
    return render(request, "francontcube/home.html")

def slides(request):
    return render(request, "francontcube/slides.html")

def pdfs(request):
    return render(request, "francontcube/pdfs.html")

def videos(request):
    return render(request, "francontcube/videos.html")