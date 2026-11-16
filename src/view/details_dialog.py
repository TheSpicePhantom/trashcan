from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from src.adapter.storage_details import StorageDetails, collect_storage_details


def _format_gb(value: int) -> str:
    gb = value / (1024**3)
    return f"{gb:.2f} GB ({value:,} Bytes)".replace(",", ".")


class StorageDetailsDialog:
    def __init__(self, parent: tk.Tk, path: str, entry_type: str) -> None:
        self._path = path
        self._entry_type = entry_type

        self.window = tk.Toplevel(parent)
        self.window.title("Trashcan – Speicher-Details")
        self.window.geometry("720x520")
        self.window.minsize(560, 400)
        self.window.transient(parent)

        self._summary = tk.StringVar(value="Lese Details …")
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text=path, wraplength=660).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=self._summary, wraplength=660).grid(
            row=1, column=0, sticky="w", pady=(8, 12)
        )

        ttk.Label(frame, text="Aufteilung (Unterordner / Benutzer-SIDs):").grid(row=2, column=0, sticky="w")
        self._split_tree = self._make_tree(frame, ("name", "gb"), ("Name", "Größe"))
        self._split_tree.grid(row=3, column=0, sticky="nsew", pady=(4, 10))

        ttk.Label(frame, text="Größte Dateien:").grid(row=4, column=0, sticky="w")
        self._files_tree = self._make_tree(frame, ("path", "gb"), ("Pfad", "Größe"))
        self._files_tree.grid(row=5, column=0, sticky="nsew", pady=(4, 0))

        threading.Thread(target=self._load, daemon=True).start()

    def _make_tree(self, parent: ttk.Frame, columns: tuple[str, str], headings: tuple[str, str]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=6)
        for col, title in zip(columns, headings, strict=True):
            tree.heading(col, text=title)
        tree.column(columns[0], width=480, anchor="w")
        tree.column(columns[1], width=120, anchor="e")
        return tree

    def _load(self) -> None:
        try:
            details = collect_storage_details(self._path, self._entry_type)
        except Exception as err:
            message = str(err)
            self.window.after(0, lambda m=message: self._summary.set(f"Fehler: {m}"))
            return
        self.window.after(0, lambda d=details: self._show(d))

    def _show(self, details: StorageDetails) -> None:
        lines = [f"Belegt auf Datenträger: {_format_gb(details.physical_bytes)}"]
        if details.shell_bytes is not None:
            lines.append(
                f"Windows-Papierkorb (Shell, dieses Profil): {_format_gb(details.shell_bytes)}"
            )
            if details.physical_bytes > details.shell_bytes * 1.25 and details.shell_bytes > 0:
                lines.append(
                    "Hinweis: Auf dem Datenträger liegt oft mehr, weil $RECYCLE.BIN "
                    "auch andere Benutzer und interne $R/$I-Dateien enthält."
                )
        self._summary.set("\n".join(lines))

        for name, size in details.sid_breakdown:
            self._split_tree.insert("", "end", values=(name, _format_gb(size)))

        for file_path, size in details.largest_files:
            self._files_tree.insert("", "end", values=(file_path, _format_gb(size)))


def show_storage_details(parent: tk.Tk, path: str, entry_type: str) -> None:
    StorageDetailsDialog(parent, path, entry_type)