// formatting_tour.js
// Guided tour for the Edit Song Formatting page.
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
// 🔧 TUNE: change the text below; each "element" must match an id in edit_formatting.html.

(function () {
    const { driver } = window.driver.js;
  
    const TOURS = {
      formatting: [
        {
          popover: {
            title: "Song formatting 🎨",
            description:
              "This page changes how the song looks <b>in the PDF</b>, such as text size, color and spacing. " +
              "It does <b>not</b> change the words or the chords of the song. " +
              "To change those, go back to the chord sheet and use <b>Edit ChordPro</b>.",
          },
        },
        {
          element: "#tour-formatting-form",
          popover: {
            title: "Your settings",
            description:
              "Type your settings in the box. You only need to write the ones you want to change. " +
              "Anything you leave out keeps its normal (default) value.",
            side: "right",
            align: "start",
          },
        },
        {
          element: "#tour-settings-list",
          popover: {
            title: "What you can change",
            description:
              "Each line is one setting, with its default value in brackets. " +
              "For example font_size is the size of the text, and alignment is left, center or right. " +
              "You don't have to use them all.",
            side: "left",
          },
        },
        {
          element: "#tour-example",
          popover: {
            title: "An example",
            description:
              "To make the text bigger and change nothing else, you would type just this. " +
              "The other settings stay at their defaults.",
            side: "left",
          },
        },
        {
          element: "#tour-braces",
          popover: {
            title: "Keep the curly braces ⚠️",
            description:
              "Your settings must stay between the curly braces { }. " +
              "If you don't want any changes, leave the box empty or just { }.",
            side: "left",
          },
        },
        {
            element: "#tour-save",
            popover: {
              title: "Save",
              description:
                "Save your changes, then open the song's PDF to see the result. " +
                "This only changes the look of the PDF. The song itself stays as it is." +
                "<br><br>" +
                "Saving also gives the song a green check ✅, even if you didn't change anything. " +
                "So if the normal look is fine, just click Save.",
              side: "top",
            },
          },
      ],
    };
  
    function startTour(name) {
      const raw = TOURS[name];
      if (!raw) return;
  
      // Skip steps whose element isn't on the page, so the tour never breaks.
      const steps = raw.filter((s) => !s.element || document.querySelector(s.element));
  
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