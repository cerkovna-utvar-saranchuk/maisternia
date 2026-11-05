#!/usr/bin/env python3
"""Збирає зашифрований inbox.enc для застосунку «Майстерня».
Використання: make_inbox.py KEY OPS.json [photo=path ...]
OPS.json: {"ops":[{"t":"photo","order":"запонк","file":"/шлях/фото.jpg","cover":false},
                  {"t":"patch","order":"хрест","set":{"cphone":"+380..."}},
                  {"t":"add","order":{"name":"Нове","status":"sketch","items":[]}}]}
Кожен запуск отримує новий id, тож застосунок прийме файл один раз."""
import sys, json, io, os, base64, time
from PIL import Image, ImageOps
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def photo_url(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    for m, q in [(1280, 80), (1000, 72), (800, 65), (640, 60)]:
        c = im.copy(); c.thumbnail((m, m))
        b = io.BytesIO(); c.save(b, "JPEG", quality=q, optimize=True)
        if len(b.getvalue()) <= 650000: break
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

key, ops_path = sys.argv[1], sys.argv[2]
spec = json.load(open(ops_path, encoding="utf-8"))
ops = []
for op in spec["ops"]:
    op = dict(op)
    if op["t"] == "photo":
        op["data"] = photo_url(op.pop("file"))
    ops.append(op)
payload = json.dumps({"id": "b%d" % int(time.time()), "ops": ops}, ensure_ascii=False).encode()
salt, iv = os.urandom(16), os.urandom(12)
k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200000).derive(key.encode())
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inbox.enc")
open(out, "wb").write(salt + iv + AESGCM(k).encrypt(iv, payload, None))
print("inbox.enc записано,", len(ops), "операцій")
