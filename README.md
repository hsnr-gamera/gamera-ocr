OCR Toolkit for Gamera
======================

Purpose
-------

"Optical character recognition" (OCR) means the extraction of the
text content from a document image.

This toolkit provides

 - python library functions for building custom ocr applications
 - a ready to use script ocr4gamera


Requirements
------------

This toolkit has been written for the Gamera framework and requires
a working installation of Gamera, version 4 or later.
See the Gamera homepage [https://gamera.sf.net/](https://gamera.sf.net/)


Documentation
-------------

For a user's guide and a developer's guide see 'doc/html/index.html'.
For release notes and a revision history see 'CHANGES'.

A comprehensive overview of design, usage and customization of the OCR
toolkit can be found in the paper

>  C. Dalitz, R. Baston:
>  [Optical Character Recognition with the  Gamera Framework.](https://lionel.kr.hsnr.de/~dalitz/data/publications/sr09-ocr-gamera.pdf)
>  In C. Dalitz (Ed.): "Document Image Analysis 
>  with the Gamera Framework." Schriftenreihe des Fachbereichs 
>  Elektrotechnik und Informatik, Hochschule Niederrhein, vol. 8,
>  pp. 53-65, Shaker Verlag (2009)

For a small exmaple including training data and test images, see
[https://gamera.informatik.hsnr.de/addons/ocr4gamera/](https://gamera.informatik.hsnr.de/addons/ocr4gamera/)

Installation
------------

Installation is done with `pip3`, which will install a python module
*gamera-ocr*. See the section "Installation" in *doc/html/index.html* or
*doc/src/index.txt*.


Authors
-------

 - Christoph Dalitz, 2009-2025, https://lionel.kr.hsnr.de/~dalitz/
 - Andreas Miller, 2023
 - Rene Baston, 2009

Please contact Christoph Dalitz for questions about this toolkit.


Acknowledgements
----------------

Thanks to Jakub Wilk, Robert Butz, and Fabian Schmitt for valuable
contributions to this toolkit.


License
-------

This toolkit is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License, either version 3
of the license, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
file LICENSE for more details.
