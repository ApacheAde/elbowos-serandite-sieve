# Serandite Sieve

Full-colour Python 3 neon gem-sorter arcade for [ElbowOS](https://x.com/ElbowOS).

Tilt a coral sieve so falling gems slide into the matching chute: coral left, gold centre, teal right. Combos stack. A miss breaks the streak.

This is an original arcade toy. It is not a commercial emulator and does not use trademarked characters.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 serandite_sieve.py --play
```

Left / A tilts the sieve left. Right / D tilts right. R restarts.

## Record a 9:16 reel

```bash
python3 serandite_sieve.py --record
```

Writes a 15-second 1080x1920 H.264 MP4 (dummy SDL video driver, ffmpeg libx264 yuv420p CRF 20, +faststart).

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/16CQeacjegCQWzFSDwOL5CFGMh61yV9GI/view?usp=drivesdk
