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

ACCENT     = "#3B82F6"
ACCENT_HOV = "#2563EB"
BG         = "#0F172A"
CARD       = "#1E293B"
CARD2      = "#273449"
TEXT       = "#F1F5F9"
SUBTEXT    = "#94A3B8"
GREEN      = "#22C55E"
RED        = "#EF4444"
GOLD       = "#EAB308"
PURPLE     = "#A855F7"

POOL_IDS = [1, 2, 3, 4]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_in_thread(fn):
    threading.Thread(target=fn, daemon=True).start()


def status_label(parent, **kwargs):
    return ctk.CTkLabel(parent, text_color=SUBTEXT, font=("Segoe UI", 12), **kwargs)


def heading(parent, text, size=18, **kwargs):
    return ctk.CTkLabel(parent, text=text, font=("Segoe UI", size, "bold"),
                        text_color=TEXT, **kwargs)


def card(parent, **kwargs):
    return ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12, **kwargs)


def primary_btn(parent, text, command, width=200, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width,
        fg_color=ACCENT, hover_color=ACCENT_HOV,
        font=("Segoe UI", 13, "bold"), corner_radius=8, **kwargs
    )


def ghost_btn(parent, text, command, width=160, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width,
        fg_color=CARD2, hover_color="#334155",
        font=("Segoe UI", 12), corner_radius=8, **kwargs
    )


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, fg_color="#0B1120", corner_radius=0, width=200, **kwargs)
        self.on_select = on_select
        self.buttons = {}
        self._active = None

        heading(self, "  WuWa Opti", size=16).pack(pady=(28, 32), padx=16, anchor="w")

        for name in ("Home", "Convene", "Echoes"):
            btn = ctk.CTkButton(
                self, text=f"  {name}", anchor="w", width=180, height=40,
                fg_color="transparent", hover_color=CARD2,
                font=("Segoe UI", 13), corner_radius=8,
                command=lambda n=name: self._select(n)
            )
            btn.pack(pady=2, padx=10)
            self.buttons[name] = btn

        # highlight Home without triggering the callback yet
        self.buttons["Home"].configure(fg_color=ACCENT)
        self._active = "Home"

    def _select(self, name):
        if self._active:
            self.buttons[self._active].configure(fg_color="transparent")
        self.buttons[name].configure(fg_color=ACCENT)
        self._active = name
        self.on_select(name)


# ---------------------------------------------------------------------------
# Home frame
# ---------------------------------------------------------------------------

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build()

    def _build(self):
        heading(self, "Account", size=22).pack(anchor="w", padx=32, pady=(32, 4))
        status_label(self, text="Link your Wuthering Waves account to get started.").pack(anchor="w", padx=32, pady=(0, 20))

        c = card(self)
        c.pack(fill="x", padx=32, pady=8)

        self.status_icon = ctk.CTkLabel(c, text="⬤", font=("Segoe UI", 14), text_color=SUBTEXT)
        self.status_icon.grid(row=0, column=0, padx=(20, 8), pady=20)
        self.status_text = ctk.CTkLabel(c, text="Not linked", font=("Segoe UI", 13, "bold"), text_color=TEXT)
        self.status_text.grid(row=0, column=1, sticky="w")
        self.detail_text = ctk.CTkLabel(c, text="", font=("Segoe UI", 11), text_color=SUBTEXT)
        self.detail_text.grid(row=1, column=1, sticky="w", pady=(0, 16))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=32, pady=12)

        self.link_btn = primary_btn(btn_frame, "🔗  Auto-Link Account", self._auto_link, width=220)
        self.link_btn.pack(side="left", padx=(0, 12))

        ghost_btn(btn_frame, "Paste URL manually", self._manual_link, width=180).pack(side="left")

        self.log_label = status_label(self, text="")
        self.log_label.pack(anchor="w", padx=32, pady=(8, 0))

        self._refresh()

    def _refresh(self):
        creds = load_cached_credentials()
        if creds:
            self.status_icon.configure(text_color=GREEN)
            self.status_text.configure(text="Linked", text_color=GREEN)
            self.detail_text.configure(
                text=f"Player ID: {creds['player_id']}   |   Region: {creds['svr_area'].upper()}"
            )
        else:
            self.status_icon.configure(text_color=SUBTEXT)
            self.status_text.configure(text="Not linked", text_color=TEXT)
            self.detail_text.configure(text="")

    def _auto_link(self):
        self.link_btn.configure(state="disabled", text="Searching...")
        self.log_label.configure(text="")

        def task():
            try:
                creds = load_credentials()
                save_credentials(creds)
                self.after(0, lambda: self._on_success(creds))
            except RuntimeError as e:
                self.after(0, lambda: self._on_error(str(e)))

        run_in_thread(task)

    def _on_success(self, creds):
        self.link_btn.configure(state="normal", text="🔗  Auto-Link Account")
        self.log_label.configure(text="✓ Account linked successfully!", text_color=GREEN)
        self._refresh()

    def _on_error(self, msg):
        self.link_btn.configure(state="normal", text="🔗  Auto-Link Account")
        self.log_label.configure(text=f"✗ {msg.splitlines()[0]}", text_color=RED)

    def _manual_link(self):
        dlg = ctk.CTkInputDialog(
            text="Paste your convene URL below:\n\n(Go to Convene Records in-game, then\nvisit wutheringwaves.kurogames.com\nand copy the URL from the Network tab)",
            title="Paste Convene URL"
        )
        url = dlg.get_input()
        if not url:
            return
        creds = parse_convene_url(url.strip())
        if creds:
            save_credentials(creds)
            self.log_label.configure(text="✓ Account linked successfully!", text_color=GREEN)
            self._refresh()
        else:
            self.log_label.configure(text="✗ Invalid URL. Make sure you copied the full convene URL.", text_color=RED)


