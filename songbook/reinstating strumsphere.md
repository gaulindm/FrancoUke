# ✅ Guide to Re-Enabling StrumSphere in Django

This guide outlines the necessary steps to bring back the English version of the site, **StrumSphere**, in a Django project previously focused on **FrancoUke**.

---

## 1. Enable URL Routing

In your **project-level `urls.py`**, re-add or uncomment the `StrumSphere` route:

```python
from django.urls import include, path

urlpatterns += [
    path("StrumSphere/", include("songbook.urls")),
]


If you're using a toggle via settings.py:

ENABLE_STRUMSPHERE = True


2. Restore or Recreate the View Route
Ensure your songbook/urls.py includes a route with the name strumsphere_songs, such as:

python
Copy
Edit
path('StrumSphere/songs/', views.song_list_view, name='strumsphere_songs'),
Or for a shared site-based route:

python
Copy
Edit
path('<str:site>/songs/', views.SongListView.as_view(), name='strumsphere_songs'),
Ensure the corresponding view supports site_name.

3. Restore Template Logic
Re-enable any conditionals or links in templates like base.html:

django
Copy
Edit
{% if site_name == "FrancoUke" %}
  <a href="{% url 'francouke_songs' %}">FrancoUke</a>
{% else %}
  <a href="{% url 'strumsphere_songs' %}">StrumSphere</a>
{% endif %}
Remove any placeholders like href="#".

4. Reinstate Footer or Cross-Site Links
In partials/footer.html, restore links like:

django
Copy
Edit
<a href="{% url 'strumsphere_songs' %}" class="btn btn-outline-primary btn-sm">Visitez StrumSphere</a>
Make sure any conditional rendering blocks like {% if ENABLE_STRUMSPHERE %} are re-enabled if needed.

5. Re-enable Site Content Filtering (Optional)
If views or templates previously filtered out "StrumSphere", restore logic such as:

python
Copy
Edit
if site_name == "StrumSphere":
    # Load StrumSphere-specific content
6. Review Context Settings
Ensure "StrumSphere" is passed to templates via:

View context (context['site_name'])

Custom context processor (if applicable)

7. Test the Following URLs
https://yourdomain.com/StrumSphere/songs/

Song details: /StrumSphere/song/<id>/

Dictionary or export routes:

/StrumSphere/dictionary/

/StrumSphere/generate_pdf/

