// Coordinate -> LED index mapping for a WIDTH x HEIGHT matrix.
//
// Kept free of Arduino/FastLED dependencies so it can be unit-tested on a PC
// (see firmware/tests).
#pragma once

#include <stdint.h>

// Returns the strip index of pixel (x, y), with (0, 0) at the first LED's
// corner. `serpentine` selects zig-zag wiring (every odd row runs backwards),
// which is how almost all flexible 16x16 WS2812B panels are wired.
// Out-of-range coordinates return `width * height` (one past the end), so
// callers can keep a spare slot as a safe write target.
static inline uint16_t matrixIndex(uint8_t x, uint8_t y, uint8_t width,
                                   uint8_t height, bool serpentine) {
  if (x >= width || y >= height) {
    return (uint16_t)width * height;
  }
  if (serpentine && (y & 0x01)) {
    x = (width - 1) - x;
  }
  return (uint16_t)y * width + x;
}
