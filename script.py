import base64
import random
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

OUTPUT_FILE = "subs1"
MAX_CONFIGS = 100          # how many configs end up in the output file
TIMEOUT = 20               # seconds per source

NEW_HOST = "161.145.150.1"
ECH_VALUE = "ip.gs+udp://8.8.8.8"

# 20 free public subscription sources (plain text or Base64).
# Dead or changed sources are skipped automatically.
SOURCES = [
    "https://github.com/mohamadfg-dev/telegram-v2ray-configs-collector/raw/refs/heads/main/category/vless.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/protocols/vless.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/top100.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/verified/configs.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/fast/configs.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vless_configs.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/all_extracted_configs.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/V2Ray-Config-By-EbraSha-All-Type.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub3.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/filtered/subs/vless.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/refs/heads/main/subscriptions/v2ray/super-sub.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/refs/heads/main/subscriptions/v2ray/all_sub.txt",
    "https://github.com/Epodonios/v2ray-configs/raw/main/All_Configs_Sub.txt",
    "https://github.com/Delta-Kronecker/V2ray-Config/raw/refs/heads/main/config/all_configs.txt",
    "https://raw.githubusercontent.com/Firmfox/Proxify/refs/heads/main/v2ray_configs/mixed/subscription-1.txt",
    "https://raw.githubusercontent.com/Firmfox/Proxify/refs/heads/main/v2ray_configs/mixed/subscription-2.txt",
    "https://github.com/Au1rxx/free-vpn-subscriptions/raw/main/output/v2ray-base64.txt",
]


def maybe_b64_decode(text):
    """Return decoded text if it is a Base64 subscription, else the text unchanged."""
    text = text.strip()
    if "://" in text:
        return text
    try:
        padded = text + "=" * (-len(text) % 4)
        return base64.b64decode(padded).decode("utf-8", errors="ignore")
    except Exception:
        return text


def fetch(url):
    """Download one source and return its vless:// lines ([] on any failure)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        lines = [l.strip() for l in maybe_b64_decode(raw).splitlines()]
        found = [l for l in lines if l.startswith("vless://")]
        print(f"OK    {len(found):5d} vless  {url}")
        return found
    except Exception as e:
        print(f"SKIP  {url}  ({e})")
        return []


def transform_vless(line):
    """
    Keep only WebSocket vless links and rewrite them:
      - address -> NEW_HOST
      - add ech, mux=true, concurrency=8
    Returns the new link, or None if the link should be dropped.
    """
    try:
        parts = urlsplit(line)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        if query.get("type") != "ws" or not parts.username:
            return None

        query["ech"] = ECH_VALUE
        query["mux"] = "true"
        query["concurrency"] = "8"

        userinfo = parts.username
        if parts.password:
            userinfo += f":{parts.password}"
        netloc = f"{userinfo}@{NEW_HOST}"
        if parts.port:
            netloc += f":{parts.port}"

        return urlunsplit((
            parts.scheme,
            netloc,
            parts.path,
            urlencode(query, safe="+/:"),
            parts.fragment,
        ))
    except Exception:
        return None


def build(all_lines, max_configs=MAX_CONFIGS):
    """Transform, de-duplicate, then pick up to max_configs at random."""
    unique = {}
    for line in all_lines:
        new = transform_vless(line)
        if new:
            unique.setdefault(new.split("#")[0], new)   # de-dupe ignoring the tag
    pool = list(unique.values())
    chosen = random.sample(pool, min(max_configs, len(pool)))
    return pool, chosen


def main():
    print(f"Downloading {len(SOURCES)} sources...")
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(fetch, SOURCES))
    all_lines = [l for r in results for l in r]
    print(f"Total vless links downloaded: {len(all_lines)}")

    pool, chosen = build(all_lines)
    print(f"Unique ws links after transform: {len(pool)}")

    if not chosen:
        # Keep the old subs1 instead of overwriting it with an empty file.
        print("No configs found. Leaving existing subs1 untouched.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(chosen) + "\n")
    print(f"Done! Saved {len(chosen)} random configs to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
