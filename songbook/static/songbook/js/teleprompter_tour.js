// teleprompter_tour.js
// Guided tour shared by the song teleprompter and the setlist teleprompter.
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
//
// 🔧 TUNE: change the text below; each "element" must match an id in the templates.
// Steps whose element is not on the page are skipped automatically, so the
// "moving between songs" step only appears on the setlist teleprompter.
//
// This file never touches teleprompter.js: it only reads the page and, when the
// tour starts, calls the public window.teleprompter.stop() to pause the scroll.

(function () {
    const { driver } = window.driver.js;
  
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
          element: "#fontsize-control",
          popover: {
            title: "Text size",
            description: "Make the text smaller or larger. Handy on a big screen or a projector.",
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
          element: "#tour-diagram-position",
          popover: {
            title: "Chord diagrams",
            description: "Show the chord diagrams at the bottom of the screen or on the right.",
            side: "bottom",
          },
        },
        {
          element: "#diagram-size-control",
          popover: {
            title: "Diagram size",
            description:
              "<b>S</b> is small, good for songs with many chords. " +
              "<b>XL</b> is extra large, good for groups learning to play.",
            side: "bottom",
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
          popover: {
            title: "Touch gestures 👆",
            description:
              "On a phone or tablet, use the lyrics area:" +
              "<ul style='padding-left:1.2em;margin:.5em 0 0'>" +
              "<li><b>Tap</b> the middle: start or pause the scroll</li>" +
              "<li><b>Swipe up or down</b>: scroll faster or slower</li>" +
              "<li><b>Drag</b> the lyrics: pauses the scroll so you can look around</li>" +
              "</ul>" +
              "<div style='margin-top:.5em'>With a mouse, clicking or using the wheel on the lyrics pauses the scroll.</div>",
          },
        },
      ],
    };
  
    function startTour(name) {
      const raw = TOURS[name];
      if (!raw) return;
  
      // Pause the auto-scroll first (public function from teleprompter.js).
      try { window.teleprompter && window.teleprompter.stop(); } catch (e) {}
  
      // Skip steps whose element isn't on this page.
      const steps = raw.filter((s) => !s.element || document.querySelector(s.element));
  
      driver({
        showProgress: true,
        nextBtnText: "Next",
        prevBtnText: "Back",
        doneBtnText: "Done",
        // Highlighted buttons can't be pressed during the tour, so nothing
        // starts scrolling or changes the song while someone is reading.
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