(function (Raphael) {
    Raphael.chord = {
        data: null, // Stores the chord data
        currentInstrument: "ukulele", // Default instrument
        isLefty: false, // Default lefty mode is off

        setInstrument: function (instrument) {
            this.currentInstrument = instrument;
        },

        toggleLeftyMode: function (isLefty) {
            this.isLefty = isLefty;
        },

        loadData: async function (filePath) {
            try {
                const response = await fetch(filePath);
                this.data = await response.json();
            } catch (error) {
                // swallow, caller can handle
            }
        },

        find: function (chordName, variation) {
            if (!this.data) return undefined;

            const chord = this.data.find((c) => c.name === chordName);
            if (!chord) {
                console.error(`Chord ${chordName} not found.`);
                return undefined;
            }

            variation = variation || 1; // Default to first variation
            if (variation > chord.variations.length) {
                variation = chord.variations.length;
            }
            return chord.variations[variation - 1];
        }
    };

    /**
     * Flexible API:
     *  - Legacy:
     *      new Raphael.chord.Chord(container, [3,2,1,1], "C#", 3)
     *  - Rich object:
     *      new Raphael.chord.Chord(container, {
     *          positions:[6,5,4,4],
     *          baseFret:4,
     *          barre:{ fromString:1, toString:4, fret:4 },
     *          fingers:[1,3,4,2]
     *      }, "C#")
     */
    Raphael.chord.Chord = function (elementOrPosition, data, labelOrVariant, offsetOrOptions) {
        const element = (typeof elementOrPosition === 'string' || elementOrPosition instanceof HTMLElement)
            ? Raphael(elementOrPosition, 100, 140)
            : Raphael(elementOrPosition.x, elementOrPosition.y, 100, 140);

        element.setViewBox(0, 0, 100, 140);

        // -----------------------------
        // Parse inputs / build options
        // -----------------------------
        let positions;
        let baseFret = 1;
        let offset = 0;
        let fingers = null;
        let barre = null;

        const isPositionsObject = (data && typeof data === 'object' && Array.isArray(data.positions));

        if (isPositionsObject) {
            positions = data.positions.slice();
            baseFret = typeof data.baseFret === 'number' ? data.baseFret : 1;
            fingers = Array.isArray(data.fingers) ? data.fingers.slice() : null;
            barre = data.barre || null;

            // offset is baseFret - 1
            offset = Math.max(0, baseFret - 1);

        } else {
            // Legacy array
            positions = Array.isArray(data) ? data.slice() : [];
            // If a 4th param (number) is passed, treat as offset
            if (typeof offsetOrOptions === 'number') {
                offset = offsetOrOptions;
                baseFret = offset + 1;
            } else if (typeof offsetOrOptions === 'object' && offsetOrOptions) {
                // if they passed an options object as 4th param
                baseFret = offsetOrOptions.baseFret || 1;
                offset = offsetOrOptions.offset || Math.max(0, baseFret - 1);
                fingers = offsetOrOptions.fingers || null;
                barre = offsetOrOptions.barre || null;
            } else {
                // auto-offset rule: only offset if the minimum fretted note > 3
                const activeFrets = positions.filter(f => f > 0);
                if (activeFrets.length) {
                    const minFret = Math.min(...activeFrets);
                    if (minFret > 3) {
                        baseFret = minFret;
                        offset = baseFret - 1;
                    }
                }
            }
        }

        const chordLabel = labelOrVariant || "";

        const numStrings = positions.length;
        const fretCount = 5; // number of frets to show
        const fretboardWidth = 100;
        const fretboardHeight = 90;
        const stringSpacing = (fretboardWidth - 40) / (numStrings - 1);
        const fretSpacing = fretboardHeight / fretCount;
        const xStart = 20;
        const yStart = 40;

        // Light border
        element.rect(0, 0, 100, 140).attr({
            stroke: '#ccc',
            'stroke-width': 1,
            fill: 'none'
        });

        // Detect if all strings open (0 or -1 won't count here as fretted)
        const allStringsOpen = positions.every((fret) => fret === 0);

        // --------------------------------
        // Draw chord name label (top)
        // --------------------------------
        if (chordLabel) {
            element.text(50, 10, chordLabel).attr({
                'font-size': 16,
                'font-weight': 'bold',
                'text-anchor': 'middle',
                'font-family': 'Arial, sans-serif'
            });
        }

        // --------------------------------
        // Draw strings
        // --------------------------------
        const stringPositions = [];
        for (let i = 0; i < numStrings; i++) {
            const x = xStart + i * stringSpacing;
            const xpos = Raphael.chord.isLefty ? (xStart + (numStrings - 1) * stringSpacing) - (x - xStart) : x;
            stringPositions.push(xpos);
            element.path(`M${xpos} ${yStart}L${xpos} ${yStart + fretboardHeight}`);
        }

        // --------------------------------
        // Draw frets
        // --------------------------------
        for (let i = 0; i <= fretCount; i++) {
            const y = yStart + i * fretSpacing;
            const isNut = (i === 0 && offset === 0);
            element.path(`M${xStart} ${y}L${xStart + (numStrings - 1) * stringSpacing} ${y}`)
                .attr({ stroke: '#000', 'stroke-width': isNut ? 4 : 1 });
        }

        // --------------------------------
        // Base fret label (e.g., "4fr") if offset > 0
        // --------------------------------
        if (offset > 0) {
            element.text(5, yStart + fretSpacing / 2, `${baseFret}fr`).attr({
                'font-size': 10,
                'font-family': 'Arial, sans-serif',
                'text-anchor': 'start'
            });
        }

        // --------------------------------
        // Barre rendering (if provided)
        // barre = { fromString: 1, toString: X, fret: N (absolute) }
        // --------------------------------
        const drawBarre = (barreObj) => {
            if (!barreObj) return;
            const from = barreObj.fromString;
            const to = barreObj.toString;
            const absoluteFret = barreObj.fret;
            if (!(from >= 1 && to >= from && absoluteFret > 0)) return;

            const adjustedFret = absoluteFret - offset; // shift by offset
            if (adjustedFret < 1 || adjustedFret > fretCount) return;

            const topStringX = stringPositions[from - 1];
            const bottomStringX = stringPositions[to - 1];
            const barY = yStart + adjustedFret * fretSpacing - fretSpacing / 2;

            const rectX = Math.min(topStringX, bottomStringX) - 6;
            const rectWidth = Math.abs(bottomStringX - topStringX) + 12;
            const rectY = barY - 6;
            const rectHeight = 12;

            element.rect(rectX, rectY, rectWidth, rectHeight, 6).attr({
                fill: '#000',
                stroke: 'none',
                opacity: 1
            });
        };

        // Render barre first so dots drawn later can skip overlapping positions
        if (barre) {
            drawBarre(barre);
        }

        // --------------------------------
        // Dots / open / muted markers
        // --------------------------------
        positions.forEach((fret, i) => {
            const x = stringPositions[i];

            if (fret === -1) {
                // Muted
                element.text(x, yStart - 10, 'X').attr({
                    'font-size': 10,
                    'font-family': 'Arial',
                    'text-anchor': 'middle'
                });
            } else if (fret === 0) {
                // Open
                element.circle(x, yStart - 10, 4).attr({ stroke: '#000', fill: '#fff' });
            } else if (fret > 0) {
                const adjusted = fret - offset;
                if (adjusted > 0) {
                    const y = yStart + adjusted * fretSpacing - fretSpacing / 2;

                    // If barre exists, don't overdraw dots that are under the barre
                    const coveredByBarre = (barre &&
                        (i + 1) >= barre.fromString &&
                        (i + 1) <= barre.toString &&
                        fret === barre.fret);

                    if (!coveredByBarre) {
                        const dot = element.circle(x, y, 5).attr({ fill: '#000' });

                        if (fingers && fingers[i]) {
                            element.text(x, y, fingers[i]).attr({
                                'font-size': 8,
                                'font-family': 'Arial',
                                fill: '#fff'
                            });
                        }
                    }
                }
            }
        });

        return { element };
    };

    // Expose Raphael's chord functionality
    window.Raphael.chord = Raphael.chord;
})(window.Raphael);
