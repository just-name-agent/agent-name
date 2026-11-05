"""Meta Model API adapters. Stdlib only. Base URL + model IDs per
https://dev.meta.ai/docs/overview (inspected 2026-11-05).

All calls go through the server proxy (scripts/), never the browser.
No MODEL_API_KEY = mock mode, clearly labeled.
"""
import json
import os
import urllib.request

BASE = "https://api.meta.ai/v1"
SPARK = "muse-spark-1.3"
WONDER = "muse-wonder-1.0"
IMAGE = "muse-image-1.0"
TRANSCRIBE = "muse-voice-transcribe-1.0"
SAM = "sam-3.1"


def _key():
    key = os.environ.get("MODEL_API_KEY", "")
    if not key:
        raise RuntimeError("MODEL_API_KEY not set — running in mock mode")
    return key


def _post(path, payload, timeout=90):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + _key(),
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def spark_decide(obs, profile, system_prompt, model=SPARK):
    """One structured decision. Returns dict. Raises on any failure."""
    res = _post("/responses", {
        "model": model,
        "reasoning": {"effort": "low"},
        "input": system_prompt + "\nState: " + json.dumps(obs),
    })
    text = _extract_text(res)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON in Spark reply")
    return json.loads(text[start:end + 1])


def _extract_text(res):
    if isinstance(res, dict):
        out = res.get("output") or res.get("outputs") or []
        chunks = []
        for item in out if isinstance(out, list) else []:
            content = item.get("content", []) if isinstance(item, dict) else []
            for c in content if isinstance(content, list) else []:
                if isinstance(c, dict) and "text" in c:
                    chunks.append(c["text"])
        if chunks:
            return "\n".join(chunks)
        for k in ("text", "output_text", "result"):
            if isinstance(res.get(k), str):
                return res[k]
    return json.dumps(res)


def generate_image(prompt):
    """Muse Image. Returns dict with image payload (base64 or URL)."""
    return _post("/images/generations", {"model": IMAGE, "prompt": prompt})


def transcribe_file(path):
    """Voice Transcribe for a local audio file. Returns transcript text."""
    import mimetypes
    boundary = "----nullsociety"
    with open(path, "rb") as f:
        blob = f.read()
    ctype = mimetypes.guess_type(path)[0] or "audio/wav"
    body = (("--%s\r\nContent-Disposition: form-data; name=\"file\"; "
             "filename=\"backstory\"\r\nContent-Type: %s\r\n\r\n" % (boundary, ctype)
             ).encode() + blob +
            ("\r\n--%s\r\nContent-Disposition: form-data; "
             "name=\"model\"\r\n\r\n%s\r\n--%s--\r\n" % (
                 boundary, TRANSCRIBE, boundary)).encode())
    req = urllib.request.Request(
        BASE + "/asr/transcribe", data=body,
        headers={"Authorization": "Bearer " + _key(),
                 "Content-Type": "multipart/form-data; boundary=" + boundary})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.load(r)
    if isinstance(res, dict):
        return res.get("text") or res.get("transcript") or json.dumps(res)
    return str(res)


def sam_segment(image_path, prompt):
    """SAM 3.1 over Model API. Request shape conditional on
    /docs/media-segmentation guide — verify live before claiming.
    Uploads image via /v1/files, then segments with text prompt."""
    with open(image_path, "rb") as f:
        blob = f.read()
    boundary = "----nullsociety"
    body = (("--%s\r\nContent-Disposition: form-data; name=\"file\"; "
             "filename=\"frame\"\r\nContent-Type: image/png\r\n\r\n" % boundary
             ).encode() + blob + ("\r\n--%s--\r\n" % boundary).encode())
    req = urllib.request.Request(
        BASE + "/files", data=body,
        headers={"Authorization": "Bearer " + _key(),
                 "Content-Type": "multipart/form-data; boundary=" + boundary})
    with urllib.request.urlopen(req, timeout=120) as r:
        up = json.load(r)
    file_id = up.get("id") if isinstance(up, dict) else None
    return _post("/responses", {
        "model": SAM,
        "input": [{"file_id": file_id, "prompt": prompt}] if file_id else prompt,
    })
