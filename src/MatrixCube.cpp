#include "MatrixCube.h"
#include <avr/interrupt.h>

// Globaler Zeiger – der Timer-Interrupt braucht ihn, um die Klasse zu erreichen
MatrixCube* _cubeInstance = nullptr;

// ---------------------------------------------------------------------------
// Timer1-Interrupt: schaltet alle 3 Ebenen im Wechsel durch (Multiplexing)
// ---------------------------------------------------------------------------
ISR(TIMER1_COMPA_vect) {
    if (_cubeInstance != nullptr) {
        _cubeInstance->_isr();
    }
}

// ---------------------------------------------------------------------------
// Konstruktor
// ---------------------------------------------------------------------------
MatrixCube::MatrixCube(const uint8_t vPins[9], const uint8_t hPins[3])
    : _layer(0)
{
    for (uint8_t i = 0; i < 9; i++) _vPin[i] = vPins[i];
    for (uint8_t i = 0; i < 3; i++) _hPin[i] = hPins[i];

    // Alle LEDs aus
    memset((void*)_led, 0, sizeof(_led));
}

// ---------------------------------------------------------------------------
// begin – Pins initialisieren und Timer starten
// ---------------------------------------------------------------------------
void MatrixCube::begin() {
    // Alle Pin-Modi setzen
    for (uint8_t i = 0; i < 9; i++) {
        pinMode(_vPin[i], OUTPUT);
    }
    for (uint8_t i = 0; i < 3; i++) {
        pinMode(_hPin[i], OUTPUT);
        digitalWrite(_hPin[i], LOW);
    }

    _cubeInstance = this;

    // Timer1 konfigurieren
    // 16 MHz / 256 (Prescaler) / 104 (OCR1A+1) = ca. 600 Interrupts/Sekunde
    // -> jede Ebene wird ca. 200x pro Sekunde aufgefrischt (flimmerfrei)
    cli();
    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1  = 0;
    OCR1A  = 103;
    TCCR1B |= (1 << WGM12);   // CTC-Modus: zaehlt bis OCR1A, dann wieder 0
    TCCR1B |= (1 << CS12);    // Prescaler 256
    TIMSK1 |= (1 << OCIE1A);  // Compare-Match-Interrupt freischalten
    sei();
}

// ---------------------------------------------------------------------------
// _isr – wird vom Timer-Interrupt aufgerufen
// Schaltet die aktuelle Ebene ab, wechselt zur naechsten und setzt die Spalten
// ---------------------------------------------------------------------------
void MatrixCube::_isr() {
    // Aktuelle Ebene ausschalten
    digitalWrite(_hPin[_layer], LOW);

    // Naechste Ebene auswaehlen
    _layer++;
    if (_layer > 2) _layer = 0;

    // Spalten-Pins der neuen Ebene setzen
    for (uint8_t y = 0; y < 3; y++) {
        for (uint8_t z = 0; z < 3; z++) {
            digitalWrite(_vPin[y * 3 + z], _led[_layer][y][z]);
        }
    }

    // Neue Ebene einschalten
    digitalWrite(_hPin[_layer], HIGH);
}

// ---------------------------------------------------------------------------
// Einzelne LED
// ---------------------------------------------------------------------------

void MatrixCube::setLed(uint8_t x, uint8_t y, uint8_t z, int8_t state) {
    x = clamp(x);
    y = clamp(y);
    z = clamp(z);

    cli();
    if      (state == LED_ON)     _led[x][y][z] = 1;
    else if (state == LED_OFF)    _led[x][y][z] = 0;
    else if (state == LED_TOGGLE) _led[x][y][z] = !_led[x][y][z];
    sei();
}

bool MatrixCube::getLed(uint8_t x, uint8_t y, uint8_t z) {
    return _led[clamp(x)][clamp(y)][clamp(z)];
}

void MatrixCube::toggleLed(uint8_t x, uint8_t y, uint8_t z) {
    setLed(x, y, z, LED_TOGGLE);
}

// ---------------------------------------------------------------------------
// Mehrere LEDs auf einmal
// ---------------------------------------------------------------------------

void MatrixCube::fillAll() {
    fillBox(0, 2, 0, 2, 0, 2, LED_ON);
}

void MatrixCube::clear() {
    fillBox(0, 2, 0, 2, 0, 2, LED_OFF);
}

void MatrixCube::fillLayer(uint8_t layer, int8_t state) {
    fillBox(layer, layer, 0, 2, 0, 2, state);
}

void MatrixCube::fillBox(uint8_t xl, uint8_t xu,
                          uint8_t yl, uint8_t yu,
                          uint8_t zl, uint8_t zu,
                          int8_t state)
{
    xl = clamp(xl); xu = clamp(xu);
    yl = clamp(yl); yu = clamp(yu);
    zl = clamp(zl); zu = clamp(zu);

    cli();
    for (uint8_t x = xl; x <= xu; x++) {
        for (uint8_t y = yl; y <= yu; y++) {
            for (uint8_t z = zl; z <= zu; z++) {
                if      (state == LED_ON)     _led[x][y][z] = 1;
                else if (state == LED_OFF)    _led[x][y][z] = 0;
                else if (state == LED_TOGGLE) _led[x][y][z] = !_led[x][y][z];
            }
        }
    }
    sei();
}

