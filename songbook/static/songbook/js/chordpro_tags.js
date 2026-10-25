/*
 * chordpro_tags.js  --  section-tag helper for the CodeMirror 5 ChordPro editor
 *
 *  Usage (after creating the editor):   ChordProTags.attach(editor);
 *
 *  Adds a toolbar above the editor and these shortcuts:
 *    Alt-E  close the last open section at the cursor      -> {eov}
 *    Alt-V  new verse   (closes the open section first)    -> {sov}
 *    Alt-C  new chorus                                     -> {soc}
 *    Alt-B  new bridge                                     -> {sob}
 *    Alt-I  new intro                                      -> {soi}
 *    Alt-O  new outro                                      -> {soo}
 *
 *  Workflow: put the cursor at the START of the first line of the next
 *  section and press Alt-V / Alt-C / ... The previous section is closed and
 *  the new one opened in one keypress. At the end of the song press Alt-E.
 */
(function (root) {
    "use strict";
  
    var NAMES = { v: "Verse", c: "Chorus", b: "Bridge", i: "Intro", o: "Outro" };
  
    // Which sections are open in `text`? (last one in the array = innermost)
    function openStack(text) {
      var re = /\{(so|eo)([icvbo])\}/g, stack = [], m;
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
    // action = "close" or one of v/c/b/i/o.  Returns null if there is nothing to do.
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
  
      function run(action) {
        var ok = applyTo(cm, action);
        cm.focus();
        status.textContent = ok ? statusText(cm) : "No open section to close";
        status.style.color = ok ? "" : "#b00020";
      }
      function button(label, title, action) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "btn btn-sm btn-outline-secondary";
        b.textContent = label;
        b.title = title;
        b.addEventListener("mousedown", function (e) { e.preventDefault(); run(action); });
        bar.appendChild(b);
      }
      button("Close (Alt-E)", "Close the last open section at the cursor", "close");
      button("Verse (Alt-V)", "Close the open section and start a verse", "v");
      button("Chorus (Alt-C)", "Close the open section and start a chorus", "c");
      button("Bridge (Alt-B)", "Close the open section and start a bridge", "b");
      button("Intro (Alt-I)", "Start an intro", "i");
      button("Outro (Alt-O)", "Close the open section and start an outro", "o");
      bar.appendChild(status);
  
      var wrapper = cm.getWrapperElement();
      wrapper.parentNode.insertBefore(bar, wrapper);
  
      cm.addKeyMap({
        "Alt-E": function () { run("close"); },
        "Alt-V": function () { run("v"); },
        "Alt-C": function () { run("c"); },
        "Alt-B": function () { run("b"); },
        "Alt-I": function () { run("i"); },
        "Alt-O": function () { run("o"); }
      });
      cm.on("cursorActivity", function () { status.textContent = statusText(cm); status.style.color = ""; });
      status.textContent = statusText(cm);
    }
  
    var api = { attach: attach, applyTo: applyTo, openStack: openStack, computeInsert: computeInsert };
    if (typeof module !== "undefined" && module.exports) module.exports = api;
    else root.ChordProTags = api;
  })(typeof window !== "undefined" ? window : this);