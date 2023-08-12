RPGMAKER TRANS v4.x README
A Translation Patching Engine for RPGMaker Games
Copyright (C) 2012-2017 Habisain
Website: https://rpgmakertrans.bitbucket.io

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License Version 3 as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Usage:

It's recommended to use the documentation at
http://rpgmakertrans.bitbucket.org. A brief overview is given below.

Simply select the game directory, patch and target directory. If you are
starting a translation, select the 'create patch' checkbox to create an empty
patch which can then be translated.

RPGMaker Trans will attempt to automatically select appropriately named
patches and target directories.

Errors will appear in a text box in the GUI. Some errors will stop the
patching process, others will not, depending on severity. Note that if
there are errors, the game may not run even if the patching completed;
check to see what the error is and if necessary try running the patcher
again.

FAQ:

1) What languages are supported?

For 2k games: Only Japanese and ASCII character set languages. Support
for other languages is a long standing planned feature, but there are
still problems in executing it...

For XP/VX/VX Ace games: All UTF-8 Characters sets are supported. The one
exception to this rule is the title bar, which displays with the current
system locale, and as such should be treated as ASCII only. (Note: the game
will run even if it cannot display the title bar correctly, but it will
be garbage text. RPGMaker Trans tries to insert a new title by encoding
the titlebar text with the current locale; if this fails, the title is
simply preserved and will likely be garbage if the system locale doesn't
match the games intended locale)

2) Distributing patched games?

Will infringe copyright, so only do this with permission from the original
creator. Otherwise, distribute the patch. Whilst this still technically
infringes copyright, it is more 'acceptable' than the alternative.

3) What's pruby? Where can I get it's source code?

pruby is the name I've given to the portable minimal ruby installation that
is distributed with RPGMaker Trans. As such, source code, license etc. can
all be obtained from www.ruby-lang.org, or www.rubyinstaller.org. pruby was
made by capturing the decompressed Ruby environment that is generated when
running the main scripts frozen by OCRA (gem install ocra).

pruby isn't part of the source tree because it's just a convenient binary
for Windows users to have (rather than having them download Ruby1.9.3). Also
of note is that it is Windows only - OS X/Linux users are assumed to have
easy access to a working Ruby installation.

4) What's the difference between v2/v3 patches?

v2 patches are more of a dump of the internal state of the string insertion
component. As such v2 patches have very few features. They are currently used
for RPGMaker 2k games.

A v3 patch actually has a more defined language etc, so v3 patches have more
features (e.g. comments, persistent translation locations, pooled translations
between files, more detail). Currently they are used for all other RPGMaker
games. Eventually, the plan is that 2k games will support v3 files as well,
along with a conversion option.
