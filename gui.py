"""
WutheringWavesOpti — GUI
Run with: python gui.py
"""

import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from wuwa.log_parser import load_credentials, load_cached_credentials, parse_convene_url, save_credentials
from wuwa.convene import fetch_all, pity_stats, POOL_TYPES
from wuwa.echo import score_build, RESONATOR_ARCHETYPES, VALID_STATS, Echo, EchoSubstat, grade

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Wuthering Waves colour palette (extracted from game UI) ──────────────────
BG      = "#070B14"   # main background
PANEL   = "#0C1525"   # card / panel
PANEL2  = "#101E30"   # elevated panel
GOLD    = "#EAB820"   # primary accent – titles & highlights
GOLD2   = "#C89818"   # dimmer gold – borders, ghost buttons
ORANGE  = "#FF8C1A"   # important numbers
WHITE   = "#F0F0F0"   # body text
GREY    = "#7A8A9E"   # subtext / labels
PURPLE  = "#7B50D4"   # 4-star / collab tag
GREEN   = "#3EC98A"   # success / linked
RED     = "#D94040"   # error
STAR5   = "#FFD700"   # 5-star gold
BORDER  = "#1C2E46"   # panel border

POOL_IDS = [1, 2, 3, 4]

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 14, "bold")
FONT_BODY   = ("Segoe UI", 13)
FONT_SMALL  = ("Segoe UI", 11)
FONT_LABEL  = ("Segoe UI", 10)
FONT_TAG    = ("Segoe UI", 9, "bold")

# ── Helpers ──────────────────────────────────────────────────────────────────

def run_bg(fn): threading.Thread(target=fn, daemon=True).start()

def tag(parent, text, color=GOLD, bg=None, **kw):
    bg = bg or "#2A1E00" if color == GOLD else "#1E1040"
    return ctk.CTkLabel(parent, text=text.upper(), font=FONT_TAG,
                        text_color=color, fg_color=bg,
                        corner_radius=4, **kw)

def wlabel(parent, text, size=13, color=WHITE, bold=False, **kw):
    w = "bold" if bold else "normal"
    return ctk.CTkLabel(parent, text=text, font=("Segoe UI", size, w),
                        text_color=color, **kw)

def panel(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=PANEL, border_color=BORDER,
                        border_width=1, corner_radius=10, **kw)

def panel2(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=PANEL2, border_color=BORDER,
                        border_width=1, corner_radius=8, **kw)

def gold_btn(parent, text, cmd, w=200, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd, width=w, height=36,
                         fg_color=GOLD, hover_color=GOLD2, text_color="#07080D",
                         font=("Segoe UI", 13, "bold"), corner_radius=6, **kw)

def ghost_btn(parent, text, cmd, w=160, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd, width=w, height=36,
                         fg_color="transparent", hover_color=PANEL2,
                         border_color=GOLD2, border_width=1,
                         text_color=GOLD, font=FONT_BODY, corner_radius=6, **kw)

def hdivider(parent):
    ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=0, pady=12)

# ── Sidebar ──────────────────────────────────────────────────────────────────

class Sidebar(ctk.CTkFrame):
    ITEMS = [("  Home", "🏠"), ("  Convene", "✦"), ("  Echoes", "◈")]

    def __init__(self, master, on_select, **kw):
        super().__init__(master, fg_color="#05090F", corner_radius=0, width=188, **kw)
        self.on_select = on_select
        self.btns = {}
        self._active = None

        # Logo
        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(fill="x", padx=20, pady=(28, 0))
        ctk.CTkLabel(logo, text="WUWA", font=("Segoe UI", 17, "bold"),
                     text_color=GOLD).pack(side="left")
        ctk.CTkLabel(logo, text=" OPTI", font=("Segoe UI", 17, "bold"),
                     text_color=WHITE).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=0, pady=20)

        for label, icon in self.ITEMS:
            name = label.strip()
            btn = ctk.CTkButton(
                self, text=f"{icon}{label}", anchor="w", width=168, height=42,
                fg_color="transparent", hover_color=PANEL2,
                text_color=GREY, font=("Segoe UI", 13),
                corner_radius=6, command=lambda n=name: self._pick(n)
            )
            btn.pack(pady=2, padx=10)
            self.btns[name] = btn

        self.btns["Home"].configure(
            fg_color=PANEL2, text_color=GOLD,
            border_color=GOLD2, border_width=1
        )
        self._active = "Home"

    def _pick(self, name):
        if self._active:
            self.btns[self._active].configure(
                fg_color="transparent", text_color=GREY,
                border_width=0
            )
        self.btns[name].configure(
            fg_color=PANEL2, text_color=GOLD,
            border_color=GOLD2, border_width=1
        )
        self._active = name
        self.on_select(name)


