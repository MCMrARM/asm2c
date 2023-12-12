import enum
import json
from functools import partial
from typing import Any, Optional


class CDataType(enum.Enum):
    U8 = 'uint8_t'
    U16 = 'uint16_t'
    U32 = 'uint32_t'
    U64 = 'uint64_t'
    R128 = 'reg128'
    S8 = 'int8_t'
    S16 = 'int16_t'
    S32 = 'int32_t'
    S64 = 'int64_t'
    BOOL = 'bool'
    U8_PTR = 'uint8_t*'
    CONST_CHAR_PTR = 'const char*'
    FUNC_PTR = 'afuncptr_t'
    FUNC = 'afunc_t'

    def size(self):
        if self == CDataType.U8 or self == CDataType.S8 or self == CDataType.BOOL:
            return 1
        if self == CDataType.U16 or self == CDataType.S16:
            return 2
        if self == CDataType.U32 or self == CDataType.S32:
            return 4
        if self == CDataType.U64 or self == CDataType.S64 or self == CDataType.FUNC_PTR or self == CDataType.U8_PTR or self == CDataType.CONST_CHAR_PTR:
            return 8
        if self == CDataType.R128:
            return 16
        raise Exception(f"Unknown size for {self}")

    def make_signed(self):
        if self == CDataType.U8:
            return CDataType.S8
        if self == CDataType.U16:
            return CDataType.S16
        if self == CDataType.U32:
            return CDataType.S32
        if self == CDataType.U64:
            return CDataType.S64
        raise Exception(f"Cannot make {self} signed")


class CExpr:
    datatype: Optional[CDataType]


class CVar(CExpr):
    def __init__(self, name: str, datatype: CDataType):
        self.name = name
        self.datatype = datatype

    def __str__(self):
        return self.name


class CCast(CExpr):
    def __init__(self, expr: CExpr, datatype: CDataType, ref: bool):
        self.expr = expr
        self.datatype = datatype
        self.ref = ref

    def __str__(self):
        if self.ref:
            return f"({self.datatype.value}&) {self.expr}"
        return f"({self.datatype.value}) {self.expr}"


class CDeref(CExpr):
    def __init__(self, expr: CExpr, datatype: CDataType):
        self.expr = expr
        self.datatype = datatype

    def __str__(self):
        return f"*({self.datatype.value}*) {self.expr}"


class CRef(CExpr):
    def __init__(self, expr: CExpr):
        self.expr = expr

    def __str__(self):
        return f"&{self.expr}"

    @property
    def datatype(self):
        return CDataType.U8_PTR


class CArrIndex(CExpr):
    def __init__(self, expr: CExpr, index: CExpr):
        self.expr = expr
        self.index = index

    def __str__(self):
        return f"{self.expr}[{self.index}]"


class CImm(CExpr):
    def __init__(self, imm: Any, datatype: Optional[CDataType] = None):
        if datatype is None:
            if type(imm) == str:
                datatype = CDataType.U8_PTR
            elif type(imm) == int:
                datatype = CDataType.U32
            else:
                raise Exception(f"Unknown CImm type: {type(imm)}")

        self.imm = imm
        self.datatype = datatype

    def __str__(self):
        if type(self.imm) == str:
            return json.dumps(self.imm)
        if self.imm is False:
            return "false"
        if self.imm is True:
            return "true"
        if self.datatype == CDataType.R128:
            return "reg128{" + str(self.imm&((1<<64)-1)) + ',' + str((self.imm>>64)&((1<<64)-1)) + "}"
        if self.datatype == CDataType.S64:
            return hex(self.imm) + 'LL'
        if self.datatype == CDataType.U64:
            return hex(self.imm) + 'LLU'
        if self.datatype in (CDataType.S32, CDataType.S16, CDataType.S8):
            return hex(self.imm)
        return hex(self.imm) + 'U'


class CAssign(CExpr):
    def __init__(self, left: CExpr, right: CExpr, datatype: Optional[CDataType] = None):
        self.left = left
        self.right = right
        self.datatype = datatype

    def __str__(self):
        if self.datatype is not None:
            return f"({self.datatype.value}&) {self.left} = {self.right}"
        return f"{self.left} = {self.right}"


class CMemWrite(CExpr):
    def __init__(self, left: CExpr, right: CExpr, datatype: CDataType):
        self.left = left
        self.right = right
        self.datatype = datatype

    def __str__(self):
        return f"*({self.datatype.value}*) {self.left} = {self.right}"


class CArith(CExpr):
    def __init__(self, left: CExpr, right: CExpr, symbol: str):
        self.left = left
        self.right = right
        self.symbol = symbol

    def __str__(self):
        return f"({self.left} {self.symbol} {self.right})"

    @property
    def datatype(self):
        return self.left.datatype


class CArith1(CExpr):
    def __init__(self, left: CExpr, symbol: str):
        self.left = left
        self.symbol = symbol

    def __str__(self):
        return f"{self.symbol}{self.left}"

    @property
    def datatype(self):
        return self.left.datatype


class CCall(CExpr):
    def __init__(self, left: CExpr, args: list[CExpr], datatype: Optional[CDataType] = None):
        self.left = left
        self.args = args
        self.datatype = datatype

    def __str__(self):
        left = str(self.left)
        if not isinstance(self.left, CVar):
            left = f'({left})'
        return f"{left}(" + ', '.join(map(str, self.args)) + ")"


class CGoto(CExpr):
    def __init__(self, dest: str):
        self.dest = dest

    def __str__(self):
        return f"goto {self.dest}"


class CIf(CExpr):
    def __init__(self, cond: CExpr, then: CExpr):
        self.cond = cond
        self.then = then

    def __str__(self):
        return f"if ({self.cond}) {self.then}"


class CReturn(CExpr):
    def __init__(self, expr: CExpr):
        self.expr = expr

    def __str__(self):
        return f"return {self.expr}"


class CBlock(CExpr):
    def __init__(self, instructions: list[CExpr]):
        self.instructions = instructions

    def __str__(self):
        return ', '.join(str(x) for x in self.instructions)


CAdd = partial(CArith, symbol="+")
CSub = partial(CArith, symbol="-")
CMul = partial(CArith, symbol="*")
CDiv = partial(CArith, symbol="/")
CMod = partial(CArith, symbol="%")
CShl = partial(CArith, symbol="<<")
CShr = partial(CArith, symbol=">>")
CAnd = partial(CArith, symbol="&")
COr = partial(CArith, symbol="|")
CXor = partial(CArith, symbol="^")
CNot = partial(CArith1, symbol="!")
CNeg = partial(CArith1, symbol="-")

CEq = partial(CArith, symbol="==")
CNe = partial(CArith, symbol="!=")
CLt = partial(CArith, symbol="<")
CLEq = partial(CArith, symbol="<=")

