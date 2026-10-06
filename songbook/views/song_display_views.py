# songbook/views/song_display_views.py

from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q, prefetch_related_objects
from django.contrib.auth import get_user_model
from django.utils import timezone
from types import SimpleNamespace
import re
import string
from urllib.parse import quote

from collections import Counter, OrderedDict
from django.core.paginator import Paginator

from songbook.mixins import SiteContextMixin
from songbook.context_processors import site_context
from songbook.models import Song, SongFormatting
from songbook.utils.transposer import extract_chords
from taggit.models import Tag
from users.models import UserPreference

User = get_user_model()


# -------------------------------------------------------------
# Landing Page (site-dependent)
# -------------------------------------------------------------
class LandingView(TemplateView):
    """
    Choose a different landing template based on site_name from site_context.
    """
    def get_template_names(self):
        context_data = site_context(self.request)
        site_name = context_data.get("site_name")

        if site_name == "StrumSphere":
            return ["sites/home_strumsphere.html"]


        return ["sites/home_francouke.html"]


# -------------------------------------------------------------
# List of Songs by a User
# -------------------------------------------------------------
def is_valid_chord(chord):
        """Only accept strings that look like real chord names."""
        chord = chord.strip()
        pattern = r'^[A-G][#b]?(m|M|maj|min|dim|aug|sus|add|o)?\d*(\(.*?\))?(/[A-G][#b]?)?$'
        return bool(re.match(pattern, chord))


class UserSongListView(SiteContextMixin, ListView):
    """
    Display all songs contributed by a specific user, filtered by site.
    Shows all songs (private + public) if viewing own collection.
    Shows only public songs if viewing someone else's collection.
    """
    model = Song
    template_name = "songbook/user_songs.html"
    context_object_name = "songs"
    paginate_by = 15

    def get_queryset(self):
        self.viewed_user = get_object_or_404(User, username=self.kwargs.get("username"))
        site_name = self.get_site_name()
        
        # 🆕 Privacy filtering
        if self.request.user == self.viewed_user:
            # Viewing your own songs: show ALL (private + public)
            qs = Song.objects.filter(
                contributor=self.viewed_user, 
                site_name=site_name
            )
        else:
            # Viewing someone else's songs: only public ones
            qs = Song.objects.filter(
                contributor=self.viewed_user, 
                site_name=site_name,
                is_public=True
            )
        
        # 🆕 Optional filter by privacy (for "My Collection" filtering)
        privacy_filter = self.request.GET.get('filter')
        if privacy_filter == 'public':
            qs = qs.filter(is_public=True)
        elif privacy_filter == 'private':
            qs = qs.filter(is_public=False)
        
        return qs.order_by("-date_posted")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewed_user'] = self.viewed_user
        context['is_own_collection'] = (self.request.user == self.viewed_user)
        
        # 🆕 Add counts for filter tabs (if viewing own collection)
        if context['is_own_collection']:
            all_songs = Song.objects.filter(
                contributor=self.viewed_user,
                site_name=self.get_site_name()
            )
            context['public_count'] = all_songs.filter(is_public=True).count()
            context['private_count'] = all_songs.filter(is_public=False).count()
            context['total_count'] = all_songs.count()
            context['current_filter'] = self.request.GET.get('filter', 'all')
        
        return context


# -------------------------------------------------------------
# ChordSheet View (detailed view of a single song)
# -------------------------------------------------------------
class ChordSheetView(DetailView):
    """
    Display a single song.
    Public songs: anyone can view
    Private songs: only the owner can view
    """
    model = Song
    template_name = "songbook/song_chord_sheet.html"
    context_object_name = "chord_sheet"

    def get_queryset(self):
        # 🆕 Privacy filtering for score view
        qs = super().get_queryset()
        
        if self.request.user.is_authenticated:
            # Show: public songs + user's own songs (public or private)
            qs = qs.filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            # Anonymous users: only public songs
            qs = qs.filter(is_public=True)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context["song"] = self.get_object()
        

        if self.request.user.is_authenticated:
            preferences, _ = UserPreference.objects.get_or_create(user=self.request.user)
        else:
            preferences = SimpleNamespace(
                font_size=18,
                theme="light",
                auto_scroll=False,
                scroll_speed=20,
            )

        context["preferences"] = preferences
        
        # 🆕 Add ownership flag for template
        #context["is_owner"] = (self.request.user == context["song"].contributor)
        context["is_owner"] = (self.request.user == self.object.contributor)

        return context


