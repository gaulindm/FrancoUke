# Project Context – FrancoUke / StrumSphere / Uke4ia

## Overview
This Django project powers three related ukulele web applications:
1. **FrancoUke** – French songbook (main)
2. **StrumSphere** – English songbook
3. **Uke4ia** – Performance/volunteer portal

All apps share a single Django project with namespaced URLs and site-specific templates.


## ✅ Current Architecture

- **Framework**: Django 5.x
- **Apps**:
  - `songbook`: Manages songs, tags, formatting, and metadata
  - `users`: Handles custom user model, registration, login, preferences
  - `tools`: Helper utilities (transposition, chord rendering, PDF generation)
  - `gigs`: Manage gigs sessions and availability 
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

### 2025-08-04: Uke4ia dashboard

# FrancoUke Project Context

## Current Features

1. **Gigs App (Uke4ia)**
   - `Venue` model with:
     - `name`, `location`
     - `image` (optional)
   - `Gig` model with:
     - `title`, `description`
     - `date`, `start_time`, `end_time` (optional)
     - `arrive_by` (optional)
     - `venue` (FK)
     - `created_at` (auto timestamp)
   - Admin:
     - List view sorted by venue/date
     - **Duplicate gig action** with:
       - Bulk duplicate
       - **Duplicate & edit** (redirect to new gig edit page)
   - Template:
     - **Horizontal scrolling grid of venues**
     - Each venue is a **column** with:
       - Venue image + name + location
       - **Stacked performances (gigs)** sorted by date
       - Optional **arrive_by** and time range
     - **Responsive behavior:**
       - Desktop: 3 venue columns at a time, **horizontal scroll**
       - Mobile: 1 column per screen (swipeable)
       - **Arrows** for desktop scroll, **auto-hidden on mobile**
       - Smooth scroll & snap-to-card

2. **Styling**
   - Pure **Bootstrap 5** for base styling
   - **Custom embedded CSS** in template for horizontal scroll
   - Scroll arrows styled with semi-transparent backgrounds

---

## Next Steps / TODO

- Auto-hide arrows if the scroll container doesn’t overflow
- Optional:
  - Filter out past gigs in the public view
  - Add “Get Directions” link for venue location
  - Consider a card hover effect to show more details

---

## Notes

- We consistently use **Gig model in backend**, but **UI shows “Performance”**
- Current layout works well for 4+ venues with horizontal scroll
- Mobile experience is optimized for **1 card per screen** with swipe navigation

### 2025-08-06: Uke4ia Navbar & Landing Page Enhancements

#### ✅ Navbar Improvements
- Added **Gig List**, **Gig Grid**, and **Availability Matrix** links for performers
- Restored **user dropdown** in the top-right corner:
  - **My Profile** → points to `users:profile`
  - **Change Password** → placeholder for now (will enable tomorrow)
  - **Logout**
- Mobile-friendly with Bootstrap 5 dropdowns

#### ✅ Landing Page Update
- Added **Uke4ia Performers** card to the landing page
- Shows **NEW!** badge to highlight the new portal
- Directs to the **Performer Gig Grid** for quick access

#### ✅ UX Polish
- Gig Grid is **scrollable by venue**, with **clickable gigs**
- My Profile accessible from **navbar dropdown** in all performer views
- Prepared the **Change Password link** as a dummy until implemented



### 2025-08-06: Uke4ia Performer Grid & Venue Dashboard

We introduced a **performer-focused gig experience** for the Uke4ia portal, enhancing volunteer UX and carpool planning:

#### ✅ New Performer Views
1. **Performer Gig Grid**
   - Horizontal **venue-based scrolling grid** using Bootstrap 5
   - **Columns = Venues**, **Rows = Gigs** for that venue
   - Each gig shows:
     - Title, date/time
     - **My availability badge** (Yes/No/Maybe/–)
     - Clickable row → Gig detail page

2. **Performer Gig Grid Detail**
   - Full gig info (venue, date, time, attire, chairs)
   - **My availability dropdown** with auto-save on submit
   - **All performers availability** shown in table with color-coded badges
   - **Sidebar with all gigs for this venue** to encourage contextual navigation

3. **Availability Matrix**
   - Now accessible to all logged-in performers (was leader-only)
   - Shows performer rows × gig columns with emoji/status icons
   - Great for **planning carpools** and group logistics

