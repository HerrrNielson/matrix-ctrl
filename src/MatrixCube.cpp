#include "MatrixCube.h"

// Globaler Zeiger – der Timer-Interrupt braucht ihn, um die _isr()-Methode
// der Klasse aufzurufen, ohne den Template-Typ kennen zu muessen.
MatrixCubeBase* _cubeInstance = nullptr;

// Timer1 Compare-Match-Interrupt
ISR(TIMER1_COMPA_vect) {
    if (_cubeInstance != nullptr) {
        _cubeInstance->_isr();
    }
}
