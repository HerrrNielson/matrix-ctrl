from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Farben ──────────────────────────────────────────────────────────────────
C_BG        = RGBColor(0x1E, 0x1E, 0x2E)   # dunkles Lila-Schwarz
C_ACCENT    = RGBColor(0x89, 0xB4, 0xFA)   # helles Blau
C_GREEN     = RGBColor(0xA6, 0xE3, 0xA1)   # helles Grün
C_YELLOW    = RGBColor(0xF9, 0xE2, 0xAF)   # Gelb
C_RED       = RGBColor(0xF3, 0x8B, 0xA8)   # Rosa/Rot
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
C_SUBTEXT   = RGBColor(0xA6, 0xAD, 0xC8)   # grau
C_BOX_BG    = RGBColor(0x31, 0x32, 0x44)   # etwas helleres Dunkel
C_BOX_BORDER= RGBColor(0x45, 0x47, 0x5A)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]   # komplett leeres Layout

# ── Hilfsfunktionen ─────────────────────────────────────────────────────────

def add_bg(slide, color=C_BG):
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_rect(slide, x, y, w, h, fill=C_BOX_BG, border=C_BOX_BORDER, radius=None):
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if border:
        shape.line.color.rgb = border
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, x, y, w, h, size=18, bold=False, color=C_WHITE,
             align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.word_wrap = wrap
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb

def add_code(slide, lines, x, y, w, h, size=12):
    """Monospace-Codeblock mit dunklem Hintergrund."""
    add_rect(slide, x, y, w, h, fill=RGBColor(0x18, 0x18, 0x2E), border=C_BOX_BORDER)
    tb = slide.shapes.add_textbox(Inches(x+0.15), Inches(y+0.12),
                                   Inches(w-0.3),  Inches(h-0.24))
    tb.word_wrap = False
    tf = tb.text_frame
    tf.word_wrap = False
    first = True
    for line in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.name = "Courier New"
        # einfaches Syntax-Highlighting
        stripped = line.strip()
        if stripped.startswith("//"):
            run.font.color.rgb = C_SUBTEXT
        elif any(kw in line for kw in ["void ", "bool ", "uint8_t ", "int8_t ",
                                        "class ", "template", "#define", "#ifndef",
                                        "#include", "return", "if ", "for ", "switch"]):
            run.font.color.rgb = C_ACCENT
        elif stripped.startswith("cube.") or stripped.startswith("MatrixCube"):
            run.font.color.rgb = C_GREEN
        else:
            run.font.color.rgb = C_WHITE

def title_slide(prs):
    slide = prs.slides.add_slide(BLANK)
    add_bg(slide)
    # dekorativer Streifen oben
    stripe = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.08))
    stripe.fill.solid(); stripe.fill.fore_color.rgb = C_ACCENT; stripe.line.fill.background()
    # LED-Punkte als Deko
    for i, (cx, cy) in enumerate([(1.0,1.5),(1.6,1.2),(1.3,2.0),(2.0,1.6),(0.7,2.3)]):
        dot = slide.shapes.add_shape(9, Inches(cx), Inches(cy), Inches(0.18), Inches(0.18))
        dot.fill.solid()
        dot.fill.fore_color.rgb = C_ACCENT if i % 2 == 0 else C_GREEN
        dot.line.fill.background()

    add_text(slide, "MatrixCube", 2.5, 1.5, 8.5, 1.5, size=54, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, "Arduino Library für den 3×3×3 LED-Würfel", 2.5, 3.0, 8.5, 0.7,
             size=22, color=C_ACCENT, align=PP_ALIGN.CENTER)
    add_text(slide, "Schulprojekt  ·  Arduino Nano  ·  C++ Templates",
             2.5, 3.75, 8.5, 0.5, size=15, color=C_SUBTEXT, align=PP_ALIGN.CENTER)
    # unterer Streifen
    s2 = slide.shapes.add_shape(1, 0, Inches(7.42), prs.slide_width, Inches(0.08))
    s2.fill.solid(); s2.fill.fore_color.rgb = C_ACCENT; s2.line.fill.background()

def chapter_slide(prs, number, title, subtitle=""):
    slide = prs.slides.add_slide(BLANK)
    add_bg(slide)
    stripe = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.08))
    stripe.fill.solid(); stripe.fill.fore_color.rgb = C_ACCENT; stripe.line.fill.background()
    add_text(slide, f"{number:02d}", 0.5, 1.8, 2, 1.8, size=96, bold=True,
             color=RGBColor(0x31,0x32,0x44), align=PP_ALIGN.LEFT)
    add_text(slide, title, 0.5, 2.5, 12, 1.2, size=40, bold=True,
             color=C_WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, 0.5, 3.7, 12, 0.6, size=18,
                 color=C_SUBTEXT, align=PP_ALIGN.LEFT)
    # horizontale Linie
    line = slide.shapes.add_shape(1, Inches(0.5), Inches(3.5),
                                   Inches(12.3), Inches(0.04))
    line.fill.solid(); line.fill.fore_color.rgb = C_ACCENT; line.line.fill.background()

