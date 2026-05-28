// Animationen fuer den 3x3x3 LED-Wuerfel
// Fuer andere Groessen: <3> durch <N> ersetzen und Pin-Arrays anpassen.

#include <MatrixCube.h>

uint8_t vPins[9] = {4, 5, 6, 7, 8, 9, 10, 11, 12};
uint8_t hPins[3] = {13, 3, 2};

MatrixCube<3> cube(vPins, hPins);

void setup() {
    cube.begin();
}

void loop() {
    animation_Blinken();
    animation_EbenenHoch();
    animation_EbenenRunter();
    animation_SaeulenNacheinander();
    animation_SpiralScroll();
    animation_SchaleZuKern();
}

void animation_Blinken() {
    for (uint8_t i = 0; i < 5; i++) {
        cube.fillAll();
        delay(300);
        cube.clear();
        delay(300);
    }
}

void animation_EbenenHoch() {
    for (uint8_t layer = 0; layer < 3; layer++) {
        cube.clear();
        cube.fillLayer(layer);
        delay(400);
    }
    cube.clear();
}

void animation_EbenenRunter() {
    for (int8_t layer = 2; layer >= 0; layer--) {
        cube.clear();
        cube.fillLayer(layer);
        delay(400);
    }
    cube.clear();
}

void animation_SaeulenNacheinander() {
    cube.clear();
    for (uint8_t y = 0; y < 3; y++) {
        for (uint8_t z = 0; z < 3; z++) {
            cube.drawPillar(AXIS_X, y, z, LED_ON);
            delay(120);
        }
    }
    delay(400);
    cube.clear();
}

void animation_SpiralScroll() {
    cube.clear();
    cube.fillLayer(0);
    for (uint8_t runde = 0; runde < 3; runde++) {
        for (uint8_t schritt = 0; schritt < 3; schritt++) {
            cube.shift(AXIS_X, +1, true);
            delay(150);
        }
    }
    cube.clear();
}

void animation_SchaleZuKern() {
    cube.clear();
    cube.fillShell(LED_ON);
    delay(600);
    cube.setLed(1, 1, 1, LED_ON);  // Mittelpunkt
    delay(400);
    cube.fillShell(LED_OFF);
    delay(400);
    cube.setLed(1, 1, 1, LED_OFF);
    delay(300);
}
