import customtkinter as ctk
import subprocess
import threading
import os
import json
from tkinter import filedialog, messagebox
import tkinter as tk

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ACCENT   = "#00FF88"
BG_DEEP  = "#0D0F14"
BG_CARD  = "#13161E"
BG_PANEL = "#1A1D28"
BORDER   = "#2A2D3E"
TEXT_DIM = "#6B7280"
TEXT_MID = "#9CA3AF"
TEXT_HI  = "#F9FAFB"
RED      = "#FF4757"
YELLOW   = "#FFD32A"

GITIGNORE_PRESETS = {
    "Python":     ["__pycache__/", "*.pyc", "*.pyo", ".env", "venv/", ".venv/", "dist/", "build/", "*.egg-info/"],
    "Node.js":    ["node_modules/", ".env", "dist/", "build/", ".DS_Store", "*.log"],
    "Web":        [".DS_Store", "*.log", ".env", "dist/", "build/"],
    "Kali/Security": ["*.log", "*.pcap", "*.cap", "credentials.txt", "passwords.txt", "*.key", ".env", "loot/", "output/"],
    "Custom":     [],
}

class TerminalBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled", font=("Courier New", 12),
                       text_color="#00FF88", fg_color="#0A0C10",
                       border_color=BORDER, border_width=1)

    def log(self, msg, color=None):
        self.configure(state="normal")
        tag = color or "normal"
        self.insert("end", msg + "\n")
        self.configure(state="disabled")
        self.see("end")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class FileListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.file_vars = {}

    def populate(self, path):
        for w in self.winfo_children():
            w.destroy()
        self.file_vars.clear()

        if not path or not os.path.isdir(path):
            return

        all_files = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), path)
                all_files.append(rel)

        for i, f in enumerate(sorted(all_files)):
            var = ctk.BooleanVar(value=True)
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", pady=1)
            cb = ctk.CTkCheckBox(row, text=f, variable=var,
                                  font=("Courier New", 11), text_color=TEXT_MID,
                                  fg_color=ACCENT, hover_color="#00CC66",
                                  checkmark_color="#000000", border_color=BORDER)
            cb.pack(anchor="w", padx=8)
            self.file_vars[f] = var

    def get_selected(self):
        return [f for f, v in self.file_vars.items() if v.get()]

    def select_all(self):
        for v in self.file_vars.values():
            v.set(True)

    def deselect_all(self):
        for v in self.file_vars.values():
            v.set(False)