def content_slide(prs, title, bullets, code_lines=None, code_x=6.8, code_w=6.1, code_h=None):
    slide = prs.slides.add_slide(BLANK)
    add_bg(slide)
    # Titelleiste
    add_rect(slide, 0, 0, 13.33, 1.0, fill=C_BOX_BG, border=None)
    line = slide.shapes.add_shape(1, 0, Inches(1.0), prs.slide_width, Inches(0.04))
    line.fill.solid(); line.fill.fore_color.rgb = C_ACCENT; line.line.fill.background()
    add_text(slide, title, 0.3, 0.12, 12.5, 0.75, size=26, bold=True,
             color=C_ACCENT, align=PP_ALIGN.LEFT)

    # Bullet-Punkte
    bx, by, bw = 0.3, 1.15, (6.2 if code_lines else 12.7)
    for i, (icon, text, color) in enumerate(bullets):
        yy = by + i * 0.72
        add_text(slide, icon, bx, yy, 0.4, 0.6, size=15, color=color)
        add_text(slide, text, bx+0.45, yy, bw-0.5, 0.65, size=15, color=C_WHITE)

    # optionaler Code-Block
    if code_lines:
        ch = code_h if code_h else max(1.2, len(code_lines) * 0.28 + 0.35)
        add_code(slide, code_lines, code_x, 1.15, code_w, ch)
    return slide

def two_col_slide(prs, title, left_bullets, right_bullets):
    slide = prs.slides.add_slide(BLANK)
    add_bg(slide)
    add_rect(slide, 0, 0, 13.33, 1.0, fill=C_BOX_BG, border=None)
    line = slide.shapes.add_shape(1, 0, Inches(1.0), prs.slide_width, Inches(0.04))
    line.fill.solid(); line.fill.fore_color.rgb = C_ACCENT; line.line.fill.background()
    add_text(slide, title, 0.3, 0.12, 12.5, 0.75, size=26, bold=True,
             color=C_ACCENT, align=PP_ALIGN.LEFT)
    for i, (icon, text, color) in enumerate(left_bullets):
        yy = 1.15 + i * 0.72
        add_text(slide, icon, 0.3, yy, 0.4, 0.6, size=15, color=color)
        add_text(slide, text, 0.75, yy, 5.7, 0.65, size=15, color=C_WHITE)
    for i, (icon, text, color) in enumerate(right_bullets):
        yy = 1.15 + i * 0.72
        add_text(slide, icon, 6.8, yy, 0.4, 0.6, size=15, color=color)
        add_text(slide, text, 7.25, yy, 5.7, 0.65, size=15, color=C_WHITE)

# ── Slides ───────────────────────────────────────────────────────────────────

# 1 — Titelfolie
title_slide(prs)

# 2 — Inhaltsübersicht
slide = prs.slides.add_slide(BLANK)
add_bg(slide)
add_rect(slide, 0, 0, 13.33, 1.0, fill=C_BOX_BG, border=None)
line = slide.shapes.add_shape(1, 0, Inches(1.0), prs.slide_width, Inches(0.04))
line.fill.solid(); line.fill.fore_color.rgb = C_ACCENT; line.line.fill.background()
add_text(slide, "Inhalt", 0.3, 0.12, 12.5, 0.75, size=26, bold=True, color=C_ACCENT)
topics = [
    ("01", "Wie der Würfel funktioniert",    "Multiplexing & LED-Puffer"),
    ("02", "Aufbau der Library",              "Templates, Basisklasse, ISR"),
    ("03", "Initialisierung",                 "begin()"),
    ("04", "Einzelne LEDs steuern",           "setLed, getLed, toggleLed"),
    ("05", "Gruppen füllen",                  "fillAll, clear, fillLayer, fillBox, fillShell"),
    ("06", "Formen zeichnen",                 "drawEdges, drawPlane, drawPillar"),
    ("07", "Verschieben & Spiegeln",          "shift, mirror, copyLayer"),
    ("08", "Verschiedene Würfelgrößen",       "Template-Parameter N"),
]
for i, (num, title, sub) in enumerate(topics):
    col = i // 4
    row = i % 4
    xx = 0.4 + col * 6.5
    yy = 1.2 + row * 1.45
    add_rect(slide, xx, yy, 6.0, 1.25, fill=C_BOX_BG, border=C_BOX_BORDER)
    add_text(slide, num, xx+0.15, yy+0.08, 0.7, 0.5, size=22, bold=True, color=C_ACCENT)
    add_text(slide, title, xx+0.75, yy+0.08, 4.9, 0.5, size=16, bold=True, color=C_WHITE)
    add_text(slide, sub,   xx+0.75, yy+0.6,  4.9, 0.45, size=12, color=C_SUBTEXT)

