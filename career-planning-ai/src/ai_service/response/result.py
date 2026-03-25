from typing import Any

__all__ = ["success", "success_msg", "error", "error_msg"]

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


class Result:
    def __init__(self, code: int, data: Any | None, msg: str = None):
        self.code = code
        self.state = code < 400
        self.msg = msg or self.__setMessage()
        self.data = data

    def __str__(self):
        return f"<Result: code={self.code}, state={self.state}, msg={self.msg}, data={self.data}>"

    def __repr__(self):
        return self.__str__()

    def __setMessage(self) -> str:
        if self.code == 200:
            return "Success! (=^･ω･^=)"
        elif self.code == 400:
            return "Bad Request! o(^・x・^)o"
        elif self.code == 401:
            return "Access restricted! (＾• ω •＾)"
        elif self.code == 402:
            return "Verification has expired(=^•ᆺ•^=)"
        elif self.code == 403:
            return "Request not allowed! (^◔ᴥ◔^)"
        elif self.code == 429:
            return "Request time interval is too short! (^-人-^)"
        elif self.code == 500:
            return "Error! (=^-ω-^=)"
        else:
            return "What! o(^・x・^)o"


def success(data: Any | None = None) -> JSONResponse:
    return JSONResponse(content=jsonable_encoder(Result(200, data)))


def success_msg(msg: str, data: Any | None = None):
    return JSONResponse(content=jsonable_encoder(Result(200, data, msg)))


def error(code: int = 500):
    return JSONResponse(content=jsonable_encoder(Result(code, None)))


def error_msg(msg: str, code: int = 500):
    return JSONResponse(content=jsonable_encoder(Result(code, None, msg)))
