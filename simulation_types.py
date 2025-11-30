from typing import TypedDict


class SwapInfo(TypedDict):
    from_: str    
    to: str
    fromAmount: float
    toAmount: float


class VictimTxn(TypedDict):
    signature: str
    programId: str
    signer: str
    swapInfo: SwapInfo