# ── Kapitel 01 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 1, "Wie der Würfel funktioniert",
              "Multiplexing & der LED-Puffer")

content_slide(prs,
    "Das Multiplexing-Prinzip",
    [
        ("▶", "27 LEDs, aber nur 12 Pins — das geht mit Multiplexing", C_ACCENT),
        ("▶", "9 vertikale Pins (vPins) schalten die Spalten in einer Ebene", C_WHITE),
        ("▶", "3 horizontale Pins (hPins) schalten eine Ebene komplett ein/aus", C_WHITE),
        ("▶", "Es leuchtet immer nur EINE Ebene gleichzeitig — aber so schnell,\n"
               "dass das Auge alle drei als gleichzeitig wahrnimmt", C_YELLOW),
        ("▶", "Der Timer-Interrupt wechselt ~600× pro Sekunde die aktive Ebene", C_GREEN),
        ("▶", "Das Auge braucht >50 ms um ein Flackern zu sehen — 1.6 ms ist unsichtbar", C_SUBTEXT),
    ],
    code_lines=[
        "// Ebene 0 aktiv:",
        "hPin[0] = HIGH  ← Ebene 0 an",
        "hPin[1] = LOW",
        "hPin[2] = LOW",
        "vPin[0..8] = Werte aus _led[0]",
        "",
        "// 1.6 ms spaeter: Ebene 1 aktiv:",
        "hPin[0] = LOW",
        "hPin[1] = HIGH  ← Ebene 1 an",
        "vPin[0..8] = Werte aus _led[1]",
        "",
        "// ... und so weiter im Kreis",
    ],
    code_x=6.8, code_w=6.1, code_h=4.0
)

content_slide(prs,
    "Der LED-Puffer _led[N][N][N]",
    [
        ("▶", "_led ist ein 3D-Array im RAM des Arduino", C_ACCENT),
        ("▶", "Index: _led[Ebene][Y][Z] — jeder Wert ist 0 (aus) oder 1 (an)", C_WHITE),
        ("▶", "Alle Steuerfunktionen schreiben NUR in dieses Array", C_WHITE),
        ("▶", "Der Timer-ISR liest das Array und gibt es auf die Pins aus", C_YELLOW),
        ("▶", "Ebene 0 = unten, Ebene N-1 = oben", C_GREEN),
        ("▶", "Wichtig: cli()/sei() schützen das Array vor gleichzeitigem\n"
               "Zugriff durch Hauptprogramm und ISR", C_RED),
    ],
    code_lines=[
        "// _led[Ebene][Y][Z]",
        "_led[0][0][0]  // unten, vorne links",
        "_led[1][1][1]  // Mitte",
        "_led[2][2][2]  // oben, hinten rechts",
        "",
        "// RAM-Verbrauch:",
        "// N=3 ->  27 Byte",
        "// N=4 ->  64 Byte",
        "// N=5 -> 125 Byte",
        "// Nano hat 2048 Byte RAM",
    ],
    code_x=6.8, code_w=6.1, code_h=3.5
)

# ── Kapitel 02 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 2, "Aufbau der Library",
              "Templates, Basisklasse, ISR")

content_slide(prs,
    "Dateistruktur der Library",
    [
        ("📄", "MatrixCube.h  — Alle Funktionen deklariert + Template-Implementierung", C_ACCENT),
        ("📄", "MatrixCube.cpp — Nur der Timer-Interrupt und der globale Zeiger", C_WHITE),
        ("📁", "examples/BasicDemo/    — Einfaches Demo-Programm", C_GREEN),
        ("📁", "examples/Animations/  — Verschiedene Animationen", C_GREEN),
        ("📄", "library.properties     — Metadaten für die Arduino IDE", C_SUBTEXT),
        ("📄", "keywords.txt           — Farb-Highlighting in der IDE", C_SUBTEXT),
    ],
    code_lines=[
        "// Benutzung:",
        "#include <MatrixCube.h>",
        "",
        "uint8_t vPins[9] = {4,5,6,7,8,9,10,11,12};",
        "uint8_t hPins[3] = {13, 3, 2};",
        "",
        "// <3> = Wuerfelgroesse (Template-Parameter)",
        "MatrixCube<3> cube(vPins, hPins);",
        "",
        "void setup() { cube.begin(); }",
        "void loop()  { cube.fillAll(); delay(500);",
        "               cube.clear();   delay(500); }",
    ],
    code_x=6.8, code_w=6.1, code_h=4.2
)

