import urllib.request
import base64
from urllib.parse import quote, urlsplit, urlunsplit, parse_qsl, urlencode
import re


# URL to download from
# url = "https://jigaarr24.pythonanywhere.com/xprr?File=31"
url = "https://github.com/mohamadfg-dev/telegram-v2ray-configs-collector/raw/refs/heads/main/category/vless.txt"

# Download the content
print("Downloading...")
with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8').strip()

print(content)
# The content is Base64 encoded, so decode it
# print("Decoding Base64...")
# decoded_bytes = base64.b64decode(content)
# decoded_text = decoded_bytes.decode('utf-8')

# Save to subs1 file
print("Saving to subs1...")
with open("subs1", "w", encoding="utf-8") as f:
    # f.write(decoded_text)
    f.write(content)



def transform_vless(str1, output_file="subs1"):
    """
    For every vless:// URL containing '&type=ws':
      1. Add 'ech=ip.js+udp://8.8.8.8' (URL-encoded value).
      2. Replace the address between '@' and ':' with 188.114.97.6.
      3. Add mux=true (MUX on).
      4. Set concurrency=8.
    """

    # with open(input_file, "r", encoding="utf-8") as f:
    #     lines = f.readlines()
    lines = str1.split('\n')
    # print(lines)
    
    out_lines = []
    changed = 0

    for line in lines:
        line = line.rstrip("\n")

        # Only process vless links that contain &type=ws
        if not line.startswith("vless://") or "&type=ws" not in line:
            
            # out_lines.append(line)
            continue
        # print('Found.')
        # --- Split the URL into its parts ---
        # vless://user@host:port?query#fragment
        parts = urlsplit(line)
        # parts.username = user
        # parts.hostname = current host
        # parts.port     = port
        # parts.query    = query string
        # parts.fragment = tag (after #)

        # --- 1) Add ech param ---
        # 'ech=ip.js+udp://8.8.8.8'  --> we URL-encode the value only
        ech_value = quote("ip.js+udp://8.8.8.8", safe="")  # -> ip.js%2Budp%3A%2F%2F8.8.8.8
        # Actually we want '+' preserved as literal plus in the host part:
        ech_value = quote("ip.js+udp://8.8.8.8", safe="+")  # -> ip.js+udp%3A%2F%2F8.8.8.8

        # --- 2) Replace host with 188.114.97.6 ---
        new_host = "188.114.97.6"

        # --- 3) & 4) Add mux=true and concurrency=8 ---
        query_pairs = parse_qsl(parts.query, keep_blank_values=True)
        query_dict = dict(query_pairs)

        query_dict["ech"] = "ip.js+udp://8.8.8.8"      # will be encoded below
        query_dict["mux"] = "true"
        query_dict["concurrency"] = "8"

        # Rebuild query (urlencode handles encoding, keeps '+' by default in query)
        new_query = urlencode(query_dict, safe="+/:")

        # Rebuild netloc with new host (keep userinfo and port)
        userinfo = parts.username or ""
        if parts.password:
            userinfo += f":{parts.password}"
        new_netloc = f"{userinfo}@{new_host}"
        if parts.port:
            new_netloc += f":{parts.port}"

        new_url = urlunsplit((
            parts.scheme,
            new_netloc,
            parts.path,
            new_query,
            parts.fragment,
        ))

        out_lines.append(new_url)
        changed += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")
    print(changed)

    print(f"Processed {changed} vless links with type=ws")
    print(f"Saved to {output_file}")


transform_vless(content)



print("Done! Content saved to 'subs1'")
# print(f"Total lines: {len(content.splitlines())}")
