const chordMap = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11};
const reverseChordMap = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'};
const instrument = 'ukulele'; // Specify the instrument


document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed.");

    const instrumentSelector = document.getElementById('instrument-selector');
    const chordContainer = document.getElementById('bottom-chord-container');
    const toggleChordBoxElement = document.getElementById('toggle-chord-box');
    const isLeftyToggle = document.getElementById('isLeftyToggle'); // Lefty mode toggle


    if (typeof songDict === 'undefined' || !Array.isArray(songDict)) {
        console.error("songDict is not defined or invalid.");
        return;
    }

    // Extract unique chords from songDict
    const uniqueChords = [...new Set(songDict.flatMap(section => 
        section.map(item => item.chord).filter(Boolean)))];

    console.log("Unique chords extracted:", uniqueChords);

    // Instrument chord data files
    const chordFiles = {
        guitar: "/static/js/guitar_chords.json",
        
        ukulele: "/static/js/ukulele_chords.json",

        baritone_ukulele: "/static/js/baritoneUke_chords.json",
        banjo: "/static/js/banjo_chords.json",
        mandolin: "/static/js/mandolin_chords.json"
    };

    // Function to load chord data for the selected instrument
    function loadInstrumentData(instrument) {
        const filePath = chordFiles[instrument];
        if (!filePath) {
            console.error("Invalid instrument selected:", instrument);
            return;
        }

        console.log(`Loading chord data for instrument: ${instrument}`);
        Raphael.chord.setInstrument(instrument); // Set the instrument in Raphael

        Raphael.chord.loadData(filePath)
            .then(() => {
                console.log(`${instrument} chord data loaded successfully.`);
                renderChords();
            })
            .catch(error => console.error(`Error loading chord data for ${instrument}:`, error));
    }

    // Function to render chord diagrams
    async function renderChords() {
        if (!chordContainer) {
            console.error("Chord container not found.");
            return;
        }

        console.log("Rendering chords into the container.");
        chordContainer.innerHTML = ''; // Clear existing content

        for (const chordName of uniqueChords) {
            console.log(`Processing chord: ${chordName}`);
            const chordData = await Raphael.chord.find(chordName, 1);

            if (!chordData) {
                console.warn(`Chord not found: ${chordName}`);
                continue;
            }

            // Create diagram container
            const diagramContainer = document.createElement('div');
            diagramContainer.className = 'chord-diagram';
            chordContainer.appendChild(diagramContainer);

            // Render the chord diagram using Raphael
            const chord = new Raphael.chord.Chord(diagramContainer, chordData, chordName);
            chord.element.setViewBox(0, 0, 100, 120);
        }

        console.log("All chords rendered successfully!");
    }

    // Lefty mode toggle
    if (isLeftyToggle) {
        isLeftyToggle.addEventListener('change', (event) => {
            const isLefty = event.target.checked;
            console.log("Lefty toggle switched:", isLefty);

            // Update Raphael lefty state
            Raphael.chord.toggleLeftyMode(isLefty);

            // Re-render chords to apply lefty layout
            renderChords();
        });
    } else {
        console.warn("isLeftyToggle element not found.");
    }

    // Chord box visibility toggle
    function toggleChordBox(isVisible) {
        const chordBox = document.getElementById('chord-container');
        if (isVisible) {
            chordBox.classList.remove('d-none');
            updateChordPHPosition('bottom'); // Default to bottom
        } else {
            chordBox.classList.add('d-none');
        }
    }

    // Initialize chord visibility toggle
    if (toggleChordBoxElement) {
        const savedState = localStorage.getItem('chordBoxVisible') === 'true';
        toggleChordBoxElement.checked = savedState;
        toggleChordBox(savedState);

        toggleChordBoxElement.addEventListener('change', () => {
            const isVisible = toggleChordBoxElement.checked;
            localStorage.setItem('chordBoxVisible', isVisible);
            toggleChordBox(isVisible);
        });
    }

    // Event listener for instrument selection
    if (instrumentSelector) {
        instrumentSelector.addEventListener('change', (event) => {
            const selectedInstrument = event.target.value;
            loadInstrumentData(selectedInstrument);
        });

        // Load initial instrument data
        loadInstrumentData(instrumentSelector.value);
    }

    // Render inline song view by default
    if (typeof renderInline === 'function') {
        console.log("Rendering inline song view.");
        renderInline(songDict, 0); // Default semitone shift is 0
    } else {
        console.error("renderInline function is not defined.");
    }
});


