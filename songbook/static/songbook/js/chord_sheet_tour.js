// chord_sheet_tour.js
// Guided tour for the chord sheet page (PDF preview + control panel).
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
//
// 🔧 TUNE: change the text below. Each "element" must match an id in the templates.
// Some steps use "byRole": the text changes depending on who is looking at the page.
// The role comes from the data-tour-role="..." attribute on the element
// (editor / viewer / anonymous). If a role has no text, the normal description is used.

(function () {
    const { driver } = window.driver.js;
  
    const TOURS = {
      chordsheet: [
        {
          popover: {
            title: "Chord sheet 🎼",
            description:
              "On one side you see a <b>preview of the song as a PDF</b>. " +
              "On the other side are the tools to change the key, edit the song and adjust its layout. " +
              "(On a phone, the preview comes first and the tools are below it.)",
          },
        },
        {
          element: "#pdf-preview",
          popover: {
            title: "PDF preview",
            description:
              "This is how the song will look when printed. After you transpose, " +
              "use the print or download buttons of the PDF viewer to print it or save it. " +
              "They look a little different in each browser.",
            side: "right",
            align: "start",
          },
        },
        {
          element: "#tour-chord-teleprompter",
          popover: {
            title: "Teleprompter 🎤",
            description: "Open this same song in the teleprompter, to play along with a scrolling view.",
            side: "bottom",
          },
        },
        {
          // Only shown to the song's owner (and administrators)
          element: "#tour-privacy",
          popover: {
            title: "Public or private?",
            description:
              "Public songs can be seen by everyone. Private songs can only be seen by you. " +
              "If you are a Leader, the button here lets you switch the song between the two.",
            side: "left",
          },
        },
        {
          element: "#tour-editor-area",
          popover: {
            title: "Song editor",
            description: "Tools for changing the song itself.",
            side: "left",
          },
          byRole: {
            editor:
              "<b>Edit ChordPro</b> changes the words and chords of the song, " +
              "without changing how it looks. Only the song's owner sees the Delete button.",
            viewer:
              "A song can be edited by the person who contributed it or by Songbook Editors. " +
              "On a public song you may see a button here to make <b>your own editable copy</b>.",
            anonymous:
              "Log in to edit your own songs. On a public song you may also see a button " +
              "above to make your own editable copy.",
          },
        },
        {
          element: "#transpose-select",
          popover: {
            title: "Change the key 🎸",
            description:
              "Choose how many semitones (half steps) to move the song up or down, " +
              "to suit your voice or to use easier chords. This works for everyone.",
            side: "left",
          },
        },
        {
          element: "#update-preview",
          popover: {
            title: "Apply transposition",
            description: "Click here and the preview refreshes with the new chords. Then you can print or save it.  The transposition is not permanent.",
            side: "left",
          },
        },
        {
          element: "#tour-formatting-area",
          popover: {
            title: "Song formatting 🎨",
            description: "Adjust how the song is laid out in the PDF.",
            side: "left",
          },
          byRole: {
            editor:
              "<b>Edit Song Formatting</b> opens the Song Formatting Editor, " +
              "where you can adjust how the PDF is laid out.",
            viewer:
              "Changing the layout needs <b>SongbookEditor</b> permission. " +
              "The note here tells you how to ask for it.",
            anonymous: "Log in to change the layout of a song.",
          },
        },
        {
          // Only exists when the song has a valid YouTube link
          element: "#tour-video",
          popover: {
            title: "Video",
            description: "Watch the song here when a video is available.",
            side: "left",
          },
        },
      ],
    };
  
    function startTour(name) {
      const raw = TOURS[name];
      if (!raw) return;
  
      const steps = raw
        // Skip steps whose element isn't on the page (not the owner, no video, etc.)
        .filter((s) => !s.element || document.querySelector(s.element))
        // Pick the text that matches who is looking at the page
        .map((s) => {
          const { byRole, ...step } = s;
          if (byRole && step.element) {
            const role = document.querySelector(step.element).dataset.tourRole;
            if (byRole[role]) {
              step.popover = { ...step.popover, description: byRole[role] };
            }
          }
          return step;
        });
  
      driver({
        showProgress: true,
        nextBtnText: "Next",
        prevBtnText: "Back",
        doneBtnText: "Done",
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