# ── Home ─────────────────────────────────────────────────────────────────────

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG, corner_radius=0, **kw)
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32, 0))
        ctk.CTkLabel(top, text="Account", font=FONT_TITLE, text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(top, text="Linked Wuthering Waves profile", font=FONT_SMALL,
                     text_color=GREY).pack(anchor="w", pady=(2, 0))

        hdivider(top)

        c = panel(self)
        c.pack(fill="x", padx=32, pady=(0, 16))

        self._icon = ctk.CTkLabel(c, text="●", font=("Segoe UI", 16), text_color=GREY)
        self._icon.grid(row=0, column=0, padx=(20, 10), pady=(20, 4))
        self._status = ctk.CTkLabel(c, text="Not linked", font=("Segoe UI", 15, "bold"), text_color=WHITE)
        self._status.grid(row=0, column=1, sticky="w")
        self._detail = ctk.CTkLabel(c, text="", font=FONT_SMALL, text_color=GREY)
        self._detail.grid(row=1, column=1, sticky="w", pady=(0, 16))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(anchor="w", padx=32, pady=4)
        self._link_btn = gold_btn(btns, "⬡  Link Account", self._auto_link, w=190)
        self._link_btn.pack(side="left", padx=(0, 10))
        ghost_btn(btns, "Paste URL", self._manual_link, w=140).pack(side="left")

        self._msg = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=GREY)
        self._msg.pack(anchor="w", padx=32, pady=(10, 0))

        self._refresh()

    def _refresh(self):
        c = load_cached_credentials()
        if c:
            self._icon.configure(text_color=GREEN)
            self._status.configure(text="Linked", text_color=GREEN)
            self._detail.configure(
                text=f"Player ID: {c['player_id']}   ·   Region: {c['svr_area'].upper()}"
            )
        else:
            self._icon.configure(text_color=GREY)
            self._status.configure(text="Not linked", text_color=WHITE)
            self._detail.configure(text="Open Convene Records in-game, then click Link Account.")

    def _auto_link(self):
        self._link_btn.configure(state="disabled", text="Searching…")
        self._msg.configure(text="")
        def task():
            try:
                creds = load_credentials()
                save_credentials(creds)
                self.after(0, lambda: self._done(creds))
            except RuntimeError as e:
                self.after(0, lambda: self._fail(str(e)))
        run_bg(task)

    def _done(self, creds):
        self._link_btn.configure(state="normal", text="⬡  Link Account")
        self._msg.configure(text="✓  Account linked successfully!", text_color=GREEN)
        self._refresh()

    def _fail(self, msg):
        self._link_btn.configure(state="normal", text="⬡  Link Account")
        self._msg.configure(text=f"✗  {msg.splitlines()[0]}", text_color=RED)

    def _manual_link(self):
        dlg = ctk.CTkInputDialog(
            text="Paste your convene URL:\n\n(Open Convene Records in-game,\nthen copy the URL from the\nbrowser Network tab)",
            title="Paste Convene URL"
        )
        url = dlg.get_input()
        if not url: return
        creds = parse_convene_url(url.strip())
        if creds:
            save_credentials(creds)
            self._msg.configure(text="✓  Account linked!", text_color=GREEN)
            self._refresh()
        else:
            self._msg.configure(text="✗  Invalid URL. Copy the full convene URL.", text_color=RED)


# ── Convene ───────────────────────────────────────────────────────────────────

