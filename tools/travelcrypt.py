#!/usr/bin/env python3
"""Versleuteling voor Travelmap Robert.

De leesbare data (data.js) wordt NOOIT gecommit. Op GitHub staan alleen:
  data.enc    gzip(data.js), versleuteld met AES-256-GCM met een vaste datasleutel (DK)
  keys.json   DK, versleuteld met een sleutel afgeleid van het wachtwoord (PBKDF2-SHA256)
  share/<id>.json  vervaldatum + DK (of, bij een deel van de data, share/<id>.enc met eigen sleutel)
                   versleuteld met een deelsleutel die alleen in de deellink staat

Gebruik (wachtwoord via omgevingsvariabele TRAVEL_PW):
  travelcrypt.py init               nieuwe DK + keys.json + data.enc maken uit data.js
  travelcrypt.py encrypt            data.js opnieuw versleutelen (zelfde DK, deellinks blijven werken)
  travelcrypt.py decrypt            data.enc -> data.js (om data bij te werken)
  travelcrypt.py passwd NIEUW       wachtwoord wijzigen (deellinks blijven werken)
  travelcrypt.py share [DAGEN] [NAAM]  deellink maken, standaard 7 dagen
  travelcrypt.py cleanup            verlopen deellinks verwijderen (geen wachtwoord nodig)
"""
import base64, datetime as dt, gzip, json, os, secrets, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://robmun.github.io/travel/"
ITER = 600_000

b64 = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")
unb64 = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def kdf(pw, salt, it):
    return PBKDF2HMAC(hashes.SHA256(), 32, salt, it).derive(pw.encode())

def wrap(key, dk):
    iv = secrets.token_bytes(12)
    return {"iv": b64(iv), "wrapped": b64(AESGCM(key).encrypt(iv, dk, None))}

def unwrap(key, w):
    return AESGCM(key).decrypt(unb64(w["iv"]), unb64(w["wrapped"]), None)

def password():
    pw = os.environ.get("TRAVEL_PW")
    if not pw: sys.exit("Zet het wachtwoord in TRAVEL_PW")
    return pw

def write_keys(pw, dk):
    salt = secrets.token_bytes(16)
    k = {"v": 1, "salt": b64(salt), "iter": ITER, **wrap(kdf(pw, salt, ITER), dk)}
    (ROOT / "keys.json").write_text(json.dumps(k, indent=1) + "\n")

def get_dk(pw):
    k = json.loads((ROOT / "keys.json").read_text())
    try: return unwrap(kdf(pw, unb64(k["salt"]), k["iter"]), k)
    except Exception: sys.exit("Wachtwoord klopt niet")

def encrypt(dk):
    data = gzip.compress((ROOT / "data.js").read_bytes(), 9, mtime=0)
    iv = secrets.token_bytes(12)
    (ROOT / "data.enc").write_bytes(iv + AESGCM(dk).encrypt(iv, data, None))

def main(a):
    cmd = a[0] if a else ""
    if cmd == "init":
        dk = secrets.token_bytes(32); write_keys(password(), dk); encrypt(dk)
    elif cmd == "encrypt":
        encrypt(get_dk(password()))
    elif cmd == "decrypt":
        raw = (ROOT / "data.enc").read_bytes()
        (ROOT / "data.js").write_bytes(gzip.decompress(AESGCM(get_dk(password())).decrypt(raw[:12], raw[12:], None)))
    elif cmd == "passwd":
        write_keys(a[1], get_dk(password()))
    elif cmd == "share":
        days = int(a[1]) if len(a) > 1 else 7
        dk = get_dk(password()); sk = secrets.token_bytes(32); sid = b64(secrets.token_bytes(6))
        exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)).replace(microsecond=0)
        (ROOT / "share").mkdir(exist_ok=True)
        (ROOT / "share" / f"{sid}.json").write_text(json.dumps({"expires": exp.isoformat(), "name": a[2] if len(a) > 2 else "", **wrap(sk, dk)}, indent=1) + "\n")
        print(f"{SITE}#s={sid}.{b64(sk)}")
        print(f"geldig tot {exp.isoformat()}")
    elif cmd == "cleanup":
        now = dt.datetime.now(dt.timezone.utc)
        d = ROOT / "share"
        for f in sorted(d.glob("*.json")):
            if dt.datetime.fromisoformat(json.loads(f.read_text())["expires"]) <= now:
                f.unlink(); print("verwijderd", f.name)
        for f in sorted(d.glob("*.enc")):
            if not f.with_suffix(".json").exists():
                f.unlink(); print("verwijderd", f.name)
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
