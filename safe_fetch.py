# TODO: Fetch Safety Gate (SSRF prevention, timeouts, robots.txt, honest User-Agent)

"""Fetch Safety Gate (safe_fetch.py) used exclusively by Agent 2b (agents/verify.py).
Enforces:
- http/https schemes only
- DNS resolution & strict refusal of private, loopback, link-local, multicast, and reserved IPs
- Re-validation of scheme and IP on every redirect hop (max 3 redirects)
- Honest User-Agent identification
- robots.txt compliance via urllib.robotparser
- Short timeouts (4.0s) and strict response byte cap (512 KB)
"""

import ipaddress
import socket
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

USER_AGENT = "SahiCheckBot/2.0 (+https://github.com/sahicheck; open-source-job-fraud-detector)"
DEFAULT_TIMEOUT = 4.0
MAX_RESPONSE_BYTES = 512 * 1024  # 512 KB
MAX_REDIRECTS = 3


class SafeFetchError(Exception):
    """Raised when a URL fails safety validation or cannot be fetched safely."""


def _validate_url_and_resolve_ips(url: str) -> Tuple[str, str, int]:
    """Validates scheme, extracts hostname/port, resolves DNS, and blocks non-global IPs."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SafeFetchError(f"Blocked scheme '{parsed.scheme}'. Only http and https are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise SafeFetchError("URL is missing a valid hostname.")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    try:
        addr_info = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SafeFetchError(f"DNS resolution failed for {hostname}: {exc}") from exc

    if not addr_info:
        raise SafeFetchError(f"No IP addresses resolved for {hostname}.")

    for entry in addr_info:
        ip_str = entry[4][0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError as exc:
            raise SafeFetchError(f"Invalid IP address resolved: {ip_str}") from exc

        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
            or not ip_obj.is_global
        ):
            raise SafeFetchError(f"Refused non-public IP address ({ip_str}) for host {hostname}.")

    return parsed.scheme, hostname, port


def _fetch_raw_once(url: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[int, Dict[str, str], bytes, str]:
    """Performs a streaming HTTP GET with manual redirect handling and safety re-checks on every hop."""
    current_url = url
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/rdap+json,application/json;q=0.9,*/*;q=0.5",
    }

    with httpx.Client(timeout=timeout, follow_redirects=False, headers=headers) as client:
        for _hop in range(MAX_REDIRECTS + 1):
            _validate_url_and_resolve_ips(current_url)

            with client.stream("GET", current_url) as response:
                status = response.status_code
                resp_headers = {k.lower(): v for k, v in response.headers.items()}

                if status in (301, 302, 303, 307, 308):
                    location = resp_headers.get("location")
                    if not location:
                        raise SafeFetchError("Redirect response missing Location header.")
                    current_url = urljoin(current_url, location)
                    continue

                chunks = []
                total_bytes = 0
                for chunk in response.iter_bytes(chunk_size=16384):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_RESPONSE_BYTES:
                        break
                    chunks.append(chunk)

                return status, resp_headers, b"".join(chunks), current_url

    raise SafeFetchError(f"Exceeded maximum redirects ({MAX_REDIRECTS}).")


def is_allowed_by_robots(url: str, timeout: float = 2.5) -> bool:
    """Checks robots.txt for the target origin before fetching HTML pages.
    If robots.txt is unreachable or 404, defaults to allowed per standard web convention.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        status, _headers, body, _final_url = _fetch_raw_once(robots_url, timeout=timeout)
        if status == 200 and body:
            rp = RobotFileParser()
            rp.parse(body.decode("utf-8", errors="ignore").splitlines())
            return rp.can_fetch(USER_AGENT, url)
        return True
    except Exception:
        return True


def safe_get_text(url: str, check_robots: bool = True, timeout: float = DEFAULT_TIMEOUT) -> Tuple[int, str, str]:
    """Safely fetches a URL and returns (status_code, decoded_text, final_url)."""
    _validate_url_and_resolve_ips(url)
    if check_robots and not is_allowed_by_robots(url):
        raise SafeFetchError(f"Blocked by robots.txt policy for {url}")

    status, _headers, raw_bytes, final_url = _fetch_raw_once(url, timeout=timeout)
    text = raw_bytes.decode("utf-8", errors="replace")
    return status, text, final_url


def safe_get_json(url: str, check_robots: bool = False, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Safely fetches a JSON/RDAP endpoint and returns the parsed dictionary."""
    import json

    status, text, _final_url = safe_get_text(url, check_robots=check_robots, timeout=timeout)
    if status >= 400:
        raise SafeFetchError(f"HTTP {status} from {url}")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise SafeFetchError("Expected JSON object response.")
    return data