# -------------------------------------------------------------
# Main Song List View (search, tag filter, artist filter)
# -------------------------------------------------------------
class SongListView(SiteContextMixin, ListView):
    """
    Display all songs for a site.
    Filters by privacy: shows public songs + authenticated user's own songs.
    """
    model = Song
    template_name = "songbook/song_list.html"
    context_object_name = "songs"
    ordering = ["songTitle"]
    paginate_by = None  # pagination is done manually, over song *families* — see get_context_data
    FAMILIES_PER_PAGE = 20

    # 🆕 Two flavours of this page share all the filtering code below:
    #   extended view (this class): every column, every song
    #   simple view   (SongListSimpleView): fewer columns, formatted songs only
    # Subclasses only change these three attributes + the template.
    view_mode = "extended"            # used by the templates (switch button, hidden controls)
    list_url_suffix = ":song_list"    # URL name (without namespace) of THIS view, for "Clear Filter" links
    formatted_only = False            # True = only songs that have a SongFormatting row

    # 🆕 The browser remembers which view was used last: a plain cookie, so it
    # survives logout (a session wouldn't) and works for anonymous visitors.
    # The navbar "Songs" link reads it (see partials/_navbar.html).
    VIEW_COOKIE = "song_list_view"
    VIEW_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # one year

    # 🆕 "Almost playable" chord mode: show songs that need exactly this many
    # chords the player doesn't know yet (1 = "learn one more chord").
    ALMOST_MAX_MISSING = 1

    # 🆕 Seasonal tag: hidden from the main list except during its month,
    # unless the user explicitly filters by this tag (any time of year).
    SEASONAL_TAG = "Xmas"
    SEASONAL_MONTH = 12  # December

    def _in_season(self):
        return timezone.now().month == self.SEASONAL_MONTH

    def get_queryset(self):
        # -------------------------------------------------------------
        # 🆕 Filter persistence: remember the last filters used on this
        # site so returning to the bare song_list URL (clicking a song,
        # clicking the nav link, browser back, etc.) restores them.
        #
        # Three cases:
        #   1. ?reset=1        -> explicit "Clear Filter" click: wipe the
        #                          saved filters and show everything.
        #   2. any other GET   -> the user just changed a filter/search/
        #                          page: save it as the new "last used".
        #   3. no GET at all   -> bare visit: fall back to whatever was
        #                          last saved for this site (or nothing).
        # -------------------------------------------------------------
        # 🆕 pk -> chords this song needs that the player doesn't know yet
        # (filled in by the "almost" chord mode below, read by build_row_data)
        self.almost_missing = {}
        self.requested_chords_list = []

        site_name = self.get_site_name()
        session_key = f"song_list_filters:{site_name}"

        if self.request.GET.get("reset") == "1":
            self.request.session.pop(session_key, None)
            self.filter_params = QueryDict("")
        elif self.request.GET:
            self.request.session[session_key] = self.request.GET.urlencode()
            self.filter_params = self.request.GET
        else:
            self.filter_params = QueryDict(self.request.session.get(session_key, ""))

        qs = super().get_queryset()
        qs = qs.filter(site_name=site_name)

        # Privacy filter
        if self.request.user.is_authenticated:
            qs = qs.filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            qs = qs.filter(is_public=True)

        # Existing filters
        if self.formatted_only or self.filter_params.get("formatted") == "1":
            # pk__in (not a join) so a song formatted by several users can't
            # appear twice; that keeps the final DISTINCT unnecessary.
            qs = qs.filter(pk__in=SongFormatting.objects.values("song_id"))

        search_query = self.filter_params.get("q", "").strip()
        selected_tag = self.filter_params.get("tag", "").strip()
        artist_name = self.kwargs.get("artist_name")

        if search_query:
            qs = qs.filter(
                Q(songTitle__icontains=search_query)
                | Q(metadata__artist__icontains=search_query)
                | Q(metadata__songwriter__icontains=search_query)
            )

        if selected_tag:
            qs = qs.filter(tags__name=selected_tag)

        # 🆕 Hide seasonal (Xmas) songs from the general list outside their
        # month — but never hide them if the user is specifically browsing
        # that tag (the "Xmas" button in the tag filter still works any time).
        if selected_tag.lower() != self.SEASONAL_TAG.lower() and not self._in_season():
            qs = qs.exclude(tags__name__iexact=self.SEASONAL_TAG)

        if artist_name:
            qs = qs.filter(metadata__artist__iexact=artist_name)

        # 🆕 Filter by club (the Song.origin field: SOUP, I-Ukes, NBU, FWC...)
        origin_filter = self.filter_params.get("origin", "").strip()
        if origin_filter:
            qs = qs.filter(origin__iexact=origin_filter)

        # 🆕 Filter by starting letter (A-Z) or number/symbol ("#")
        letter_filter = self.filter_params.get("letter", "").strip().upper()
        if letter_filter:
            if letter_filter == "#":
                # Titles that DON'T start with a letter (numbers, symbols, etc.)
                qs = qs.exclude(songTitle__iregex=r"^[A-Za-z]")
            else:
                qs = qs.filter(songTitle__istartswith=letter_filter)

        chord_filter = self.filter_params.get("chords", "").strip()
        chord_mode = self.filter_params.get("chord_mode", "playable")

        if chord_filter:
            self.requested_chords_list = [c.strip() for c in chord_filter.split(",") if c.strip()]
            requested_chords = {c.lower() for c in self.requested_chords_list}

            # One pass for all three modes. Only real chords count — [N.C.]
            # and other junk tokens are ignored, otherwise a song containing
            # N.C. could never be "playable" (or would always be "missing" it).
            matching_pks = []
            for pk, chords_used in qs.values_list("pk", "chords_used"):
                if not chords_used:
                    continue
                # lowercase -> original spelling, so we can show "Em" not "em"
                song_map = {
                    c.strip().lower(): c.strip()
                    for c in chords_used.split(",")
                    if is_valid_chord(c.strip())
                }
                song_chords = set(song_map)
                if not song_chords:
                    continue

                if chord_mode == "playable":
                    # every chord in the song is one the player knows
                    if song_chords.issubset(requested_chords):
                        matching_pks.append(pk)

                elif chord_mode == "almost":
                    # song needs 1 (ALMOST_MAX_MISSING) chord(s) the player
                    # doesn't know yet; fully playable songs are NOT included
                    missing = song_chords - requested_chords
                    if 1 <= len(missing) <= self.ALMOST_MAX_MISSING:
                        matching_pks.append(pk)
                        self.almost_missing[pk] = sorted(song_map[k] for k in missing)

                else:  # contains
                    if requested_chords.issubset(song_chords):
                        matching_pks.append(pk)

            qs = qs.filter(pk__in=matching_pks)

        # 🆕 Filter by NUMBER of chords used (2, 3, 4, 5, or "gt5" meaning >5)
        chord_count_filter = self.filter_params.get("chord_count", "").strip()
        if chord_count_filter:
            matching_pks = []
            for pk, chords_used in qs.values_list("pk", "chords_used"):
                # Only count real chords - excludes [N.C.] and any junk tokens
                valid_chords = {
                    c.strip() for c in (chords_used or "").split(",")
                    if is_valid_chord(c.strip())
                }
                count = len(valid_chords)

                if chord_count_filter == "gt5":
                    if count > 5:
                        matching_pks.append(pk)
                else:
                    try:
                        target = int(chord_count_filter)
                    except ValueError:
                        target = None
                    if target is not None and count == target:
                        matching_pks.append(pk)

            qs = qs.filter(pk__in=matching_pks)

        # 🆕 Filter by decade (e.g. "1980" means 1980-1989)
        decade_filter = self.filter_params.get("decade", "").strip()
        if decade_filter:
            try:
                decade_start = int(decade_filter)
            except ValueError:
                decade_start = None

            if decade_start is not None:
                decade_end = decade_start + 9
                matching_pks = []
                for pk, metadata in qs.values_list("pk", "metadata"):
                    year_str = (metadata or {}).get("year")
                    if year_str:
                        try:
                            year = int(year_str)
                        except (ValueError, TypeError):
                            continue
                        if decade_start <= year <= decade_end:
                            matching_pks.append(pk)
                qs = qs.filter(pk__in=matching_pks)

        # 🆕 Filter by musical key (manual {key:} tag if set, else auto-detected)
        key_filter = self.filter_params.get("key", "").strip()
        if key_filter:
            matching_pks = []
            for pk, metadata, detected_key in qs.values_list("pk", "metadata", "detected_key"):
                manual_key = (metadata or {}).get("key")
                effective_key = manual_key if manual_key else detected_key
                if effective_key == key_filter:
                    matching_pks.append(pk)
            qs = qs.filter(pk__in=matching_pks)

        # 🆕 PERFORMANCE: no .distinct(). Nothing above can produce duplicate
        # rows (formatted uses pk__in, tag/exclude match one row per song), and
        # DISTINCT over full rows (incl. songChordPro + JSON) cost ~1s here.
        return qs
    
    

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        # Remember the last view used — but not for a "Songs by <artist>" page
        if not self.kwargs.get("artist_name"):
            response.set_cookie(
                self.VIEW_COOKIE,
                self.view_mode,
                max_age=self.VIEW_COOKIE_MAX_AGE,
                samesite="Lax",
            )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_name = self.get_site_name()
        context["selected_artist"] = self.kwargs.get("artist_name")
        context["search_query"] = self.filter_params.get("q", "")
        context["selected_tag"] = self.filter_params.get("tag", "")
        context["show_formatted"] = self.filter_params.get("formatted") == "1"
        context["view_mode"] = self.view_mode
        # The cookie is only sent back with the NEXT request, so also tell the
        # navbar which view this page is. (Not on artist pages: they're always
        # the extended layout and shouldn't change the remembered choice.)
        if not self.kwargs.get("artist_name"):
            context["song_view_pref"] = self.view_mode
        context["list_url_suffix"] = self.list_url_suffix

        # 🆕 Preferred teleprompter style: instead of two columns (one per
        # style), send the user straight to whichever style they prefer.
        # A link to switch styles lives on the teleprompter page itself.
        # Defaults to "inline" (chord symbols) for anonymous users and
        # anyone who hasn't set a preference yet.
        if self.request.user.is_authenticated:
            preferences, _ = UserPreference.objects.get_or_create(user=self.request.user)
            teleprompter_style = getattr(preferences, "teleprompter_style", "inline")
        else:
            teleprompter_style = "inline"
        context["teleprompter_style"] = teleprompter_style
        context["teleprompter_url_name"] = (
            "teleprompter:teleprompter_beginner"
            if teleprompter_style == "beginner"
            else "teleprompter:teleprompter"
        )


        # 🆕 Alphabet filter (A-Z + # for numbers/symbols)
        context["alphabet_filter"] = list(string.ascii_uppercase) + ["#"]
        context["selected_letter"] = self.filter_params.get("letter", "").strip().upper()

        # Tags
        if self.request.user.is_authenticated:
            site_songs = Song.objects.filter(site_name=site_name).filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            site_songs = Song.objects.filter(site_name=site_name, is_public=True)

        all_tags = Tag.objects.filter(song__in=site_songs).distinct().values_list("name", flat=True)
        context["all_tags"] = all_tags

        # 🆕 All unique chords across the site for the clickable buttons
        # In get_context_data():
        # 🆕 PERFORMANCE: one lightweight query feeds the chord, decade and
        # key filter buttons below. values_list() fetches only these three
        # columns, so we no longer load every visible song in full
        # (songChordPro + lyrics_with_chords JSON) three separate times.
        all_chords = set()
        all_decades = set()
        all_keys = set()
        all_origins = set()
        for chords_used, metadata, detected_key, origin in site_songs.values_list(
            "chords_used", "metadata", "detected_key", "origin"
        ):
            metadata = metadata or {}

            # Origins (clubs)
            if origin:
                all_origins.add(origin)

            # Chords
            if chords_used:
                for chord in chords_used.split(","):
                    chord = chord.strip()
                    if is_valid_chord(chord):
                        all_chords.add(chord)

            # Decades
            year_str = metadata.get("year")
            if year_str:
                try:
                    all_decades.add((int(year_str) // 10) * 10)
                except (ValueError, TypeError):
                    pass

            # Keys: manual {key:} tag if set, else auto-detected
            # (same rule as Song.effective_key)
            effective_key = metadata.get("key") or detected_key
            if effective_key:
                all_keys.add(effective_key)

        context["all_chords"] = sorted(all_chords)
        context["chord_filter"] = self.filter_params.get("chords", "")
        # 🆕 URL-safe copy for building filter links: a raw "F#m" in an href
        # starts a URL fragment at "#" and silently drops every later parameter.
        context["chord_filter_qs"] = quote(self.filter_params.get("chords", ""), safe="")
        context["chord_mode"] = self.filter_params.get("chord_mode", "playable")

        # 🆕 Chord-count filter
        context["chord_count_choices"] = [
            {"value": "2", "label": "2"},
            {"value": "3", "label": "3"},
            {"value": "4", "label": "4"},
            {"value": "5", "label": "5"},
            {"value": "gt5", "label": ">5"},
        ]
        context["chord_count_filter"] = self.filter_params.get("chord_count", "")

        # 🆕 Decade filter — only offer decades that actually have songs
        # (all_decades is collected in the single pass above)
        context["all_decades"] = sorted(all_decades)
        context["decade_filter"] = self.filter_params.get("decade", "")

        # 🆕 Key filter — only offer keys that actually appear (using effective_key:
        # manual {key:} tag if set, else the auto-detected key)
        # (all_keys is collected in the single pass above)
        context["all_keys"] = sorted(all_keys)
        context["key_filter"] = self.filter_params.get("key", "")

        # 🆕 Origin (club) filter — only offer origins that actually have songs
        # (all_origins is collected in the single pass above)
        context["all_origins"] = sorted(all_origins)
        context["origin_filter"] = self.filter_params.get("origin", "")

        # 🆕 Group songs into "families" — one row per distinct title, with
        # other same-titled versions (different club/contributor origins)
        # tucked underneath. Grouped by normalized title since cloned_from
        # is reserved for personal tweaks, not club-origin variants, so it
        # can't be relied on to link these versions together.
        families = OrderedDict()
        for song in context["songs"]:
            key = (song.songTitle or "").strip().lower()
            families.setdefault(key, []).append(song)

        def pick_primary(songs_in_family):
            for s in songs_in_family:
                if (s.origin or "").strip().upper() == "NBU":
                    return s
            # No NBU version: fall back to the oldest (lowest id = added
            # first; date_posted isn't reliable here since it gets bumped
            # forward on every content edit).
            return min(songs_in_family, key=lambda s: s.id)

        family_list = []
        for songs_in_family in families.values():
            primary = pick_primary(songs_in_family)
            other_versions = [s for s in songs_in_family if s.id != primary.id]
            family_list.append({
                "primary": primary,
                "other_versions": other_versions,
                "version_count": len(songs_in_family),
            })
        family_list.sort(key=lambda f: (f["primary"].songTitle or "").strip().lower())

        # 🆕 "Learn one more chord" suggestions (almost mode only): for each
        # missing chord, how many song FAMILIES it would unlock. Counted per
        # family so several versions of one song don't inflate the number.
        # Each suggestion links to the same page with that chord added to the
        # player's chords and the mode switched to "playable".
        context["almost_mode"] = bool(self.almost_missing)
        unlock_counter = Counter()
        for songs_in_family in families.values():
            family_missing = set()
            for s in songs_in_family:
                family_missing.update(self.almost_missing.get(s.id, []))
            unlock_counter.update(family_missing)

        unlock_suggestions = []
        for chord, count in unlock_counter.most_common(8):
            params = self.filter_params.copy()
            params["chords"] = ",".join(self.requested_chords_list + [chord])
            params["chord_mode"] = "playable"
            if "page" in params:
                del params["page"]
            unlock_suggestions.append({
                "chord": chord,
                "count": count,
                "url": "?" + params.urlencode(),
            })
        context["unlock_suggestions"] = unlock_suggestions

        # 🆕 Manual pagination over families, not raw Song rows, so a
        # family never gets split awkwardly across two pages.
        paginator = Paginator(family_list, self.FAMILIES_PER_PAGE)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()

        # 🆕 PERFORMANCE: fetch tags and "is formatted" for ALL songs on this
        # page in two queries, instead of two queries per song.
        page_songs = []
        for family in page_obj.object_list:
            page_songs.append(family["primary"])
            page_songs.extend(family["other_versions"])
        prefetch_related_objects(page_songs, "tags")
        formatted_ids = set(
            SongFormatting.objects.filter(
                song_id__in=[s.id for s in page_songs]
            ).values_list("song_id", flat=True)
        )

        def build_row_data(song):
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            chords = [c for c in chords if is_valid_chord(c)]  # 🆕 drop N.C. and other non-chord tokens
            tags = [tag.name for tag in song.tags.all()]  # prefetched above
            is_formatted = song.id in formatted_ids
            return {
                "song": song,
                "chords": ", ".join(chords),
                # 🆕 "almost" mode only: chords the player still needs for this song
                "missing_chords": ", ".join(self.almost_missing.get(song.id, [])),
                "tags": ", ".join(tags),
                "is_formatted": is_formatted,
            }

        # Song data — only for this page's families. Each entry carries its
        # own full row data PLUS the same row data for every other version
        # in its family, so the template can render a complete row (artist,
        # year, tags, chords, PDF, teleprompter) for every version, not just
        # the primary one.
        song_data = []
        for family in page_obj.object_list:
            primary_data = build_row_data(family["primary"])
            primary_data["other_versions"] = [
                build_row_data(v) for v in family["other_versions"]
            ]
            primary_data["version_count"] = family["version_count"]
            song_data.append(primary_data)

        context["song_data"] = song_data
        return context


# -------------------------------------------------------------
# Simple view: same filters as SongListView, but fewer columns and
# ONLY formatted songs — the friendly list for everyday members.
# -------------------------------------------------------------
class SongListSimpleView(SongListView):
    template_name = "songbook/song_list_simple.html"
    view_mode = "simple"
    list_url_suffix = ":song_list_simple"
    formatted_only = True