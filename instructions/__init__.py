from instructions.nop import *

from instructions.clc import *
from instructions.sec import *
from instructions.cli import *
from instructions.sei import *
from instructions.clv import *
from instructions.cld import *
from instructions.sed import *

from instructions.txa import *
from instructions.tax import *
from instructions.tya import *
from instructions.tay import *
from instructions.inx import *
from instructions.iny import *
from instructions.dex import *
from instructions.dey import *

from instructions.txs import *
from instructions.tsx import *
from instructions.pha import *
from instructions.pla import *
from instructions.php import *
from instructions.plp import *

from instructions.lda import *
from instructions.ldx import *
from instructions.ldy import *


__all__ = [
    "nop",
    "clc", "sec", "cli", "sei", "clv", "cld", "sed",
    "txa", "tax", "tya", "tay", "inx", "iny", "dex", "dey",
    "txs", "tsx", "pha", "plp", "php", "plp",
    "lda", "ldx", "ldy",
]