#### ✅ UI/UX Highlights
- **Bootstrap 5 CDN** for consistent styling
- **Horizontal scrolling grid** (mobile swipe-friendly)
- **Clickable gig rows** for immediate navigation to details
- **Badges & emojis** for clear visual availability
- **Venue sidebar in detail page** for quick cross-gig navigation

#### ⚡ Impact
- Dramatically improved **volunteer coordination**
- **Visual dashboard** for performers without affecting the public gigs page
- Lays groundwork for **future AJAX auto-save** and **carpooling features**

### Aug 3: 


### ✅ Multi-Site Base Template System
- `base_francouke.html`, `base_strumsphere.html`, `base_uke4ia.html`
- Pages extend `{% extends base_template %}` dynamically from `SiteContextMixin`
- Navbar, footer, and Bootstrap 5.3 are now consistent

### ✅ URL & Namespace Refactor
- All template links use:
  ```django
  {% url site_namespace|add:':view_name' arg %}


### 2025-08-01: Phase 1 – Core Volunteer Management (Gigs Module)

We have implemented the **Gigs module** for StrumSphere to manage volunteer performers and their event availability.

#### ✅ Features Completed:
- **Gigs App (`gigs`)**
  - `Gig` model with title, description, location, start/end time
  - `Availability` model: user → gig → status (Yes/Maybe/No)
- **Player Workflow**
  - "My Gig Availability" page for performers
  - Dropdown to select Yes/Maybe/No for upcoming gigs
  - Saves automatically and redirects
- **Leader Workflow**
  - Role-aware "Availability Matrix" page (performer rows × gig columns)
  - Shows ✅ / ❌ / 🤔 for availability
  - Only accessible to `Leaders` group
- **Admin Management**
  - Gigs managed in admin with inline availability
  - Matrix provides a clean roster overview
- **Navigation**
  - Integrated into `_navbar.html` dropdown
  - Role-aware (Performers & Leaders) and site-aware (StrumSphere only)

#### ⚡ Notes:
- Phase 1 core functionality is complete and stable
- Responsive with Bootstrap; future mobile polish (PWA) is possible
- Email/push reminders are **planned for Phase 2**

Next Steps:
- Add optional `dress_code` and `equipment` fields to `Gig`
- Consider dashboard/email reminders for pending responses




### July 23 : Added permanent transpose button to admin panel
- Admins can transpose by 1 semitone up or down from Change Song admin form
- Admins can also transpose by 1 semitone up or down in bulk in song list



### July 22 : Fixed transposition:
Fix: Song transposition preview now respects site namespace (FrancoUke, StrumSphere).

Issue: Applying transposition reset the iframe source to a path missing the namespace, causing a 404

Fix: Updated JS in _control_panel.html to dynamically update only the query params of the iframe URL using URL.searchParams

Result: Transposition preview now works consistently across both site contexts




### July 16 : Major update

Site Routing Strategy
We implemented namespaced URLs for each edition:

Namespace	    Path Prefix	    Purpose
francouke	    /FrancoUke/	    French song edition
strumsphere	  /StrumSphere/	  English song edition

# FrancoUke/urls.py
path("FrancoUke/", include(("songbook.urls", "songbook"), namespace="francouke")),
path("StrumSphere/", include(("songbook.urls", "songbook"), namespace="strumsphere")),
Each version of the site uses the same songbook app, but templates and views adapt based on the active site_name.

## Multi-site Editing Logic Update (2025-07-16)

### Summary
We have removed the previous restriction that prevented editing songs across site namespaces (e.g., FrancoUke vs. StrumSphere).

### Changes:
- Songs can now be edited regardless of `site_name` in the URL.
- The `site_name` value on the `Song` model is preserved on save (it is no longer overwritten).
- Redirects after song update now use the actual `Song.site_name`, ensuring correct namespace.
- Navbar now dynamically shows:
  - "Chansonnier FrancoUke" for FrancoUke
  - "StrumSphere Songbook" for StrumSphere

### Rationale:
We needed editorial flexibility across sites while preserving content ownership and context integrity.

### Next Steps:
- Consider adding a context processor for global `site_name`
- Monitor for accidental cross-site edits in logs (optional)

🎉 This update simplifies UX and improves cross-site workflow dramatically.


## July 14:
Added chord definition and support for guitalele



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