# ---------------------------------------------------------------------------
# Convene frame
# ---------------------------------------------------------------------------

class ConveneFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._selected_pools = set(POOL_IDS)
        self._build()

    def _build(self):
        heading(self, "Convene History", size=22).pack(anchor="w", padx=32, pady=(32, 4))
        status_label(self, text="Select banners and fetch your pull history.").pack(anchor="w", padx=32, pady=(0, 20))

        # Pool selector buttons
        pool_card = card(self)
        pool_card.pack(fill="x", padx=32, pady=(0, 12))
        ctk.CTkLabel(pool_card, text="Banners to fetch", font=("Segoe UI", 12, "bold"),
                     text_color=SUBTEXT).pack(anchor="w", padx=16, pady=(14, 6))

        self.pool_btns = {}
        row = ctk.CTkFrame(pool_card, fg_color="transparent")
        row.pack(padx=12, pady=(0, 14), fill="x")
        for pool_id, name in POOL_TYPES.items():
            if pool_id not in POOL_IDS:
                continue
            btn = ctk.CTkButton(
                row, text=name, width=170, height=34,
                fg_color=ACCENT, hover_color=ACCENT_HOV,
                font=("Segoe UI", 11), corner_radius=6,
                command=lambda p=pool_id: self._toggle_pool(p)
            )
            btn.pack(side="left", padx=4)
            self.pool_btns[pool_id] = btn

        # Fetch buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(anchor="w", padx=32, pady=8)
        self.fetch_btn = primary_btn(btn_row, "⬇  Fetch History", lambda: self._fetch(force=False), width=200)
        self.fetch_btn.pack(side="left")
        ghost_btn(btn_row, "↺  Force Refresh", lambda: self._fetch(force=True), width=160).pack(side="left", padx=10)
        self.fetch_status = status_label(btn_row, text="")
        self.fetch_status.pack(side="left", padx=8)

        # Results
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.results_frame.pack(fill="both", expand=True, padx=32, pady=12)

    def _toggle_pool(self, pool_id):
        if pool_id in self._selected_pools:
            self._selected_pools.discard(pool_id)
            self.pool_btns[pool_id].configure(fg_color=CARD2, hover_color="#334155")
        else:
            self._selected_pools.add(pool_id)
            self.pool_btns[pool_id].configure(fg_color=ACCENT, hover_color=ACCENT_HOV)

    def _fetch(self, force=False):
        creds = load_cached_credentials()
        if not creds:
            messagebox.showwarning("Not Linked", "Link your account first on the Home tab.")
            return
        if not self._selected_pools:
            messagebox.showwarning("No Banners", "Select at least one banner to fetch.")
            return

        self.fetch_btn.configure(state="disabled", text="Fetching...")
        self.fetch_status.configure(text="")
        for w in self.results_frame.winfo_children():
            w.destroy()

        def task():
            try:
                data, from_cache = fetch_all(creds, list(self._selected_pools), force=force)
                self.after(0, lambda: self._show_results(data, from_cache))
            except Exception as e:
                self.after(0, lambda: self._fetch_error(str(e)))

        run_in_thread(task)

    def _fetch_error(self, msg):
        self.fetch_btn.configure(state="normal", text="⬇  Fetch History")
        self.fetch_status.configure(text=f"✗ {msg}", text_color=RED)

    def _show_results(self, data, from_cache=False):
        self.fetch_btn.configure(state="normal", text="⬇  Fetch History")
        total = sum(len(v) for v in data.values())
        source = "cached" if from_cache else "live"
        self.fetch_status.configure(text=f"✓ {total} records loaded ({source})", text_color=GREEN)

        for pool_id, records in sorted(data.items()):
            if not records:
                continue
            stats = pity_stats(records)
            pool_name = POOL_TYPES.get(pool_id, f"Pool {pool_id}")

            section = card(self.results_frame)
            section.pack(fill="x", pady=8)

            # Header row
            hdr = ctk.CTkFrame(section, fg_color=CARD2, corner_radius=8)
            hdr.pack(fill="x", padx=12, pady=(12, 8))

            ctk.CTkLabel(hdr, text=pool_name, font=("Segoe UI", 13, "bold"),
                         text_color=TEXT).pack(side="left", padx=16, pady=10)

            for label, val, color in [
                (f"{stats['total_pulls']} pulls", "", TEXT),
                (f"5★ pity: {stats['current_pity_5']}", "", GOLD),
                (f"4★ pity: {stats['current_pity_4']}", "", PURPLE),
                (f"5★ rate: {stats['rate_5star']}%", "", GREEN),
            ]:
                ctk.CTkLabel(hdr, text=label, font=("Segoe UI", 11),
                             text_color=color).pack(side="right", padx=12, pady=10)

            # Pull rows (last 30)
            for r in records[:30]:
                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=1)

                star_color = GOLD if r.rarity == 5 else (PURPLE if r.rarity == 4 else SUBTEXT)
                stars = "★" * r.rarity

                ctk.CTkLabel(row, text=stars, font=("Segoe UI", 11),
                             text_color=star_color, width=60).pack(side="left")
                ctk.CTkLabel(row, text=r.name, font=("Segoe UI", 12),
                             text_color=TEXT, width=200, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=r.type, font=("Segoe UI", 11),
                             text_color=SUBTEXT, width=100).pack(side="left")
                ctk.CTkLabel(row, text=r.pull_time, font=("Segoe UI", 10),
                             text_color=SUBTEXT).pack(side="left", padx=8)

            ctk.CTkFrame(section, fg_color="transparent", height=8).pack()


