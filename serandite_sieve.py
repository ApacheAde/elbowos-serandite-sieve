"""Serandite Sieve — neon gem-sorter arcade for ElbowOS. Python 3 + pygame."""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/SERANDITE_SIEVE_ElbowOS.mp4")
BG = (22, 8, 28)
PLUM = (78, 24, 64)
CORAL = (255, 118, 136)
GOLD = (255, 206, 78)
TEAL = (62, 232, 196)
CREAM = (255, 236, 220)
INK = (14, 4, 18)
COLS = (CORAL, GOLD, TEAL)
NAMES = ("CORAL", "GOLD", "TEAL")


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption("Serandite Sieve")
        self.font = pygame.font.Font(None, 92)
        self.mid = pygame.font.Font(None, 54)
        self.small = pygame.font.Font(None, 40)
        self.reset()

    def reset(self):
        self.tilt = 0.0
        self.score = 0
        self.combo = 0
        self.gems = []
        self.sparks = []
        self.motes = [
            [random.randrange(80, 1000), random.randrange(200, 1800), random.choice(COLS)]
            for _ in range(40)
        ]
        self.tick = 0
        self.spawn_in = 8
        self.flash = 0
        self.banner = "SORT THE SIEVE"

    def spawn(self):
        c = random.randrange(3)
        self.gems.append(
            {
                "x": random.uniform(220, 860),
                "y": 250.0,
                "vx": random.uniform(-1.2, 1.2),
                "vy": 1.5,
                "c": c,
                "r": 26,
                "on": False,
                "alive": True,
            }
        )

    def sieve_y(self, x):
        return 1240 + (x - 540) * math.sin(self.tilt) * 0.92

    def burst(self, x, y, col):
        for _ in range(10):
            a = random.random() * math.tau
            s = random.uniform(2, 8)
            self.sparks.append([x, y, math.cos(a) * s, math.sin(a) * s, col, 16])

    def resolve(self, g):
        g["alive"] = False
        bins = (270, 540, 810)
        idx = min(range(3), key=lambda i: abs(g["x"] - bins[i]))
        if 120 < g["x"] < 960 and idx == g["c"]:
            self.combo += 1
            self.score += 100 + self.combo * 15
            self.banner = f"{NAMES[g['c']]} +{100 + self.combo * 15}"
            self.flash = 8
            self.burst(g["x"], 1660, COLS[g["c"]])
        else:
            self.combo = 0
            self.banner = "MISS"
            self.flash = -8
            self.burst(g["x"], 1660, (180, 60, 90))

    def step(self, auto=False):
        self.tick += 1
        self.spawn_in -= 1
        if self.spawn_in <= 0:
            self.spawn()
            self.spawn_in = 16
        if auto:
            self.autotilt()
        for g in self.gems:
            g["vy"] += 0.38
            sy = self.sieve_y(g["x"])
            if g["y"] + g["r"] >= sy and g["y"] < sy + 36 and 150 < g["x"] < 930:
                g["y"] = sy - g["r"]
                g["vy"] = 0
                g["on"] = True
                g["vx"] += math.sin(self.tilt) * 1.7
                g["vx"] *= 0.9
            else:
                g["on"] = False
                g["vx"] *= 0.995
            g["x"] += g["vx"]
            g["y"] += g["vy"]
            if g["x"] < 90 or g["x"] > 990:
                g["vx"] *= -0.6
                g["x"] = max(90, min(990, g["x"]))
            if g["y"] > 1635:
                self.resolve(g)
        self.gems = [g for g in self.gems if g["alive"]]
        nxt = []
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[5] -= 1
            if s[5] > 0:
                nxt.append(s)
        self.sparks = nxt
        for m in self.motes:
            m[1] -= 1.4
            if m[1] < 180:
                m[1] = 1780
                m[0] = random.randrange(80, 1000)
        if self.flash:
            self.flash += -1 if self.flash > 0 else 1

    def autotilt(self):
        gem = None
        for g in self.gems:
            if g["y"] < 1600 and (gem is None or g["y"] > gem["y"]):
                gem = g
        if gem is None:
            self.tilt *= 0.9
            return
        tx = (270, 540, 810)[gem["c"]]
        if gem["x"] < tx - 24:
            self.tilt = min(0.52, self.tilt + 0.045)
        elif gem["x"] > tx + 24:
            self.tilt = max(-0.52, self.tilt - 0.045)
        else:
            self.tilt *= 0.82

    def draw(self, surf):
        surf.fill(BG)
        for i in range(18):
            shade = (32 + i, 10 + i // 2, 40 + i)
            pygame.draw.rect(surf, shade, (0, i * 110, W, 110))
        for m in self.motes:
            pygame.draw.circle(surf, m[2], (int(m[0]), int(m[1])), 3)
        pygame.draw.polygon(surf, PLUM, [(40, 280), (180, 180), (900, 180), (1040, 280)])
        pygame.draw.polygon(surf, (120, 40, 90), [(70, 270), (200, 200), (880, 200), (1010, 270)], 4)
        bins = ((270, CORAL), (540, GOLD), (810, TEAL))
        for x, col in bins:
            pygame.draw.polygon(surf, col, [(x - 110, 1760), (x + 110, 1760), (x + 70, 1588), (x - 70, 1588)])
            pygame.draw.polygon(surf, CREAM, [(x - 110, 1760), (x + 110, 1760), (x + 70, 1588), (x - 70, 1588)], 3)
            lab = self.small.render(NAMES[COLS.index(col)], True, INK)
            surf.blit(lab, lab.get_rect(center=(x, 1690)))
        a = (150, self.sieve_y(150))
        b = (930, self.sieve_y(930))
        pygame.draw.line(surf, (255, 168, 150), a, b, 22)
        pygame.draw.line(surf, CREAM, a, b, 6)
        lip = 36
        pygame.draw.circle(surf, CORAL, (int(a[0]), int(a[1])), lip)
        pygame.draw.circle(surf, TEAL, (int(b[0]), int(b[1])), lip)
        for g in self.gems:
            col = COLS[g["c"]]
            pygame.draw.circle(surf, col, (int(g["x"]), int(g["y"])), g["r"])
            pygame.draw.circle(surf, CREAM, (int(g["x"] - 7), int(g["y"] - 8)), 8)
            pygame.draw.circle(surf, INK, (int(g["x"]), int(g["y"])), g["r"], 3)
        for s in self.sparks:
            pygame.draw.circle(surf, s[4], (int(s[0]), int(s[1])), max(2, s[5] // 3))
        title = self.font.render("SERANDITE SIEVE", True, CREAM)
        surf.blit(title, title.get_rect(center=(W // 2, 90)))
        sc = self.mid.render(f"SCORE  {self.score}", True, GOLD if self.flash >= 0 else CORAL)
        surf.blit(sc, sc.get_rect(center=(W // 2, 168)))
        tag = self.small.render(self.banner, True, TEAL)
        surf.blit(tag, tag.get_rect(center=(W // 2, 230)))
        foot = self.mid.render("x.com/ElbowOS", True, CORAL)
        surf.blit(foot, foot.get_rect(center=(W // 2, 1860)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.tilt = max(-0.55, self.tilt - 0.04)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.tilt = min(0.55, self.tilt + 0.04)
            else:
                self.tilt *= 0.92
            self.step(False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        for _ in range(frames):
            self.step(True)
            self.draw(self.screen)
            proc.stdin.write(pygame.image.tostring(self.screen, "RGB"))
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
