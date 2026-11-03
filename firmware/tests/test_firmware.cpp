// Host-side tests for the matrix test sketch.
//
//   make -C firmware/tests
//
// 1. matrixIndex(): bijective for both wiring styles, correct serpentine
//    order, safe on out-of-range input.
// 2. The real test_matrix.ino, compiled against mock/FastLED.h, run through
//    setup() and one loop(): correct pin/power settings, every LED gets lit,
//    corner markers land on the right physical LEDs, no out-of-bounds writes.
#include <stdio.h>

#include <set>

#include "../test_matrix/matrix_map.h"
#include "mock/FastLED.h"

uint32_t g_millis = 0;
MockSerial Serial;
MockFastLED FastLED;

// Pull in the sketch itself.
#include "../test_matrix/test_matrix.ino"

static int failures = 0;
#define EXPECT(cond)                                                   \
  do {                                                                 \
    if (!(cond)) {                                                     \
      printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);           \
      failures++;                                                      \
    }                                                                  \
  } while (0)

static void testMappingIsBijective(bool serpentine) {
  std::set<uint16_t> seen;
  for (uint8_t y = 0; y < 16; y++)
    for (uint8_t x = 0; x < 16; x++) {
      uint16_t i = matrixIndex(x, y, 16, 16, serpentine);
      EXPECT(i < 256);
      seen.insert(i);
    }
  EXPECT(seen.size() == 256);
}

static void testMappingValues() {
  // Progressive: row-major.
  EXPECT(matrixIndex(0, 0, 16, 16, false) == 0);
  EXPECT(matrixIndex(15, 0, 16, 16, false) == 15);
  EXPECT(matrixIndex(0, 1, 16, 16, false) == 16);
  EXPECT(matrixIndex(15, 15, 16, 16, false) == 255);
  // Serpentine: odd rows reversed, so row 1 starts where row 0 ends.
  EXPECT(matrixIndex(15, 1, 16, 16, true) == 16);
  EXPECT(matrixIndex(0, 1, 16, 16, true) == 31);
  EXPECT(matrixIndex(0, 2, 16, 16, true) == 32);
  EXPECT(matrixIndex(0, 15, 16, 16, true) == 255);
  // Consecutive strip indices are always physically adjacent in serpentine.
  for (uint16_t i = 0; i + 1 < 256; i++) {
    int ax = -1, ay = -1, bx = -1, by = -1;
    for (uint8_t y = 0; y < 16; y++)
      for (uint8_t x = 0; x < 16; x++) {
        uint16_t k = matrixIndex(x, y, 16, 16, true);
        if (k == i) { ax = x; ay = y; }
        if (k == i + 1) { bx = x; by = y; }
      }
    EXPECT(abs(ax - bx) + abs(ay - by) == 1);
  }
  // Out of range -> one past the end.
  EXPECT(matrixIndex(16, 0, 16, 16, true) == 256);
  EXPECT(matrixIndex(0, 16, 16, 16, false) == 256);
  EXPECT(matrixIndex(255, 255, 16, 16, true) == 256);
  // Non-square panels.
  EXPECT(matrixIndex(7, 1, 8, 32, true) == 8);
  EXPECT(matrixIndex(0, 31, 8, 32, false) == 248);
}

static void testSketch() {
  setup();
  EXPECT(FastLED.dataPin == 16);
  EXPECT(FastLED.numLeds == 256);
  EXPECT(FastLED.maxMilliamps > 0 && FastLED.maxMilliamps <= 3000);
  EXPECT(FastLED.brightness > 0 && FastLED.brightness <= 128);
  EXPECT(!Serial.lines.empty());

  size_t before = FastLED.frames.size();
  loop();
  const auto &frames = FastLED.frames;
  EXPECT(frames.size() > before + 256);

  // Every LED is lit in at least one frame (chain walk covers the strip).
  std::vector<bool> lit(256, false);
  for (size_t f = before; f < frames.size(); f++)
    for (int i = 0; i < 256; i++)
      if (frames[f][i]) lit[i] = true;
  for (int i = 0; i < 256; i++) EXPECT(lit[i]);

  // First frame of loop() is the corner test.
  const auto &corners = frames[before];
  EXPECT(corners[0] == CRGB(CRGB::Red));                // (0,0)
  EXPECT(corners[15] == CRGB(CRGB::Green));             // (15,0)
  EXPECT(corners[SERPENTINE ? 255 : 240] == CRGB(CRGB::Blue));   // (0,15)
  EXPECT(corners[SERPENTINE ? 240 : 255] == CRGB(CRGB::White));  // (15,15)
  int litCount = 0;
  for (int i = 0; i < 256; i++) litCount += corners[i] ? 1 : 0;
  EXPECT(litCount == 4);

  // The spare slot must never be written.
  EXPECT(!leds[NUM_LEDS]);

  // One loop takes a bounded time (no runaway delays).
  EXPECT(g_millis < 60000);
}

int main() {
  testMappingIsBijective(false);
  testMappingIsBijective(true);
  testMappingValues();
  testSketch();
  if (failures) {
    printf("%d failure(s)\n", failures);
    return 1;
  }
  printf("All firmware tests passed (%zu frames simulated)\n",
         FastLED.frames.size());
  return 0;
}
