#!E:\dreamsavior\rpgmakermt\python\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'PyBuilder==0.11.6','console_scripts','pyb_'
__requires__ = 'PyBuilder==0.11.6'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('PyBuilder==0.11.6', 'console_scripts', 'pyb_')()
    )
