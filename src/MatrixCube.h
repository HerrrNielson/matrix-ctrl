#ifndef MATRIXCUBE_H
#define MATRIXCUBE_H

#include <Arduino.h>
#include <avr/interrupt.h>

// Konstanten fuer den state-Parameter
#define LED_ON     1
#define LED_OFF    0
#define LED_TOGGLE -1

// Achsen-Konstanten fuer shift() und drawPlane()
#define AXIS_X 0
#define AXIS_Y 1
#define AXIS_Z 2

// ---------------------------------------------------------------------------
// Abstrakte Basisklasse – nur damit der ISR die _isr()-Methode aufrufen kann,
// ohne den Template-Typ kennen zu muessen.
// ---------------------------------------------------------------------------
class MatrixCubeBase {
public:
    virtual void _isr() = 0;
};

// Globaler Zeiger fuer den Timer-Interrupt (definiert in MatrixCube.cpp)
extern MatrixCubeBase* _cubeInstance;


// ---------------------------------------------------------------------------
// Template-Klasse MatrixCube<N>
//
//   N  = Seitenlaenge des Wuerfels (z.B. 3 fuer 3x3x3, 4 fuer 4x4x4)
//   vPins muss N*N Pins enthalten (Spalten)
//   hPins muss N   Pins enthalten (Ebenen)
//
// Achtung RAM-Verbrauch: N^3 Bytes fuer den LED-Puffer
//   N=3 -> 27 Byte, N=4 -> 64 Byte, N=5 -> 125 Byte
// Arduino Nano hat 2048 Byte RAM – N=5 ist das sinnvolle Maximum.
// ---------------------------------------------------------------------------
template <uint8_t N>
class MatrixCube : public MatrixCubeBase {
public:

    // -----------------------------------------------------------------------
    // Konstruktor
    //   vPins: Array mit N*N Pins fuer die vertikalen Spalten
    //   hPins: Array mit N   Pins fuer die horizontalen Ebenen
    // -----------------------------------------------------------------------
    MatrixCube(const uint8_t vPins[N * N], const uint8_t hPins[N])
        : _layer(0)
    {
        for (uint8_t i = 0; i < N * N; i++) _vPin[i] = vPins[i];
        for (uint8_t i = 0; i < N;     i++) _hPin[i] = hPins[i];
        memset((void*)_led, 0, sizeof(_led));
    }

    // Pins und Timer einrichten – einmal in setup() aufrufen
    void begin() {
        for (uint8_t i = 0; i < N * N; i++) pinMode(_vPin[i], OUTPUT);
        for (uint8_t i = 0; i < N;     i++) {
            pinMode(_hPin[i], OUTPUT);
            digitalWrite(_hPin[i], LOW);
        }

        _cubeInstance = this;

        // Timer1: CTC-Modus, Prescaler 256
        // 16 MHz / 256 / 104 = ~600 Interrupts/s -> jede Ebene ~600/N mal/s aufgefrischt
        cli();
        TCCR1A = 0;
        TCCR1B = 0;
        TCNT1  = 0;
        OCR1A  = 103;
        TCCR1B |= (1 << WGM12);   // CTC-Modus
        TCCR1B |= (1 << CS12);    // Prescaler 256
        TIMSK1 |= (1 << OCIE1A);  // Interrupt freischalten
        sei();
    }


    // =======================================================================
    // Einzelne LED
    // =======================================================================

    // Eine LED an Position (x, y, z) setzen
    // x = Ebene (0 = unten, N-1 = oben), y und z = Position in der Ebene
    void setLed(uint8_t x, uint8_t y, uint8_t z, int8_t state = LED_ON) {
        x = clamp(x); y = clamp(y); z = clamp(z);
        cli();
        applyState(_led[x][y][z], state);
        sei();
    }

    // Zustand einer LED abfragen (true = an)
    bool getLed(uint8_t x, uint8_t y, uint8_t z) {
        return _led[clamp(x)][clamp(y)][clamp(z)];
    }