class GitHubDeployer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ GitDeploy — by CYBERSAREEN")
        self.geometry("1200x820")
        self.minsize(1000, 700)
        self.configure(fg_color=BG_DEEP)

        self.project_path = ctk.StringVar()
        self.repo_name    = ctk.StringVar()
        self.username     = ctk.StringVar(value="CYBERSAREEN")
        self.branch       = ctk.StringVar(value="main")
        self.commit_msg   = ctk.StringVar(value="Initial commit")
        self.gitignore_preset = ctk.StringVar(value="Python")
        self.create_gitignore = ctk.BooleanVar(value=True)
        self.private_repo  = ctk.BooleanVar(value=False)

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="⚡ GitDeploy",
                     font=("Courier New", 22, "bold"), text_color=ACCENT).pack(side="left", padx=24, pady=16)
        ctk.CTkLabel(hdr, text="Full-throttle GitHub automation",
                     font=("Courier New", 12), text_color=TEXT_DIM).pack(side="left", pady=16)
        ctk.CTkLabel(hdr, text="github.com/CYBERSAREEN",
                     font=("Courier New", 11), text_color=TEXT_DIM).pack(side="right", padx=24)

        # Body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)
        body.columnconfigure(0, weight=4)
        body.columnconfigure(1, weight=6)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12, border_color=BORDER, border_width=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self._section(left, "📁 PROJECT")
        proj_row = ctk.CTkFrame(left, fg_color="transparent")
        proj_row.pack(fill="x", padx=16, pady=(0, 12))
        self.path_entry = ctk.CTkEntry(proj_row, textvariable=self.project_path,
                                        placeholder_text="Select project folder…",
                                        font=("Courier New", 11), height=36,
                                        fg_color=BG_DEEP, border_color=BORDER, text_color=TEXT_HI)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(proj_row, text="Browse", width=80, height=36,
                      font=("Courier New", 11, "bold"), fg_color=BG_PANEL, hover_color=BORDER,
                      text_color=ACCENT, border_color=ACCENT, border_width=1,
                      command=self._browse).pack(side="right")

        self._section(left, "⚙️  CONFIG")
        self._field(left, "GitHub Username", self.username)
        self._field(left, "Repository Name  (--repo)", self.repo_name, placeholder="REPORTS_DVWA-BWAPP_POC")
        self._field(left, "Branch", self.branch)
        self._field(left, "Commit Message  (-m)", self.commit_msg)

        # Options
        opt = ctk.CTkFrame(left, fg_color=BG_PANEL, corner_radius=8)
        opt.pack(fill="x", padx=16, pady=8)
        ctk.CTkCheckBox(opt, text="Create .gitignore automatically",
                         variable=self.create_gitignore,
                         font=("Courier New", 11), text_color=TEXT_MID,
                         fg_color=ACCENT, hover_color="#00CC66", checkmark_color="#000",
                         border_color=BORDER, command=self._toggle_preset).pack(anchor="w", padx=12, pady=(10, 4))
        preset_row = ctk.CTkFrame(opt, fg_color="transparent")
        preset_row.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(preset_row, text="Preset:", font=("Courier New", 11), text_color=TEXT_DIM).pack(side="left")
        self.preset_menu = ctk.CTkOptionMenu(preset_row, variable=self.gitignore_preset,
                                              values=list(GITIGNORE_PRESETS.keys()),
                                              font=("Courier New", 11), height=30,
                                              fg_color=BG_DEEP, button_color=BG_PANEL,
                                              button_hover_color=BORDER, text_color=ACCENT,
                                              dropdown_fg_color=BG_PANEL)
        self.preset_menu.pack(side="left", padx=8)
        ctk.CTkCheckBox(opt, text="Private repository",
                         variable=self.private_repo,
                         font=("Courier New", 11), text_color=TEXT_MID,
                         fg_color=ACCENT, hover_color="#00CC66", checkmark_color="#000",
                         border_color=BORDER).pack(anchor="w", padx=12, pady=(0, 10))

        # Deploy button
        ctk.CTkButton(left, text="🚀  DEPLOY TO GITHUB",
                      font=("Courier New", 15, "bold"), height=52,
                      fg_color=ACCENT, hover_color="#00CC66", text_color="#000000",
                      corner_radius=10, command=self._confirm_deploy).pack(fill="x", padx=16, pady=(12, 8))

        # Quick actions
        qa = ctk.CTkFrame(left, fg_color="transparent")
        qa.pack(fill="x", padx=16, pady=(0, 12))
        for txt, cmd, col in [
            ("git status", self._status, BG_PANEL),
            ("git log",    self._log,    BG_PANEL),
            ("git pull",   self._pull,   BG_PANEL),
        ]:
            ctk.CTkButton(qa, text=txt, height=30, font=("Courier New", 11),
                          fg_color=col, hover_color=BORDER, text_color=ACCENT,
                          border_color=BORDER, border_width=1,
                          command=cmd).pack(side="left", expand=True, padx=3)

    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=5)
        right.rowconfigure(1, weight=4)
        right.columnconfigure(0, weight=1)

        # File list
        fl = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=12, border_color=BORDER, border_width=1)
        fl.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        fl.rowconfigure(1, weight=1)
        fl.columnconfigure(0, weight=1)

        hrow = ctk.CTkFrame(fl, fg_color="transparent")
        hrow.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        ctk.CTkLabel(hrow, text="📂 FILES TO COMMIT",
                     font=("Courier New", 12, "bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkButton(hrow, text="↻ Refresh", width=80, height=28,
                      font=("Courier New", 10), fg_color=BG_PANEL, hover_color=BORDER,
                      text_color=TEXT_MID, border_color=BORDER, border_width=1,
                      command=self._refresh_files).pack(side="right", padx=(4, 0))
        ctk.CTkButton(hrow, text="All", width=40, height=28,
                      font=("Courier New", 10), fg_color=BG_PANEL, hover_color=BORDER,
                      text_color=ACCENT, border_color=BORDER, border_width=1,
                      command=lambda: self.file_list.select_all()).pack(side="right", padx=(4, 0))
        ctk.CTkButton(hrow, text="None", width=50, height=28,
                      font=("Courier New", 10), fg_color=BG_PANEL, hover_color=BORDER,
                      text_color=TEXT_DIM, border_color=BORDER, border_width=1,
                      command=lambda: self.file_list.deselect_all()).pack(side="right", padx=(4, 0))

        self.file_list = FileListFrame(fl, fg_color=BG_DEEP, corner_radius=8)
        self.file_list.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # Terminal
        term = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=12, border_color=BORDER, border_width=1)
        term.grid(row=1, column=0, sticky="nsew")
        term.rowconfigure(1, weight=1)
        term.columnconfigure(0, weight=1)

        trow = ctk.CTkFrame(term, fg_color="transparent")
        trow.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        ctk.CTkLabel(trow, text="⬛ TERMINAL OUTPUT",
                     font=("Courier New", 12, "bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkButton(trow, text="Clear", width=60, height=26,
                      font=("Courier New", 10), fg_color=BG_PANEL, hover_color=BORDER,
                      text_color=TEXT_DIM, border_color=BORDER, border_width=1,
                      command=lambda: self.terminal.clear()).pack(side="right")

        self.terminal = TerminalBox(term, height=180)
        self.terminal.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.terminal.log("GitDeploy ready. Select a project folder to begin.", "#00FF88")
        self.terminal.log(f"Remote will be set to: https://github.com/CYBERSAREEN/<repo>.git", "#6B7280")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _section(self, parent, title):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(row, text=title, font=("Courier New", 11, "bold"),
                     text_color=ACCENT).pack(side="left")
        ctk.CTkFrame(row, fg_color=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _field(self, parent, label, var, placeholder=""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text=label, font=("Courier New", 10),
                     text_color=TEXT_DIM, width=160, anchor="w").pack(side="left")
        ctk.CTkEntry(row, textvariable=var, placeholder_text=placeholder,
                     font=("Courier New", 11), height=32,
                     fg_color=BG_DEEP, border_color=BORDER,
                     text_color=TEXT_HI).pack(side="left", fill="x", expand=True)

    def _toggle_preset(self):
        state = "normal" if self.create_gitignore.get() else "disabled"
        self.preset_menu.configure(state=state)

    def _browse(self):
        path = filedialog.askdirectory(title="Select Project Folder")
        if path:
            self.project_path.set(path)
            name = os.path.basename(path)
            if not self.repo_name.get():
                self.repo_name.set(name)
            self._refresh_files()
            self.terminal.log(f"📁 Project: {path}", "#00FF88")

    def _refresh_files(self):
        self.file_list.populate(self.project_path.get())
        n = len(self.file_list.file_vars)
        self.terminal.log(f"↻ Found {n} files", TEXT_DIM)

    # ── Git commands ──────────────────────────────────────────────────────────
    def _run(self, cmd, cwd=None):
        try:
            result = subprocess.run(cmd, cwd=cwd or self.project_path.get(),
                                    capture_output=True, text=True, shell=True)
            out = result.stdout.strip()
            err = result.stderr.strip()
            if out:
                self.terminal.log(out)
            if err:
                self.terminal.log(err, RED if result.returncode != 0 else TEXT_DIM)
            return result.returncode == 0
        except Exception as e:
            self.terminal.log(f"ERROR: {e}", RED)
            return False

    def _status(self):
        path = self.project_path.get()
        if not path:
            self.terminal.log("⚠ No project selected.", YELLOW); return
        self.terminal.log("\n── git status ──", ACCENT)
        self._run("git status", path)

    def _log(self):
        path = self.project_path.get()
        if not path:
            self.terminal.log("⚠ No project selected.", YELLOW); return
        self.terminal.log("\n── git log (last 5) ──", ACCENT)
        self._run("git log --oneline -5", path)

    def _pull(self):
        path = self.project_path.get()
        if not path:
            self.terminal.log("⚠ No project selected.", YELLOW); return
        self.terminal.log("\n── git pull ──", ACCENT)
        self._run("git pull", path)

    # ── .gitignore ────────────────────────────────────────────────────────────
    def _write_gitignore(self, path):
        preset = self.gitignore_preset.get()
        lines  = GITIGNORE_PRESETS.get(preset, [])
        gi_path = os.path.join(path, ".gitignore")

        # Always add sensible defaults
        defaults = [".DS_Store", "Thumbs.db", "*.log", ".env", ".env.*"]
        final = list(dict.fromkeys(defaults + lines))  # dedupe

        with open(gi_path, "w") as f:
            f.write(f"# Generated by GitDeploy — preset: {preset}\n\n")
            for line in final:
                f.write(line + "\n")

        self.terminal.log(f"✅ .gitignore created ({preset} preset, {len(final)} rules)", ACCENT)
        return gi_path

    # ── Deploy ────────────────────────────────────────────────────────────────
    def _confirm_deploy(self):
        path   = self.project_path.get()
        repo   = self.repo_name.get().strip()
        user   = self.username.get().strip()
        branch = self.branch.get().strip()
        msg    = self.commit_msg.get().strip()

        if not path:
            messagebox.showerror("Missing", "Please select a project folder first."); return
        if not repo:
            messagebox.showerror("Missing", "Please enter a repository name."); return
        if not user:
            messagebox.showerror("Missing", "Please enter your GitHub username."); return

        selected = self.file_list.get_selected()
        if not selected:
            messagebox.showerror("No files", "No files selected to commit."); return

        url = f"https://github.com/{user}/{repo}.git"

        # Build gitignore preview
        gi_note = ""
        if self.create_gitignore.get():
            preset = self.gitignore_preset.get()
            gi_note = f"\n\n📄 .gitignore preset: {preset}"

        confirm = messagebox.askyesno(
            "Confirm Deploy",
            f"🚀 Ready to deploy?\n\n"
            f"  Project : {os.path.basename(path)}\n"
            f"  Repo    : {url}\n"
            f"  Branch  : {branch}\n"
            f"  Files   : {len(selected)} selected\n"
            f"  Commit  : \"{msg}\""
            f"{gi_note}\n\n"
            f"Proceed?"
        )
        if confirm:
            threading.Thread(target=self._deploy, daemon=True).start()

    def _deploy(self):
        path   = self.project_path.get()
        repo   = self.repo_name.get().strip()
        user   = self.username.get().strip()
        branch = self.branch.get().strip()
        msg    = self.commit_msg.get().strip()
        url    = f"https://github.com/{user}/{repo}.git"

        self.terminal.log(f"\n{'━'*50}", ACCENT)
        self.terminal.log(f"🚀 DEPLOYING → {url}", ACCENT)
        self.terminal.log(f"{'━'*50}\n", ACCENT)

        # Step 1: .gitignore
        if self.create_gitignore.get():
            self.terminal.log("Step 1/7 · Writing .gitignore…", YELLOW)
            self._write_gitignore(path)
            self._refresh_files()
        else:
            self.terminal.log("Step 1/7 · Skipping .gitignore", TEXT_DIM)

        # Step 2: git init
        self.terminal.log("\nStep 2/7 · git init", YELLOW)
        git_dir = os.path.join(path, ".git")
        if not os.path.isdir(git_dir):
            self._run("git init", path)
        else:
            self.terminal.log("  (already initialized)", TEXT_DIM)

        # Step 3: Set remote
        self.terminal.log("\nStep 3/7 · Setting remote origin", YELLOW)
        self._run("git remote remove origin", path)  # remove if exists (ignore error)
        ok = self._run(f'git remote add origin {url}', path)
        if not ok:
            self._run(f'git remote set-url origin {url}', path)
        self.terminal.log(f"  origin → {url}", TEXT_MID)

        # Step 4: Stage selected files
        self.terminal.log("\nStep 4/7 · Staging files", YELLOW)
        selected = self.file_list.get_selected()
        for f in selected:
            self._run(f'git add "{f}"', path)
        self.terminal.log(f"  {len(selected)} files staged ✅", ACCENT)

        # Step 5: Commit
        self.terminal.log(f"\nStep 5/7 · Committing: \"{msg}\"", YELLOW)
        ok = self._run(f'git commit -m "{msg}"', path)
        if not ok:
            self.terminal.log("  ⚠ Commit may have failed (nothing new to commit?)", YELLOW)

        # Step 6: Branch
        self.terminal.log(f"\nStep 6/7 · Setting branch → {branch}", YELLOW)
        self._run(f"git branch -M {branch}", path)

        # Step 7: Push
        self.terminal.log(f"\nStep 7/7 · Pushing to GitHub…", YELLOW)
        ok = self._run(f"git push -u origin {branch}", path)

        self.terminal.log(f"\n{'━'*50}", ACCENT)
        if ok:
            self.terminal.log(f"✅ DEPLOYED SUCCESSFULLY!", ACCENT)
            self.terminal.log(f"🌐 {url}", ACCENT)
        else:
            self.terminal.log(f"❌ Push failed. Check credentials / repo exists on GitHub.", RED)
            self.terminal.log("💡 Tip: Make sure you've created the repo on github.com first", YELLOW)
            self.terminal.log("💡 Tip: Use a Personal Access Token as your password", YELLOW)
        self.terminal.log(f"{'━'*50}\n", ACCENT)


if __name__ == "__main__":
    app = GitHubDeployer()
    app.mainloop()
