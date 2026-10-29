/*
 * chordpro_tags.js  --  section-tag + clean-up helper for the CodeMirror 5 ChordPro editor
 *
 *  Usage (after creating the editor):   ChordProTags.attach(editor);
 *
 *  Section shortcuts (a new section closes the open one first):
 *    Alt-V  verse      {sov}      Alt-C  chorus     {soc}
 *    Alt-B  bridge     {sob}      Alt-I  intro      {soi}
 *    Alt-O  outro      {soo}      Alt-D  interlude  {sod}
 *    Alt-S  center (unlabelled)   {sos}
 *    Alt-E  close the last open section at the cursor   ({eov}, {eoc}, ...)
 *
 *  Clean-up:
 *    Alt-P  echoes: turns [Ooh.] into (Ooh.) -- every [ ] that is not a chord.
 *           Works on the selection if there is one, otherwise on the whole song.
 *           Also repairs damaged brackets such as [Un-der the (Em]board  ->  (Un-der the [Em]board
 *           and turns count cues [2,3,4] into {c:(234)}.
 *
 *  Workflow: put the cursor at the START of the first line of the next
 *  section and press Alt-V / Alt-C / ... At the end of the song press Alt-E.
 */
(function (root) {
    "use strict";
  
    var NAMES = { v: "Verse", c: "Chorus", b: "Bridge", i: "Intro", o: "Outro", d: "Interlude", s: "Center" };
    var KINDS = "icvbods";
  
    // ---- section tags ------------------------------------------------------
  
    // Which sections are open in `text`? (last one in the array = innermost)
    function openStack(text) {
      var re = new RegExp("\\{(so|eo)([" + KINDS + "])\\}", "g"), stack = [], m;
      while ((m = re.exec(text)) !== null) {
        if (m[1] === "so") {
          stack.push(m[2]);
        } else {
          var k = stack.lastIndexOf(m[2]);
          if (k > -1) stack.splice(k, 1);
        }
      }
      return stack;
    }
  
    // Text to insert at character offset `pos`, and where the caret should land.
    // action = "close" or one of the kinds (v c b i o d s).  Returns null if there is nothing to do.
    function computeInsert(value, pos, action) {
      var stack = openStack(value.slice(0, pos));
      var lines = [];
      if (action === "close") {
        if (!stack.length) return null;
        lines.push("{eo" + stack[stack.length - 1] + "}");
      } else {
        if (stack.length) { lines.push("{eo" + stack[stack.length - 1] + "}"); lines.push(""); }
        lines.push("{so" + action + "}");
      }
      var prev = pos > 0 ? value[pos - 1] : "\n";
      var next = pos < value.length ? value[pos] : "\n";
      var text = (prev !== "\n" ? "\n" : "") + lines.join("\n");
      var caret;
      if (next === "\n") {
        caret = pos + text.length + 1;   // land on the line after our last line
      } else {
        text += "\n";                    // cursor was in front of text: give the tag its own line
        caret = pos + text.length;
      }
      return { text: text, caret: caret };
    }
  
    // Works on any CodeMirror 5 editor. Returns false if nothing was inserted.
    function applyTo(cm, action) {
      var cursor = cm.getCursor();
      var pos = cm.indexFromPos(cursor);
      var res = computeInsert(cm.getValue(), pos, action);
      if (!res) return false;
      cm.replaceRange(res.text, cursor, cursor);       // one undo step
      var end = Math.min(res.caret, cm.getValue().length);
      cm.setCursor(cm.posFromIndex(end));
      return true;
    }
  
    // ---- echoes: [ ] that is not a chord  ->  ( ) ----------------------------
  
    var CHORD = "\\*?[A-G][#b]?(?:maj|min|dim|aug|sus|add|m|M|o|\\+)?\\d*(?:[b#+]\\d+)*" +
                "(?:sus\\d?|add\\d+)?(?:/(?:[A-G][#b]?|\\d))?\\*?/*";
    var CHORD_GROUP = new RegExp("^(?:" + CHORD + ")(?:\\s*-\\s*(?:" + CHORD + "))*$");
    var NO_CHORD = /^N\.?C\.?\s*\/*$/;
    var STRUM_ONLY = /^[\s\/\\x\-\d]*$/i;          // [/ - / - /], [x2], [] ... leave alone
  
    function isChord(inner) {
      var t = inner.trim();
      return CHORD_GROUP.test(t) || NO_CHORD.test(t) || STRUM_ONLY.test(t);
    }
  
    // Pure function: returns { text, repaired, converted, cues }.
    function convertEchoes(text) {
      var repaired = 0, converted = 0, cues = 0;
      // Only touch the parts of the text that are outside {...} directives.
      var parts = text.split(/(\{[^}\n]*\})/);
      for (var i = 0; i < parts.length; i += 2) {
        var p = parts[i];
        // 1. damaged brackets:  [Un-der the (Em]board-walk.)  ->  (Un-der the [Em]board-walk.)
        p = p.replace(/\[([^\]\[(\n]*)\(([A-G][#b]?[A-Za-z0-9+\/*]*)\]/g, function (m, pre, ch) {
          repaired++; return "(" + pre + "[" + ch + "]";
        });
        // 2. count cues:  [2,3,4]  ->  {c:(234)}
        p = p.replace(/[ \t]*\[(\d(?:\s*,\s*\d)+)\]/g, function (m, digits) {
          cues++; return " {c:(" + digits.replace(/\D/g, "") + ")}";
        });
        // 3. echoes:  [Ooh.]  ->  (Ooh.)
        p = p.replace(/\[([^\]\[\n]*)\]/g, function (m, inner) {
          if (isChord(inner)) return m;
          converted++; return "(" + inner + ")";
        });
        parts[i] = p;
      }
      return { text: parts.join(""), repaired: repaired, converted: converted, cues: cues };
    }
  
    // On the selection, or on the whole song when nothing is selected. One undo step.
    function applyEchoes(cm) {
      var sel = cm.somethingSelected(), from, to, text;
      if (sel) {
        from = cm.getCursor("from"); to = cm.getCursor("to"); text = cm.getRange(from, to);
      } else {
        var last = cm.lastLine();
        from = { line: 0, ch: 0 }; to = { line: last, ch: cm.getLine(last).length }; text = cm.getValue();
      }
      var res = convertEchoes(text);
      res.scope = sel ? "selection" : "song";
      if (!res.repaired && !res.converted && !res.cues) return res;
      var cur = cm.getCursor(), scroll = cm.getScrollInfo();
      cm.replaceRange(res.text, from, to);
      if (!sel) { cm.setCursor(cur); cm.scrollTo(scroll.left, scroll.top); }
      return res;
    }
  
    function echoMessage(res) {
      var bits = [];
      if (res.converted) bits.push(res.converted + " echo" + (res.converted > 1 ? "es" : "") + " changed to ( )");
      if (res.repaired) bits.push(res.repaired + " broken bracket" + (res.repaired > 1 ? "s" : "") + " repaired");
      if (res.cues) bits.push(res.cues + " count cue" + (res.cues > 1 ? "s" : "") + " converted");
      return bits.length ? bits.join(", ") + " (" + res.scope + ")" : "No echoes found (" + res.scope + ")";
    }
  
    // ---- editor integration ----------------------------------------------------
  
    function statusText(cm) {
      var before = cm.getRange({ line: 0, ch: 0 }, cm.getCursor());
      var s = openStack(before);
      return s.length
        ? "Open here: " + s.map(function (k) { return NAMES[k]; }).join(" > ")
        : "No open section";
    }
  
    function attach(cm) {
      var bar = document.createElement("div");
      bar.style.cssText = "margin:0 0 6px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;font:14px sans-serif";
      var status = document.createElement("span");
      status.style.cssText = "margin-left:8px;color:#555";
  
      function say(msg, bad) { status.textContent = msg; status.style.color = bad ? "#b00020" : ""; }
  
      function run(action) {
        var ok = applyTo(cm, action);
        cm.focus();
        if (ok) say(statusText(cm)); else say("No open section to close", true);
      }
      function runEchoes() {
        var res = applyEchoes(cm);
        cm.focus();
        say(echoMessage(res), !(res.converted || res.repaired || res.cues));
      }
      function button(label, title, fn) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "btn btn-sm btn-outline-secondary";
        b.textContent = label;
        b.title = title;
        b.addEventListener("mousedown", function (e) { e.preventDefault(); fn(); });
        bar.appendChild(b);
      }
      function sec(label, title, action) { button(label, title, function () { run(action); }); }
  
      sec("Close (Alt-E)", "Close the last open section at the cursor", "close");
      sec("Verse (Alt-V)", "Close the open section and start a verse", "v");
      sec("Chorus (Alt-C)", "Close the open section and start a chorus", "c");
      sec("Bridge (Alt-B)", "Close the open section and start a bridge", "b");
      sec("Intro (Alt-I)", "Start an intro", "i");
      sec("Outro (Alt-O)", "Close the open section and start an outro", "o");
      sec("Interlude (Alt-D)", "Close the open section and start an interlude", "d");
      sec("Center (Alt-S)", "Close the open section and start an unlabelled centered section", "s");
      button("Echoes [ ]\u2192( ) (Alt-P)",
             "Turn [ ] that is not a chord into ( ) in the selection, or in the whole song if nothing is selected",
             runEchoes);
      bar.appendChild(status);
  
      var wrapper = cm.getWrapperElement();
      wrapper.parentNode.insertBefore(bar, wrapper);
  
      cm.addKeyMap({
        "Alt-E": function () { run("close"); },
        "Alt-V": function () { run("v"); },
        "Alt-C": function () { run("c"); },
        "Alt-B": function () { run("b"); },
        "Alt-I": function () { run("i"); },
        "Alt-O": function () { run("o"); },
        "Alt-D": function () { run("d"); },
        "Alt-S": function () { run("s"); },
        "Alt-P": function () { runEchoes(); }
      });
      cm.on("cursorActivity", function () { say(statusText(cm)); });
      say(statusText(cm));
    }
  
    var api = {
      attach: attach, applyTo: applyTo, applyEchoes: applyEchoes,
      openStack: openStack, computeInsert: computeInsert, convertEchoes: convertEchoes, isChord: isChord
    };
    if (typeof module !== "undefined" && module.exports) module.exports = api;
    else root.ChordProTags = api;
  })(typeof window !== "undefined" ? window : this);