    // Eine LED umschalten (an -> aus oder aus -> an)
    void toggleLed(uint8_t x, uint8_t y, uint8_t z) {
        setLed(x, y, z, LED_TOGGLE);
    }


    // =======================================================================
    // Mehrere LEDs auf einmal
    // =======================================================================

    // Alle LEDs einschalten
    void fillAll() {
        fillBox(0, N-1, 0, N-1, 0, N-1, LED_ON);
    }

    // Alle LEDs ausschalten
    void clear() {
        fillBox(0, N-1, 0, N-1, 0, N-1, LED_OFF);
    }

    // Eine komplette Ebene setzen (layer: 0 .. N-1)
    void fillLayer(uint8_t layer, int8_t state = LED_ON) {
        fillBox(layer, layer, 0, N-1, 0, N-1, state);
    }

    // Einen rechteckigen Bereich setzen (Grenzen inklusive, jeweils 0 .. N-1)
    void fillBox(uint8_t xl, uint8_t xu,
                 uint8_t yl, uint8_t yu,
                 uint8_t zl, uint8_t zu,
                 int8_t state = LED_ON)
    {
        xl = clamp(xl); xu = clamp(xu);
        yl = clamp(yl); yu = clamp(yu);
        zl = clamp(zl); zu = clamp(zu);
        cli();
        for (uint8_t x = xl; x <= xu; x++)
            for (uint8_t y = yl; y <= yu; y++)
                for (uint8_t z = zl; z <= zu; z++)
                    applyState(_led[x][y][z], state);
        sei();
    }

    // Nur die Aussenhuelle des Wuerfels setzen (Mittelpunkt bleibt unveraendert)
    void fillShell(int8_t state = LED_ON) {
        cli();
        for (uint8_t x = 0; x < N; x++)
            for (uint8_t y = 0; y < N; y++)
                for (uint8_t z = 0; z < N; z++) {
                    // Auf der Schale, wenn mindestens eine Koordinate am Rand liegt
                    if (x == 0 || x == N-1 || y == 0 || y == N-1 || z == 0 || z == N-1)
                        applyState(_led[x][y][z], state);
                }
        sei();
    }


    // =======================================================================
    // Formen zeichnen
    // =======================================================================

    // Die 12 Kanten des Wuerfels zeichnen
    // (Positionen wo mindestens 2 Koordinaten einen Eckwert haben)
    void drawEdges(int8_t state = LED_ON) {
        cli();
        for (uint8_t x = 0; x < N; x++)
            for (uint8_t y = 0; y < N; y++)
                for (uint8_t z = 0; z < N; z++) {
                    uint8_t corners = 0;
                    if (x == 0 || x == N-1) corners++;
                    if (y == 0 || y == N-1) corners++;
                    if (z == 0 || z == N-1) corners++;
                    if (corners >= 2)
                        applyState(_led[x][y][z], state);
                }
        sei();
    }

    // Eine ganze Ebene (Scheibe) zeichnen
    // axis: AXIS_X (horizontal), AXIS_Y oder AXIS_Z (vertikal)
    // pos: 0 .. N-1
    void drawPlane(uint8_t axis, uint8_t pos, int8_t state = LED_ON) {
        pos = clamp(pos);
        switch (axis) {
            case AXIS_X: fillBox(pos,  pos,  0, N-1, 0, N-1, state); break;
            case AXIS_Y: fillBox(0, N-1, pos,  pos,  0, N-1, state); break;
            case AXIS_Z: fillBox(0, N-1, 0, N-1, pos,  pos,  state); break;
        }
    }

    // Eine Saeule zeichnen
    // axis: Richtung der Saeule, a und b sind die anderen beiden Koordinaten
    void drawPillar(uint8_t axis, uint8_t a, uint8_t b, int8_t state = LED_ON) {
        a = clamp(a); b = clamp(b);
        switch (axis) {
            case AXIS_X: fillBox(0, N-1, a,   a,   b,   b,   state); break;
            case AXIS_Y: fillBox(a,   a,   0, N-1, b,   b,   state); break;
            case AXIS_Z: fillBox(a,   a,   b,   b,   0, N-1, state); break;
        }
    }