void MatrixCube::fillShell(int8_t state) {
    cli();
    for (uint8_t x = 0; x < 3; x++) {
        for (uint8_t y = 0; y < 3; y++) {
            for (uint8_t z = 0; z < 3; z++) {
                // Eine LED liegt auf der Schale, wenn mindestens eine
                // Koordinate den Rand (0 oder 2) beruehrt
                bool onShell = (x == 0 || x == 2 ||
                                y == 0 || y == 2 ||
                                z == 0 || z == 2);
                if (onShell) {
                    if      (state == LED_ON)     _led[x][y][z] = 1;
                    else if (state == LED_OFF)    _led[x][y][z] = 0;
                    else if (state == LED_TOGGLE) _led[x][y][z] = !_led[x][y][z];
                }
            }
        }
    }
    sei();
}

// ---------------------------------------------------------------------------
// Formen zeichnen
// ---------------------------------------------------------------------------

void MatrixCube::drawEdges(int8_t state) {
    // Die 12 Kanten sind alle Positionen, bei denen mindestens
    // zwei Koordinaten einen Eckwert (0 oder 2) haben
    cli();
    for (uint8_t x = 0; x < 3; x++) {
        for (uint8_t y = 0; y < 3; y++) {
            for (uint8_t z = 0; z < 3; z++) {
                uint8_t corners = 0;
                if (x == 0 || x == 2) corners++;
                if (y == 0 || y == 2) corners++;
                if (z == 0 || z == 2) corners++;

                if (corners >= 2) {
                    if      (state == LED_ON)     _led[x][y][z] = 1;
                    else if (state == LED_OFF)    _led[x][y][z] = 0;
                    else if (state == LED_TOGGLE) _led[x][y][z] = !_led[x][y][z];
                }
            }
        }
    }
    sei();
}

void MatrixCube::drawPlane(uint8_t axis, uint8_t pos, int8_t state) {
    pos = clamp(pos);
    switch (axis) {
        case AXIS_X: fillBox(pos, pos, 0, 2, 0, 2, state); break; // horizontale Ebene
        case AXIS_Y: fillBox(0, 2, pos, pos, 0, 2, state); break; // senkrechte Scheibe in Y
        case AXIS_Z: fillBox(0, 2, 0, 2, pos, pos, state); break; // senkrechte Scheibe in Z
    }
}

void MatrixCube::drawPillar(uint8_t axis, uint8_t a, uint8_t b, int8_t state) {
    a = clamp(a);
    b = clamp(b);
    switch (axis) {
        case AXIS_X: fillBox(0, 2, a, a, b, b, state); break;
        case AXIS_Y: fillBox(a, a, 0, 2, b, b, state); break;
        case AXIS_Z: fillBox(a, a, b, b, 0, 2, state); break;
    }
}

// ---------------------------------------------------------------------------
// Verschieben
// ---------------------------------------------------------------------------

void MatrixCube::shift(uint8_t axis, int8_t dir, bool wrap) {
    // Aktuellen Zustand zwischenspeichern
    uint8_t tmp[3][3][3];

    cli();
    memcpy(tmp, (const void*)_led, sizeof(tmp));
    memset((void*)_led, 0, sizeof(_led));

    for (uint8_t x = 0; x < 3; x++) {
        for (uint8_t y = 0; y < 3; y++) {
            for (uint8_t z = 0; z < 3; z++) {
                // Neue Position berechnen
                int8_t nx = (int8_t)x;
                int8_t ny = (int8_t)y;
                int8_t nz = (int8_t)z;

                if      (axis == AXIS_X) nx += dir;
                else if (axis == AXIS_Y) ny += dir;
                else                     nz += dir;

                if (wrap) {
                    // Wraparound: LEDs, die herausfallen, kommen auf der anderen Seite wieder rein
                    nx = ((nx % 3) + 3) % 3;
                    ny = ((ny % 3) + 3) % 3;
                    nz = ((nz % 3) + 3) % 3;
                } else {
                    // Kein Wrap: LEDs ausserhalb des Wuerfels verschwinden
                    if (nx < 0 || nx > 2 || ny < 0 || ny > 2 || nz < 0 || nz > 2) continue;
                }

                _led[nx][ny][nz] = tmp[x][y][z];
            }
        }
    }
    sei();
}

// ---------------------------------------------------------------------------
// Spiegeln und Kopieren
// ---------------------------------------------------------------------------

void MatrixCube::mirror(uint8_t axis) {
    cli();
    uint8_t t;
    for (uint8_t a = 0; a < 3; a++) {
        for (uint8_t b = 0; b < 3; b++) {
            // Immer die gegenueberliegenden Elemente (0 <-> 2) tauschen
            switch (axis) {
                case AXIS_X:
                    t = _led[0][a][b]; _led[0][a][b] = _led[2][a][b]; _led[2][a][b] = t;
                    break;
                case AXIS_Y:
                    t = _led[a][0][b]; _led[a][0][b] = _led[a][2][b]; _led[a][2][b] = t;
                    break;
                case AXIS_Z:
                    t = _led[a][b][0]; _led[a][b][0] = _led[a][b][2]; _led[a][b][2] = t;
                    break;
            }
        }
    }
    sei();
}

void MatrixCube::copyLayer(uint8_t from, uint8_t to) {
    from = clamp(from);
    to   = clamp(to);

    cli();
    for (uint8_t y = 0; y < 3; y++) {
        for (uint8_t z = 0; z < 3; z++) {
            _led[to][y][z] = _led[from][y][z];
        }
    }
    sei();
}
