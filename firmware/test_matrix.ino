#include <FastLED.h>

// WLED Driver Matrix Test Sketch
// This sketch tests the 16x16 LED matrix using the FastLED library.
// It assumes the use of WS2812B LEDs, a common type for 5V matrices.

#define LED_PIN     16      // GPIO16 is connected to the data output on our PCB
#define MATRIX_WIDTH  16
#define MATRIX_HEIGHT 16
#define NUM_LEDS    (MATRIX_WIDTH * MATRIX_HEIGHT)
#define BRIGHTNESS  50      // Keep brightness relatively low for testing (max 255)
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

// Helper to map x, y coordinates to the 1D array of LEDs.
// Adjust this logic if the matrix is wired differently (e.g. serpentine, zigzag).
// Standard layout assumes top-left is 0,0 and continues row by row.
uint16_t XY(uint8_t x, uint8_t y) {
  // If your matrix is a standard zigzag (serpentine) layout:
  // uncomment the code below:
  /*
  uint16_t i;
  if (y & 0x01) {
    // Odd rows run backwards
    uint8_t reverseX = (MATRIX_WIDTH - 1) - x;
    i = (y * MATRIX_WIDTH) + reverseX;
  } else {
    // Even rows run forwards
    i = (y * MATRIX_WIDTH) + x;
  }
  return i;
  */

  // Default: Left to Right, Top to Bottom
  return (y * MATRIX_WIDTH) + x;
}

void setup() {
  delay(2000); // Power-up safety delay

  // Initialize FastLED
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);

  // Clear the matrix
  FastLED.clear();
  FastLED.show();
}

void loop() {
  // Test pattern 1: Moving pixel
  for(int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB::Red;
    FastLED.show();
    delay(10);
    leds[i] = CRGB::Black;
  }

  // Test pattern 2: Color fill
  fill_solid(leds, NUM_LEDS, CRGB::Green);
  FastLED.show();
  delay(1000);

  fill_solid(leds, NUM_LEDS, CRGB::Blue);
  FastLED.show();
  delay(1000);

  // Test pattern 3: Rainbow over the whole matrix
  for(int j = 0; j < 255; j++) {
    fill_rainbow(leds, NUM_LEDS, j, 7);
    FastLED.show();
    delay(20);
  }
}
