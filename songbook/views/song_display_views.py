# songbook/views/song_display_views.py

from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q, prefetch_related_objects
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.utils import timezone
from types import SimpleNamespace
import re
import string
from urllib.parse import quote, urlencode

from collections import Counter, OrderedDict
from django.core.paginator import Paginator

from songbook.mixins import SiteContextMixin
from songbook.context_processors import site_context
from songbook.models import Song, SongFormatting
from songbook.utils.transposer import extract_chords
from taggit.models import Tag
from users.models import UserPreference
from ratings.utils import face_icon, rating_mine, rating_summaries  # ⭐ song ratings (optional 'ratings' app)

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

        # Same rule as SongUpdateView.test_func: staff, anyone with the
        # change_song permission (the Songbook Editors group), or the contributor
        user = self.request.user
        context["can_edit"] = user.is_authenticated and (
            user.is_staff
            or user.has_perm("songbook.change_song")
            or user == self.object.contributor
        )

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
    #   simple view   (SongListSimpleView): fewer columns, same songs
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

    # 🆕 PERFORMANCE / BOTS: crawlers don't keep cookies, so saving "last used
    # filters" for them just fills the django_session table with junk rows
    # (one per request). Any user agent containing one of these words is
    # treated as a bot and doesn't get a session saved.
    BOT_MARKERS = ("bot", "crawler", "spider", "externalagent")

    # 🆕 PERFORMANCE: how long the filter-button data (chords, decades, keys,
    # origins, tags) is cached. A newly added song shows up in the buttons
    # within this many seconds.
    FILTER_OPTIONS_CACHE_SECONDS = 600  # 10 minutes

    def _in_season(self):
        return timezone.now().month == self.SEASONAL_MONTH

    def _looks_like_bot(self):
        ua = self.request.META.get("HTTP_USER_AGENT", "").lower()
        return any(marker in ua for marker in self.BOT_MARKERS)

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
        #                          page: save it as the new "last used"
        #                          (but not for bots - see BOT_MARKERS).
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
            # 🆕 Bots still get the filtered page, but nothing is written
            # to the session table for them.
            if not self._looks_like_bot():
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
        #
        # 🆕 PERFORMANCE: load only the three columns needed to group songs
        # into families (id, title, origin). The big fields (songChordPro,
        # lyrics_with_chords, metadata...) are NOT loaded for the whole
        # songbook any more; get_context_data loads them again, but only for
        # the ~20 families shown on the current page.
        return qs.only("id", "songTitle", "origin")
    
    

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

    # -------------------------------------------------------------
    # 🆕 PERFORMANCE: data for the filter buttons (tags, chords, decades,
    # keys, origins). It only changes when songs are added or edited, so it
    # is built once and cached instead of being rebuilt on every page load.
    #
    # The cache key includes the site and the user, because logged-in
    # members also see their own private songs (so their buttons can differ).
    # -------------------------------------------------------------
    def get_filter_options(self, site_name):
        if self.request.user.is_authenticated:
            user_part = f"user{self.request.user.id}"
        else:
            user_part = "anon"
        safe_site = str(site_name).replace(" ", "_")
        cache_key = f"songlist_filter_options:{safe_site}:{user_part}"

        options = cache.get(cache_key)
        if options is not None:
            return options

        # Cache miss: build everything (this is the old per-request code)
        if self.request.user.is_authenticated:
            site_songs = Song.objects.filter(site_name=site_name).filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            site_songs = Song.objects.filter(site_name=site_name, is_public=True)

        # Same tags as before, but without a subquery on the song table
        # (this cut the query from ~159 ms to ~4 ms locally). Everything is in
        # ONE filter() call so the conditions apply to the same song.
        if self.request.user.is_authenticated:
            visible = Q(song__is_public=True) | Q(song__contributor=self.request.user)
        else:
            visible = Q(song__is_public=True)

        all_tags = list(
            Tag.objects.filter(visible, song__site_name=site_name)
            .distinct()
            .values_list("name", flat=True)
        )

        # One lightweight query feeds the chord, decade, key and origin
        # buttons. values_list() fetches only these four columns, so we
        # never load songChordPro / lyrics_with_chords JSON here.
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

        options = {
            "all_tags": all_tags,
            "all_chords": sorted(all_chords),
            "all_decades": sorted(all_decades),
            "all_keys": sorted(all_keys),
            "all_origins": sorted(all_origins),
        }
        cache.set(cache_key, options, self.FILTER_OPTIONS_CACHE_SECONDS)
        return options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_name = self.get_site_name()
        context["selected_artist"] = self.kwargs.get("artist_name")
        context["search_query"] = self.filter_params.get("q", "")
        context["selected_tag"] = self.filter_params.get("tag", "")
        context["show_formatted"] = self.filter_params.get("formatted") == "1"
        # 🆕 How many filters are switched on (the search box doesn't count: it is
        # always visible). Shown as a badge on the mobile "Filters" button so a
        # collapsed filter panel never hides the fact that the list is filtered.
        filter_keys = ("tag", "letter", "chords", "chord_count", "decade", "key", "origin")
        active_filters = sum(1 for k in filter_keys if self.filter_params.get(k, "").strip())
        if self.view_mode != "simple" and self.filter_params.get("formatted") == "1":
            active_filters += 1
        context["active_filter_count"] = active_filters
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

        # 🆕 PERFORMANCE: tags, chords, decades, keys and origins for the
        # filter buttons come from the cache (see get_filter_options above).
        options = self.get_filter_options(site_name)
        context["all_tags"] = options["all_tags"]
        context["all_chords"] = options["all_chords"]
        context["all_decades"] = options["all_decades"]
        context["all_keys"] = options["all_keys"]
        context["all_origins"] = options["all_origins"]

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

        # 🆕 Decade filter — only offers decades that actually have songs
        context["decade_filter"] = self.filter_params.get("decade", "")

        # 🆕 Key filter — only offers keys that actually appear (using effective_key:
        # manual {key:} tag if set, else the auto-detected key)
        context["key_filter"] = self.filter_params.get("key", "")

        # 🆕 Origin (club) filter — only offers origins that actually have songs
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
        def title_key(f):
            return (f["primary"].songTitle or "").strip().lower()

        # ⭐ Optional sort: ?sort=rating puts the best-rated songs first.
        # Unrated songs go last; ties are broken by number of votes, then title.
        # Only here do we need ratings for EVERY song (one grouped query);
        # otherwise just the current page's songs are looked up further down.
        sort = "rating" if self.filter_params.get("sort") == "rating" else ""
        all_summaries = None
        if sort == "rating":
            all_summaries = rating_summaries()

            def rating_key(f):
                summary = all_summaries.get(f["primary"].id)
                avg = summary["avg"] if summary else None
                votes = summary["n"] if summary else 0
                return (avg is None, -(avg or 0), -votes, title_key(f))

            family_list.sort(key=rating_key)
        else:
            family_list.sort(key=title_key)

        # ⭐ Links for the sortable "Rating" column header (keep every other filter)
        def sort_url(value):
            params = self.filter_params.copy()
            if "page" in params:
                del params["page"]
            if value:
                params["sort"] = value
            elif "sort" in params:
                del params["sort"]
            return "?" + params.urlencode()

        context["sort"] = sort
        context["sort_by_rating_url"] = sort_url("rating")
        context["sort_by_title_url"] = sort_url("")

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

        # 🆕 PERFORMANCE: the songs grouped above are lightweight (see the end
        # of get_queryset). Reload FULL rows for only the songs on this page,
        # in one query, and put them in place of the lightweight ones.
        shown_ids = []
        for family in page_obj.object_list:
            shown_ids.append(family["primary"].id)
            shown_ids.extend(v.id for v in family["other_versions"])
        full_songs = Song.objects.in_bulk(shown_ids)
        for family in page_obj.object_list:
            family["primary"] = full_songs.get(family["primary"].id, family["primary"])
            family["other_versions"] = [
                full_songs.get(v.id, v) for v in family["other_versions"]
            ]

        # 🆕 PERFORMANCE: fetch tags for ALL songs on this page in one query,
        # instead of one query per song.
        page_songs = []
        for family in page_obj.object_list:
            page_songs.append(family["primary"])
            page_songs.extend(family["other_versions"])
        prefetch_related_objects(page_songs, "tags")

        # ⭐ Ratings for the songs on this page: one query (already have them if sorting)
        page_ids = [s.id for s in page_songs]
        summaries = all_summaries if all_summaries is not None else rating_summaries(page_ids)
        mine = rating_mine(page_ids, self.request.user)  # the logged-in user's own ratings

        def build_row_data(song):
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            chords = [c for c in chords if is_valid_chord(c)]  # 🆕 drop N.C. and other non-chord tokens
            tags = [tag.name for tag in song.tags.all()]  # prefetched above
            return {
                "song": song,
                "chords": ", ".join(chords),
                # 🆕 "almost" mode only: chords the player still needs for this song
                "missing_chords": ", ".join(self.almost_missing.get(song.id, [])),
                "tags": ", ".join(tags),
                # ⭐ ratings (average, number of votes, nearest face icon)
                "avg_rating": (summaries.get(song.id) or {}).get("avg"),
                "rating_count": (summaries.get(song.id) or {}).get("n", 0),
                "rating_face": face_icon((summaries.get(song.id) or {}).get("avg")),
                "avg_play": (summaries.get(song.id) or {}).get("avg_play"),
                "avg_sing": (summaries.get(song.id) or {}).get("avg_sing"),
                "my_rating": mine.get(song.id),
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
# Simple view: same filters and songs as SongListView, but fewer columns —
# the friendly list for everyday members. (Unformatted songs are tracked on
# the editors' songs_to_format page, not by hiding them here.)
# -------------------------------------------------------------
class SongListSimpleView(SongListView):
    template_name = "songbook/song_list_simple.html"
    view_mode = "simple"
    list_url_suffix = ":song_list_simple"


# -------------------------------------------------------------
# Editors' to-do list: songs that have no formatting yet.
# "Not formatted" uses the same rule as the song list's "formatted" filter
# (no SongFormatting row for the song), just inverted.
# Login required, and only staff / people with the change_song permission
# (same rule as editing a song), so crawlers can never reach it.
# -------------------------------------------------------------
class SongsToFormatView(LoginRequiredMixin, UserPassesTestMixin, SiteContextMixin, ListView):
    model = Song
    template_name = "songbook/songs_to_format.html"
    context_object_name = "songs"
    paginate_by = 50

    # value used in the URL -> label shown in the dropdown
    CHORD_COUNT_CHOICES = [
        ("le1", "0–1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("gt10", ">10"),
    ]
    NO_ORIGIN = "none"  # URL value for songs that have no origin

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.has_perm("songbook.change_song")

    @staticmethod
    def _chord_bucket(chords_used):
        """Number of real chords in the song, as one of the choice values."""
        count = len({
            c.strip() for c in (chords_used or "").split(",")
            if is_valid_chord(c.strip())
        })
        if count <= 1:
            return "le1"
        if count > 10:
            return "gt10"
        return str(count)

    def get_queryset(self):
        user = self.request.user
        base = (
            Song.objects.filter(site_name=self.get_site_name())
            .filter(Q(is_public=True) | Q(contributor=user))
            .exclude(pk__in=SongFormatting.objects.values("song_id"))
        )

        # Filter persistence: remember the last filters used on this site, so
        # coming back to the bare URL (e.g. after formatting a song) restores them.
        #   ?reset=1                  -> "Clear filters": forget the saved ones
        #   ?origin=... / ?chord_count=... -> the user just changed a filter: save it
        #   anything else (bare URL, or only ?page=2) -> use the saved filters
        session_key = f"songs_to_format_filters:{self.get_site_name()}"
        GET = self.request.GET
        if GET.get("reset") == "1":
            self.request.session.pop(session_key, None)
            filter_params = QueryDict("")
        elif "origin" in GET or "chord_count" in GET:
            filter_params = GET
            self.request.session[session_key] = urlencode({
                "origin": GET.get("origin", ""),
                "chord_count": GET.get("chord_count", ""),
            })
        else:
            filter_params = QueryDict(self.request.session.get(session_key, ""))

        origin = filter_params.get("origin", "").strip()
        chord_count = filter_params.get("chord_count", "").strip()
        if chord_count not in dict(self.CHORD_COUNT_CHOICES):
            chord_count = ""  # ignore junk in the URL





        self.origin_filter = origin
        self.chord_count_filter = chord_count

        # One lightweight query (3 columns, no lyrics) feeds the filtering AND
        # the numbers shown in the dropdowns.
        origin_display = {}          # lowercase origin -> spelling to show
        origin_counts = Counter()    # songs per origin (respecting the chord filter)
        chord_counts = Counter()     # songs per chord bucket (respecting the origin filter)
        matching_pks = []
        total = 0

        for pk, song_origin, chords_used in base.values_list("pk", "origin", "chords_used"):
            total += 1
            song_origin = (song_origin or "").strip()
            origin_key = song_origin.lower() or self.NO_ORIGIN
            origin_display.setdefault(origin_key, song_origin or "—")
            bucket = self._chord_bucket(chords_used)

            origin_ok = not origin or origin_key == origin.lower()
            chords_ok = not chord_count or bucket == chord_count

            if chords_ok:
                origin_counts[origin_key] += 1
            if origin_ok:
                chord_counts[bucket] += 1
            if origin_ok and chords_ok:
                matching_pks.append(pk)

        self.total_to_format = total
        self.origin_choices = [
            {"value": origin_display[k], "label": origin_display[k], "count": origin_counts.get(k, 0)}
            for k in sorted(origin_display, key=lambda k: origin_display[k].lower())
        ]
        # the "no origin" entry needs a URL value that can't clash with a real club
        for choice in self.origin_choices:
            if choice["value"] == "—":
                choice["value"] = self.NO_ORIGIN
        self.chord_count_choices = [
            {"value": v, "label": label, "count": chord_counts.get(v, 0)}
            for v, label in self.CHORD_COUNT_CHOICES
        ]

        qs = base
        if origin or chord_count:
            qs = qs.filter(pk__in=matching_pks)
        return qs.only("id", "songTitle", "origin", "metadata").order_by("songTitle")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["origin_filter"] = self.origin_filter
        context["chord_count_filter"] = self.chord_count_filter
        context["origin_choices"] = self.origin_choices
        context["chord_count_choices"] = self.chord_count_choices
        context["total_to_format"] = self.total_to_format
        context["filters_active"] = bool(self.origin_filter or self.chord_count_filter)

        # Keeps the filters when moving between pages: href="?{{ filter_qs }}page=2"
        params = {}
        if self.origin_filter:
            params["origin"] = self.origin_filter
        if self.chord_count_filter:
            params["chord_count"] = self.chord_count_filter
        context["filter_qs"] = (urlencode(params) + "&") if params else ""
        return context