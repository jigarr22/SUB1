import urllib.request
import base64

# URL to download from
url = "https://jigaarr24.pythonanywhere.com/xprr?File=31"

# Download the content
print("Downloading...")
with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8').strip()

# The content is Base64 encoded, so decode it
print("Decoding Base64...")
decoded_bytes = base64.b64decode(content)
decoded_text = decoded_bytes.decode('utf-8')

# Save to subs1 file
print("Saving to subs1...")
with open("subs1", "w", encoding="utf-8") as f:
    f.write(decoded_text)

print("Done! Content saved to 'subs1'")
print(f"Total lines: {len(decoded_text.splitlines())}")
