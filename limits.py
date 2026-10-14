# limits.py — per-config speed limiting (token bucket) + VLESS/Trojan header parsing.
# Pure helpers, no imports from main (avoids the old circular import).
import asyncio
import base64
import hashlib
import time
import uuid as _uuid

MIN_RATE = 8 * 1024          # never throttle below 8 KB/s
MIN_BURST = 64 * 1024        # allow small bursts so handshakes stay snappy


class TokenBucket:
    __slots__ = ("rate", "capacity", "tokens", "last", "lock")

    def __init__(self, rate: int):
        self.rate = max(int(rate), MIN_RATE)
        self.capacity = max(self.rate, MIN_BURST)
        self.tokens = float(self.capacity)
        self.last = time.monotonic()
        self.lock = asyncio.Lock()

    async def consume(self, n: int):
        if n <= 0:
            return
        async with self.lock:
            while True:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
                self.last = now
                # Frames larger than the bucket are allowed to drive tokens negative,
                # which turns into a proportional wait instead of a deadlock.
                if self.tokens >= min(n, self.capacity):
                    self.tokens -= n
                    return
                deficit = min(n, self.capacity) - self.tokens
                await asyncio.sleep(min(max(deficit / self.rate, 0.005), 0.5))


_buckets: dict = {}


def bucket_for(uid: str, direction: str, rate: int):
    """Shared bucket per (config, direction). Returns None when unlimited."""
    if not rate or rate <= 0:
        _buckets.pop((uid, direction), None)
        return None
    key = (uid, direction)
    b = _buckets.get(key)
    if b is None or b.rate != max(int(rate), MIN_RATE):
        b = TokenBucket(rate)
        _buckets[key] = b
    return b


def drop_buckets(uid: str):
    for d in ("up", "down"):
        _buckets.pop((uid, d), None)


def vless_uuid_from_chunk(chunk: bytes):
    """VLESS request header = version(1) + uuid(16) + ... Return the uuid string or None."""
    if not chunk or len(chunk) < 17 or chunk[0] != 0:
        return None
    try:
        return str(_uuid.UUID(bytes=bytes(chunk[1:17])))
    except Exception:
        return None


# ---------------------------------------------------------------- trojan
_HEX = frozenset("0123456789abcdef")


def trojan_hash(password: str) -> str:
    """Trojan identifies users by hex(SHA224(password)) — 56 lowercase hex chars."""
    return hashlib.sha224(str(password).encode("utf-8")).hexdigest()


def trojan_hash_from_chunk(chunk: bytes):
    """Trojan request = hex(SHA224(password))[56] + CRLF + cmd + addr + CRLF + payload.

    Returns the lowercase hex digest carried by the client, or None when the first
    bytes are not a well-formed Trojan header.
    """
    if not chunk or len(chunk) < 58:
        return None
    if bytes(chunk[56:58]) != b"\r\n":
        return None
    try:
        head = bytes(chunk[:56]).decode("ascii").lower()
    except Exception:
        return None
    return head if all(c in _HEX for c in head) else None


def decode_early_data(proto_header: str | None):
    """Xray clients may ship the first bytes in Sec-WebSocket-Protocol (base64url)."""
    if not proto_header:
        return None
    token = proto_header.split(",")[0].strip()
    if not token:
        return None
    try:
        pad = "=" * (-len(token) % 4)
        data = base64.urlsafe_b64decode(token + pad)
        return data if data else None
    except Exception:
        return None
