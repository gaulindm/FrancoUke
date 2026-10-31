/*
 * "Take a chance" - one-click ChordPro tidy-up for the song form.
 *
 * Nothing changes until you press Apply in the preview window, and Apply is
 * one editor change, so Ctrl-Z undoes the whole cleanup. Nothing is saved
 * until you press Update on the form.
 *
 * What it does:
 *   - gathers the header directives into one block at the top (title and artist
 *     first), in a standard order; KEEPS empty directives
 *   - drops an empty directive only when the same directive also has a value
 *   - REMOVES the tags this club never uses: {album:}, {recording:}, {tempo:}
 *   - moves any YouTube link on its own line (header or body, with or without
 *     https://, or a comment holding only a link) into {youtube: ...}
 *   - strips trailing spaces (the single-space gap lines are left alone)
 *   - tidies header comments:  {c: Thanks}  ->  {c:Thanks}
 *   - empty comments {c: } become single-space gap lines
 *   - songs with NO section tags: blank lines become single-space gap lines
 *   - collapses repeated blank lines
 *   - puts a single-space gap line before and after lines that hold only chords
 *     (intro / outro / interlude), outside {so?}...{eo?} sections
 *   - a comment that starts with "Thanks" ({c:Thanks to Susan McCarthy}) is an
 *     acknowledgement: it moves into the Acknowledgement field and leaves the text
 *   - never adds section tags
 * It also offers two form-field changes (shown in the preview):
 *   - Song title written with dashes (Dont-Stand-So-Close-To-Me) -> spaces. Only
 *     done when the title has dashes and NO spaces, so normal titles are untouched.
 *   - A checkbox to set Origin to OZBCOZ (ticked when Origin is empty).
 *
 * It only REPORTS (never changes): title missing its apostrophe, the same
 * chord twice in a row, unrecognised {tags}, and YouTube links buried in text.
 */
