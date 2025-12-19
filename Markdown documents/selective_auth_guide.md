# Selective Authentication Implementation Guide

## 🎯 Your Authentication Needs

Based on your setup, here's how to implement **selective authentication** - where most content is public but specific actions require login.

---

## 📚 FrancoUke & StrumSphere (Songbook App)

### Scenario:
- ✅ **Public:** View songs, lyrics, chords, teleprompter, PDFs
- 🔒 **Auth Required:** Edit ChordPro fields

### Implementation:

#### 1. Song List View (Public)
```python
# songbook/views.py

from django.shortcuts import render
from .models import Song

def song_list(request):
    """Public - Anyone can view the song list"""
    songs = Song.objects.all()
    return render(request, 'songbook/song_list.html', {'songs': songs})
```

#### 2. Song Detail View (Public)
```python
def song_detail(request, song_id):
    """Public - Anyone can view song details"""
    song = get_object_or_404(Song, pk=song_id)
    return render(request, 'songbook/song_detail.html', {'song': song})
```

#### 3. Edit ChordPro View (Protected)
```python
from django.contrib.auth.decorators import login_required

@login_required  # 🔒 Only authenticated users
def edit_chordpro(request, song_id):
    """Protected - Only logged-in users can edit ChordPro"""
    song = get_object_or_404(Song, pk=song_id)
    
    if request.method == 'POST':
        song.chordpro = request.POST.get('chordpro')
        song.save()
        return redirect('songbook:song_detail', song_id=song.id)
    
    return render(request, 'songbook/edit_chordpro.html', {'song': song})
```

#### 4. Template with Conditional Edit Button
```django
{# songbook/song_detail.html #}

<h1>{{ song.title }}</h1>
<div class="chordpro-display">
    {{ song.chordpro|safe }}
</div>

{# Only show edit button to authenticated users #}
{% if user.is_authenticated %}
    <a href="{% url 'songbook:edit_chordpro' song.id %}" class="btn btn-primary">
        Edit ChordPro
    </a>
{% else %}
    <p class="text-muted">
        <a href="{% url 'users:login' %}?next={{ request.path }}">Login</a> 
        to edit this song
    </p>
{% endif %}
```

---

## 🎵 Uke4ia (Two-Sided App)

### Scenario:
- ✅ **Public:** `/about/`, `/public_board/`, `/contact/`
- 🔒 **Auth Required:** `/board/`, `/availability/`, `/setlists/`

### Implementation:

#### Public Views (No Auth)
```python
# public/views.py or board/views.py

def about(request):
    """Public - Anyone can view"""
    return render(request, 'uke4ia/about.html')

def public_board(request):
    """Public - Show upcoming events to everyone"""
    events = Event.objects.filter(is_public=True)
    return render(request, 'uke4ia/public_board.html', {'events': events})

def contact(request):
    """Public - Anyone can contact"""
    return render(request, 'uke4ia/contact.html')
```

#### Protected Views (Auth Required)
```python
# board/views.py

from django.contrib.auth.decorators import login_required

@login_required
def full_board(request):
    """Protected - Only authenticated performers"""
    events = Event.objects.all()
    return render(request, 'uke4ia/full_board.html', {'events': events})

@login_required
def performer_event_list(request):
    """Protected - Performer's events and availability"""
    user_events = request.user.events.all()
    return render(request, 'uke4ia/performer_events.html', {'events': user_events})

@login_required
def availability_matrix(request):
    """Protected - Manage performer availability"""
    return render(request, 'uke4ia/availability_matrix.html')
```

#### URL Configuration
```python
# board/urls.py (or public/urls.py)

from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    # Public URLs - No authentication needed
    path('about/', views.about, name='about'),
    path('public-board/', views.public_board, name='public_board'),
    path('contact/', views.contact, name='contact'),
    
    # Protected URLs - Authentication required
    path('', views.full_board, name='full_board'),  # /board/
    path('events/', views.performer_event_list, name='performer_event_list'),
    path('availability/', views.availability_matrix, name='availability_matrix'),
]
```

---