class ConveneFrame(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG, corner_radius=0, **kw)
        self._sel = set(POOL_IDS)
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32, 0))
        ctk.CTkLabel(top, text="Convene Records", font=FONT_TITLE, text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(top, text="Pull history & pity tracker", font=FONT_SMALL,
                     text_color=GREY).pack(anchor="w", pady=(2, 0))
        hdivider(top)

        # Banner toggles
        brow = ctk.CTkFrame(self, fg_color="transparent")
        brow.pack(anchor="w", padx=32, pady=(0, 12))
        self._pool_btns = {}
        for pid, name in POOL_TYPES.items():
            if pid not in POOL_IDS: continue
            b = ctk.CTkButton(
                brow, text=name, width=175, height=32,
                fg_color=PANEL2, hover_color="#162438",
                border_color=GOLD2, border_width=1,
                text_color=GOLD, font=("Segoe UI", 11), corner_radius=6,
                command=lambda p=pid: self._toggle(p)
            )
            b.pack(side="left", padx=4)
            self._pool_btns[pid] = b

        # Action row
        arow = ctk.CTkFrame(self, fg_color="transparent")
        arow.pack(anchor="w", padx=32, pady=(0, 16))
        self._fbtn = gold_btn(arow, "⬇  Fetch History", lambda: self._fetch(False), w=190)
        self._fbtn.pack(side="left")
        ghost_btn(arow, "↺  Force Refresh", lambda: self._fetch(True), w=160).pack(side="left", padx=10)
        self._fmsg = ctk.CTkLabel(arow, text="", font=FONT_SMALL, text_color=GREY)
        self._fmsg.pack(side="left", padx=4)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=32, pady=0)

    def _toggle(self, pid):
        if pid in self._sel:
            self._sel.discard(pid)
            self._pool_btns[pid].configure(fg_color=PANEL, text_color=GREY, border_color=BORDER)
        else:
            self._sel.add(pid)
            self._pool_btns[pid].configure(fg_color=PANEL2, text_color=GOLD, border_color=GOLD2)

    def _fetch(self, force):
        if not load_cached_credentials():
            messagebox.showwarning("Not Linked", "Link your account on the Home tab first.")
            return
        if not self._sel:
            messagebox.showwarning("No Banners", "Enable at least one banner.")
            return
        self._fbtn.configure(state="disabled", text="Fetching…")
        self._fmsg.configure(text="")
        for w in self._scroll.winfo_children(): w.destroy()

        def task():
            try:
                creds = load_cached_credentials()
                data, cached = fetch_all(creds, list(self._sel), force=force)
                self.after(0, lambda: self._show(data, cached))
            except Exception as e:
                self.after(0, lambda: self._err(str(e)))
        run_bg(task)

    def _err(self, msg):
        self._fbtn.configure(state="normal", text="⬇  Fetch History")
        self._fmsg.configure(text=f"✗  {msg}", text_color=RED)

    def _show(self, data, cached):
        self._fbtn.configure(state="normal", text="⬇  Fetch History")
        total = sum(len(v) for v in data.values())
        src = "cached" if cached else "live"
        self._fmsg.configure(text=f"✓  {total} records  ({src})", text_color=GREEN)

        for pid, records in sorted(data.items()):
            if not records: continue
            s = pity_stats(records)
            name = POOL_TYPES.get(pid, f"Pool {pid}")

            c = panel(self._scroll)
            c.pack(fill="x", pady=8)

            # Header
            hdr = ctk.CTkFrame(c, fg_color=PANEL2, corner_radius=8)
            hdr.pack(fill="x", padx=12, pady=(12, 0))

            left = ctk.CTkFrame(hdr, fg_color="transparent")
            left.pack(side="left", padx=16, pady=10)
            ctk.CTkLabel(left, text=name, font=("Segoe UI", 13, "bold"), text_color=GOLD).pack(anchor="w")
            ctk.CTkLabel(left, text=f"{s['total_pulls']} total pulls", font=FONT_SMALL, text_color=GREY).pack(anchor="w")

            right = ctk.CTkFrame(hdr, fg_color="transparent")
            right.pack(side="right", padx=16, pady=10)
            for lbl, val, col in [
                ("5★ pity", s["current_pity_5"], ORANGE),
                ("4★ pity", s["current_pity_4"], PURPLE),
                ("5★ rate", f"{s['rate_5star']}%", GREEN),
            ]:
                box = ctk.CTkFrame(right, fg_color="transparent")
                box.pack(side="left", padx=10)
                ctk.CTkLabel(box, text=str(val), font=("Segoe UI", 18, "bold"), text_color=col).pack()
                ctk.CTkLabel(box, text=lbl, font=FONT_LABEL, text_color=GREY).pack()

            # Pull rows
            pulls = ctk.CTkFrame(c, fg_color="transparent")
            pulls.pack(fill="x", padx=12, pady=(8, 12))

            # Column headers
            hr = ctk.CTkFrame(pulls, fg_color="transparent")
            hr.pack(fill="x", pady=(0, 4))
            for txt, w in [("Rarity", 72), ("Name", 220), ("Type", 110), ("Date", 160)]:
                ctk.CTkLabel(hr, text=txt, font=FONT_LABEL, text_color=GREY, width=w, anchor="w").pack(side="left")

            ctk.CTkFrame(pulls, height=1, fg_color=BORDER).pack(fill="x", pady=4)

            for r in records[:30]:
                row = ctk.CTkFrame(pulls, fg_color="transparent", height=28)
                row.pack(fill="x")
                row.pack_propagate(False)
                sc = STAR5 if r.rarity == 5 else (PURPLE if r.rarity == 4 else "#5B8FD4")
                ctk.CTkLabel(row, text="★"*r.rarity, font=("Segoe UI", 11, "bold"),
                             text_color=sc, width=72, anchor="w").pack(side="left")
                nc = GOLD if r.rarity == 5 else WHITE
                ctk.CTkLabel(row, text=r.name, font=FONT_BODY, text_color=nc,
                             width=220, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=r.type, font=FONT_SMALL, text_color=GREY,
                             width=110, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=r.pull_time, font=FONT_LABEL, text_color=GREY,
                             width=160, anchor="w").pack(side="left")

            ctk.CTkFrame(c, fg_color="transparent", height=4).pack()


