from datetime import timedelta

from starlette.requests import Request

from endpoints.auth_api import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


def sanitize_header_cookies(request_headers: dict) -> dict:
    request_headers["cookie"] = "REDACTED"
    return request_headers


async def get_body(request: Request):
    return await request.body()


def get_api_login_token():
    return create_access_token(
        data={"sub": "api"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
