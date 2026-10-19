// board_tour.js
// Guided tour for the private club board (full_board.html).
// Needs Driver.js 1.x loaded first (driver.js.iife.js + driver.css).
//
// 🔧 TUNE: change the text below.
// This tour points at the board using CSS selectors (no ids needed in the loops):
//   .board-column                                   -> the first column
//   .card[data-bs-target^="#eventModal"]            -> the first event card
//   ... td.text-end .badge                          -> the "Y / M / N / –" badge on that card
//   ... .badge.bg-info                              -> the first "Rehearsal" label (if any)
// Steps without an element are shown in the middle of the screen.
// "byRole" picks the text for leaders or ordinary members; the role comes from
// data-tour-role="leader|member" on the tour button.

(function () {
    const { driver } = window.driver.js;
  
    const CARD = '.card[data-bs-target^="#eventModal"]';
  
    const TOURS = {
      board: [
        {
          popover: {
            title: "Your club's board 📋",
            description:
              "This is where the club's events and rehearsals are listed. " +
              "This tour shows how to read the board and how to tell the group if you can come.",
          },
        },
        {
          element: ".board-column",
          popover: {
            title: "Columns",
            description:
              "Events are sorted into columns, such as upcoming and past events. " +
              "If you can't see them all, scroll sideways.",
            side: "right",
            align: "start",
          },
        },
        {
          element: CARD,
          popover: {
            title: "An event card",
            description:
              "Each card shows the photo, title, date and time of an event. " +
              "<b>Click anywhere on the card</b> to open the full details.",
            side: "right",
            align: "start",
          },
        },
        {
          element: CARD + " td.text-end .badge",
          popover: {
            title: "Your answer",
            description:
              "This little badge shows <i>your</i> availability: " +
              "<b>Y</b> yes (green), <b>M</b> maybe (yellow), <b>N</b> no (red), " +
              "or <b>–</b> if you haven't answered yet.",
            side: "left",
          },
        },
        {
          // Only shown if the board has a rehearsal
          element: CARD + " .badge.bg-info",
          popover: {
            title: "Rehearsals 🎤",
            description:
              "Rehearsals have this label. They don't ask for your availability. " +
              "Open one to read the practice notes.",
            side: "bottom",
          },
        },
        {
          popover: {
            title: "Inside an event window",
            description:
              "After you click a card, the window shows the place, the time, what to wear and any notes. " +
              "For a performance you will also find:" +
              "<ul style='padding-left:1.2em;margin:.5em 0 0'>" +
              "<li><b>Your Availability</b>: choose Yes, Maybe or No, then press <b>Save</b>.</li>" +
              "<li><b>Group Availability</b>: how many people said Yes, No or Maybe.</li>" +
              "<li><b>View Setlist</b>: the songs for the event, when a setlist exists.</li>" +
              "</ul>",
          },
          byRole: {
            leader:
              "After you click a card, the window shows the place, the time, what to wear and any notes. " +
              "For a performance you will also find:" +
              "<ul style='padding-left:1.2em;margin:.5em 0 0'>" +
              "<li><b>Your Availability</b>: choose Yes, Maybe or No, then press <b>Save</b>.</li>" +
              "<li><b>Group Availability</b>: how many people said Yes, No or Maybe.</li>" +
              "<li><b>View Setlist</b>: the songs for the event.</li>" +
              "</ul>" +
              "<div style='margin-top:.5em'><b>As a leader</b> you can also create or edit the setlist here, " +
              "and edit the notes of a rehearsal.</div>",
          },
        },
      ],
    };
  
    function startTour(name, role) {
      const raw = TOURS[name];
      if (!raw) return;
  
      const steps = raw
        // Skip steps whose element isn't on the page (no rehearsal, empty board, ...)
        .filter((s) => !s.element || document.querySelector(s.element))
        // Pick the text that matches the person's role
        .map((s) => {
          const { byRole, ...step } = s;
          if (byRole && byRole[role]) {
            step.popover = { ...step.popover, description: byRole[role] };
          }
          return step;
        });
  
      driver({
        showProgress: true,
        nextBtnText: "Next",
        prevBtnText: "Back",
        doneBtnText: "Done",
        // Cards can't be clicked during the tour, so no event window opens by accident.
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
      btn.addEventListener("click", () => startTour(btn.dataset.tour, btn.dataset.tourRole));
    });
  })();