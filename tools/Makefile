BIN = ../bin

GPP = g++

LIBINTELHEX = hextosyx/libintelhex

HEXTOSYX  = $(BIN)/hextosyx

all: $(HEXTOSYX)

.PHONY: clean

$(HEXTOSYX): hextosyx/hextosyx.cpp
	$(GPP) -Ofast -std=c++0x -I$(LIBINTELHEX)/include $(LIBINTELHEX)/src/intelhex.cc $^ -o $@

clean:
	$(RM) $(HEXTOSYX)