# ---------------------------------------------------------------------------
# Echo frame
# ---------------------------------------------------------------------------

SUBSTAT_OPTIONS = ["— none —"] + VALID_STATS


class EchoSlotWidget(ctk.CTkFrame):
    def __init__(self, master, slot, **kwargs):
        super().__init__(master, fg_color=CARD2, corner_radius=10, **kwargs)
        self.slot = slot
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=f"Echo {self.slot}", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT).grid(row=0, column=0, columnspan=2, padx=14, pady=(12, 6), sticky="w")

        ctk.CTkLabel(self, text="Name", font=("Segoe UI", 10), text_color=SUBTEXT).grid(row=1, column=0, padx=14, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="e.g. Tempest Mephis", width=220, height=30)
        self.name_entry.grid(row=1, column=1, padx=(0, 14), pady=2, sticky="w")

        ctk.CTkLabel(self, text="Main Stat", font=("Segoe UI", 10), text_color=SUBTEXT).grid(row=2, column=0, padx=14, sticky="w")
        self.main_var = ctk.StringVar(value=VALID_STATS[0])
        self.main_menu = ctk.CTkOptionMenu(self, variable=self.main_var,
                                           values=VALID_STATS, width=220, height=30,
                                           fg_color=CARD, button_color=ACCENT, button_hover_color=ACCENT_HOV)
        self.main_menu.grid(row=2, column=1, padx=(0, 14), pady=2, sticky="w")

        ctk.CTkLabel(self, text="Substats", font=("Segoe UI", 10), text_color=SUBTEXT).grid(row=3, column=0, padx=14, pady=(8, 2), sticky="nw")

        self.sub_vars = []
        sub_frame = ctk.CTkFrame(self, fg_color="transparent")
        sub_frame.grid(row=3, column=1, padx=(0, 14), pady=(6, 12), sticky="w")
        for i in range(5):
            v = ctk.StringVar(value="— none —")
            self.sub_vars.append(v)
            ctk.CTkOptionMenu(sub_frame, variable=v, values=SUBSTAT_OPTIONS,
                              width=220, height=28,
                              fg_color=CARD, button_color=ACCENT, button_hover_color=ACCENT_HOV
                              ).pack(pady=2)

    def get_echo(self) -> Echo:
        substats = [
            EchoSubstat(stat=v.get(), value=0.0)
            for v in self.sub_vars if v.get() != "— none —"
        ]
        return Echo(
            slot=self.slot,
            name=self.name_entry.get().strip() or f"Echo {self.slot}",
            main_stat=self.main_var.get(),
            substats=substats,
        )


class EchoFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build()

    def _build(self):
        heading(self, "Echo Optimizer", size=22).pack(anchor="w", padx=32, pady=(32, 4))
        status_label(self, text="Select a resonator and enter your echo stats to get a build score.").pack(anchor="w", padx=32, pady=(0, 16))

        # Resonator picker
        picker_card = card(self)
        picker_card.pack(fill="x", padx=32, pady=(0, 12))
        ctk.CTkLabel(picker_card, text="Resonator", font=("Segoe UI", 12, "bold"),
                     text_color=SUBTEXT).pack(anchor="w", padx=16, pady=(14, 6))

        self.resonator_var = ctk.StringVar(value=sorted(RESONATOR_ARCHETYPES.keys())[0])
        resonator_menu = ctk.CTkOptionMenu(
            picker_card, variable=self.resonator_var,
            values=sorted(RESONATOR_ARCHETYPES.keys()), width=240, height=36,
            fg_color=CARD2, button_color=ACCENT, button_hover_color=ACCENT_HOV,
            font=("Segoe UI", 12)
        )
        resonator_menu.pack(anchor="w", padx=16, pady=(0, 14))

        # Scrollable echo slots + results
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=32, pady=8)

        # Echo slots in 2-column grid
        slots_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        slots_frame.pack(fill="x")
        self.slot_widgets = []
        for i in range(5):
            w = EchoSlotWidget(slots_frame, slot=i + 1)
            w.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            self.slot_widgets.append(w)
        slots_frame.columnconfigure(0, weight=1)
        slots_frame.columnconfigure(1, weight=1)

        # Score button
        primary_btn(scroll, "⚡  Score Build", self._score, width=220).pack(pady=16)

        # Results
        self.results_card = card(scroll)
        self.results_card.pack(fill="x", pady=8)
        self.results_label = ctk.CTkLabel(self.results_card, text="Enter your echo stats above and click Score Build.",
                                          font=("Segoe UI", 12), text_color=SUBTEXT)
        self.results_label.pack(padx=20, pady=20)
        self.result_rows_frame = None

    def _score(self):
        resonator = self.resonator_var.get()
        echoes = [w.get_echo() for w in self.slot_widgets]
        results = score_build(echoes, resonator)

        # Clear old results
        for w in self.results_card.winfo_children():
            w.destroy()

        archetype = results[0]["archetype"] if results else "—"
        heading(self.results_card, f"{resonator}  ·  {archetype}", size=14).pack(anchor="w", padx=16, pady=(14, 8))

        grade_colors = {"S": GREEN, "A": ACCENT, "B": GOLD, "C": "#F97316", "D": RED}

        total = 0
        for r in results:
            row = ctk.CTkFrame(self.results_card, fg_color=CARD2, corner_radius=8)
            row.pack(fill="x", padx=12, pady=4)

            ctk.CTkLabel(row, text=f"Echo {r['slot']}  {r['name']}",
                         font=("Segoe UI", 12), text_color=TEXT, width=260, anchor="w").pack(side="left", padx=14, pady=10)
            ctk.CTkLabel(row, text=r["main_stat"],
                         font=("Segoe UI", 11), text_color=SUBTEXT, width=130).pack(side="left")
            ctk.CTkLabel(row, text=f"{r['score']} / 100",
                         font=("Segoe UI", 12), text_color=TEXT, width=90).pack(side="left")
            g = r["grade"]
            ctk.CTkLabel(row, text=g, font=("Segoe UI", 14, "bold"),
                         text_color=grade_colors.get(g, TEXT), width=40).pack(side="left")
            total += r["score"]

        avg = total / len(results) if results else 0
        overall = grade(avg)
        summary = ctk.CTkFrame(self.results_card, fg_color="transparent")
        summary.pack(fill="x", padx=12, pady=(8, 16))
        ctk.CTkLabel(summary, text=f"Overall  {avg:.1f} / 100",
                     font=("Segoe UI", 13, "bold"), text_color=TEXT).pack(side="left", padx=14)
        ctk.CTkLabel(summary, text=f"Grade  {overall}",
                     font=("Segoe UI", 14, "bold"),
                     text_color=grade_colors.get(overall, TEXT)).pack(side="left", padx=8)


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wuthering Waves Opti")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG)

        self.frames = {
            "Home":    HomeFrame(self),
            "Convene": ConveneFrame(self),
            "Echoes":  EchoFrame(self),
        }
        for f in self.frames.values():
            f.pack_forget()

        self.sidebar = Sidebar(self, on_select=self._show_frame)
        self.sidebar.pack(side="left", fill="y")

        self._show_frame("Home")

    def _show_frame(self, name):
        for n, f in self.frames.items():
            if n == name:
                f.pack(side="left", fill="both", expand=True)
            else:
                f.pack_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
