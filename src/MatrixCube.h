#ifndef MATRIXCUBE_H
#define MATRIXCUBE_H

#include <Arduino.h>

// Konstanten fuer den state-Parameter
#define LED_ON     1
#define LED_OFF    0
#define LED_TOGGLE -1

// Achsen-Konstanten fuer shift() und drawPlane()
#define AXIS_X 0
#define AXIS_Y 1
#define AXIS_Z 2

class MatrixCube {
public:
    // -------------------------------------------------------------
    // Konstruktor
    //   vPins: Array mit 9 Pins fuer die vertikalen Spalten
    //   hPins: Array mit 3 Pins fuer die horizontalen Ebenen
    // -------------------------------------------------------------
    MatrixCube(const uint8_t vPins[9], const uint8_t hPins[3]);

    // Pins und Timer einrichten – einmal in setup() aufrufen
    void begin();


    // =============================================================
    // Einzelne LED
    // =============================================================

    // Eine LED an Position (x, y, z) setzen
    // x = Ebene (0 = unten, 2 = oben)
    // y, z = Position in der Ebene (0..2)
    // state: LED_ON, LED_OFF oder LED_TOGGLE
    void setLed(uint8_t x, uint8_t y, uint8_t z, int8_t state = LED_ON);

    // Zustand einer LED abfragen (true = an)
    bool getLed(uint8_t x, uint8_t y, uint8_t z);

    // Eine LED umschalten (an -> aus oder aus -> an)
    void toggleLed(uint8_t x, uint8_t y, uint8_t z);


    // =============================================================
    // Mehrere LEDs auf einmal
    // =============================================================

    // Alle LEDs einschalten
    void fillAll();

    // Alle LEDs ausschalten
    void clear();

    // Eine komplette Ebene setzen (layer: 0..2)
    void fillLayer(uint8_t layer, int8_t state = LED_ON);

    // Einen rechteckigen Bereich setzen
    // xl..xu = Ebenen-Bereich, yl..yu = Y-Bereich, zl..zu = Z-Bereich (jeweils 0..2)
    void fillBox(uint8_t xl, uint8_t xu,
                 uint8_t yl, uint8_t yu,
                 uint8_t zl, uint8_t zu,
                 int8_t state = LED_ON);

    // Nur die Aussenhuelle des Wuerfels einschalten (Mittelpunkt bleibt aus)
    void fillShell(int8_t state = LED_ON);


    // =============================================================
    // Formen zeichnen
    // =============================================================

    // Nur die 12 Kanten des Wuerfels einschalten
    void drawEdges(int8_t state = LED_ON);

    // Eine ganze Ebene (Scheibe) zeichnen
    // axis: AXIS_X (Hoehe), AXIS_Y oder AXIS_Z
    // pos: 0, 1 oder 2
    void drawPlane(uint8_t axis, uint8_t pos, int8_t state = LED_ON);

    // Eine senkrechte Saeule zeichnen
    // axis gibt die Richtung an, a und b sind die anderen beiden Koordinaten
    void drawPillar(uint8_t axis, uint8_t a, uint8_t b, int8_t state = LED_ON);


    // =============================================================
    // Verschieben (Scroll-Effekte)
    // =============================================================

    // Den gesamten Inhalt des Wuerfels um eine Position verschieben
    // axis: AXIS_X / AXIS_Y / AXIS_Z
    // dir: +1 (vorwaerts) oder -1 (rueckwaerts)
    // wrap: true = LEDs die herausfallen tauchen auf der anderen Seite wieder auf
    void shift(uint8_t axis, int8_t dir, bool wrap = false);


    // =============================================================
    // Spiegeln und Kopieren
    // =============================================================

    // Den Wuerfel entlang einer Achse spiegeln
    void mirror(uint8_t axis);

    // Eine Ebene auf eine andere kopieren
    void copyLayer(uint8_t from, uint8_t to);


    // =============================================================
    // Interner ISR-Aufruf – NICHT manuell aufrufen!
    // =============================================================
    void _isr();

private:
    uint8_t _vPin[9];
    uint8_t _hPin[3];

    // LED-Puffer: [Ebene 0..2][Y 0..2][Z 0..2]
    volatile uint8_t _led[3][3][3];

    // Welche Ebene gerade vom Multiplexer angesteuert wird
    volatile uint8_t _layer;

    // Wert auf 0..2 begrenzen
    static uint8_t clamp(uint8_t v) { return v > 2 ? 2 : v; }
};

// Globaler Zeiger fuer den Timer-Interrupt
extern MatrixCube* _cubeInstance;

#endif