content_slide(prs,
    "Templates — warum und wie",
    [
        ("▶", "Templates sind ein 'Bauplan' — der Compiler erzeugt den fertigen\n"
               "Code erst wenn du den Parameter angibst", C_ACCENT),
        ("▶", "template <uint8_t N>  →  N ist die Seitenlänge des Würfels", C_WHITE),
        ("▶", "MatrixCube<3>  →  Compiler ersetzt alle N durch 3", C_GREEN),
        ("▶", "MatrixCube<4>  →  Compiler ersetzt alle N durch 4", C_GREEN),
        ("▶", "Alle Array-Größen (_led[N][N][N], vPin[N*N]) werden zur\n"
               "Kompilierzeit berechnet — kein dynamischer Speicher nötig", C_YELLOW),
    ],
    code_lines=[
        "// Template-Deklaration:",
        "template <uint8_t N>",
        "class MatrixCube : public MatrixCubeBase {",
        "  volatile uint8_t _led[N][N][N];",
        "  uint8_t _vPin[N * N];",
        "  uint8_t _hPin[N];",
        "  ...",
        "};",
        "",
        "// Zwei verschiedene Instanzen moeglich:",
        "MatrixCube<3> kleinerWuerfel(v3, h3);",
        "MatrixCube<4> grosserWuerfel(v4, h4);",
    ],
    code_x=6.8, code_w=6.1, code_h=4.5
)

content_slide(prs,
    "Basisklasse & ISR — das Verbindungsstück",
    [
        ("▶", "Problem: Der Timer-ISR ist eine normale C-Funktion — sie kennt\n"
               "keinen Template-Typ wie MatrixCube<3>", C_RED),
        ("▶", "Lösung: abstrakte Basisklasse MatrixCubeBase mit virtual _isr()", C_ACCENT),
        ("▶", "MatrixCube<N> erbt von MatrixCubeBase und überschreibt _isr()", C_WHITE),
        ("▶", "Der globale Zeiger _cubeInstance zeigt auf MatrixCubeBase* —\n"
               "C++ findet automatisch die richtige _isr()-Version (Polymorphismus)", C_GREEN),
        ("▶", "cli()/sei() in allen Schreibfunktionen verhindern Datenkonflikte\n"
               "zwischen ISR und Hauptprogramm", C_YELLOW),
    ],
    code_lines=[
        "// Basisklasse:",
        "class MatrixCubeBase {",
        "  virtual void _isr() = 0;",
        "};",
        "",
        "// ISR (in MatrixCube.cpp):",
        "MatrixCubeBase* _cubeInstance = nullptr;",
        "",
        "ISR(TIMER1_COMPA_vect) {",
        "  if (_cubeInstance != nullptr)",
        "    _cubeInstance->_isr();",
        "}",
        "",
        "// begin() registriert die Instanz:",
        "_cubeInstance = this;",
    ],
    code_x=6.8, code_w=6.1, code_h=5.2
)

# ── Kapitel 03 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 3, "Initialisierung", "begin()")