## 🧊 FrancontCube (Future Training Feature)

### Scenario:
- ✅ **Public Now:** All cube learning content
- 🔒 **Auth Required (Future):** Timer, leaderboard

### Current Setup (All Public)
```python
# francontcube/views.py

def home(request):
    """Public - Anyone can learn"""
    return render(request, 'francontcube/home.html')

def tutorial(request, tutorial_id):
    """Public - Free tutorials"""
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    return render(request, 'francontcube/tutorial.html', {'tutorial': tutorial})
```

### Future Protected Features
```python
from django.contrib.auth.decorators import login_required

@login_required
def training_timer(request):
    """Protected - Track practice times"""
    return render(request, 'francontcube/timer.html')

@login_required
def leaderboard(request):
    """Protected - Show user rankings"""
    scores = Score.objects.select_related('user').order_by('-score')
    return render(request, 'francontcube/leaderboard.html', {'scores': scores})

@login_required
def submit_score(request):
    """Protected - Save practice results"""
    if request.method == 'POST':
        score = request.POST.get('score')
        Score.objects.create(user=request.user, score=score)
        return redirect('francontcube:leaderboard')
```

#### Template with Optional Features
```django
{# francontcube/home.html #}

<h1>FrancontCube - Apprends le Rubik's Cube</h1>

{# Always available #}
<a href="{% url 'francontcube:tutorials' %}">Tutoriels Gratuits</a>

{# Show extra features to authenticated users #}
{% if user.is_authenticated %}
    <div class="authenticated-features">
        <h3>Tes outils d'entraînement:</h3>
        <a href="{% url 'francontcube:timer' %}">⏱️ Chronomètre</a>
        <a href="{% url 'francontcube:leaderboard' %}">🏆 Classement</a>
    </div>
{% else %}
    <div class="auth-prompt">
        <p><a href="{% url 'users:login' %}">Connecte-toi</a> pour accéder au chronomètre et au classement!</p>
    </div>
{% endif %}
```

---

## 🔗 Setlists (Bridge Between Apps)

### Scenario:
Uke4ia performers create setlists using StrumSphere songs

### Implementation:

```python
# setlists/views.py

from django.contrib.auth.decorators import login_required
from songbook.models import Song
from .models import Setlist

@login_required
def create_setlist(request):
    """Protected - Only performers can create setlists"""
    songs = Song.objects.filter(site__name='StrumSphere')  # From StrumSphere
    
    if request.method == 'POST':
        setlist = Setlist.objects.create(
            created_by=request.user,
            name=request.POST.get('name')
        )
        song_ids = request.POST.getlist('songs')
        setlist.songs.set(song_ids)
        return redirect('setlists:detail', setlist.id)
    
    return render(request, 'setlists/create.html', {'songs': songs})

@login_required
def setlist_detail(request, setlist_id):
    """Protected - View/edit your setlists"""
    setlist = get_object_or_404(Setlist, pk=setlist_id, created_by=request.user)
    return render(request, 'setlists/detail.html', {'setlist': setlist})
```

---

## 🎨 Navbar Patterns

### Pattern 1: Show/Hide Links Based on Auth
```django
{# In your navbar partial #}

{% if user.is_authenticated %}
    <a href="{% url 'songbook:edit' %}">Edit Songs</a>
    <a href="{% url 'board:full_board' %}">My Board</a>
    <a href="{% url 'setlists:my_setlists' %}">My Setlists</a>
{% else %}
    <a href="{% url 'users:login' %}">Login to Edit</a>
{% endif %}
```

### Pattern 2: Always Show, Conditionally Enable
```django
<a href="{% url 'francontcube:timer' %}" 
   {% if not user.is_authenticated %}class="disabled" title="Login required"{% endif %}>
    ⏱️ Timer
</a>
```

### Pattern 3: Show Different Text
```django
{% if user.is_authenticated %}
    <a href="{% url 'songbook:my_songs' %}">My Contributions</a>
{% else %}
    <a href="{% url 'songbook:song_list' %}">Browse Songs</a>
{% endif %}
```

---

## 🧪 Testing Your Authentication

