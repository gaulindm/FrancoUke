// chordpro_tour.js
// Guided tour for the ChordPro editing page and its cheat sheet.
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
//
// 🔧 TUNE: change the text below.
// Where the tour points:
//   the ChordPro text box   -> the CodeMirror editor (.CodeMirror) on song_form.html
//   the Save button         -> the submit button of #song-form (Update / Create)
//   the cheat sheet cards   -> the ids that are written in _chordpro_cheatsheet.html
// A step whose element is not on the page is skipped, so the tour never breaks.

(function () {
    const { driver } = window.driver.js;
  
    // The page turns the text box into a CodeMirror editor and hides the real <textarea>,
    // so the tour points at the visible editor (.CodeMirror) and only falls back to the textarea.
    function editorBox() {
      return (
        document.querySelector(".CodeMirror") ||
        document.querySelector('#id_songChordPro, textarea[name="songChordPro"], textarea')
      );
    }
  
    // An "element" can be a CSS selector (text) or a small function that finds the element.
    function find(el) {
      if (typeof el === "function") return el();
      return document.querySelector(el);
    }
  
    function saveButton() {
      const box = editorBox();
      const form = document.getElementById("song-form") || (box && box.closest("form"));
      return form && form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
    }
  
    const TOURS = {
      chordpro: [
        {
          popover: {
            title: "Writing or editing a song ✍️",
            description:
              "A song is written as plain text in a format called <b>ChordPro</b>: " +
              "the lyrics, with chords in [square brackets], and <b>tags</b> in {curly braces}." +
              "<br><br>" +
              "The tags do more than you might think. They fill in the <b>header of the PDF and of the teleprompter</b>, " +
              "so the more tags you fill in, the better both look.",
          },
        },
        {
          element: editorBox,
          popover: {
            title: "The song text",
            description:
              "Write or fix the song here. Put each tag on its own line, " +
              "and put chords in [square brackets] right before the word where they change. " +
              "When you type a bracket, the closing one is added for you." +
              "<br><br>" +
              "Handy keys: <b>Ctrl+F</b> to find, <b>Ctrl+H</b> to replace, <b>Ctrl+Z</b> to undo.",
            side: "right",
            align: "start",
          },
        },
        {
          element: "#tour-cheatsheet",
          popover: {
            title: "The cheat sheet",
            description:
              "Every tag the PDF and the teleprompter understand, with examples. " +
              "Click a title to open it.",
            side: "left",
            align: "start",
          },
        },
        {
          element: "#tour-cheat-header",
          popover: {
            title: "Header tags 📋",
            description:
              "Title, artist, year, capo, time signature, strumming pattern, songwriter, " +
              "the first note and the count in. <b>The more you fill in, the better the header looks</b>, " +
              "in the PDF and in the teleprompter. A line with nothing to show is simply left out. " +
              "Use <b>Copy all header tags</b> to paste every header tag at the top of a song, then fill in the ones you need.",
            side: "left",
          },
        },
        {
          element: "#tour-cheat-sections",
          popover: {
            title: "Sections 🎼",
            description:
              "Mark an intro, verse, chorus, bridge and so on. Each one starts with a tag and ends with a matching tag, " +
              "and the PDF prints a label (Chorus, Bridge…) in the margin. Verses have no label.",
            side: "left",
          },
        },
        {
          element: "#tour-cheat-comments",
          popover: {
            title: "Notes and comments 💬",
            description:
              "There are several kinds of notes, and they all start with <b>{c: …}</b>. " +
              "A note on its own line prints in red. A note inside a lyric line is small and grey. " +
              "<b>{c:(234)}</b> adds a count cue at the end of the line, " +
              "and <b>{c:VG1}</b> or <b>{c:VG2}</b> labels the next line for Vocal Group 1 or 2. " +
              "<b>{instruction: …}</b> is a small note under a section label (not on verses).",
            side: "left",
          },
        },
        {
          element: "#tour-cheat-styles",
          popover: {
            title: "Colours and styles 🎨",
            description:
              "Wrap words in tags to make them <b>bold</b>, <i>italic</i> or underlined, " +
              "to colour them (red, blue, green…) or to highlight them.",
            side: "left",
          },
        },
        {
          element: "#tour-cheat-optional",
          popover: {
            title: "Chords 🎸",
            description:
              "A chord goes in [square brackets]. An <b>optional chord</b>, one players may leave out, " +
              "goes inside an opt tag and is printed in grey italic.",
            side: "left",
          },
        },
        {
          element: "#tour-cheat-youtube",
          popover: {
            title: "YouTube video ▶️",
            description:
              "The <b>youtube</b> tag is what drives the video players. " +
              "Without it, a song has no video. Paste the full YouTube link (it must start with https://), " +
              "and add a time to the link if the video should start part-way.",
            side: "left",
          },
        },
        {
          element: saveButton,
          popover: {
            title: "Save",
            description:
              "Press <b>Update</b> (or <b>Create</b> for a new song), then open the PDF or the teleprompter to see the result. " +
              "The artist, year, capo, key and the other tags are read again every time you save. " +
              "(The title tag is only used when a song has no title yet.)",
            side: "top",
          },
        },
      ],
    };
  
    function startTour(name) {
      const raw = TOURS[name];
      if (!raw) return;
  
      // Keep only the steps whose element exists; turn function elements into real elements.
      const steps = raw
        .map((s) => {
          if (!s.element) return s;
          const found = find(s.element);
          return found ? { ...s, element: found } : null;
        })
        .filter(Boolean);
  
      driver({
        showProgress: true,
        nextBtnText: "Next",
        prevBtnText: "Back",
        doneBtnText: "Done",
        // Highlighted boxes and buttons can't be used during the tour,
        // so nothing is typed or saved by accident while someone is reading.
        disableActiveInteraction: true,
        steps: steps,
        onDestroyed: () => {
          try { localStorage.setItem("tourSeen:" + name, "1"); } catch (e) {}
        },
      }).drive();
    }
  
    document.addEventListener("DOMContentLoaded", () => {
      const btn = document.getElementById("start-tour");
      if (!btn) return;
      btn.addEventListener("click", () => startTour(btn.dataset.tour));
    });
  })();