# ── Echoes ────────────────────────────────────────────────────────────────────

SUB_OPTS = ["— none —"] + VALID_STATS
GRADE_COLORS = {"S": GREEN, "A": GOLD, "B": ORANGE, "C": GREY, "D": RED}


class EchoSlot(ctk.CTkFrame):
    def __init__(self, master, slot, **kw):
        super().__init__(master, fg_color=PANEL2, border_color=BORDER,
                         border_width=1, corner_radius=8, **kw)
        self.slot = slot
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=6)
        hdr.pack(fill="x", padx=10, pady=(10, 6))
        ctk.CTkLabel(hdr, text=f"ECHO {self.slot}", font=FONT_TAG,
                     text_color=GOLD).pack(side="left", padx=12, pady=6)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(body, text="Name", font=FONT_LABEL, text_color=GREY).grid(
            row=0, column=0, sticky="w", pady=3)
        self._name = ctk.CTkEntry(body, placeholder_text="e.g. Tempest Mephis",
                                  width=210, height=28, fg_color=PANEL,
                                  border_color=BORDER, text_color=WHITE)
        self._name.grid(row=0, column=1, padx=(8, 0), pady=3, sticky="w")

        ctk.CTkLabel(body, text="Main stat", font=FONT_LABEL, text_color=GREY).grid(
            row=1, column=0, sticky="w", pady=3)
        self._main = ctk.StringVar(value=VALID_STATS[0])
        ctk.CTkOptionMenu(body, variable=self._main, values=VALID_STATS,
                          width=210, height=28, fg_color=PANEL, button_color=GOLD2,
                          button_hover_color=GOLD, text_color=WHITE,
                          font=FONT_SMALL, corner_radius=6
                          ).grid(row=1, column=1, padx=(8, 0), pady=3, sticky="w")

        ctk.CTkLabel(body, text="Substats", font=FONT_LABEL, text_color=GREY).grid(
            row=2, column=0, sticky="nw", pady=(8, 3))
        sf = ctk.CTkFrame(body, fg_color="transparent")
        sf.grid(row=2, column=1, padx=(8, 0), pady=(6, 10), sticky="w")
        self._subs = []
        for _ in range(5):
            v = ctk.StringVar(value="— none —")
            self._subs.append(v)
            ctk.CTkOptionMenu(sf, variable=v, values=SUB_OPTS,
                              width=210, height=26, fg_color=PANEL, button_color=GOLD2,
                              button_hover_color=GOLD, text_color=WHITE,
                              font=FONT_SMALL, corner_radius=6
                              ).pack(pady=2)

    def get(self) -> Echo:
        subs = [EchoSubstat(v.get(), 0.0) for v in self._subs if v.get() != "— none —"]
        return Echo(self.slot, self._main.get(), subs, self._name.get().strip() or f"Echo {self.slot}")


