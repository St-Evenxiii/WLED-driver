// Minimal host-side stand-in for Arduino + FastLED, just enough to compile
// and run test_matrix.ino on a PC. It records every frame passed to show()
// so tests can inspect what the sketch would have sent to the LEDs.
#pragma once

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include <cstdarg>
#include <string>
#include <vector>

// ---- Arduino ---------------------------------------------------------------
extern uint32_t g_millis;
inline uint32_t millis() { return g_millis; }
inline void delay(uint32_t ms) { g_millis += ms; }

struct MockSerial {
  std::vector<std::string> lines;
  std::string cur;
  void begin(unsigned long) {}
  void println() { lines.push_back(cur); cur.clear(); }
  void println(const char *s) { cur += s; println(); }
  int printf(const char *fmt, ...) {
    char buf[256];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof buf, fmt, ap);
    va_end(ap);
    for (const char *p = buf; *p; ++p) {
      if (*p == '\n') println(); else cur += *p;
    }
    return n;
  }
};
extern MockSerial Serial;

// ---- FastLED ---------------------------------------------------------------
struct CRGB {
  uint8_t r, g, b;
  CRGB() : r(0), g(0), b(0) {}
  CRGB(uint8_t r_, uint8_t g_, uint8_t b_) : r(r_), g(g_), b(b_) {}
  CRGB(uint32_t c) : r(c >> 16), g(c >> 8), b(c) {}  // NOLINT
  bool operator==(const CRGB &o) const { return r == o.r && g == o.g && b == o.b; }
  bool operator!=(const CRGB &o) const { return !(*this == o); }
  explicit operator bool() const { return r || g || b; }
  enum : uint32_t {
    Black = 0x000000, Red = 0xFF0000, Green = 0x008000, Blue = 0x0000FF,
    White = 0xFFFFFF, Cyan = 0x00FFFF, Magenta = 0xFF00FF,
  };
};

struct CHSV {
  uint8_t h, s, v;
  CHSV(uint8_t h_, uint8_t s_, uint8_t v_) : h(h_), s(s_), v(v_) {}
  operator CRGB() const {  // crude, but non-black for v > 0
    return CRGB(v, (uint8_t)(h | 1), (uint8_t)(255 - h) | 1);
  }
};

inline void fill_solid(CRGB *leds, int n, const CRGB &c) {
  for (int i = 0; i < n; i++) leds[i] = c;
}

enum EOrder { RGB, GRB };
enum LEDType { WS2812B };
enum { TypicalLEDStrip = 0xFFB0F0 };

struct CLEDController {
  CLEDController &setCorrection(uint32_t) { return *this; }
};

struct MockFastLED {
  CRGB *leds = nullptr;
  int numLeds = 0;
  int dataPin = -1;
  uint8_t brightness = 255;
  uint32_t maxMilliamps = 0;
  std::vector<std::vector<CRGB>> frames;
  CLEDController ctrl;

  template <LEDType T, int PIN, EOrder O>
  CLEDController &addLeds(CRGB *l, int n) {
    leds = l; numLeds = n; dataPin = PIN;
    return ctrl;
  }
  void setBrightness(uint8_t b) { brightness = b; }
  void setMaxPowerInVoltsAndMilliamps(uint8_t, uint32_t ma) { maxMilliamps = ma; }
  void show() { frames.emplace_back(leds, leds + numLeds); }
  void clear(bool writeData = false) {
    fill_solid(leds, numLeds, CRGB::Black);
    if (writeData) show();
  }
  void delay(uint32_t ms) { ::delay(ms); }
};
extern MockFastLED FastLED;