function updateChordPlacement(placement) {
    const lyricsContainer = document.getElementById('lyrics-container');
    
    // Reset all classes first
    lyricsContainer.classList.remove(
        'chords-inline',
        'chords-above',
        'chords-above-with-diagram',
        'lyrics-only'
    );

    // Apply class based on placement value
    switch (placement) {
        case 'lyrics_only':
            lyricsContainer.classList.add('lyrics-only');
            break;
        case 'inline':
            lyricsContainer.classList.add('chords-inline');
            break;
        case 'above':
            lyricsContainer.classList.add('chords-above');
            break;
        case 'above_with_diagram':
            lyricsContainer.classList.add('chords-above-with-diagram');
            break;
        default:
            console.warn('Invalid placement value:', placement);
    }
}


function renderInline(songDict, semitones) {
    const songContainer = document.getElementById('song-content');
    let htmlContent = ''; // Start with an empty string

    let inChorus = false; // Track whether we're inside a chorus section

    songDict.forEach(section => {
        section.forEach(item => {
            if (item.directive) {
                switch (item.directive) {
                    case "{soc}":
                        if (!inChorus) {
                            htmlContent += `<div class="chorus">`;
                            inChorus = true;
                        }
                        break;
                    case "{eoc}":
                        if (inChorus) {
                            htmlContent += `</div>`;
                            inChorus = false;
                        }
                        break;
                }
            } else if (item.chord !== undefined) {
                const transposedChord = item.chord ? transposeChord(item.chord, semitones) : '';
                const chordSpan = transposedChord ? `<span class="chord">[${transposedChord}]</span>` : '';
                const lyricSpan = item.lyric ? `<span class="lyric">${item.lyric}</span>` : '';
                htmlContent += `<span class="line">${chordSpan} ${lyricSpan}</span>`;
            } else if (item.format === 'LINEBREAK') {
                htmlContent += '<br>';
            } else if (item.format === 'PARAGRAPHBREAK') {
                htmlContent += '<br><br>'; // Extra break for paragraph separation
            }
        });
        
    });

    // Ensure any unclosed section is properly closed
    if (inChorus) {
        htmlContent += `</div>`;
    }

    songContainer.innerHTML = htmlContent; // Set the complete HTML
}

function loadInstrumentData(instrument) {
    const chordFiles = {
        guitar: "{% static 'js/guitar_chords.json' %}",
        ukulele: "{% static 'js/ukulele_chords.json' %}",
        baritone_ukulele: "{% static 'js/baritoneUke_chords.json' %}",
        banjo: "{% static 'js/banjo_chords.json' %}",
        mandolin: "{% static 'js/mandolin_chords.json' %}"
    };

    const filePath = chordFiles[instrument];
    if (!filePath) {
        console.error("Invalid instrument selected.");
        return;
    }

    Raphael.chord.setInstrument(instrument);
    Raphael.chord.loadData(filePath)
        .then(() => {
            console.log(`${instrument} chord data loaded.`);
            renderChords();
        })
        .catch(error => console.error(`Error loading chord data for ${instrument}:`, error));
}

function renderChords() {
    const container = document.getElementById('bottom-chord-container');
    container.innerHTML = ''; // Clear existing diagrams

    uniqueChords.forEach((chordName) => {
        const chordData = Raphael.chord.find(chordName, 1);
        if (!chordData) {
            console.warn(`Chord ${chordName} not found.`);
            return;
        }

        const diagramContainer = document.createElement('div');
        diagramContainer.className = 'chord-diagram';
        container.appendChild(diagramContainer);

        const chord = new Raphael.chord.Chord(diagramContainer, chordData, chordName);
        chord.element.setViewBox(0, 0, 100, 120);
    });
}



function toggleChordBox(isVisible) {
    const chordContainer = document.getElementById('chord-container');
    if (isVisible) {
        chordContainer.classList.remove('d-none');
        updateChordPHPosition('bottom'); // Ensure default position is set to bottom
    } else {
        chordContainer.classList.add('d-none');
    }
}

function renderChords() {
    console.log("Rendering chords:", uniqueChords); // Debugging
    const container = document.getElementById('bottom-chord-container');
    container.innerHTML = ''; // Clear existing diagrams

    uniqueChords.forEach((chordName) => {
        const chordData = Raphael.chord.find(chordName, 1);
        if (!chordData) {
            console.warn(`Chord ${chordName} not found.`);
            return;
        }

        // Create and render the chord diagram
        const diagramContainer = document.createElement('div');
        diagramContainer.className = 'chord-diagram';
        container.appendChild(diagramContainer);

        const chord = new Raphael.chord.Chord(diagramContainer, chordData, chordName);
        chord.element.setViewBox(0, 0, 100, 120);
    });
}