    // =======================================================================
    // Verschieben (Scroll-Effekte)
    // =======================================================================

    // Den gesamten Inhalt des Wuerfels um eine Position verschieben
    // axis: AXIS_X / AXIS_Y / AXIS_Z
    // dir: +1 (vorwaerts) oder -1 (rueckwaerts)
    // wrap: true -> LEDs die herausfallen kommen auf der anderen Seite wieder rein
    void shift(uint8_t axis, int8_t dir, bool wrap = false) {
        uint8_t tmp[N][N][N];
        cli();
        memcpy(tmp, (const void*)_led, sizeof(tmp));
        memset((void*)_led, 0, sizeof(_led));

        for (uint8_t x = 0; x < N; x++)
            for (uint8_t y = 0; y < N; y++)
                for (uint8_t z = 0; z < N; z++) {
                    int8_t nx = (int8_t)x;
                    int8_t ny = (int8_t)y;
                    int8_t nz = (int8_t)z;

                    if      (axis == AXIS_X) nx += dir;
                    else if (axis == AXIS_Y) ny += dir;
                    else                     nz += dir;

                    if (wrap) {
                        nx = ((nx % (int8_t)N) + N) % N;
                        ny = ((ny % (int8_t)N) + N) % N;
                        nz = ((nz % (int8_t)N) + N) % N;
                    } else {
                        if (nx < 0 || nx >= N || ny < 0 || ny >= N || nz < 0 || nz >= N) continue;
                    }

                    _led[nx][ny][nz] = tmp[x][y][z];
                }
        sei();
    }


    // =======================================================================
    // Spiegeln und Kopieren
    // =======================================================================

    // Den Wuerfel entlang einer Achse spiegeln (Ebene 0 <-> Ebene N-1, usw.)
    void mirror(uint8_t axis) {
        cli();
        uint8_t t;
        for (uint8_t a = 0; a < N; a++)
            for (uint8_t b = 0; b < N; b++)
                for (uint8_t i = 0; i < N / 2; i++) {  // nur bis zur Haelfte tauschen
                    uint8_t j = N - 1 - i;
                    switch (axis) {
                        case AXIS_X: t = _led[i][a][b]; _led[i][a][b] = _led[j][a][b]; _led[j][a][b] = t; break;
                        case AXIS_Y: t = _led[a][i][b]; _led[a][i][b] = _led[a][j][b]; _led[a][j][b] = t; break;
                        case AXIS_Z: t = _led[a][b][i]; _led[a][b][i] = _led[a][b][j]; _led[a][b][j] = t; break;
                    }
                }
        sei();
    }

    // Eine Ebene auf eine andere kopieren
    void copyLayer(uint8_t from, uint8_t to) {
        from = clamp(from); to = clamp(to);
        cli();
        for (uint8_t y = 0; y < N; y++)
            for (uint8_t z = 0; z < N; z++)
                _led[to][y][z] = _led[from][y][z];
        sei();
    }


    // =======================================================================
    // ISR-Aufruf – NICHT manuell aufrufen!
    // =======================================================================
    void _isr() override {
        digitalWrite(_hPin[_layer], LOW);

        _layer++;
        if (_layer >= N) _layer = 0;

        for (uint8_t y = 0; y < N; y++)
            for (uint8_t z = 0; z < N; z++)
                digitalWrite(_vPin[y * N + z], _led[_layer][y][z]);

        digitalWrite(_hPin[_layer], HIGH);
    }

private:
    uint8_t          _vPin[N * N];
    uint8_t          _hPin[N];
    volatile uint8_t _led[N][N][N];
    volatile uint8_t _layer;

    // Wert auf 0 .. N-1 begrenzen
    static uint8_t clamp(uint8_t v) { return v >= N ? N - 1 : v; }

    // Hilfsfunktion: state auf eine LED-Variable anwenden
    static void applyState(volatile uint8_t& led, int8_t state) {
        if      (state == LED_ON)     led = 1;
        else if (state == LED_OFF)    led = 0;
        else if (state == LED_TOGGLE) led = !led;
    }
};

#endif
