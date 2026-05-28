# MatrixCube

Arduino Library zur Steuerung eines N×N×N LED-Würfels mit Multiplexing.  
Entwickelt für den Arduino Nano (ATmega328P) im Rahmen eines Schulprojekts.

---

## Inhalt

```
src/
  MatrixCube.h        – Deklaration und Template-Implementierung
  MatrixCube.cpp      – Timer-Interrupt (ISR)
examples/
  BasicDemo/          – Einfaches Demo-Programm
  Animations/         – Verschiedene Animationen
library.properties    – Arduino IDE Metadaten
keywords.txt          – Syntax-Highlighting in der IDE
MatrixCube_Praesentation.pptx  – Präsentation zur Library
```

---

## Hardware

| Pins | Anzahl | Funktion |
|------|--------|----------|
| vPins | N×N | Schalten die Spalten innerhalb einer Ebene |
| hPins | N   | Schalten die einzelnen Ebenen ein/aus |

**Standard-Belegung (3×3×3):**
```
vPins: 4, 5, 6, 7, 8, 9, 10, 11, 12
hPins: 13, 3, 2
```

---

## Schnellstart

```cpp
#include <MatrixCube.h>

uint8_t vPins[9] = {4, 5, 6, 7, 8, 9, 10, 11, 12};
uint8_t hPins[3] = {13, 3, 2};

MatrixCube<3> cube(vPins, hPins);  // <3> = Würfelgröße

void setup() {
    cube.begin();
}

void loop() {
    cube.fillAll();
    delay(500);
    cube.clear();
    delay(500);
}
```

Für andere Würfelgrößen einfach `<3>` durch `<4>` oder `<5>` ersetzen und die Pin-Arrays entsprechend anpassen (N×N vPins, N hPins).

---

## Funktionsübersicht

### Initialisierung
| Funktion | Beschreibung |
|----------|-------------|
| `begin()` | Pins und Timer einrichten – einmal in `setup()` aufrufen |

### Einzelne LED
| Funktion | Beschreibung |
|----------|-------------|
| `setLed(x, y, z, state)` | Eine LED setzen – `LED_ON`, `LED_OFF` oder `LED_TOGGLE` |
| `getLed(x, y, z)` | Aktuellen Zustand abfragen (`true` = an) |
| `toggleLed(x, y, z)` | LED umschalten (an ↔ aus) |

### Gruppen
| Funktion | Beschreibung |
|----------|-------------|
| `fillAll()` | Alle LEDs einschalten |
| `clear()` | Alle LEDs ausschalten |
| `fillLayer(layer, state)` | Komplette Ebene setzen (0 = unten, N-1 = oben) |
| `fillBox(xl,xu, yl,yu, zl,zu, state)` | Rechteckigen Bereich setzen |
| `fillShell(state)` | Nur die Außenhülle setzen (Kern bleibt unverändert) |

### Formen
| Funktion | Beschreibung |
|----------|-------------|
| `drawEdges(state)` | Die 12 Kanten des Würfels zeichnen |
| `drawPlane(axis, pos, state)` | Flache Scheibe entlang einer Achse zeichnen |
| `drawPillar(axis, a, b, state)` | Säule entlang einer Achse zeichnen |

### Scroll & Transformation
| Funktion | Beschreibung |
|----------|-------------|
| `shift(axis, dir, wrap)` | Gesamten Inhalt um 1 Position verschieben |
| `mirror(axis)` | Würfelinhalt entlang einer Achse spiegeln |
| `copyLayer(from, to)` | Eine Ebene auf eine andere kopieren |

### Konstanten
| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `LED_ON` | 1 | LED einschalten |
| `LED_OFF` | 0 | LED ausschalten |
| `LED_TOGGLE` | -1 | LED umschalten |
| `AXIS_X` | 0 | Horizontale Achse (Ebenen) |
| `AXIS_Y` | 1 | Tiefe |
| `AXIS_Z` | 2 | Breite |

---

## RAM-Verbrauch (Arduino Nano: 2048 Byte)

| Größe | LED-Puffer | Pins |
|-------|-----------|------|
| 3×3×3 | 27 Byte | 12 Pins |
| 4×4×4 | 64 Byte | 20 Pins |
| 5×5×5 | 125 Byte | 30 Pins ⚠️ zu viele für Nano |
