"""Generate the 6 robot portraits with Muse Image (needs MODEL_API_KEY).

Saves PNGs to assets/portraits/<NAME>.png. Mock mode: the web client
draws procedural placeholder portraits labeled as placeholders.
"""
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.profiles import SAMPLES, CREATOR_TEMPLATE  # noqa: E402
from meta.adapters import generate_image  # noqa: E402


def save_image(payload, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = payload.get("data", [{}])[0] if isinstance(payload, dict) else {}
    if data.get("b64_json"):
        with open(path, "wb") as f:
            f.write(base64.b64decode(data["b64_json"]))
    elif data.get("url"):
        import urllib.request
        urllib.request.urlretrieve(data["url"], path)
    else:
        with open(path + ".json", "w") as f:
            f.write(str(payload))
        print("saved raw payload, no image bytes: %s" % path)
        return
    print("wrote %s" % path)


def main():
    if not os.environ.get("MODEL_API_KEY"):
        print("GAP: MODEL_API_KEY not set. Portraits stay procedural placeholders.")
        sys.exit(2)
    for p in SAMPLES[:5] + [CREATOR_TEMPLATE]:
        prompt = ("pixel-art robot portrait, front view, plain dark background, "
                  "friendly humanoid, accent color, character: %s, %s" % (
                      p["name"], p["backstory"]))
        save_image(generate_image(prompt), "assets/portraits/%s.png" % p["name"])


if __name__ == "__main__":
    main()
