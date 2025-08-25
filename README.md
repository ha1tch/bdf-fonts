# bdf-fonts

**This was started as a fork of the original compilation by IT Studio Rech**
https://github.com/IT-Studio-Rech/bdf-fonts

Given that that particular project seems to be stalled or unatended, I decided to keep my own fork, adding fonts that are useful for my projects, and hopefully for others as well.

I'm keeping the notices of the original repo, and adding my own below:

---

These are BDF fonts, a simple bitmap font-format that can be created
by many font tools. Given that these are bitmap fonts, they will look good on
very low resolution screens such as the LED displays.

---
### Most fonts in this directory are public domain, except for the following exceptions, they each have their own licensing terms:
| Font | License |
|------|---------|
| tom-thumb.bdf | MIT |
| cozette.bdf | MIT |
| sinclair.bdf | Amstrad copyright |
| tahoma-*.bdf | LGPL 2.1 |
| All others | Public Domain |

# Not in the Public Domain:

Tom-Thumb.bdf is included in this directory under [MIT license](http://vt100.tarunz.org/LICENSE). Tom-thumb.bdf was created by [@robey](http://twitter.com/robey) and originally published at https://robey.lag.net/2010/01/23/tiny-monospace-font.html

---

Cozette.bdf is included in this fork under the MIT License, Copyright (c) 2020, Slavfox
https://github.com/the-moonwitch/Cozette

---

sinclair.bdf is the result of extracting the Sinclair font from a ZX Spectrum ROM. In a separate folder (sinclair/) I placed the ROM I used and the program I wrote to extract the font, so you can reproduce the same results if you wish.
The Sinclair ROM is copyrighted by Amstrad plc, and the terms of sharing can be read here:
https://github.com/ha1tch/bdf-fonts/tree/main/sinclair
The font extraction program sinclair.go is mine and I've placed it in the public domain.

---

The files named tahoma-xx.bdf are the result of extracting the bitmapped versions of the Wine Tahoma .ttf font created by the Wine Project. The original Wine Tahoma is here:
https://gitlab.winehq.org/wine/wine/-/blob/HEAD/fonts/tahoma.ttf
The Wine Tahoma font is free software under the LGPL 2.1 license
https://gitlab.winehq.org/wine/wine/-/blob/HEAD/LICENSE
Since the Wine Tahoma ttf was distributed by the Wine Project as a binary, and the extracted .bdf files I produced are structured text files, the bdf files are essentially source code, which I have shared in source code form. In my view this is more than compliant with the LGPL.






