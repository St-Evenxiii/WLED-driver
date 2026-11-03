// WLED driver board - 16x16 matrix bring-up test
//
// Exercises the ESP32 -> 74HCT125 -> matrix data path on GPIO16 before you
// flash WLED. Watch the Serial Monitor (115200 baud) to see which test is
// running and what you should be looking at.
//
// Requires the FastLED library (Library Manager -> "FastLED").
// Board: "ESP32 Dev Module".

#include <FastLED.h>

#include "matrix_map.h"

// ---- Configuration -------------------------------------------------------
#define LED_PIN        16      // GPIO16 -> U1 (74HCT125) -> R1 -> J4 DIN
#define MATRIX_WIDTH   16
#define MATRIX_HEIGHT  16
#define SERPENTINE     true    // false for "progressive" (all rows same way)
#define LED_TYPE       WS2812B
#define COLOR_ORDER    GRB
#define BRIGHTNESS     64      // 0-255
// Current budget enforced by FastLED. A full-white 16x16 panel can draw
// ~15 A; keep this at or below what your 5 V supply (and the PCB) can take.
#define MAX_MILLIAMPS  2000

#define NUM_LEDS (MATRIX_WIDTH * MATRIX_HEIGHT)

// One spare slot so out-of-range XY() writes land somewhere harmless.
CRGB leds[NUM_LEDS + 1];

uint16_t XY(uint8_t x, uint8_t y) {
  return matrixIndex(x, y, MATRIX_WIDTH, MATRIX_HEIGHT, SERPENTINE);
}

static void show(uint16_t ms) {
  FastLED.show();
  FastLED.delay(ms);
}

static void announce(const char *msg) {
  Serial.println(msg);
}

// 1. Corner markers: identifies the origin and orientation.
//    (0,0)=red, (W-1,0)=green, (0,H-1)=blue, (W-1,H-1)=white.
static void testCorners() {
  announce("Corners: red=(0,0) green=(W-1,0) blue=(0,H-1) white=(W-1,H-1)");
  FastLED.clear();
  leds[XY(0, 0)] = CRGB::Red;
  leds[XY(MATRIX_WIDTH - 1, 0)] = CRGB::Green;
  leds[XY(0, MATRIX_HEIGHT - 1)] = CRGB::Blue;
  leds[XY(MATRIX_WIDTH - 1, MATRIX_HEIGHT - 1)] = CRGB::White;
  show(3000);
}

// 2. Solid primaries: if red shows as green, fix COLOR_ORDER.
static void testPrimaries() {
  const CRGB colors[] = {CRGB::Red, CRGB::Green, CRGB::Blue};
  const char *names[] = {"Fill: RED", "Fill: GREEN", "Fill: BLUE"};
  for (uint8_t i = 0; i < 3; i++) {
    announce(names[i]);
    fill_solid(leds, NUM_LEDS, colors[i]);
    show(1000);
  }
}

// 3. Strip order: one pixel walks the chain. A stuck/dark pixel here means
//    a bad LED or solder joint at that position (data stops propagating).
static void testChain() {
  announce("Chain walk: a single pixel visits every LED in wiring order");
  for (uint16_t i = 0; i < NUM_LEDS; i++) {
    FastLED.clear();
    leds[i] = CRGB::Red;
    show(8);
  }
}

// 4. Rows then columns through XY(): straight lines confirm SERPENTINE.
static void testRowsColumns() {
  announce("Rows then columns: lines must be straight (check SERPENTINE)");
  for (uint8_t y = 0; y < MATRIX_HEIGHT; y++) {
    FastLED.clear();
    for (uint8_t x = 0; x < MATRIX_WIDTH; x++) leds[XY(x, y)] = CRGB::Cyan;
    show(60);
  }
  for (uint8_t x = 0; x < MATRIX_WIDTH; x++) {
    FastLED.clear();
    for (uint8_t y = 0; y < MATRIX_HEIGHT; y++) leds[XY(x, y)] = CRGB::Magenta;
    show(60);
  }
}

// 5. Diagonal rainbow: smooth gradient = mapping and timing are good.
static void testRainbow() {
  announce("Diagonal rainbow (5 s)");
  uint32_t start = millis();
  uint8_t hue = 0;
  while (millis() - start < 5000) {
    for (uint8_t y = 0; y < MATRIX_HEIGHT; y++) {
      for (uint8_t x = 0; x < MATRIX_WIDTH; x++) {
        leds[XY(x, y)] = CHSV(hue + (x + y) * 8, 255, 255);
      }
    }
    hue++;
    show(16);
  }
}

// 6. Full white at the power budget: checks the supply/wiring under load.
//    Brownouts or a pink/yellow tint at the far end mean you need thicker
//    wires or power injection.
static void testWhiteLoad() {
  announce("Full white, current-limited to MAX_MILLIAMPS (3 s)");
  fill_solid(leds, NUM_LEDS, CRGB::White);
  show(3000);
}

void setup() {
  Serial.begin(115200);
  delay(2000);  // power-up settle; gives you time to open the monitor
  Serial.println();
  Serial.println("WLED driver matrix test");
  Serial.printf("GPIO%d, %dx%d, %s wiring, max %d mA\n", LED_PIN, MATRIX_WIDTH,
                MATRIX_HEIGHT, SERPENTINE ? "serpentine" : "progressive",
                MAX_MILLIAMPS);

  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS)
      .setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);
  FastLED.clear(true);
}

void loop() {
  testCorners();
  testPrimaries();
  testChain();
  testRowsColumns();
  testRainbow();
  testWhiteLoad();
  FastLED.clear(true);
  FastLED.delay(500);
}
