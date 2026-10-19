// teleprompter_tour.js
// Guided tour shared by the song teleprompter and the setlist teleprompter.
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
//
// 🔧 TUNE: change the text below; each "element" must match an id in the templates.
// Steps whose element is not on the page (or not visible) are skipped automatically,
// so the "moving between songs" step only appears on the setlist teleprompter.
//
// Layout the tour walks through:
//   top bar      : Start, Speed, Text size, Chord style, Reset, (setlist: ⬅️ ➡️), ⋯
//   diagram panel: Bottom/Right and S/M/L/XL buttons
//   second row   : Transpose, Chord colour, Light/Dark (+ setlist name, Hide Chords)
//                  It is hidden until the ⋯ button is pressed, so the tour opens it
//                  while it runs and puts it back the way it was afterwards.
//
// This file never touches teleprompter.js: it only reads the page and, when the
// tour starts, calls the public window.teleprompter.stop() to pause the scroll.

(function () {
  const { driver } = window.driver.js;

  // Steps that point at the chord-diagram panel. The popover goes on the side
  // that has room: above the panel when it is at the bottom, left of it when
  // the panel is on the right.
  const DIAGRAM_STEPS = new Set(["#tour-diagram-position", "#diagram-size-control"]);

  const TOURS = {
    teleprompter: [
      {
        popover: {
          title: "Teleprompter 🎤",
          description:
            "The lyrics and chords scroll by themselves, so you can play along. " +
            "This tour shows the buttons and the touch gestures. " +
            "The scrolling is paused while the tour runs.",
        },
      },
      {
        element: "#scroll-toggle",
        popover: {
          title: "Start / Pause",
          description: "Starts the lyrics scrolling. Press it again to pause.",
          side: "bottom",
        },
      },
      {
        element: "#tour-speed",
        popover: {
          title: "Speed",
          description: "<b>−</b> scrolls more slowly and <b>+</b> scrolls faster.",
          side: "bottom",
        },
      },
      {
        element: "#fontsize-control",
        popover: {
          title: "Text size",
          description: "Make the text smaller or larger. Handy on a big screen or a projector.",
          side: "bottom",
        },
      },
      {
        element: "#tour-chord-style",
        popover: {
          title: "Chord style",
          description:
            "<b>Above</b> puts the chord names above the words, which many new players find easier. " +
            "<b>Inline</b> puts them inside the line, right where the chord changes.",
          side: "bottom",
        },
      },
      {
        // These buttons live in the chord-diagram panel
        element: "#tour-diagram-position",
        popover: {
          title: "Chord diagrams",
          description:
            "The chord diagrams have their own little toolbar. " +
            "Show them at the <b>bottom</b> of the screen or on the <b>right</b>.",
          side: "top",
        },
      },
      {
        element: "#diagram-size-control",
        popover: {
          title: "Diagram size",
          description:
            "<b>S</b> is small, good for songs with many chords. " +
            "<b>XL</b> is extra large, good for groups learning to play.",
          side: "top",
        },
      },
      {
        element: "#scroll-reset",
        popover: {
          title: "Reset",
          description: "Stops the scrolling and goes back to the top of the song.",
          side: "bottom",
        },
      },
      {
        // Setlist teleprompter only
        element: "#next-song-btn",
        popover: {
          title: "Moving between songs",
          description:
            "The ⬅️ and ➡️ buttons go to the previous and next song in the setlist. " +
            "On a touch screen you can also <b>swipe</b> right or left, " +
            "or <b>tap the left or right edge</b> of the screen.",
          side: "bottom",
        },
      },
      {
        element: "#tp-more-toggle",
        popover: {
          title: "More settings ⋯",
          description:
            "This button shows or hides a second row with the settings you rarely " +
            "change during a set: the key, the chord colour and light or dark. " +
            "On the setlist page it also holds the setlist name and <b>Hide Chords</b>. " +
            "The row is open for this tour, and closes again when the tour ends " +
            "if it was closed before.",
          side: "bottom",
        },
      },
      {
        element: "#transpose-control",
        popover: {
          title: "Change the key",
          description:
            "Move the song up or down in half steps (semitones) to suit your voice. " +
            "The teleprompter remembers your choice for this song on this device. " +
            "The song itself is not changed.",
          side: "bottom",
        },
      },
      {
        element: "#chordcolor-control",
        popover: {
          title: "Chord colour",
          description: "Pick the colour of the chord names so they are easy to see.",
          side: "bottom",
        },
      },
      {
        element: "#tour-theme",
        popover: {
          title: "Light or dark",
          description: "Switch between a light and a dark background.",
          side: "bottom",
        },
      },
      {
        popover: {
          title: "Touch gestures 👆",
          description:
            "On a phone or tablet, use the lyrics area:" +
            "<ul style='padding-left:1.2em;margin:.5em 0 0'>" +
            "<li><b>Tap</b> the middle: start or pause the scroll</li>" +
            "<li><b>Swipe up or down</b>: scroll the lyrics by hand (change the auto-scroll speed with the − and + buttons)</li>" +
            "<li><b>Drag</b> the lyrics: pauses the scroll so you can look around</li>" +
            "</ul>" +
            "<div style='margin-top:.5em'>With a mouse, clicking or using the wheel on the lyrics pauses the scroll.</div>",
        },
      },
    ],
  };

  // True when the element exists AND is actually drawn on screen.
  function isShown(selector) {
    const el = document.querySelector(selector);
    return !!el && el.getClientRects().length > 0;
  }

  function startTour(name) {
    const raw = TOURS[name];
    if (!raw) return;

    // Pause the auto-scroll first (public function from teleprompter.js).
    try { window.teleprompter && window.teleprompter.stop(); } catch (e) {}

    // Open the second row (⋯) for the tour, remembering whether it was closed.
    // tpShowMoreControls(open) comes from teleprompter_base.html; it does not
    // save to localStorage, so the person's own choice is never overwritten.
    const moreBar = document.getElementById("controls-more");
    const wasClosed = !!(moreBar && moreBar.hidden);
    if (wasClosed && window.tpShowMoreControls) window.tpShowMoreControls(true);

    // Skip steps whose element isn't on this page or isn't visible
    // (e.g. the next-song button on the song page).
    const onRight = document.body.classList.contains("chords-right");
    const steps = raw
      .filter((s) => !s.element || isShown(s.element))
      .map((s) => {
        if (!DIAGRAM_STEPS.has(s.element)) return s;
        // Copy the step so the original stays untouched, and pick the side with room
        return Object.assign({}, s, {
          popover: Object.assign({}, s.popover, { side: onRight ? "left" : "top" }),
        });
      });

    // Runs when the tour ends (Done, ✕ or Esc). onDestroyStarted is used instead of
    // onDestroyed because Driver.js skips onDestroyed on some endings.
    let tour;
    const finish = () => {
      // Put the second row back the way it was
      if (wasClosed && window.tpShowMoreControls) window.tpShowMoreControls(false);
      try { localStorage.setItem("tourSeen:" + name, "1"); } catch (e) {}
      tour.destroy();
    };

    tour = driver({
      showProgress: true,
      nextBtnText: "Next",
      prevBtnText: "Back",
      doneBtnText: "Done",
      // Highlighted buttons can't be pressed during the tour, so nothing
      // starts scrolling or changes the song while someone is reading.
      disableActiveInteraction: true,
      steps: steps,
      onDestroyStarted: finish,
    });
    tour.drive();
  }

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("start-tour");
    if (!btn) return;
    btn.addEventListener("click", () => startTour(btn.dataset.tour));
  });
})();