# Project Context: StrumSphere /FrancoUke

## 🌐 Overview

This Django project serves two music-focused sites, **FrancoUke** and **StrumSphere**, with shared backend logic. Users can view, create, update, and manage ukulele chord charts, including metadata and chord formatting.

**StrumSphere** has been temporairly disabled and can easily be reanabled.

## ✅ Current Architecture

- **Framework**: Django 5.x
- **Apps**:
  - `songbook`: Manages songs, tags, formatting, and metadata
  - `users`: Handles custom user model, registration, login, preferences
  - `tools`: Helper utilities (transposition, chord rendering, PDF generation)
- **Custom User Model**: Implemented (`users.CustomUser`)
- **Authentication**: Includes registration, login, password reset
- **Database**:
  - **Development**: SQLite (default, simple local dev)
  - **Production (planned)**: MySQL on PythonAnywhere
  

## 🧩 Core App Structure

### `Song` Model (`models.py`)
- Stores user-contributed chord charts in **ChordPro** format.
- Fields include:
  - `songTitle`, `songChordPro`, `lyrics_with_chords` (auto-generated JSON),
  - Metadata fields parsed from ChordPro: `title`, `artist`, `capo`, `key`, etc.
  - `site_name`: distinguishes content between **FrancoUke** and **StrumSphere**.
- ChordPro content is processed and converted to JSON for rendering and PDF generation.

---

## 🔗 URL Routing (`urls.py`)
Routes are duplicated for both FrancoUke and StrumSphere using site-specific prefixes:

- **Song Management**:
  - `/<site>/song/<id>/`: View song details.
  - `/<site>/song/new/`, `update/`, `delete/`: Create/update/delete functionality.
- **Artists**:
  - Filter by artist name or initial letter.
- **PDF Exports**:
  - Single and multi-song PDF generation (`preview_pdf`, `generate_single_song_pdf`, etc.).
- **Chord Dictionary**:
  - Site-specific dictionary views under `/FrancoUke/` or `/StrumSphere/`.

---

## 🧠 Views (`views.py`)
Implements a mix of CBVs and FBVs:
- Uses `ScoreView`, `SongCreateView`, `SongUpdateView`, and `SongDeleteView`.
- Custom functions handle PDF creation and formatting (`generate_single_song_pdf`, etc.).
- Views respect the `site_name` context to distinguish content and routing.

---

## 🛠 Notable Features
- **Multi-site Logic**: Single codebase powers two branded experiences.
- **Dynamic Metadata Extraction**: Parses ChordPro content for structured metadata.
- **User-Contributed Content**: Integrated with Django’s `User` model.
- **Tagging**: Via `TaggableManager` for song classification.


### Temporarily disabled StrumSphere
The StrumSphere site routes have been temporarily disabled to prioritize and promote the FrancoUke experience. This change is fully reversible and has been implemented without removing core logic.

Implementation Details:
- A custom middleware (DisableStrumSphereMiddleware) was added at songbook/core/middleware/disable_strumsphere.py.
- All requests starting with /StrumSphere/ now return a custom 403 Forbidden page using the strumsphere_disabled.html template.
- Existing logic, models, and view functions remain intact for future reactivation.
- Template located at songbook/templates/songbook/strumsphere_disabled.html.

Reactivation Guide:
- Remove or comment out the middleware reference in MIDDLEWARE inside settings.py.
- Optionally adjust routing or toggle logic for staged reintroduction. 
- Ref: Disabling Strumsphere on francouke@gmail.com account of chatgpt

### User Authentication Enhancements (June 2025)
Significant improvements were made to user authentication and recovery:

## ✅ Custom User Registration
- Uses users.CustomUser model exclusively
- Custom CustomUserCreationForm ensures registration aligns with the custom model
- Registration is site-aware using site_name logic (FrancoUke / StrumSphere)
- Success message includes a direct link to instrument preferences

✅ Password Recovery Flow
- Full Django-based password reset system implemented with:
  - password_reset/ → Request form
  - password_reset/done/ → Confirmation
  - reset/<uidb64>/<token>/ → Secure token reset link
  - reset/done/ → Success message
- Custom templates created:
  - password_reset_form.html
  - password_reset_done.html
  - password_reset_confirm.html
  - password_reset_complete.html
  - password_reset_email.html
  - password_reset_subject.txt
- All views respect Django namespacing (app_name = 'users')
- reverse_lazy('users:...') used to explicitly set success_url paths

## ✉️ Email Backend
- NO CONSOLE FOR DEV SITE, THEREFORE NO GIT EITHER
- Support for SMTP (e.g., Gmail) with App Passwords configured for production on PythonAnywhere




## Affichage des accords amélioré dans les paroles hyphénées (mai 2025)

Le moteur de rendu PDF a été mis à jour pour respecter les règles typographiques musicales liées aux changements d'accords au sein des paroles.

- Les accords placés au début d’un mot sont précédés d’un espace
- Les accords insérés en milieu de mot (ex. "Ba-tail-[F]leur") ne génèrent plus d’espace avant
- Les traits d’union sont respectés pour la séparation des syllabes, ce qui permet un alignement propre et naturel des accords sur les paroles

Ces améliorations permettent une lecture plus fluide et une expérience fidèle à celle des partitions vocales.