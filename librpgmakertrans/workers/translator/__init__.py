"""
translator
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides the translators - these handle parsing translation data,
serving translation requests and the output format on translation data
after it is changed.
"""

from . import translator2 as __translator2
from . import translator3 as __translator3 
from .translatorbase import TranslatorManager
