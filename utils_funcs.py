from starlette.requests import Request


def sanitize_header_cookies(request_headers: dict) -> dict:
    request_headers["cookie"] = "REDACTED"
    return request_headers


async def get_body(request: Request):
    return await request.body()
