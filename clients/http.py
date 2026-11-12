import logging
import random
import time
import uuid
from typing import Any

import requests

from clients.errors import NotFoundError, ServiceUnavailableError

RUN_ID = str(uuid.uuid4())[:8]

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [run_id={RUN_ID}] %(levelname)s: %(message)s",
)
logger = logging.getLogger("city_summary")

RETRYABLE_STATUSES = {500, 502, 503, 504}
MAX_ATTEMPTS = 3
TIMEOUT = (3.0, 7.0)


def fetch_json(url: str, params: dict[str, Any] | None = None) -> Any:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)

            if response.status_code == 404:
                raise NotFoundError(f"Resource not found: {url}")

            if response.status_code == 429:
                if attempt == MAX_ATTEMPTS:
                    raise ServiceUnavailableError("Rate limit exceeded after retries")
                retry_after_raw = response.headers.get("Retry-After", "1")
                delay = float(retry_after_raw) if retry_after_raw.isdigit() else 1.0
                logger.warning("429 Too Many Requests for %s, waiting %ss", url, delay)
                time.sleep(delay)
                continue

            if response.status_code in RETRYABLE_STATUSES:
                if attempt == MAX_ATTEMPTS:
                    raise ServiceUnavailableError(
                        f"Server error {response.status_code} for {url}"
                    )
                delay = (2 ** (attempt - 1)) + random.uniform(0, 0.3)
                logger.warning(
                    "Status %s for %s, retry %s/%s in %.2fs",
                    response.status_code,
                    url,
                    attempt,
                    MAX_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)
                continue

            if response.status_code >= 400:
                raise ServiceUnavailableError(
                    f"Unexpected HTTP {response.status_code} for {url}"
                )

            try:
                return response.json()
            except ValueError as exc:
                raise ServiceUnavailableError(f"Invalid JSON from {url}") from exc

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            if attempt == MAX_ATTEMPTS:
                raise ServiceUnavailableError(f"Network error for {url}") from exc
            delay = (2 ** (attempt - 1)) + random.uniform(0, 0.3)
            logger.warning(
                "Network error (%s) for %s, retry %s/%s in %.2fs",
                type(exc).__name__,
                url,
                attempt,
                MAX_ATTEMPTS,
                delay,
            )
            time.sleep(delay)

    raise ServiceUnavailableError(f"Failed to fetch {url}")
