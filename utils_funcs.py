def sanitize_header_cookies(request_headers: dict) -> dict:
    request_headers["cookie"] = "REDACTED"
    return request_headers
