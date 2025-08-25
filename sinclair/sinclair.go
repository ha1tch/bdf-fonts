package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"time"
)

const (
	// ZX Spectrum 48K ROM character set location
	CHARSET_OFFSET = 0x3D00 // 15616 decimal
	CHAR_HEIGHT    = 8      // Each character is 8 pixels tall
	CHAR_WIDTH     = 8      // Each character is 8 pixels wide
	CHAR_SIZE      = 8      // 8 bytes per character
	FIRST_CHAR     = 32     // First printable character (space)
	LAST_CHAR      = 127    // Last character (DEL)
	NUM_CHARS      = LAST_CHAR - FIRST_CHAR + 1
)

// Character names for BDF format
var charNames = map[int]string{
	32: "space", 33: "exclam", 34: "quotedbl", 35: "numbersign",
	36: "dollar", 37: "percent", 38: "ampersand", 39: "quotesingle",
	40: "parenleft", 41: "parenright", 42: "asterisk", 43: "plus",
	44: "comma", 45: "hyphen", 46: "period", 47: "slash",
	48: "zero", 49: "one", 50: "two", 51: "three",
	52: "four", 53: "five", 54: "six", 55: "seven",
	56: "eight", 57: "nine", 58: "colon", 59: "semicolon",
	60: "less", 61: "equal", 62: "greater", 63: "question",
	64: "at", 65: "A", 66: "B", 67: "C", 68: "D", 69: "E", 70: "F", 71: "G",
	72: "H", 73: "I", 74: "J", 75: "K", 76: "L", 77: "M", 78: "N", 79: "O",
	80: "P", 81: "Q", 82: "R", 83: "S", 84: "T", 85: "U", 86: "V", 87: "W",
	88: "X", 89: "Y", 90: "Z", 91: "bracketleft", 92: "backslash",
	93: "bracketright", 94: "asciicircum", 95: "underscore",
	96: "grave", 97: "a", 98: "b", 99: "c", 100: "d", 101: "e", 102: "f", 103: "g",
	104: "h", 105: "i", 106: "j", 107: "k", 108: "l", 109: "m", 110: "n", 111: "o",
	112: "p", 113: "q", 114: "r", 115: "s", 116: "t", 117: "u", 118: "v", 119: "w",
	120: "x", 121: "y", 122: "z", 123: "braceleft", 124: "bar",
	125: "braceright", 126: "asciitilde", 127: "DEL",
}

func main() {
	if len(os.Args) != 2 {
		fmt.Printf("Usage: %s <zx_spectrum_48k_rom.bin>\n", os.Args[0])
		fmt.Printf("Example: %s zx48.rom\n", os.Args[0])
		os.Exit(1)
	}

	romFile := os.Args[1]

	// Read the ROM file
	romData, err := ioutil.ReadFile(romFile)
	if err != nil {
		log.Fatalf("Error reading ROM file %s: %v", romFile, err)
	}

	// Verify ROM size (should be 16KB for ZX Spectrum 48K)
	if len(romData) < CHARSET_OFFSET+NUM_CHARS*CHAR_SIZE {
		log.Fatalf("ROM file too small. Expected at least %d bytes, got %d",
			CHARSET_OFFSET+NUM_CHARS*CHAR_SIZE, len(romData))
	}

	fmt.Printf("Extracting character set from %s...\n", romFile)
	fmt.Printf("Character data starts at offset 0x%04X (%d)\n", CHARSET_OFFSET, CHARSET_OFFSET)

	// Extract character set and convert to BDF
	bdfContent := generateBDF(romData[CHARSET_OFFSET:])

	// Write BDF file
	outputFile := "sinclair.bdf"
	err = ioutil.WriteFile(outputFile, []byte(bdfContent), 0644)
	if err != nil {
		log.Fatalf("Error writing BDF file: %v", err)
	}

	fmt.Printf("Successfully created %s\n", outputFile)
	fmt.Printf("Contains %d characters (%d-%d)\n", NUM_CHARS, FIRST_CHAR, LAST_CHAR)
}

func generateBDF(charData []byte) string {
	var bdf string

	// BDF Header
	bdf += "STARTFONT 2.1\n"
	bdf += "FONT -Sinclair-ZXSpectrum-Medium-R-Normal--8-80-75-75-C-80-ISO8859-1\n"
	bdf += "SIZE 8 75 75\n"
	bdf += "FONTBOUNDINGBOX 8 8 0 -2\n"
	bdf += "COMMENT \"ZX Spectrum 48K Character Set\"\n"
	bdf += fmt.Sprintf("COMMENT \"Extracted on %s\"\n", time.Now().Format("2006-01-02 15:04:05"))
	bdf += "COMMENT \"Original character set from Sinclair ZX Spectrum 48K ROM\"\n"

	// Font properties
	bdf += "STARTPROPERTIES 7\n"
	bdf += "FOUNDRY \"Sinclair\"\n"
	bdf += "FAMILY_NAME \"ZX Spectrum\"\n"
	bdf += "WEIGHT_NAME \"Medium\"\n"
	bdf += "SLANT \"R\"\n"
	bdf += "SETWIDTH_NAME \"Normal\"\n"
	bdf += "PIXEL_SIZE 8\n"
	bdf += "POINT_SIZE 80\n"
	bdf += "ENDPROPERTIES\n"

	bdf += fmt.Sprintf("CHARS %d\n", NUM_CHARS)

	// Process each character
	for i := 0; i < NUM_CHARS; i++ {
		charCode := FIRST_CHAR + i
		charName := getCharName(charCode)

		// Extract 8 bytes for this character
		charBytes := charData[i*CHAR_SIZE : (i+1)*CHAR_SIZE]

		// Generate BDF character entry
		bdf += fmt.Sprintf("STARTCHAR %s\n", charName)
		bdf += fmt.Sprintf("ENCODING %d\n", charCode)
		bdf += "SWIDTH 640 0\n" // Scaled width (8 pixels * 80 units/pixel)
		bdf += "DWIDTH 8 0\n"   // Device width in pixels
		bdf += "BBX 8 8 0 -2\n" // Bounding box: width height x_offset y_offset
		bdf += "BITMAP\n"

		// Convert each byte to hex (each byte represents one row of pixels)
		for _, b := range charBytes {
			bdf += fmt.Sprintf("%02X\n", b)
		}

		bdf += "ENDCHAR\n"
	}

	bdf += "ENDFONT\n"
	return bdf
}

func getCharName(charCode int) string {
	if name, exists := charNames[charCode]; exists {
		return name
	}
	// Fallback for unmapped characters
	return fmt.Sprintf("char%03d", charCode)
}

// Utility function to display character bitmap (for debugging)
func displayCharBitmap(charBytes []byte, charCode int) {
	fmt.Printf("Character %d ('%c'):\n", charCode, charCode)
	for _, b := range charBytes {
		for bit := 7; bit >= 0; bit-- {
			if (b>>bit)&1 == 1 {
				fmt.Print("██")
			} else {
				fmt.Print("  ")
			}
		}
		fmt.Println()
	}
	fmt.Println()
}
