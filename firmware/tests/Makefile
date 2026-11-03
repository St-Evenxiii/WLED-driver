CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Werror -O1

test: test_firmware
	./test_firmware

test_firmware: test_firmware.cpp mock/FastLED.h ../test_matrix/test_matrix.ino ../test_matrix/matrix_map.h
	$(CXX) $(CXXFLAGS) -Imock -x c++ test_firmware.cpp -o $@

clean:
	rm -f test_firmware

.PHONY: test clean
