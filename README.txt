RPGMAKER TRANS v2.x README
A Translation Patching Engine for RPGMaker Games
Copyright (C) 2012-2014 Habisain

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License Version 3 as 
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Prerequisites:

IF YOU ARE MISSING MSVCR100.DLL INSTALL THE MS VC++ REDISTRIBUTABLE HERE:

http://www.microsoft.com/en-us/download/details.aspx?id=26999

Most people will have this installed, but if not, that's where to get it.

Usage:

Simply select the game directory, patch and target directory. If you are 
starting a translation, select the 'create patch' checkbox to create an empty
patch which can then be translated.

If you are translating, checking the "Use UTF-8 BOM" checkbox will cause
all patch files to have a UTF-8 BOM. This is needed for some editors to
recognise UTF-8 files. However, it will break other editors, and is
specifically not recommended by the UTF-8 Standard. If you are patching
a game, then this checkbox has no effect; RPGMaker Trans will recognise
patches with and without the UTF-8 BOM.

RPGMaker Trans will attempt to automatically select appropriately named
patches and target directories. 

Errors will appear in a text box in the GUI. Some errors will stop the
patching process, others will not, depending on severity. Note that if
there are errors, the game may not run even if the patching completed;
check to see what the error is and if necessary try running the patcher
again.

FAQ:

1) What languages are supported?

Only Japanese and ASCII character set languages. Other languages will be
supported eventually.

2) Distributing patched games?

Will infringe copyright, so only do this with permission from the original
creator. Otherwise, distribute the patch. Whilst this still technically
infringes copyright, it is more 'acceptable' than the alternative.

3) I get a "cannot get ZipImporter instance" error.

Not a question, but due to bugs in cx_freeze (the component I use to turn
Python scripts into an EXE), RPGMaker Trans cannot be run from a directory
containing non-ASCII characters. Solution is to run RPGMaker Trans
from a directory whose path only contains ASCII characters.