(function () {
    "use strict";
  
    // Origin code offered by the preview's checkbox.
    var ORIGIN_CODE = "OZBCOZ";
  
    // Output order of the header block (display names keep their capitals).
    var HEADER_NAMES = [
      "title", "artist", "youtube", "songwriter", "capo", "key",
      "year", "1stnote", "timeSignature",
      "strumming", "count_in", "short_instruction_1", "short_instruction_2",
      "suggested_alternate"
    ];
    var HEADER_LOOKUP = {};
    HEADER_NAMES.forEach(function (n) { HEADER_LOOKUP[n.toLowerCase()] = n; });
    HEADER_LOOKUP["t"] = "title"; // {t:...} is the short form of {title:...}
  
    // Tags this club never uses: removed wherever they appear.
    var REMOVE = { album: true, recording: true, tempo: true };
  
    // Tags the app knows; anything else is reported as "unrecognised".
    var KNOWN = {};
    HEADER_NAMES.concat([
      "t", "c", "comment", "ci", "cb", "x_strumming", "subtitle", "st",
      "sov", "eov", "soc", "eoc", "sob", "eob", "soi", "eoi", "soo", "eoo",
      "sot", "eot", "sog", "eog",
      "start_of_verse", "end_of_verse", "start_of_chorus", "end_of_chorus",
      "start_of_bridge", "end_of_bridge", "start_of_tab", "end_of_tab",
      "define", "chord", "new_page", "np", "new_song", "ns", "column_break", "colb"
    ]).forEach(function (n) { KNOWN[n.toLowerCase()] = true; });
  
    var DIRECTIVE_RE = /^\s*\{\s*([A-Za-z0-9_]+)\s*(?::\s*(.*?))?\s*\}\s*$/;
    var BARE_URL_RE = /^\s*(https?:\/\/\S+)\s*$/i;
    // A line that is only a YouTube link (https:// optional).
    var YT_BARE_RE = /^\s*((?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com|youtu\.be)\/\S+)\s*$/i;
    var SECTION_START_RE = /^(so[vcbiot]|sog|start_of_\w+)$/i;
    var EMPTY_COMMENT_RE = /^\s*\{\s*(?:c|comment)\s*:\s*\}\s*$/i;
    var MISSING_APOSTROPHE_RE =
      /\b(dont|cant|isnt|arent|didnt|doesnt|wasnt|couldnt|wouldnt|shouldnt|hasnt|havent|im|ive|youre|theyre)\b/i;
  
    function parseDirective(line) {
      var m = DIRECTIVE_RE.exec(line);
      if (!m) return null;
      return { name: m[1], value: (m[2] || "").trim(), line: line.trim() };
    }
  
    // YouTube link held by a whole line, or by a comment that holds nothing else.
    function ytFromLine(line) {
      var m = YT_BARE_RE.exec(line);
      if (!m) {
        var d = parseDirective(line);
        if (d && /^(c|comment)$/i.test(d.name) && d.value) m = YT_BARE_RE.exec(d.value);
      }
      if (!m) return null;
      return /^https?:\/\//i.test(m[1]) ? m[1] : "https://" + m[1];
    }
  
    // ---- Chord-only lines (intro / outro / interlude) -------------------------
    var CHORD_TOKEN_RE = new RegExp(
      "^\\*?(?:[A-G][#b]?(?:maj|min|dim|aug|sus|add|m|M|o|\\+)?[0-9]*(?:sus[0-9]|add[0-9])?" +
      "(?:[-#b][0-9])?(?:\\/[A-G][#b]?)?\\/*|N\\.?C\\.?)$"
    );
    var SECTION_END_RE = /^(eo[vcbiot]|eog|end_of_\w+)$/i;
  
    function bracketIsChords(content) {
      var tokens = content.split(/\s*-\s*|\s+/).filter(Boolean);
      return tokens.length > 0 && tokens.every(function (t) { return CHORD_TOKEN_RE.test(t); });
    }
  
    // True for lines such as "[G] [D] [C] [G]" or "[F - Dm7] [G///]" with no words.
    function isChordOnly(line) {
      if (parseDirective(line)) return false;
      var t = line.trim();
      if (!t) return false;
      var re = /\[([^\]]*)\]/g, m, n = 0;
      while ((m = re.exec(t))) {
        if (!bracketIsChords(m[1])) return false;
        n++;
      }
      if (!n) return false;
      return t.replace(/\[[^\]]*\]/g, "").replace(/[\s\-|\/]/g, "") === "";
    }
  
    function isCommentLine(line) {
      var d = parseDirective(line);
      return !!d && /^(c|comment)$/i.test(d.name);
    }
  
    function isSectionTagLine(line) {
      var d = parseDirective(line);
      return !!d && (SECTION_START_RE.test(d.name) || SECTION_END_RE.test(d.name));
    }
  
    // Adds " " before and after each run of chord-only lines. Returns {lines, added}.
    function addChordLineGaps(lines, flags) {
      var n = lines.length, inSec = new Array(n), co = new Array(n), open = false;
      for (var i = 0; i < n; i++) {
        var d = parseDirective(lines[i]);
        if (d && SECTION_START_RE.test(d.name)) { open = true; inSec[i] = true; }
        else if (d && SECTION_END_RE.test(d.name)) { inSec[i] = true; open = false; }
        else inSec[i] = open;
        co[i] = !inSec[i] && isChordOnly(lines[i]);
      }
      var chordLines = co.filter(Boolean).length;
      var textLines = lines.filter(function (l) { return !isBlankish(l); }).length;
      if (chordLines > 4 && chordLines > 0.3 * textLines) {
        flags.push("Many lines hold only chords (chords above the lyrics?) - no gap lines were added around them.");
        return { lines: lines, added: 0 };
      }
      var before = new Array(n), after = new Array(n);
      for (i = 0; i < n; i++) {
        if (!co[i] || (i > 0 && co[i - 1])) continue;
        var s = i;                                   // start of the run
        if (s > 0 && !inSec[s - 1] && isCommentLine(lines[s - 1])) s--;   // keep a label such as {c:Intro} attached
        var e = i;
        while (e + 1 < n && co[e + 1]) e++;
        if (s > 0 && !isBlankish(lines[s - 1]) && !isSectionTagLine(lines[s - 1])) before[s] = true;
        if (e < n - 1 && !isBlankish(lines[e + 1]) && !isSectionTagLine(lines[e + 1])) after[e] = true;
      }
      var out = [], added = 0;
      for (i = 0; i < n; i++) {
        if (before[i]) { out.push(" "); added++; }
        out.push(lines[i]);
        if (after[i]) { out.push(" "); added++; }
      }
      return { lines: out, added: added };
    }
  
    function isBlankish(line) { return line.trim() === ""; }
  
    var ACK_RE = /^\s*\{\s*(?:c|comment)\s*:\s*(thanks\b[^}]*?)\s*\}\s*$/i;
    var ACK_MAX = 100;   // Song.acknowledgement max_length
  
    // opts.acknowledgement: current text of the Acknowledgement field, or null if the form has none.
    function analyze(raw, opts) {
      opts = opts || {};
      var changes = [];
      var flags = [];
      var lines = raw.replace(/\r\n?/g, "\n").split("\n");
  
      // 1. Trailing spaces. A line that is exactly " " is an intentional gap line.
      var stripped = 0;
      lines = lines.map(function (l) {
        if (l === " ") return l;
        var t = l.replace(/[ \t\u00a0\u200b]+$/, "");
        if (t !== l && t !== "") stripped++;
        return t;
      });
      if (stripped) changes.push("Removed trailing spaces from " + stripped + " line(s).");
  
      // 1b. "Thanks ..." comment = acknowledgement.
      var ack = null;
      var ackIdx = -1, extraThanks = 0;
      lines.forEach(function (l, i) {
        if (!ACK_RE.test(l)) return;
        if (ackIdx === -1) ackIdx = i; else extraThanks++;
      });
      if (ackIdx !== -1) {
        var thanks = ACK_RE.exec(lines[ackIdx])[1].replace(/\s+/g, " ").trim();
        var current = opts.acknowledgement;      // undefined/null = the form has no such field
        if (current === undefined || current === null) {
          // nothing to move it into: leave the comment where it is
        } else if (thanks.length > ACK_MAX) {
          flags.push("The Thanks comment is longer than " + ACK_MAX + " characters, so it was left in the text.");
        } else if (!current) {
          lines.splice(ackIdx, 1);
          ack = thanks;
          changes.push('Moved the comment into the Acknowledgement field: "' + thanks + '".');
        } else if (current.toLowerCase() === thanks.toLowerCase()) {
          lines.splice(ackIdx, 1);
          changes.push("Removed the Thanks comment (the Acknowledgement field already says the same).");
        } else {
          flags.push('Acknowledgement already reads "' + current + '", so the comment "' + thanks + '" was left in the text.');
        }
        if (extraThanks) flags.push(extraThanks + " other comment(s) starting with Thanks were left in the text - check them.");
      }
  
      // 2. Header zone = leading blanks, directives and bare links, up to the first lyric / section.
      var end = 0;
      while (end < lines.length) {
        var l = lines[end];
        if (isBlankish(l) || BARE_URL_RE.test(l) || YT_BARE_RE.test(l)) { end++; continue; }
        var d = parseDirective(l);
        if (d && !SECTION_START_RE.test(d.name)) { end++; continue; }
        break;
      }
      var zone = lines.slice(0, end);
      var body = lines.slice(end);
      var urls = [];              // YouTube links found anywhere
      var removed = [];           // unused tags that were removed
  
      var entries = {};           // canonical header name -> [{value, line}]
      var headerSeq = [];         // header directive lines in their original order
      var headerPositions = [];   // where they sat in the zone
      var rest = [];              // comments, unknown tags, non-YouTube links (kept, in order)
      var droppedEmptyComments = 0;
  
      zone.forEach(function (l, idx) {
        if (isBlankish(l)) return;
        var yt1 = ytFromLine(l);
        if (yt1) { urls.push(yt1); return; }
        if (BARE_URL_RE.test(l)) { rest.push(l.trim()); return; }
        var dr = parseDirective(l);
        if (dr && REMOVE[dr.name.toLowerCase()]) { removed.push(dr); return; }
        if (EMPTY_COMMENT_RE.test(l)) { droppedEmptyComments++; return; }
        var d = parseDirective(l);
        var canon = d && HEADER_LOOKUP[d.name.toLowerCase()];
        if (canon) {
          (entries[canon] = entries[canon] || []).push({ value: d.value, line: d.line });
          headerSeq.push(d.line);
          headerPositions.push(idx);
        } else if (d && /^(c|comment)$/i.test(d.name) && d.value) {
          var tidy = "{" + d.name + ":" + d.value + "}";
          if (tidy !== d.line) changes.push("Tidied comment: " + d.line + "  ->  " + tidy);
          rest.push(tidy);
        } else {
          rest.push(l.trim());
        }
      });
      if (droppedEmptyComments) {
        changes.push("Removed " + droppedEmptyComments + " empty {c: } line(s) from the header area.");
      }
  
      // Pull YouTube-only lines and unused tags out of the body too
      // (after the header, so a header link wins when there are several).
      // Pull YouTube-only lines and unused tags out of the body too.
      body = body.filter(function (l) {
        var u = ytFromLine(l);
        if (u) { urls.push(u); return false; }
        var d = parseDirective(l);
        if (d && REMOVE[d.name.toLowerCase()]) { removed.push(d); return false; }
        return true;
      });
  
      if (removed.length) {
        var counts = {};
        removed.forEach(function (d) {
          var k = "{" + d.name.toLowerCase() + ":}";
          counts[k] = (counts[k] || 0) + 1;
        });
        changes.push("Removed unused tags: " + Object.keys(counts).map(function (k) {
          return k + (counts[k] > 1 ? " x" + counts[k] : "");
        }).join(", ") + ".");
        removed.filter(function (d) { return d.value; }).forEach(function (d) {
          changes.push("   (the removed " + d.line + " had a value - cancel if you want to keep it)");
        });
      }
  
      // An existing {youtube:} value without https:// would not be read by the parser.
      (entries["youtube"] || []).forEach(function (e) {
        if (e.value && !/^https?:\/\//i.test(e.value) && YT_BARE_RE.test(e.value)) {
          e.value = "https://" + e.value.replace(/^\/+/, "");
          e.line = "{youtube: " + e.value + "}";
          changes.push("Added https:// to the {youtube:} link.");
        }
      });
  
      var leftover = {};
  
      // 3. YouTube links found on their own line -> {youtube: ...}
      if (urls.length) {
        var yt = entries["youtube"] || [];
        var have = yt.filter(function (e) { return e.value; });
        var first = urls[0];
        if (!have.length) {
          entries["youtube"] = [{ value: first, line: "{youtube: " + first + "}" }];
          changes.push("Moved the YouTube link into {youtube: " + first + "}.");
          urls = urls.slice(1);
        } else {
          urls = urls.filter(function (u) {
            var same = have.some(function (e) { return e.value === u; });
            if (same) changes.push("Removed a loose YouTube link already held by {youtube:}.");
            return !same;
          });
        }
        urls.forEach(function (u) {
          leftover[u] = true;
          rest.push(u);
          flags.push("Extra YouTube link kept as a loose line (different from {youtube:}): " + u);
        });
      }
  
      // 4. Build the header block. Empty directives are KEPT; an empty one is dropped
      //    only when the same directive also has a value.
      var headerOut = [];
      var droppedDupes = 0;
      HEADER_NAMES.forEach(function (name) {
        var list = entries[name];
        if (!list || !list.length) return;
        var filled = list.filter(function (e) { return e.value; });
        var keep;
        if (!filled.length) {
          keep = [list[0]];
          droppedDupes += list.length - 1;
        } else {
          var seen = {};
          keep = filled.filter(function (e) {
            if (seen[e.value]) return false;
            seen[e.value] = true;
            return true;
          });
          droppedDupes += list.length - keep.length;
          if (keep.length > 1) flags.push("{" + name + ":} has " + keep.length + " different values - all kept, please check.");
        }
        keep.forEach(function (e) { headerOut.push(e.line); });
      });
      if (droppedDupes) {
        changes.push("Removed " + droppedDupes + " duplicate directive(s) (an empty one beside a filled-in one).");
      }
      var contiguous = headerPositions.length < 2 ||
        (headerPositions[headerPositions.length - 1] - headerPositions[0] + 1 === headerPositions.length);
      var sameOrder = headerSeq.length === headerOut.length &&
        headerSeq.every(function (x, i) { return x === headerOut[i]; });
      if (headerSeq.length && (!contiguous || !sameOrder)) {
        changes.push("Gathered the header directives into one block at the top, in standard order.");
      }
  
      // 5. Body: blank-line handling. Never adds section tags.
      var hasTags = body.some(function (l) {
        var d = parseDirective(l);
        return d && SECTION_START_RE.test(d.name);
      });
      var bodyOut = [];
      var kind = [];   // parallel to bodyOut: "comment" / "blank" for converted lines
      var emptyCommentsToGaps = 0, blanksToGaps = 0, collapsed = 0;
      body.forEach(function (l) {
        var k = "";
        if (EMPTY_COMMENT_RE.test(l)) { l = " "; k = "comment"; }
        else if (l === "" && !hasTags) { l = " "; k = "blank"; }
        else if (isBlankish(l) && l !== " ") { l = ""; }
        if (l === "" || l === " ") {
          if (!bodyOut.length) return;                       // no leading blanks
          if (bodyOut[bodyOut.length - 1] === l) { collapsed++; return; }
        }
        bodyOut.push(l);
        kind.push(k);
      });
      while (bodyOut.length && (bodyOut[bodyOut.length - 1] === "" || bodyOut[bodyOut.length - 1] === " ")) {
        bodyOut.pop();
        kind.pop();
      }
      kind.forEach(function (k) {
        if (k === "comment") emptyCommentsToGaps++;
        else if (k === "blank") blanksToGaps++;
      });
      var gaps = addChordLineGaps(bodyOut, flags);
      bodyOut = gaps.lines;
      if (gaps.added) {
        changes.push("Added " + gaps.added + " single-space gap line(s) before/after lines that hold only chords (intro/outro/interlude).");
      }
      if (emptyCommentsToGaps) changes.push("Turned " + emptyCommentsToGaps + " empty {c: } line(s) into single-space gap lines.");
      if (blanksToGaps) changes.push("No section tags in this song: changed " + blanksToGaps + " blank line(s) to single-space gap lines.");
      if (collapsed) changes.push("Collapsed " + collapsed + " repeated blank line(s).");
  
      // 6. Assemble: directives, blank, comments, blank, body.
      var out = [];
      if (headerOut.length) out = out.concat(headerOut);
      if (rest.length) { if (out.length) out.push(""); out = out.concat(rest); }
      if (bodyOut.length) { if (out.length) out.push(""); out = out.concat(bodyOut); }
      var text = out.join("\n");
  
      // 7. Report-only checks.
      var titleEntry = (entries["title"] || [])[0];
      if (!titleEntry) {
        flags.push("No {title:} directive found.");
      } else if (MISSING_APOSTROPHE_RE.test(titleEntry.value)) {
        flags.push("The title may be missing an apostrophe: " + titleEntry.value);
      }
  
      var unknown = {};
      var repeats = [];
      out.forEach(function (l) {
        var d = parseDirective(l);
        if (/(?:youtube\.com|youtu\.be)\//i.test(l) && !(d && d.name.toLowerCase() === "youtube") && !leftover[l.trim()]) {
          flags.push("A YouTube link sits inside other text and was not moved: " + l.trim().slice(0, 70));
        }
        if (d) {
          if (!KNOWN[d.name.toLowerCase()]) unknown[d.name] = true;
          return;
        }
        var prev = null;
        var re = /\[([^\]]+)\]/g, m;
        while ((m = re.exec(l))) {
          var chord = m[1].trim();
          if (prev !== null && chord === prev) {
            repeats.push(l.trim().slice(0, 70));
            break;
          }
          prev = chord;
        }
      });
      Object.keys(unknown).forEach(function (n) {
        flags.push("Unrecognised tag {" + n + "} - check the spelling.");
      });
      if (repeats.length) {
        repeats.slice(0, 5).forEach(function (r) {
          flags.push("Same chord twice in a row (typo?): " + r);
        });
        if (repeats.length > 5) flags.push("...and " + (repeats.length - 5) + " more lines with a repeated chord.");
      }
  
      return { text: text, ack: ack, changes: changes, flags: flags, changed: text !== raw.replace(/\r\n?/g, "\n") };
    }
  
    // "Dont-Stand-So-Close" -> "Dont Stand So Close". Returns null when no change is
    // needed. Only slug-style titles (dashes, no spaces) are touched.
    function fixTitle(value) {
      var v = (value || "").trim();
      if (!v || v.indexOf("-") === -1 || /\s/.test(v)) return null;
      var out = v.replace(/-+/g, " ").replace(/\s+/g, " ").trim();
      return out && out !== value ? out : null;
    }
  
    // ---- Preview window ------------------------------------------------------
    function esc(s) {
      return String(s).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }
  
    function list(items, empty) {
      if (!items.length) return "<p class='text-muted mb-0'>" + empty + "</p>";
      return "<ul class='mb-0'>" + items.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</ul>";
    }
  
    // extras: { titleChange: {from, to} | null, origin: {current} | null }
    function showPreview(result, extras, onApply) {
      var old = document.getElementById("take-a-chance-modal");
      if (old) old.remove();
      var wrap = document.createElement("div");
      wrap.innerHTML =
        '<div class="modal fade" id="take-a-chance-modal" tabindex="-1" aria-hidden="true">' +
        '<div class="modal-dialog modal-lg modal-dialog-scrollable"><div class="modal-content">' +
        '<div class="modal-header"><h5 class="modal-title">Take a chance - preview</h5>' +
        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div>' +
        '<div class="modal-body">' +
        "<h6>Changes it would make</h6>" + list(result.changes.concat(extras.titleChange
          ? ["Song title: " + extras.titleChange.from + "  ->  " + extras.titleChange.to] : []),
          "Nothing to change.") +
        (extras.origin
          ? '<div class="form-check mt-3"><input class="form-check-input" type="checkbox" id="take-a-chance-origin"' +
            (extras.origin.current ? "" : " checked") + '><label class="form-check-label" for="take-a-chance-origin">' +
            "Set Origin to " + ORIGIN_CODE + (extras.origin.current ? " (currently: " + esc(extras.origin.current) + ")" : "") +
            "</label></div>" : "") +
        "<h6 class='mt-3'>Please check (not changed)</h6>" + list(result.flags, "Nothing to flag.") +
        "<p class='small text-muted mt-3 mb-0'>Ctrl-Z undoes the ChordPro changes in the editor " +
        "(the title, origin and acknowledgement boxes are changed by hand if needed). Nothing is saved until you press Update.</p></div>" +
        '<div class="modal-footer">' +
        '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>' +
        '<button type="button" class="btn btn-primary" id="take-a-chance-apply"' +
        (result.changed || extras.titleChange || extras.origin ? "" : " disabled") + ">Apply</button></div></div></div></div>";
      document.body.appendChild(wrap.firstChild);
      var el = document.getElementById("take-a-chance-modal");
      var modal = new bootstrap.Modal(el);
      document.getElementById("take-a-chance-apply").addEventListener("click", function () {
        var box = document.getElementById("take-a-chance-origin");
        onApply({ setOrigin: !!(box && box.checked) });
        modal.hide();
      });
      el.addEventListener("hidden.bs.modal", function () { el.remove(); });
      modal.show();
    }
  
    function init() {
      var btn = document.getElementById("take-a-chance");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var ed = (typeof editor !== "undefined") ? editor : null;
        if (!ed) { alert("The editor is not ready yet."); return; }
        var ackEl = document.getElementById("id_acknowledgement");
        var result = analyze(ed.getValue(), { acknowledgement: ackEl ? ackEl.value.trim() : null });
        var titleEl = document.getElementById("id_songTitle");
        var originEl = document.getElementById("id_origin");
        var newTitle = titleEl ? fixTitle(titleEl.value) : null;
        var extras = {
          titleChange: newTitle ? { from: titleEl.value, to: newTitle } : null,
          origin: originEl && originEl.value.trim() !== ORIGIN_CODE ? { current: originEl.value.trim() } : null
        };
        showPreview(result, extras, function (choice) {
          if (result.changed) {
            var doc = ed.getDoc();
            var last = doc.lastLine();
            // One replaceRange = one undo step.
            doc.replaceRange(result.text, { line: 0, ch: 0 }, { line: last, ch: doc.getLine(last).length });
          }
          if (extras.titleChange) titleEl.value = extras.titleChange.to;
          if (result.ack && ackEl) ackEl.value = result.ack;
          if (choice.setOrigin && originEl) originEl.value = ORIGIN_CODE;
        });
      });
    }
  
    window.ChordProCleanup = { analyze: analyze, fixTitle: fixTitle };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  })();