function updateStyle(styleName, value) {
    console.log(`updateStyle called with styleName: ${styleName}, value: ${value}`);

    // Ensure the parameters are not undefined
    if (!styleName || value === undefined) {
        console.error('Invalid parameters passed to updateStyle.');
        return;
    }

    const songContent = document.getElementById('song-content');
    if (!songContent) {
        console.error('song-content element not found.');
        return;
    }

    const chords = document.querySelectorAll('#song-content .chord');

    switch (styleName) {
        case 'lineHeight':
            songContent.style.lineHeight = value;
            break;
        case 'fontSize':
        case 'color':
            songContent.style[styleName] = value;
            break;
        case 'chordColor':
            chords.forEach(chord => chord.style.color = value);
            break;
        case 'chordWeight':
            chords.forEach(chord => chord.style.fontWeight = value);
            break;
        default:
            console.error(`Unsupported styleName: ${styleName}`);
            break;
    }
}



function printDiv(divId) {
    const contentElement = document.getElementById(divId);

    if (!contentElement) {
        console.error(`Element with ID "${divId}" not found.`);
        return;
    }

    // Clone the content to manipulate it safely
    const clonedContent = contentElement.cloneNode(true);

    // Check visibility of the bottom chords inline
    const bottomPlaceholder = clonedContent.querySelector("#bottom-chord-diagram-placeholder");
    const isBottomVisible = bottomPlaceholder && 
        window.getComputedStyle(bottomPlaceholder).display !== "none" && 
        bottomPlaceholder.offsetWidth > 0 && 
        bottomPlaceholder.offsetHeight > 0;

    if (!isBottomVisible) {
        console.log("Bottom chord placeholder is hidden and will not be included in the print view.");
        if (bottomPlaceholder) bottomPlaceholder.remove(); // Remove if hidden
    } else {
        console.log("Bottom chord placeholder is visible and will be included in the print view.");
        if (bottomPlaceholder) {
            const chordContainer = bottomPlaceholder.querySelector("#bottom-chord-container");
            if (chordContainer) {
                // Apply styles to position chords at the bottom page margin
                bottomPlaceholder.style.position = "fixed";
                bottomPlaceholder.style.bottom = "20px"; // Space from the bottom edge
                bottomPlaceholder.style.left = "0";
                bottomPlaceholder.style.width = "100%";
                bottomPlaceholder.style.backgroundColor = "white"; // Ensure visibility on colored backgrounds

                chordContainer.style.display = "flex";
                chordContainer.style.flexDirection = "row";
                chordContainer.style.justifyContent = "center";
                chordContainer.style.alignItems = "center";
                chordContainer.style.gap = "10px";
                chordContainer.style.flexWrap = "wrap"; // Wrap if too many chords
            }
        }
    }

    // Open a new print window
    const printWindow = window.open("", "", "height=600,width=800");
    if (!printWindow) {
        console.error("Unable to open print window.");
        return;
    }

    // Write content into the print window
    printWindow.document.write("<html><head><title>Print Score</title>");
    printWindow.document.write("<style>");
    printWindow.document.write(`
        body { font-family: Arial, sans-serif; margin: 20px; }
        #song_header { width: 100%; border-collapse: collapse; }
        #song_header td { padding: 5px; text-align: center; }
        .verse, .chorus { margin: 20px 0; padding: 10px; }
        .verse { background-color: #e9f7e9; border-left: 4px solid #28a745; }
        .chorus { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        #bottom-chord-container { display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; }
        #bottom-chord-diagram-placeholder { position: fixed; bottom: 20px; left: 0; width: 100%; background-color: white; }
        .chord-diagram { margin: 5px; width: 100px; height: 120px; border: 1px solid #ccc; }
        @media print { 
            .verse, .chorus { page-break-inside: avoid; }
            #bottom-chord-diagram-placeholder { position: fixed; bottom: 20px; left: 0; width: 100%; }
        }
    `);
    printWindow.document.write("</style></head><body>");
    printWindow.document.write(clonedContent.innerHTML);
    printWindow.document.write("</body></html>");
    printWindow.document.close();

    // Trigger print
    printWindow.print();
}