### Test Matrix:

| Page | Logged Out | Logged In |
|------|------------|-----------|
| `/francouke/songs/` | ✅ Can view | ✅ Can view |
| `/francouke/song/5/edit/` | ❌ Redirect to login | ✅ Can edit |
| `/strumsphere/songs/` | ✅ Can view | ✅ Can view |
| `/about/` | ✅ Can view | ✅ Can view |
| `/public_board/` | ✅ Can view | ✅ Can view |
| `/board/` | ❌ Redirect to login | ✅ Can view |
| `/board/availability/` | ❌ Redirect to login | ✅ Can edit |
| `/setlists/create/` | ❌ Redirect to login | ✅ Can create |
| `/francontcube/` | ✅ Can view | ✅ Can view |
| `/francontcube/timer/` | ❌ Redirect to login | ✅ Can use |

---

## 💡 Advanced: Permission-Based Access

If you want **different user types** (not just auth/no-auth):

### Create User Groups
```python
# In Django admin or management command

from django.contrib.auth.models import Group, Permission

# Create groups
song_editors = Group.objects.create(name='Song Editors')
performers = Group.objects.create(name='Uke4ia Performers')
speedcubers = Group.objects.create(name='Speedcubers')

# Assign permissions
edit_song = Permission.objects.get(codename='change_song')
song_editors.permissions.add(edit_song)
```

### Use in Views
```python
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('songbook.change_song', raise_exception=True)
def edit_chordpro(request, song_id):
    """Only users with 'change_song' permission can edit"""
    # Your edit logic
    pass
```

### Check in Templates
```django
{% if perms.songbook.change_song %}
    <a href="{% url 'songbook:edit' song.id %}">Edit</a>
{% endif %}
```

---

## 📋 Implementation Checklist

### FrancoUke/StrumSphere:
- [ ] Song viewing is public (no `@login_required`)
- [ ] ChordPro editing has `@login_required`
- [ ] Edit buttons only show for authenticated users
- [ ] PDF generation is public
- [ ] Teleprompter is public

### Uke4ia:
- [ ] `/about/`, `/public_board/`, `/contact/` are public
- [ ] `/board/` has `@login_required`
- [ ] `/availability/` has `@login_required`
- [ ] Setlist creation has `@login_required`
- [ ] Navbar adapts based on authentication (already done! ✅)

### FrancontCube:
- [ ] All current pages are public
- [ ] Plan for future timer/leaderboard with `@login_required`
- [ ] Consider showing "Login for advanced features" prompt

### General:
- [ ] `LOGIN_REDIRECT_URL = 'landing'` in settings.py ✅
- [ ] Landing page shows all 4 apps
- [ ] Test login flow from each app
- [ ] Test direct access to protected pages
- [ ] Verify `?next=` parameter works correctly

---

## 🎯 Quick Reference

### When to Use `@login_required`:

✅ **Use it for:**
- Creating/editing content (ChordPro, setlists)
- Personal data (my availability, my scores)
- User-specific features (timer tracking, leaderboard submission)

❌ **Don't use it for:**
- Viewing public content (songs, tutorials, public events)
- General information pages (about, contact)
- Features meant to attract new users

### The Rule of Thumb:
**"Can I show this to my grandma without her needing an account?"**
- Yes → Don't require login
- No → Use `@login_required`

---

## 🆘 Common Questions

**Q: Should I require login to view the StrumSphere teleprompter?**
A: No - keep it public to showcase your platform. Only protect editing.

**Q: What if someone tries to edit a song without logging in?**
A: `@login_required` automatically redirects them to login, then back to the edit page.

**Q: Can the same user be both a song editor AND a Uke4ia performer?**
A: Yes! Your users can have multiple roles. That's why the landing page is perfect.

**Q: Should I show the landing page to logged-in users?**
A: Yes - they might want to switch between apps (edit songs → check Uke4ia schedule → practice cubing).

---

This setup gives you **maximum flexibility** while keeping your apps mostly public. Users only need to authenticate when they want to contribute or access personalized features. Perfect for a community-focused project! 🎉
