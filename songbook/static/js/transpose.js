const chordMap = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11};
const reverseChordMap = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'};

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

function renderSong(songDict, semitones) {
    const songContainer = document.getElementById('song-content');
    songContainer.innerHTML = '';
    songDict.forEach(section => {
        section.forEach(item => {
            if (item.chord !== undefined) {
                const transposedChord = item.chord ? transposeChord(item.chord, semitones) : '';
                if (transposedChord) {
                    songContainer.innerHTML += `<span class="line"><span class="chord">[${transposedChord}]</span> <span class="lyric">${item.lyric}</span></span>`;
                } else {
                    songContainer.innerHTML += `<span class="line"><span class="lyric">${item.lyric}</span></span>`;
                }
            } else if (item.format === 'LINEBREAK') {
                songContainer.innerHTML += '<br>';
            } else if (item.directive) {
                if (item.directive === "{sov}") {
                    songContainer.innerHTML += '<div class="verse"><h3>Verse</h3>';
                } else if (item.directive === "{eov}") {
                    songContainer.innerHTML += '</div>';
                } else if (item.directive === "{soc}") {
                    songContainer.innerHTML += '<div class="chorus"><h3>Chorus</h3>';
                } else if (item.directive === "{eoc}") {
                    songContainer.innerHTML += '</div>';
                } else if (item.directive === "{sob}") {
                    songContainer.innerHTML += '<div class="bridge"><h3>Bridge</h3>';
                } else if (item.directive === "{eob}") {
                    songContainer.innerHTML += '</div>';
                }
            }
        });
    });
}

function transposeSong(semitones) {
    renderSong(songDict, parseInt(semitones));
}

// Initial render
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed'); // Debugging: Check if DOMContentLoaded event is fired
    renderSong(songDict, 0);
});