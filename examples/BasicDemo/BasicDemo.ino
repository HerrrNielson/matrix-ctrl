// Einfaches Demo fuer den 3x3x3 LED-Wuerfel
// Zeigt die wichtigsten Funktionen der MatrixCube-Library

#include <MatrixCube.h>

// Pins fuer die 9 vertikalen Spalten
uint8_t vPins[9] = {4, 5, 6, 7, 8, 9, 10, 11, 12};

// Pins fuer die 3 horizontalen Ebenen (unten -> oben)
uint8_t hPins[3] = {13, 3, 2};

// Wuerfel-Objekt erstellen
MatrixCube cube(vPins, hPins);

void setup() {
    cube.begin(); // Pins und Timer initialisieren
}

void loop() {

    // --- Alle LEDs an ---
    cube.fillAll();
    delay(800);

    // --- Alle LEDs aus ---
    cube.clear();
    delay(400);

    // --- Einzelne LEDs setzen ---
    cube.setLed(0, 0, 0, LED_ON);  // untere linke vorne
    cube.setLed(1, 1, 1, LED_ON);  // Mitte
    cube.setLed(2, 2, 2, LED_ON);  // obere rechte hinten
    delay(800);
    cube.clear();

    // --- Ebenen nacheinander aufleuchten ---
    for (uint8_t layer = 0; layer < 3; layer++) {
        cube.fillLayer(layer, LED_ON);
        delay(300);
        cube.fillLayer(layer, LED_OFF);
    }

    // --- Kanten des Wuerfels ---
    cube.drawEdges(LED_ON);
    delay(800);
    cube.clear();

    // --- Aussenschale ---
    cube.fillShell(LED_ON);
    delay(800);
    cube.clear();

    // --- Scroll-Effekt: Ebene von unten nach oben ---
    cube.fillLayer(0, LED_ON);
    delay(200);
    for (uint8_t i = 0; i < 4; i++) {
        cube.shift(AXIS_X, +1); // eine Position nach oben schieben
        delay(200);
    }
    cube.clear();

    // --- Scroll mit Wrap: Ebene kreist endlos ---
    cube.fillLayer(0, LED_ON);
    for (uint8_t i = 0; i < 6; i++) {
        cube.shift(AXIS_X, +1, true); // wrap=true -> kommt unten wieder rein
        delay(200);
    }
    cube.clear();

    delay(500);
}