content_slide(prs,
    "begin() — Einmalig in setup() aufrufen",
    [
        ("1.", "Setzt alle N×N vertikale Pins auf OUTPUT", C_ACCENT),
        ("2.", "Setzt alle N horizontale Pins auf OUTPUT und LOW (alle Ebenen aus)", C_WHITE),
        ("3.", "Speichert 'this' im globalen _cubeInstance — damit der ISR die\n"
               "Klasse findet", C_WHITE),
        ("4.", "Konfiguriert Timer1: CTC-Modus, Prescaler 256, OCR1A=103\n"
               "→ 16 MHz / 256 / 104 ≈ 600 Interrupts/Sekunde", C_YELLOW),
        ("5.", "cli() vor Timer-Konfiguration, sei() danach — verhindert\n"
               "Störungen während des Setups", C_GREEN),
    ],
    code_lines=[
        "void MatrixCube<N>::begin() {",
        "  for (i = 0; i < N*N; i++)",
        "    pinMode(_vPin[i], OUTPUT);",
        "  for (i = 0; i < N; i++) {",
        "    pinMode(_hPin[i], OUTPUT);",
        "    digitalWrite(_hPin[i], LOW);",
        "  }",
        "  _cubeInstance = this;",
        "",
        "  cli();           // Interrupts aus",
        "  OCR1A = 103;     // Zaehler-Ziel",
        "  TCCR1B |= (1 << WGM12);  // CTC",
        "  TCCR1B |= (1 << CS12);   // /256",
        "  TIMSK1 |= (1 << OCIE1A); // IRQ an",
        "  sei();           // Interrupts ein",
        "}",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

# ── Kapitel 04 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 4, "Einzelne LEDs steuern",
              "setLed · getLed · toggleLed")

content_slide(prs,
    "setLed(x, y, z, state)",
    [
        ("▶", "Setzt eine einzelne LED an Position (Ebene x, Y=y, Z=z)", C_ACCENT),
        ("▶", "state: LED_ON (1), LED_OFF (0) oder LED_TOGGLE (-1)", C_WHITE),
        ("▶", "clamp() begrenzt alle Koordinaten auf 0..N-1\n"
               "→ verhindert Array-Überlauf (Speicherfehler in C++)", C_YELLOW),
        ("▶", "cli()/sei() schützen den Schreibzugriff auf _led", C_WHITE),
        ("▶", "applyState() wendet den state-Wert auf die LED-Variable an", C_GREEN),
        ("▶", "Standardwert ist LED_ON — setLed(0,0,0) reicht aus", C_SUBTEXT),
    ],
    code_lines=[
        "// Einschalten:",
        "cube.setLed(0, 0, 0, LED_ON);",
        "cube.setLed(0, 0, 0);        // gleich",
        "",
        "// Ausschalten:",
        "cube.setLed(2, 1, 0, LED_OFF);",
        "",
        "// Umschalten:",
        "cube.setLed(1, 1, 1, LED_TOGGLE);",
        "",
        "// Intern:",
        "void setLed(x, y, z, state) {",
        "  x = clamp(x);  // max. N-1",
        "  cli();",
        "  applyState(_led[x][y][z], state);",
        "  sei();",
        "}",
    ],
    code_x=6.8, code_w=6.1, code_h=5.8
)

content_slide(prs,
    "getLed() & toggleLed()",
    [
        ("getLed", "Gibt den aktuellen Zustand zurück (true = an, false = aus)", C_ACCENT),
        ("▶", "Liest einfach _led[x][y][z] — kein cli() nötig, da das Lesen\n"
               "eines einzelnen Bytes auf AVR unteilbar (atomar) ist", C_WHITE),
        ("▶", "Nützlich um Entscheidungen vom LED-Zustand abhängig zu machen", C_SUBTEXT),
        ("", "", C_WHITE),
        ("toggleLed", "Kürzel für setLed(x, y, z, LED_TOGGLE)", C_ACCENT),
        ("▶", "Ruft intern nur setLed() auf — kein eigener Code dahinter", C_WHITE),
        ("▶", "Praktisch für Blink-Effekte in einer Schleife", C_GREEN),
    ],
    code_lines=[
        "// getLed:",
        "bool an = cube.getLed(1, 1, 1);",
        "if (an) {",
        "  cube.setLed(1,1,1, LED_OFF);",
        "}",
        "",
        "// toggleLed:",
        "cube.toggleLed(0, 0, 0);",
        "// identisch mit:",
        "cube.setLed(0, 0, 0, LED_TOGGLE);",
        "",
        "// Blink-Effekt:",
        "for (int i = 0; i < 10; i++) {",
        "  cube.toggleLed(1, 1, 1);",
        "  delay(200);",
        "}",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

# ── Kapitel 05 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 5, "Gruppen füllen",
              "fillAll · clear · fillLayer · fillBox · fillShell")

content_slide(prs,
    "fillAll() & clear()",
    [
        ("fillAll()", "Schaltet alle N³ LEDs ein", C_ACCENT),
        ("clear()",   "Schaltet alle N³ LEDs aus", C_ACCENT),
        ("▶", "Beide sind nur Abkürzungen für fillBox() mit dem kompletten Bereich", C_WHITE),
        ("▶", "fillAll() = fillBox(0, N-1, 0, N-1, 0, N-1, LED_ON)", C_SUBTEXT),
        ("▶", "clear()   = fillBox(0, N-1, 0, N-1, 0, N-1, LED_OFF)", C_SUBTEXT),
        ("▶", "clear() am Anfang jeder Animation ist gute Praxis", C_GREEN),
    ],
    code_lines=[
        "cube.fillAll();   // alle 27 LEDs an",
        "delay(500);",
        "cube.clear();     // alle aus",
        "delay(200);",
    ],
    code_x=6.8, code_w=6.1, code_h=1.8
)

content_slide(prs,
    "fillLayer(layer, state)",
    [
        ("▶", "Setzt alle N² LEDs einer kompletten horizontalen Ebene", C_ACCENT),
        ("▶", "layer: 0 = unterste Ebene, N-1 = oberste Ebene", C_WHITE),
        ("▶", "state: LED_ON, LED_OFF oder LED_TOGGLE", C_WHITE),
        ("▶", "Intern: fillBox(layer, layer, 0, N-1, 0, N-1, state)\n"
               "→ X-Bereich auf eine Ebene eingeschränkt, Y und Z komplett", C_YELLOW),
        ("▶", "Gut für Ebenen-Animationen: Ebene hochscrollen, aufleuchten lassen", C_GREEN),
    ],
    code_lines=[
        "// Jede Ebene kurz aufleuchten:",
        "for (uint8_t i = 0; i < 3; i++) {",
        "  cube.fillLayer(i, LED_ON);",
        "  delay(300);",
        "  cube.fillLayer(i, LED_OFF);",
        "}",
        "",
        "// Intern:",
        "void fillLayer(layer, state) {",
        "  fillBox(layer, layer,",
        "          0, N-1,",
        "          0, N-1, state);",
        "}",
    ],
    code_x=6.8, code_w=6.1, code_h=4.5
)

content_slide(prs,
    "fillBox(xl, xu, yl, yu, zl, zu, state)",
    [
        ("▶", "Die universellste Füll-Funktion — setzt alle LEDs in einem\n"
               "rechteckigen 3D-Bereich", C_ACCENT),
        ("▶", "Alle anderen Fill-Funktionen rufen intern fillBox() auf", C_WHITE),
        ("▶", "Parameter: untere und obere Grenze für jede Achse (inklusive)", C_WHITE),
        ("▶", "Drei verschachtelte Schleifen: x von xl..xu, y von yl..yu, z von zl..zu", C_YELLOW),
        ("▶", "Alles zwischen cli()/sei() — der ISR sieht immer einen\n"
               "konsistenten Zustand", C_GREEN),
    ],
    code_lines=[
        "// Untere Haelfte einschalten:",
        "cube.fillBox(0, 1,  0, 2,  0, 2,  LED_ON);",
        "",
        "// Nur einen Streifen in der Mitte:",
        "cube.fillBox(0, 2,  1, 1,  0, 2,  LED_ON);",
        "",
        "// Innerer 1x1x1-Kern:",
        "cube.fillBox(1, 1,  1, 1,  1, 1,  LED_ON);",
        "",
        "// Intern (vereinfacht):",
        "cli();",
        "for x von xl bis xu:",
        "  for y von yl bis yu:",
        "    for z von zl bis zu:",
        "      applyState(_led[x][y][z], state);",
        "sei();",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

content_slide(prs,
    "fillShell(state)",
    [
        ("▶", "Setzt nur die LEDs die auf der Außenfläche des Würfels liegen", C_ACCENT),
        ("▶", "Der innere Kern bleibt unverändert (bei N=3: die mittlere LED)", C_WHITE),
        ("▶", "Eine LED ist auf der Schale wenn mindestens eine Koordinate\n"
               "am Rand liegt: x==0, x==N-1, y==0, y==N-1, z==0 oder z==N-1", C_YELLOW),
        ("▶", "Gut kombinierbar mit setLed(N/2, N/2, N/2) für Kern-Effekte", C_GREEN),
        ("▶", "Bei N=3: 26 LEDs auf der Schale, 1 LED im Kern", C_SUBTEXT),
    ],
    code_lines=[
        "// Schale an, Kern aus:",
        "cube.fillShell(LED_ON);",
        "cube.setLed(1, 1, 1, LED_OFF);",
        "",
        "// Schale aus, Kern an:",
        "cube.fillShell(LED_OFF);",
        "cube.setLed(1, 1, 1, LED_ON);",
        "",
        "// Logik intern:",
        "if (x==0 || x==N-1 ||",
        "    y==0 || y==N-1 ||",
        "    z==0 || z==N-1) {",
        "  // auf der Schale -> setzen",
        "}",
    ],
    code_x=6.8, code_w=6.1, code_h=4.8
)

# ── Kapitel 06 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 6, "Formen zeichnen",
              "drawEdges · drawPlane · drawPillar")

content_slide(prs,
    "drawEdges(state)",
    [
        ("▶", "Zeichnet die 12 Kanten des Würfels (nur Rand-LEDs)", C_ACCENT),
        ("▶", "Ecke = alle 3 Koordinaten am Rand  →  8 Eckpunkte", C_WHITE),
        ("▶", "Kante = genau 2 Koordinaten am Rand  →  bei N=3: Kantenmittelpunkte", C_WHITE),
        ("▶", "Fläche = genau 1 Koordinate am Rand  →  Flächenmitten (nicht gezeichnet)", C_SUBTEXT),
        ("▶", "Kern = keine Koordinate am Rand      →  Körpermitte (nicht gezeichnet)", C_SUBTEXT),
        ("▶", "Der Code zählt die 'Eck-Koordinaten' und zeichnet ab Wert ≥ 2", C_YELLOW),
    ],
    code_lines=[
        "cube.drawEdges(LED_ON);",
        "",
        "// Logik intern:",
        "uint8_t corners = 0;",
        "if (x==0 || x==N-1) corners++;",
        "if (y==0 || y==N-1) corners++;",
        "if (z==0 || z==N-1) corners++;",
        "if (corners >= 2)",
        "  applyState(_led[x][y][z], state);",
        "",
        "// corners == 3 -> Eckpunkt (8 St.)",
        "// corners == 2 -> Kante    (12 St.)",
        "// corners == 1 -> Flaeche",
        "// corners == 0 -> Kern",
    ],
    code_x=6.8, code_w=6.1, code_h=5.0
)

content_slide(prs,
    "drawPlane(axis, pos, state)",
    [
        ("▶", "Zeichnet eine komplette flache Scheibe durch den Würfel", C_ACCENT),
        ("▶", "axis: AXIS_X = horizontal (wie fillLayer), AXIS_Y / AXIS_Z = senkrecht", C_WHITE),
        ("▶", "pos: 0, 1 oder 2 — Position der Scheibe entlang der gewählten Achse", C_WHITE),
        ("▶", "Intern: ruft fillBox() auf mit einer Achse auf genau 'pos' fixiert", C_YELLOW),
        ("▶", "AXIS_X entspricht fillLayer() — nur andere Schreibweise", C_SUBTEXT),
    ],
    code_lines=[
        "// Horizontale Scheiben:",
        "cube.drawPlane(AXIS_X, 0); // unten",
        "cube.drawPlane(AXIS_X, 1); // Mitte",
        "cube.drawPlane(AXIS_X, 2); // oben",
        "",
        "// Senkrechte Scheiben:",
        "cube.drawPlane(AXIS_Y, 0); // vorne",
        "cube.drawPlane(AXIS_Z, 2); // rechts",
        "",
        "// Intern (AXIS_X):",
        "fillBox(pos,pos, 0,N-1, 0,N-1);",
        "// Intern (AXIS_Y):",
        "fillBox(0,N-1, pos,pos, 0,N-1);",
        "// Intern (AXIS_Z):",
        "fillBox(0,N-1, 0,N-1, pos,pos);",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

content_slide(prs,
    "drawPillar(axis, a, b, state)",
    [
        ("▶", "Zeichnet eine Säule (Linie) durch den kompletten Würfel", C_ACCENT),
        ("▶", "axis: Richtung der Säule — AXIS_X, AXIS_Y oder AXIS_Z", C_WHITE),
        ("▶", "a, b: die beiden Koordinaten die festgehalten werden\n"
               "(die dritte Achse läuft automatisch von 0 bis N-1)", C_WHITE),
        ("▶", "Intern: fillBox() mit zwei Achsen auf je eine Position fixiert,\n"
               "die Richtungs-Achse läuft von 0 bis N-1", C_YELLOW),
        ("▶", "9 Säulen in AXIS_X-Richtung = alle vertikalen Säulen des Würfels", C_GREEN),
    ],
    code_lines=[
        "// Alle 9 vertikalen Saeulen:",
        "for (uint8_t y = 0; y < 3; y++)",
        "  for (uint8_t z = 0; z < 3; z++)",
        "    cube.drawPillar(AXIS_X, y, z);",
        "",
        "// Mittelsaeule:",
        "cube.drawPillar(AXIS_X, 1, 1);",
        "",
        "// Intern (AXIS_X):",
        "fillBox(0,N-1, a,a, b,b, state);",
        "// Intern (AXIS_Y):",
        "fillBox(a,a, 0,N-1, b,b, state);",
        "// Intern (AXIS_Z):",
        "fillBox(a,a, b,b, 0,N-1, state);",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

# ── Kapitel 07 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 7, "Verschieben & Spiegeln",
              "shift · mirror · copyLayer")

content_slide(prs,
    "shift(axis, dir, wrap)",
    [
        ("▶", "Verschiebt den gesamten Würfelinhalt um 1 Position", C_ACCENT),
        ("▶", "axis: Richtung — AXIS_X (hoch/runter), AXIS_Y, AXIS_Z", C_WHITE),
        ("▶", "dir: +1 (vorwärts) oder -1 (rückwärts)", C_WHITE),
        ("▶", "wrap=false: LEDs die herausfallen verschwinden", C_YELLOW),
        ("▶", "wrap=true:  LEDs die herausfallen kommen auf der anderen Seite\n"
               "wieder herein (Torus/Ring-Effekt)", C_GREEN),
        ("▶", "Intern: Kopie in tmp[], _led auf 0 setzen, dann neue Positionen\n"
               "berechnen und eintragen", C_SUBTEXT),
    ],
    code_lines=[
        "// Ebene von unten nach oben:",
        "cube.fillLayer(0);",
        "for (int i = 0; i < 3; i++) {",
        "  cube.shift(AXIS_X, +1);",
        "  delay(200);",
        "}",
        "",
        "// Kreisende Ebene (Wrap):",
        "cube.fillLayer(0);",
        "for (int i = 0; i < 9; i++) {",
        "  cube.shift(AXIS_X, +1, true);",
        "  delay(150);",
        "}",
        "",
        "// Wrap-Rechnung intern:",
        "nx = ((nx % N) + N) % N;",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

content_slide(prs,
    "mirror(axis) & copyLayer(from, to)",
    [
        ("mirror()", "Spiegelt den Würfelinhalt entlang einer Achse", C_ACCENT),
        ("▶", "AXIS_X: oben ↔ unten     AXIS_Y: vorne ↔ hinten     AXIS_Z: links ↔ rechts", C_WHITE),
        ("▶", "Tauscht immer Pärchen: Index 0 ↔ N-1, Index 1 ↔ N-2, usw.\n"
               "Schleife geht nur bis N/2 — sonst würde zweimal getauscht", C_YELLOW),
        ("", "", C_WHITE),
        ("copyLayer()", "Kopiert eine Ebene auf eine andere (Quelle bleibt unverändert)", C_ACCENT),
        ("▶", "Praktisch für Animationen: Zustand einfrieren und auf andere Ebene übertragen", C_WHITE),
        ("▶", "Zwei Schleifen über Y und Z: _led[to][y][z] = _led[from][y][z]", C_GREEN),
    ],
    code_lines=[
        "// Spiegeln:",
        "cube.mirror(AXIS_X); // oben <-> unten",
        "cube.mirror(AXIS_Y); // vorne <-> hinten",
        "",
        "// Tausch-Logik intern:",
        "for i von 0 bis N/2:",
        "  j = N - 1 - i",
        "  tausche _led[i] mit _led[j]",
        "",
        "// Layer kopieren:",
        "cube.copyLayer(0, 2);",
        "// Ebene 0 -> Ebene 2 kopieren",
        "",
        "// Intern:",
        "for y: for z:",
        "  _led[to][y][z] = _led[from][y][z];",
    ],
    code_x=6.8, code_w=6.1, code_h=5.5
)

# ── Kapitel 08 ───────────────────────────────────────────────────────────────
chapter_slide(prs, 8, "Verschiedene Würfelgrößen",
              "Template-Parameter N")

content_slide(prs,
    "Andere Würfelgrößen verwenden",
    [
        ("▶", "Einfach den Template-Parameter <N> ändern — der Rest passt sich an", C_ACCENT),
        ("▶", "Mehr Pins nötig: N×N vPins und N hPins", C_WHITE),
        ("▶", "Arduino Nano hat 14 digitale + 6 analoge Pins = 20 gesamt\n"
               "→ N=4 braucht 16+4=20 Pins — genau möglich!", C_YELLOW),
        ("▶", "RAM-Verbrauch wächst mit N³ — bei N=5 schon 125 Byte Puffer", C_RED),
        ("▶", "Timer-Frequenz bleibt gleich, jede Ebene bekommt weniger Zeit\n"
               "pro Sekunde → bei N>4 kann leichtes Flimmern auftreten", C_SUBTEXT),
    ],
    code_lines=[
        "// 3x3x3 (original):",
        "uint8_t vPins[9]  = {4..12};",
        "uint8_t hPins[3]  = {13,3,2};",
        "MatrixCube<3> cube(vPins, hPins);",
        "",
        "// 4x4x4:",
        "uint8_t vPins[16] = {2,3,...,17};",
        "uint8_t hPins[4]  = {18,19,A0,A1};",
        "MatrixCube<4> cube(vPins, hPins);",
        "",
        "// 5x5x5:",
        "uint8_t vPins[25] = { ... }; // 25 Pins!",
        "uint8_t hPins[5]  = { ... };",
        "MatrixCube<5> cube(vPins, hPins);",
        "// Achtung: kaum noch Pins frei auf Nano",
    ],
    code_x=6.8, code_w=6.1, code_h=5.8
)

# ── Abschlussfolie ───────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
add_bg(slide)
stripe = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.08))
stripe.fill.solid(); stripe.fill.fore_color.rgb = C_ACCENT; stripe.line.fill.background()

add_text(slide, "Zusammenfassung", 0.5, 0.6, 12, 0.8, size=32, bold=True, color=C_ACCENT)
line = slide.shapes.add_shape(1, Inches(0.5), Inches(1.4), Inches(12.3), Inches(0.04))
line.fill.solid(); line.fill.fore_color.rgb = C_ACCENT; line.line.fill.background()

summary = [
    ("✓", "Multiplexing lässt 27 LEDs mit nur 12 Pins betreiben", C_GREEN),
    ("✓", "Der LED-Puffer _led[N][N][N] trennt Logik und Ausgabe sauber", C_GREEN),
    ("✓", "Timer-ISR sorgt automatisch für flimmerfreie Darstellung", C_GREEN),
    ("✓", "cli()/sei() schützen den Puffer vor gleichzeitigem Zugriff", C_GREEN),
    ("✓", "Templates machen die Library für beliebige Würfelgrößen nutzbar", C_GREEN),
    ("✓", "15 Funktionen für einzelne LEDs, Gruppen, Formen und Animationen", C_GREEN),
]
for i, (icon, text, color) in enumerate(summary):
    col = i // 3
    row = i % 3
    xx = 0.4 + col * 6.4
    yy = 1.6 + row * 1.6
    add_rect(slide, xx, yy, 6.0, 1.35, fill=C_BOX_BG, border=C_BOX_BORDER)
    add_text(slide, icon, xx+0.2,  yy+0.35, 0.5,  0.6, size=18, color=C_GREEN)
    add_text(slide, text, xx+0.7,  yy+0.12, 5.0,  1.1, size=14, color=C_WHITE)

s2 = slide.shapes.add_shape(1, 0, Inches(7.42), prs.slide_width, Inches(0.08))
s2.fill.solid(); s2.fill.fore_color.rgb = C_ACCENT; s2.line.fill.background()

# ── Speichern ────────────────────────────────────────────────────────────────
prs.save("/home/user/matrix-ctrl/MatrixCube_Praesentation.pptx")
print("Fertig!")
