// song_list_tour.js
// Guided tours for the song list pages (simple view + extended view).
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
// 🔧 TUNE: change the step text below; each "element" must match an id in the templates.

(function () {
  const { driver } = window.driver.js;

  const TOURS = {
    simple: [
      {
        popover: {
          title: "Welcome to the songbook 🎵",
          description:
            "This is the <b>simple view</b>. It's made for browsing, reading and playing along, " +
            "and it's the best choice for most people.",
        },
      },
      {
        element: "#tour-filters",
        popover: {
          title: "Find songs",
          description: "Narrow the list by letter, tag, decade, key, or by the chords you already know.",
          side: "bottom",
        },
      },
      {
        element: "#tour-first-title",
        popover: {
          title: "Song title",
          description: "Click a title to open the song as a PDF you can read or print.",
          side: "right",
        },
      },
      {
        element: "#tour-first-teleprompter",
        popover: {
          title: "Teleprompter 🎤",
          description: "Opens a scrolling view of the lyrics and chords for playing along.",
          side: "left",
        },
      },
      {
        element: "#tour-first-video",
        popover: {
          title: "Video",
          description: "Listen to or watch the song when a video is available.",
          side: "left",
        },
      },
      {
        element: "#tour-rating-col",
        popover: {
          title: "Ratings ⭐",
          description:
            "Everyone can see how songs are rated. Click the heading to show the best rated first. " +
            "Log in to rate songs yourself.",
          side: "bottom",
        },
      },
      {
        element: "#tour-chords-col",
        popover: {
          title: "Chords played",
          description: "The chords each song uses, so you can see at a glance whether it's within reach.",
          side: "bottom",
        },
      },
      {
        element: "#tour-switch-view",
        popover: {
          title: "Need more tools?",
          description:
            "The <b>extended view</b> is for people who want to edit the ChordPro text, " +
            "adjust PDF formatting, or transpose a song before printing or exporting. " +
            "If you just want to read and play, stay right here.",
          side: "bottom",
        },
      },
    ],

    extended: [
      {
        popover: {
          title: "Extended view 🛠️",
          description:
            "This view shows every column and gives access to the song tools. " +
            "It's meant for people who edit songs or prepare them for printing or exporting. " +
            "If you only want to read and play, the <b>simple view</b> is easier.",
        },
      },
      {
        element: "#tour-filters",
        popover: {
          title: "Filters",
          description: "The same filters as the simple view.",
          side: "bottom",
        },
      },
      {
        element: "#tour-first-title",
        popover: {
          title: "Song title",
          description:
            "Click a title to open the chord sheet. From there you can edit the ChordPro text, " +
            "adjust the PDF formatting and transpose the song before you print or export it.",
          side: "right",
        },
      },
      {
        element: "#generateReportBtn",
        popover: {
          title: "Multi-song report",
          description:
            "Pick a tag in the filters, then use this button to make one PDF with all the songs in that tag.",
          side: "top",
        },
      },
      {
        element: "#tour-switch-view",
        popover: {
          title: "Back to the simple view",
          description: "Use this button any time to go back to the simpler layout.",
          side: "bottom",
        },
      },
    ],
  };

  function startTour(name) {
    const steps = TOURS[name];
    if (!steps) return;

    // Skip steps whose element isn't on the page (e.g. filters hidden on a phone,
    // or an empty list with no first row), so the tour never breaks.
    const available = steps.filter(
      (s) => !s.element || document.querySelector(s.element)
    );

    driver({
      showProgress: true,
      nextBtnText: "Next",
      prevBtnText: "Back",
      doneBtnText: "Done",
      steps: available,
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