class EchoFrame(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG, corner_radius=0, **kw)
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32, 0))
        ctk.CTkLabel(top, text="Echo Optimizer", font=FONT_TITLE, text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(top, text="Score your build per resonator archetype", font=FONT_SMALL,
                     text_color=GREY).pack(anchor="w", pady=(2, 0))
        hdivider(top)

        # Resonator picker
        rp = panel(self)
        rp.pack(fill="x", padx=32, pady=(0, 14))
        ctk.CTkLabel(rp, text="RESONATOR", font=FONT_TAG, text_color=GOLD).pack(
            anchor="w", padx=16, pady=(12, 4))
        self._res = ctk.StringVar(value=sorted(RESONATOR_ARCHETYPES.keys())[0])
        ctk.CTkOptionMenu(rp, variable=self._res,
                          values=sorted(RESONATOR_ARCHETYPES.keys()),
                          width=280, height=34, fg_color=PANEL2,
                          button_color=GOLD2, button_hover_color=GOLD,
                          text_color=WHITE, font=("Segoe UI", 13), corner_radius=6
                          ).pack(anchor="w", padx=16, pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=32)

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x")
        self._slots = []
        for i in range(5):
            s = EchoSlot(grid, i + 1)
            s.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            self._slots.append(s)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        gold_btn(scroll, "⚡  Score Build", self._score, w=220).pack(pady=16)

        self._res_panel = panel(scroll)
        self._res_panel.pack(fill="x", pady=8)
        ctk.CTkLabel(self._res_panel, text="Enter your echo stats above and click Score Build.",
                     font=FONT_SMALL, text_color=GREY).pack(padx=20, pady=20)

    def _score(self):
        res = self._res.get()
        echoes = [s.get() for s in self._slots]
        results = score_build(echoes, res)

        for w in self._res_panel.winfo_children(): w.destroy()

        arch = results[0]["archetype"] if results else "—"
        hdr = ctk.CTkFrame(self._res_panel, fg_color=PANEL2, corner_radius=8)
        hdr.pack(fill="x", padx=12, pady=(12, 8))
        ctk.CTkLabel(hdr, text=res, font=("Segoe UI", 14, "bold"), text_color=GOLD).pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(hdr, text=arch.replace("_", " ").upper(), font=FONT_TAG, text_color=GREY).pack(side="left")

        total = 0
        for r in results:
            row = ctk.CTkFrame(self._res_panel, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)

            # Score bar background
            bar_w = 220
            box = ctk.CTkFrame(row, fg_color=PANEL2, corner_radius=6, width=bar_w + 120)
            box.pack(fill="x")
            box.pack_propagate(False)

            left = ctk.CTkFrame(box, fg_color="transparent")
            left.pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(left, text=f"Echo {r['slot']}  {r['name']}",
                         font=FONT_BODY, text_color=WHITE, width=220, anchor="w").pack(anchor="w")
            ctk.CTkLabel(left, text=r["main_stat"], font=FONT_SMALL, text_color=GREY, anchor="w").pack(anchor="w")

            # Bar
            bar_frame = ctk.CTkFrame(box, fg_color="transparent")
            bar_frame.pack(side="left", padx=8)
            ctk.CTkProgressBar(bar_frame, width=180, height=6,
                                fg_color=PANEL, progress_color=GOLD,
                                corner_radius=3
                                ).pack(pady=2, after=bar_frame.pack_configure(expand=True))
            # set value
            pb = bar_frame.winfo_children()
            if pb: pb[-1].set(r["score"] / 100)

            ctk.CTkLabel(bar_frame, text=f"{r['score']} / 100",
                         font=FONT_SMALL, text_color=GREY).pack()

            g = r["grade"]
            ctk.CTkLabel(box, text=g, font=("Segoe UI", 20, "bold"),
                         text_color=GRADE_COLORS.get(g, WHITE), width=48
                         ).pack(side="right", padx=16)

            total += r["score"]

        avg = total / len(results) if results else 0
        og = grade(avg)
        foot = ctk.CTkFrame(self._res_panel, fg_color="transparent")
        foot.pack(fill="x", padx=12, pady=(8, 16))
        ctk.CTkLabel(foot, text=f"Overall Score", font=FONT_SMALL, text_color=GREY).pack(side="left", padx=12)
        ctk.CTkLabel(foot, text=f"{avg:.1f} / 100", font=("Segoe UI", 15, "bold"), text_color=ORANGE).pack(side="left")
        ctk.CTkLabel(foot, text=f"  Grade  {og}", font=("Segoe UI", 15, "bold"),
                     text_color=GRADE_COLORS.get(og, WHITE)).pack(side="left")


# ── App ───────────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wuthering Waves Opti")
        self.geometry("1140x740")
        self.minsize(960, 620)
        self.configure(fg_color=BG)

        self._frames = {
            "Home":    HomeFrame(self),
            "Convene": ConveneFrame(self),
            "Echoes":  EchoFrame(self),
        }
        for f in self._frames.values():
            f.pack_forget()

        self._sidebar = Sidebar(self, on_select=self._show)
        self._sidebar.pack(side="left", fill="y")

        self._show("Home")

    def _show(self, name):
        for n, f in self._frames.items():
            f.pack(side="left", fill="both", expand=True) if n == name else f.pack_forget()


if __name__ == "__main__":
    App().mainloop()