function transposeChord(chord, semitones) {
    const chordRegex = /^([A-G][#b]?)(m|M|maj|min|dim|aug|sus|add|7|9|11|13)?$/;
    const match = chord.match(chordRegex);

    if (!match) {
        return chord; // Return the original chord if it doesn't match the expected pattern
    }

    const baseChord = match[1];
    const chordType = match[2] || '';

    const newValue = (chordMap[baseChord] + semitones + 12) % 12;

    return reverseChordMap[newValue] + chordType;
}


function transposeSong(semitones) {
    renderInline(songDict, parseInt(semitones));
}

function updateChordPHPosition(position) {
    // List of all placeholders
    const placeholders = [
        'top-chord-diagram-placeholder',
        'bottom-chord-diagram-placeholder',
        'left-chord-diagram-placeholder',
        'right-chord-diagram-placeholder'
    ];

    // Hide all placeholders
    placeholders.forEach(placeholderId => {
        const placeholder = document.getElementById(placeholderId);
        if (placeholder) {
            placeholder.classList.add('d-none');
        }
    });

    // Handle "None" option
    if (position === 'none') {
        // Hide the chord container if it exists
        const chordContainer = document.getElementById('chord-container');
        if (chordContainer) {
            chordContainer.classList.add('d-none');
        } else {
            console.error("Chord container not found.");
        }
        // Adjust lyrics-container for no chords
        adjustLyricsContainer(position);
        return; // Exit early since no further action is needed
    }

    // Find the selected placeholder
    const selectedPlaceholder = document.getElementById(`${position}-chord-diagram-placeholder`);
    if (selectedPlaceholder) {
        selectedPlaceholder.classList.remove('d-none'); // Make it visible
    } else {
        console.warn(`Placeholder for position "${position}" not found.`);
        return; // Exit if the placeholder doesn't exist
    }

    // Append the chord container to the selected placeholder
    const chordContainer = document.getElementById('chord-container');
    if (chordContainer) {
        selectedPlaceholder.appendChild(chordContainer);
        chordContainer.classList.remove('d-none'); // Ensure visibility
    } else {
        console.error("Chord container not found.");
        return; // Exit if the chord container doesn't exist
    }

    // Adjust layout for top and bottom positions
    if (position === 'top' || position === 'bottom') {
        chordContainer.classList.add('horizontal');
        chordContainer.classList.remove('vertical');
        chordContainer.style.display = 'flex';
        chordContainer.style.flexDirection = 'row'; // Horizontal layout
        chordContainer.style.flexWrap = 'wrap'; // Allow wrapping
        chordContainer.style.justifyContent = 'center'; // Center-align
    } else {
        // Reset layout for left and right positions
        chordContainer.classList.add('vertical');
        chordContainer.classList.remove('horizontal');
        chordContainer.style.display = 'flex';
        chordContainer.style.flexDirection = 'column'; // Vertical layout
        chordContainer.style.flexWrap = 'nowrap';
        chordContainer.style.justifyContent = 'flex-start'; // Align to top/left
    }

    // Dynamically adjust lyrics-container
    adjustLyricsContainer(position);
}




function adjustLyricsContainer(position) {
    const lyricsContainer = document.getElementById('lyrics-container');
    if (!lyricsContainer) {
        console.warn('Lyrics container not found.');
        return;
    }

    if (position === 'left' || position === 'right') {
        // Shrink lyrics container for left/right positioning
        lyricsContainer.style.flex = '0 0 70%'; // 70% width
    } else {
        // Expand lyrics container for top/bottom positioning
        lyricsContainer.style.flex = '1 1 auto'; // Full width
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('printPreviewModal');
    const instrumentSelector = document.getElementById('instrument-selector');
    if (instrumentSelector) {
        loadInstrumentData(instrumentSelector.value); // Load default instrument
    }
    modal.addEventListener('show.bs.modal', function () {
        // Populate the modal song header and lyrics
        document.getElementById('modal-song-header').innerHTML = document.getElementById('song_header').outerHTML;
        document.getElementById('modal-lyrics-container').innerHTML = document.getElementById('song-content').innerHTML;

        // Define modal placeholders
        const modalPlaceholders = {
            top: document.getElementById('modal-top-chord-placeholder'),
            bottom: document.getElementById('modal-bottom-chord-placeholder'),
            left: document.getElementById('modal-left-chord-placeholder'),
            right: document.getElementById('modal-right-chord-placeholder'),
        };

        // Define main view placeholders
        const mainPlaceholders = {
            top: document.getElementById('top-chord-diagram-placeholder'),
            bottom: document.getElementById('bottom-chord-diagram-placeholder'),
            left: document.getElementById('left-chord-diagram-placeholder'),
            right: document.getElementById('right-chord-diagram-placeholder'),
        };

        // Clear all modal placeholders
        Object.values(modalPlaceholders).forEach(placeholder => {
            placeholder.innerHTML = ''; // Clear content
            placeholder.classList.add('d-none'); // Hide by default
        });

        // Populate modal placeholders from the main view
        Object.keys(mainPlaceholders).forEach(position => {
            const mainPlaceholder = mainPlaceholders[position];
            const modalPlaceholder = modalPlaceholders[position];

            if (mainPlaceholder && mainPlaceholder.innerHTML.trim()) {
                // Copy content to the corresponding modal placeholder
                modalPlaceholder.innerHTML = mainPlaceholder.innerHTML;
                modalPlaceholder.classList.remove('d-none'); // Show the placeholder

                // Apply layout-specific classes
                if (position === 'top' || position === 'bottom') {
                    modalPlaceholder.classList.add('horizontal');
                    modalPlaceholder.classList.remove('vertical');
                } else {
                    modalPlaceholder.classList.add('vertical');
                    modalPlaceholder.classList.remove('horizontal');
                }
            }
        });

        console.log('Modal placeholders populated successfully.');
    });
});
