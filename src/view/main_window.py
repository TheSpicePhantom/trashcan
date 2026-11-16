from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.adapter.archive_drop import archive_paths_into_trash
from src.adapter.config_store import load_trash_settings, save_trash_location
from src.adapter.folder_actions import FolderActionError, delete_contents, open_in_explorer
from src.adapter.scan_service import collect_trash_entries
from src.model.analysis import FolderSizeEntry, directory_size_bytes
from src.view.details_dialog import show_storage_details
from src.version import VERSION
from src.view.app_icon import apply_window_icon
from src.view.drop_support import hook_drop_files

APP_TITLE = "Trashcan"


def _format_bytes(value: int) -> str:
    return f"{value:,}".replace(",", ".")


class TrashCanApp:
    def __init__(self) -> None:
        self._trash_path: Path | None = None
        self._entries: list[FolderSizeEntry] = []
        self._pending_drops: list[Path] = []
        self._sort_column = "bytes"
        self._sort_reverse = True

        self.root = tk.Tk()
        apply_window_icon(self.root)
        self.root.title(f"{APP_TITLE} {VERSION} – Mülleimer")
        self.root.minsize(780, 480)
        self.root.geometry("960x620")

        self._status_var = tk.StringVar(value="Mülleimer wird vorbereitet …")
        self._path_var = tk.StringVar(value="(kein Mülleimer)")
        self._summary_var = tk.StringVar(value="")

        self._build_ui()
        self._bind_drag_and_drop()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.after(100, self._bootstrap)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(1, weight=1)

        ttk.Label(toolbar, text="Mülleimer:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(toolbar, textvariable=self._path_var).grid(row=0, column=1, sticky="ew")

        buttons = ttk.Frame(toolbar)
        buttons.grid(row=0, column=2, padx=(8, 0))
        ttk.Button(buttons, text="Öffnen …", command=self._choose_trash_location).grid(
            row=0, column=0, padx=(0, 6)
        )
        ttk.Button(buttons, text="Im Explorer anzeigen", command=self._open_trash_in_explorer).grid(
            row=0, column=1
        )

        options = ttk.Frame(toolbar)
        options.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Label(
            options,
            text="Auf die EXE ziehen: still komprimieren · Auf dieses Fenster ziehen: mit Anzeige",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self._analyze_btn = ttk.Button(options, text="Neu analysieren", command=self._start_analyze)
        self._analyze_btn.grid(row=1, column=0, sticky="w")
        self._progress = ttk.Progressbar(options, mode="indeterminate", length=140)
        self._progress.grid(row=1, column=1, padx=(12, 0))

        table_frame = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("path", "mb", "gb", "bytes", "typ")
        self._tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("path", text="Ordner", command=lambda: self._sort_by("path"))
        self._tree.heading("mb", text="MB", command=lambda: self._sort_by("mb"))
        self._tree.heading("gb", text="GB", command=lambda: self._sort_by("gb"))
        self._tree.heading("bytes", text="Bytes", command=lambda: self._sort_by("bytes"))
        self._tree.heading("typ", text="Typ", command=lambda: self._sort_by("typ"))

        self._tree.column("path", width=460, minwidth=200, anchor="w")
        self._tree.column("mb", width=90, minwidth=70, anchor="e")
        self._tree.column("gb", width=90, minwidth=70, anchor="e")
        self._tree.column("bytes", width=120, minwidth=90, anchor="e")
        self._tree.column("typ", width=100, minwidth=80, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self._tree.bind("<Double-1>", self._open_selected)
        self._tree.bind("<Button-3>", self._on_tree_right_click)

        self._context_menu = tk.Menu(self.root, tearoff=0)
        self._context_menu.add_command(label="Kopieren", command=self._copy_selected_path)
        self._context_menu.add_command(label="Zeile kopieren", command=self._copy_selected_row)
        self._context_menu.add_command(label="Öffnen", command=self._open_selected_path)
        self._context_menu.add_command(label="Speicher-Details …", command=self._show_storage_details)
        self._context_menu.add_separator()
        self._context_menu.add_command(label="Inhalt löschen", command=self._confirm_delete_selected)

        footer = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self._summary_var).grid(row=0, column=0, sticky="w")
        ttk.Label(footer, textvariable=self._status_var).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _bind_drag_and_drop(self) -> None:
        enabled = hook_drop_files(self.root, lambda paths: self._queue_dropped_paths(paths))
        if not enabled:
            self._status_var.set(self._status_var.get() + " (pip install windnd für Drag & Drop)")

    def _bootstrap(self) -> None:
        settings = load_trash_settings()
        if settings.trash_location is not None:
            self._apply_trash_location(settings.trash_location)
            self._start_analyze()
            return

        if not self._choose_trash_location():
            self._status_var.set("Kein Mülleimer gewählt. Bitte „Öffnen …“ nutzen.")

    def _choose_trash_location(self) -> bool:
        chosen = filedialog.askdirectory(
            title="Ordner wählen, in dem dein Mülleimer liegen soll",
            mustexist=True,
            parent=self.root,
        )
        if not chosen:
            return False

        path = Path(chosen)
        save_trash_location(path)
        self._apply_trash_location(path)
        self._status_var.set(f"Mülleimer gespeichert: {path}")
        if self._pending_drops:
            self._process_pending_drops()
        else:
            self._start_analyze()
        return True

    def _apply_trash_location(self, path: Path) -> None:
        self._trash_path = path
        self._path_var.set(str(path))

    def _queue_dropped_paths(self, paths: list[str]) -> None:
        existing = {str(path) for path in self._pending_drops}
        for raw in paths:
            candidate = Path(raw)
            key = str(candidate)
            if key in existing:
                continue
            if candidate.exists():
                self._pending_drops.append(candidate)
                existing.add(key)
        if not self._pending_drops:
            return
        if self._trash_path is None:
            messagebox.showinfo(
                APP_TITLE,
                "Zuerst „Öffnen …“ und einen Mülleimer-Ordner wählen.",
                parent=self.root,
            )
            return
        self._process_pending_drops()

    def _process_pending_drops(self) -> None:
        if self._trash_path is None or not self._pending_drops:
            return

        drops = list(self._pending_drops)
        self._pending_drops.clear()
        self._analyze_btn.state(["disabled"])
        self._progress.start(12)
        self._status_var.set(f"Archiviere {len(drops)} Element(e) …")

        trash_path = self._trash_path
        threading.Thread(
            target=self._run_archive,
            args=(drops, trash_path),
            daemon=True,
        ).start()

    def _run_archive(self, drops: list[Path], trash_path: Path) -> None:
        try:
            results, errors = archive_paths_into_trash(drops, trash_path)
        except Exception as err:
            message = str(err)
            self.root.after(0, lambda m=message: self._on_archive_failed(m))
            return
        self.root.after(0, lambda r=results, e=errors: self._on_archive_done(r, e))

    def _on_archive_failed(self, message: str) -> None:
        self._progress.stop()
        self._analyze_btn.state(["!disabled"])
        self._status_var.set(f"Archivierung fehlgeschlagen: {message}")
        messagebox.showerror(APP_TITLE, message, parent=self.root)

    def _on_archive_done(self, results: list, errors: list[str]) -> None:
        self._progress.stop()
        self._analyze_btn.state(["!disabled"])

        if results:
            names = ", ".join(result.zip_path.name for result in results[:3])
            if len(results) > 3:
                names += f" (+{len(results) - 3} weitere)"
            self._status_var.set(f"{len(results)} ZIP(s) erstellt: {names}")
        if errors:
            messagebox.showwarning(
                APP_TITLE,
                "Einige Elemente konnten nicht archiviert werden:\n\n" + "\n".join(errors),
                parent=self.root,
            )

        self._start_analyze()

    def _open_trash_in_explorer(self) -> None:
        if self._trash_path is None:
            messagebox.showinfo(
                APP_TITLE,
                "Zuerst einen Mülleimer-Ordner wählen.",
                parent=self.root,
            )
            return
        try:
            open_in_explorer(str(self._trash_path))
        except (FolderActionError, OSError) as err:
            messagebox.showerror(APP_TITLE, str(err), parent=self.root)

    def _start_analyze(self) -> None:
        if self._trash_path is None or not self._trash_path.is_dir():
            messagebox.showwarning(
                APP_TITLE,
                "Kein gültiger Mülleimer-Ordner. Bitte zuerst wählen.",
                parent=self.root,
            )
            return

        self._analyze_btn.state(["disabled"])
        self._progress.start(12)
        self._status_var.set("Analysiere Mülleimer …")
        self._tree.delete(*self._tree.get_children())

        trash_path = self._trash_path
        threading.Thread(target=self._run_scan, args=(trash_path,), daemon=True).start()

    def _run_scan(self, trash_path: Path) -> None:
        try:
            entries = collect_trash_entries(trash_path)
        except Exception as err:
            message = str(err)
            self.root.after(0, lambda m=message: self._on_scan_failed(m))
            return
        self.root.after(0, lambda e=entries: self._on_scan_done(e))

    def _on_scan_failed(self, message: str) -> None:
        self._progress.stop()
        self._analyze_btn.state(["!disabled"])
        self._status_var.set(f"Fehler: {message}")
        messagebox.showerror(APP_TITLE, message, parent=self.root)

    def _on_scan_done(self, entries: list[FolderSizeEntry]) -> None:
        self._progress.stop()
        self._analyze_btn.state(["!disabled"])
        self._entries = entries
        self._populate_table()

        if not entries:
            self._summary_var.set("0 Einträge im Mülleimer")
            self._status_var.set("Mülleimer ist leer.")
            return

        total = sum(entry.bytes_total for entry in entries)
        total_gb = round(total / (1024**3), 2)
        self._summary_var.set(f"{len(entries)} Einträge · gesamt {total_gb} GB ({_format_bytes(total)} Bytes)")
        self._status_var.set("Fertig. Doppelklick oder Rechtsklick für Aktionen.")

    def _sort_key(self, entry: FolderSizeEntry, column: str):
        match column:
            case "path":
                return entry.path.lower()
            case "mb":
                return entry.size_mb
            case "gb":
                return entry.size_gb
            case "bytes":
                return entry.bytes_total
            case "typ":
                return entry.entry_type
            case _:
                return entry.bytes_total

    def _sort_by(self, column: str) -> None:
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = column != "path"
        self._entries.sort(key=lambda e: self._sort_key(e, column), reverse=self._sort_reverse)
        self._populate_table()

    def _populate_table(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for entry in self._entries:
            self._tree.insert(
                "",
                "end",
                iid=entry.path,
                values=(
                    entry.path,
                    f"{entry.size_mb:.2f}",
                    f"{entry.size_gb:.2f}",
                    _format_bytes(entry.bytes_total),
                    entry.entry_type,
                ),
            )

    def _selected_path_and_type(self) -> tuple[str, str] | None:
        selected = self._tree.selection()
        if not selected:
            return None
        path = selected[0]
        if not path:
            return None
        values = self._tree.item(path, "values")
        entry_type = values[4] if len(values) > 4 else "Ordner"
        return path, str(entry_type)

    def _open_selected(self, _event: object) -> None:
        self._open_selected_path()

    def _on_tree_right_click(self, event: tk.Event) -> None:
        row_id = self._tree.identify_row(event.y)
        if not row_id:
            return
        self._tree.selection_set(row_id)
        self._tree.focus(row_id)
        try:
            self._context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._context_menu.grab_release()

    def _copy_selected_path(self) -> None:
        selected = self._selected_path_and_type()
        if selected is None:
            return
        path, _ = selected
        self._clipboard_set(path)
        self._status_var.set(f"Pfad kopiert: {path}")

    def _copy_selected_row(self) -> None:
        selected = self._tree.selection()
        if not selected:
            return
        values = self._tree.item(selected[0], "values")
        if len(values) < 5:
            return
        ort, mb, gb, bytes_str, typ = values
        text = (
            f"Ort: {ort}\n"
            f"Größe: {gb} GB ({mb} MB, {bytes_str} Bytes)\n"
            f"Typ: {typ}"
        )
        self._clipboard_set(text)
        self._status_var.set("Zeile kopiert (Ort, Größe, Typ).")

    def _clipboard_set(self, text: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update_idletasks()

    def _open_selected_path(self) -> None:
        selected = self._selected_path_and_type()
        if selected is None:
            return
        path, _entry_type = selected
        try:
            open_in_explorer(path)
        except (FolderActionError, OSError) as err:
            messagebox.showerror(APP_TITLE, f"Konnte nicht öffnen:\n{path}\n\n{err}", parent=self.root)

    def _show_storage_details(self) -> None:
        selected = self._selected_path_and_type()
        if selected is None:
            return
        path, entry_type = selected
        show_storage_details(self.root, path, entry_type)

    def _confirm_delete_selected(self) -> None:
        selected = self._selected_path_and_type()
        if selected is None:
            return
        path, entry_type = selected

        if entry_type == "Datei":
            message = f"Diese Datei wirklich unwiderruflich löschen?\n\n{path}"
        else:
            message = (
                "Den Inhalt dieses Ordners wirklich unwiderruflich löschen?\n\n"
                f"{path}\n\n"
                "Der Ordner selbst bleibt bestehen; nur der Inhalt wird entfernt."
            )

        confirmed = messagebox.askyesno(
            "Inhalt löschen – Bestätigung",
            message,
            icon="warning",
            default="no",
            parent=self.root,
        )
        if not confirmed:
            self._status_var.set("Löschen abgebrochen.")
            return

        self._status_var.set(f"Lösche Inhalt von: {path}")
        threading.Thread(
            target=self._run_delete,
            args=(path, entry_type),
            daemon=True,
        ).start()

    def _run_delete(self, path: str, entry_type: str) -> None:
        try:
            delete_contents(path, entry_type)
        except FolderActionError as err:
            message = str(err)
            self.root.after(0, lambda p=path, m=message: self._on_delete_failed(p, m))
            return
        self.root.after(0, lambda p=path: self._on_delete_done(p))

    def _on_delete_failed(self, path: str, message: str) -> None:
        self._status_var.set(f"Löschen fehlgeschlagen: {path}")
        messagebox.showerror(APP_TITLE, f"Inhalt konnte nicht gelöscht werden:\n{path}\n\n{message}", parent=self.root)

    def _on_delete_done(self, path: str) -> None:
        self._entries = [entry for entry in self._entries if entry.path != path]
        self._populate_table()
        total = sum(entry.bytes_total for entry in self._entries)
        total_gb = round(total / (1024**3), 2)
        self._summary_var.set(
            f"{len(self._entries)} Einträge · gesamt {total_gb} GB ({_format_bytes(total)} Bytes)"
        )
        self._status_var.set(f"Inhalt gelöscht: {path}")

    def run(self) -> int:
        self.root.mainloop()
        return 0


def run() -> int:
    return TrashCanApp().run()