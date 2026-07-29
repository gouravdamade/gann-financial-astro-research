from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from jhora_kaala_intermediate_witness_protocol import (
    AYANA_SAMPLE_ID,
    CAPTURED_STATUS,
    DEFAULT_AYANA_TEMPLATE,
    DEFAULT_HORA_TEMPLATE,
    DEFAULT_KAALA_WITNESS,
    HORA_SAMPLE_ID,
    PLANETS,
    read_csv,
    validate_ayana_rows,
    validate_hora_rows,
    witness_gate_summary,
    write_csv,
)
from jhora_witness_protocol import require_pinned_jhora, sha256


ASSISTANT_CONTRACT = "GANN_JHORA_KAALA_CAPTURE_ASSISTANT_V1"
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_JHORA_EXE = Path(
    r"D:\GannFinancialAstro\external_validators"
    r"\jagannatha_hora_8_0\app\bin\jhora.exe"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_intermediate_20260729"
)
DEFAULT_HORA_OUTPUT = (
    DEFAULT_OUTPUT_DIR / "jhora_hora_boundary_witness_completed.csv"
)
DEFAULT_AYANA_OUTPUT = (
    DEFAULT_OUTPUT_DIR / "jhora_ayana_intermediate_witness_completed.csv"
)
CAPTURE_NOTE = (
    "Reviewer-entered from the selected visible JHora evidence. The assistant "
    "hashed the evidence and performed no astrological inference."
)


class CaptureValidationError(ValueError):
    def __init__(self, issues: list[str]) -> None:
        self.issues = issues
        super().__init__("\n".join(issues))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open the guided visible-JHora Hora/Ayana capture assistant or "
            "inspect completed packet status."
        )
    )
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--hora-packet", type=Path, default=DEFAULT_HORA_OUTPUT)
    parser.add_argument(
        "--ayana-packet",
        type=Path,
        default=DEFAULT_AYANA_OUTPUT,
    )
    parser.add_argument(
        "--kaala-witness",
        type=Path,
        default=DEFAULT_KAALA_WITNESS,
    )
    return parser.parse_args()


def utc_capture_time(raw: str | None = None) -> str:
    if raw:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("capture time must include a timezone")
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _required_evidence(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"visible evidence file is missing: {resolved}")
    return resolved


def _required_reviewer(reviewer: str) -> str:
    value = reviewer.strip()
    if not value:
        raise ValueError("reviewer name is required")
    return value


def _number_text(value: object) -> str:
    if value is None or str(value).strip() == "":
        return ""
    return f"{float(value):.12g}"


def _capture_provenance(
    *,
    evidence_path: Path,
    reviewer: str,
    captured_at_utc: str | None,
) -> dict[str, str]:
    evidence = _required_evidence(evidence_path)
    return {
        "evidence_path": str(evidence),
        "evidence_sha256": sha256(evidence),
        "reviewer": _required_reviewer(reviewer),
        "captured_at_utc": utc_capture_time(captured_at_utc),
        "status": CAPTURED_STATUS,
        "notes": CAPTURE_NOTE,
    }


def assemble_hora_capture_rows(
    template_rows: list[dict[str, str]],
    *,
    evidence_path: Path,
    reviewer: str,
    sunrise_lmt_hour: object,
    hora_lord: str,
    awards: Mapping[str, object],
    captured_at_utc: str | None = None,
) -> list[dict[str, str]]:
    normalized_awards = {
        str(planet).strip().upper(): value for planet, value in awards.items()
    }
    missing = sorted(set(PLANETS) - set(normalized_awards))
    extra = sorted(set(normalized_awards) - set(PLANETS))
    if missing or extra:
        raise ValueError(
            f"Hora award matrix mismatch: missing={missing}, extra={extra}"
        )
    provenance = _capture_provenance(
        evidence_path=evidence_path,
        reviewer=reviewer,
        captured_at_utc=captured_at_utc,
    )
    sunrise_text = _number_text(sunrise_lmt_hour)
    lord = hora_lord.strip().upper()
    rows = copy.deepcopy(template_rows)
    for row in rows:
        planet = str(row.get("planet") or "").strip().upper()
        row.update(provenance)
        row["jhora_sunrise_lmt_hour"] = sunrise_text
        row["jhora_hora_lord"] = lord
        row["jhora_hora_virupa"] = _number_text(
            normalized_awards.get(planet)
        )
    return rows


def assemble_ayana_capture_rows(
    template_rows: list[dict[str, str]],
    *,
    evidence_path: Path,
    reviewer: str,
    values: Mapping[str, Mapping[str, object]],
    captured_at_utc: str | None = None,
) -> list[dict[str, str]]:
    normalized_values = {
        str(planet).strip().upper(): dict(planet_values)
        for planet, planet_values in values.items()
    }
    missing = sorted(set(PLANETS) - set(normalized_values))
    extra = sorted(set(normalized_values) - set(PLANETS))
    if missing or extra:
        raise ValueError(
            f"Ayana value matrix mismatch: missing={missing}, extra={extra}"
        )
    provenance = _capture_provenance(
        evidence_path=evidence_path,
        reviewer=reviewer,
        captured_at_utc=captured_at_utc,
    )
    rows = copy.deepcopy(template_rows)
    for row in rows:
        planet = str(row.get("planet") or "").strip().upper()
        planet_values = normalized_values.get(planet, {})
        row.update(provenance)
        row["jhora_tropical_longitude_deg"] = _number_text(
            planet_values.get("tropical_longitude_deg")
        )
        row["jhora_kranti_deg"] = _number_text(
            planet_values.get("kranti_deg")
        )
        row["jhora_ayana_virupa"] = _number_text(
            planet_values.get("ayana_virupa")
        )
    return rows


def _atomic_write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    write_csv(temporary, rows)
    os.replace(temporary, path)


def _refuse_template_overwrite(output_path: Path, template_path: Path) -> None:
    if output_path.resolve() == template_path.resolve():
        raise ValueError("completed output may not overwrite the pending template")


def export_hora_packet(
    *,
    evidence_path: Path,
    reviewer: str,
    sunrise_lmt_hour: object,
    hora_lord: str,
    awards: Mapping[str, object],
    output_path: Path = DEFAULT_HORA_OUTPUT,
    template_path: Path = DEFAULT_HORA_TEMPLATE,
    locked_kaala_path: Path = DEFAULT_KAALA_WITNESS,
    captured_at_utc: str | None = None,
) -> dict[str, object]:
    _refuse_template_overwrite(output_path, template_path)
    rows = assemble_hora_capture_rows(
        read_csv(template_path),
        evidence_path=evidence_path,
        reviewer=reviewer,
        sunrise_lmt_hour=sunrise_lmt_hour,
        hora_lord=hora_lord,
        awards=awards,
        captured_at_utc=captured_at_utc,
    )
    issues = validate_hora_rows(rows, read_csv(locked_kaala_path))
    if issues:
        raise CaptureValidationError(issues)
    _atomic_write(output_path, rows)
    return {
        "contract": ASSISTANT_CONTRACT,
        "status": "valid_hora_packet_written",
        "sampleId": HORA_SAMPLE_ID,
        "rows": len(rows),
        "output": str(output_path.resolve()),
        "sha256": sha256(output_path),
    }


def export_ayana_packet(
    *,
    evidence_path: Path,
    reviewer: str,
    values: Mapping[str, Mapping[str, object]],
    output_path: Path = DEFAULT_AYANA_OUTPUT,
    template_path: Path = DEFAULT_AYANA_TEMPLATE,
    locked_kaala_path: Path = DEFAULT_KAALA_WITNESS,
    captured_at_utc: str | None = None,
) -> dict[str, object]:
    _refuse_template_overwrite(output_path, template_path)
    rows = assemble_ayana_capture_rows(
        read_csv(template_path),
        evidence_path=evidence_path,
        reviewer=reviewer,
        values=values,
        captured_at_utc=captured_at_utc,
    )
    issues = validate_ayana_rows(rows, read_csv(locked_kaala_path))
    if issues:
        raise CaptureValidationError(issues)
    _atomic_write(output_path, rows)
    return {
        "contract": ASSISTANT_CONTRACT,
        "status": "valid_ayana_packet_written",
        "sampleId": AYANA_SAMPLE_ID,
        "rows": len(rows),
        "output": str(output_path.resolve()),
        "sha256": sha256(output_path),
    }


def packet_status(
    *,
    hora_path: Path = DEFAULT_HORA_OUTPUT,
    ayana_path: Path = DEFAULT_AYANA_OUTPUT,
    locked_kaala_path: Path = DEFAULT_KAALA_WITNESS,
) -> dict[str, object]:
    return witness_gate_summary(
        hora_path=hora_path,
        ayana_path=ayana_path,
        kaala_witness_path=locked_kaala_path,
    )


def launch_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("JHora Kaala Evidence Capture")
    root.geometry("1120x820")
    root.minsize(980, 720)

    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
    style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
    style.configure("Status.TLabel", foreground="#1f5f70")

    reviewer_var = tk.StringVar()
    hora_evidence_var = tk.StringVar()
    ayana_evidence_var = tk.StringVar()
    sunrise_var = tk.StringVar()
    hora_lord_var = tk.StringVar()
    hora_award_vars = {planet: tk.StringVar() for planet in PLANETS}
    ayana_vars = {
        planet: {
            "tropical_longitude_deg": tk.StringVar(),
            "kranti_deg": tk.StringVar(),
            "ayana_virupa": tk.StringVar(),
        }
        for planet in PLANETS
    }
    status_var = tk.StringVar(
        value="Pending visible JHora evidence. Production formulas remain locked."
    )

    shell = ttk.Frame(root, padding=(18, 14))
    shell.pack(fill="both", expand=True)
    ttk.Label(
        shell,
        text="Visible JHora Kaala Evidence Capture",
        style="Title.TLabel",
    ).pack(anchor="w")
    ttk.Label(
        shell,
        text=(
            "Enter only values you can see in the pinned JHora 8.0 window. "
            "The assistant hashes evidence and refuses contradictory packets."
        ),
        wraplength=1030,
    ).pack(anchor="w", pady=(2, 10))

    top = ttk.Frame(shell)
    top.pack(fill="x", pady=(0, 10))
    ttk.Label(top, text="Reviewer", style="Heading.TLabel").pack(side="left")
    ttk.Entry(top, textvariable=reviewer_var, width=34).pack(
        side="left", padx=(8, 18)
    )

    def launch_pinned_jhora() -> None:
        try:
            require_pinned_jhora(DEFAULT_JHORA_EXE)
            subprocess.Popen([str(DEFAULT_JHORA_EXE)])
            status_var.set("Pinned JHora 8.0 launched. Keep this assistant open.")
        except Exception as exc:
            messagebox.showerror("JHora launch failed", str(exc))

    def open_protocol() -> None:
        protocol = REPO_ROOT / "jhora_kaala_intermediate_witness_protocol_20260729.md"
        os.startfile(protocol)  # type: ignore[attr-defined]

    ttk.Button(top, text="Open JHora", command=launch_pinned_jhora).pack(
        side="left", padx=4
    )
    ttk.Button(top, text="Open protocol", command=open_protocol).pack(
        side="left", padx=4
    )

    notebook = ttk.Notebook(shell)
    notebook.pack(fill="both", expand=True)
    hora_tab = ttk.Frame(notebook, padding=14)
    ayana_tab = ttk.Frame(notebook, padding=14)
    verify_tab = ttk.Frame(notebook, padding=14)
    notebook.add(hora_tab, text="1. Hora boundary")
    notebook.add(ayana_tab, text="2. Historical Ayana")
    notebook.add(verify_tab, text="3. Verify packet")

    def browse_evidence(target: tk.StringVar) -> None:
        selected = filedialog.askopenfilename(
            title="Choose uncropped visible JHora evidence",
            filetypes=(
                ("Image or PDF evidence", "*.png *.jpg *.jpeg *.bmp *.pdf"),
                ("All files", "*.*"),
            ),
        )
        if selected:
            target.set(selected)

    ttk.Label(
        hora_tab,
        text="Case 8 Hora boundary",
        style="Heading.TLabel",
    ).grid(row=0, column=0, columnspan=4, sticky="w")
    ttk.Label(
        hora_tab,
        text=(
            "Fixture: 2025-03-07 19:30 Asia/Kolkata, Tokyo reference "
            "location. Capture visible apparent-tip sunrise in LMT, the "
            "selected Hora lord, and every 0/60 award."
        ),
        wraplength=980,
    ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(2, 12))
    ttk.Label(hora_tab, text="Uncropped evidence").grid(
        row=2, column=0, sticky="w"
    )
    ttk.Entry(
        hora_tab,
        textvariable=hora_evidence_var,
        state="readonly",
        width=76,
    ).grid(row=2, column=1, columnspan=2, sticky="ew", padx=8)
    ttk.Button(
        hora_tab,
        text="Choose...",
        command=lambda: browse_evidence(hora_evidence_var),
    ).grid(row=2, column=3, sticky="e")
    ttk.Label(hora_tab, text="Sunrise LMT hour").grid(
        row=3, column=0, sticky="w", pady=(8, 0)
    )
    ttk.Entry(hora_tab, textvariable=sunrise_var, width=18).grid(
        row=3, column=1, sticky="w", padx=8, pady=(8, 0)
    )
    ttk.Label(hora_tab, text="Visible Hora lord").grid(
        row=3, column=2, sticky="e", pady=(8, 0)
    )
    ttk.Combobox(
        hora_tab,
        textvariable=hora_lord_var,
        values=PLANETS,
        state="readonly",
        width=16,
    ).grid(row=3, column=3, sticky="e", pady=(8, 0))

    ttk.Label(hora_tab, text="Planet", style="Heading.TLabel").grid(
        row=4, column=0, sticky="w", pady=(16, 4)
    )
    ttk.Label(
        hora_tab,
        text="Visible Hora award (virupa)",
        style="Heading.TLabel",
    ).grid(row=4, column=1, columnspan=2, sticky="w", pady=(16, 4))
    for offset, planet in enumerate(PLANETS, start=5):
        ttk.Label(hora_tab, text=planet.title()).grid(
            row=offset, column=0, sticky="w", pady=3
        )
        ttk.Entry(
            hora_tab,
            textvariable=hora_award_vars[planet],
            width=18,
        ).grid(row=offset, column=1, sticky="w", padx=8, pady=3)
    hora_tab.columnconfigure(1, weight=1)
    hora_tab.columnconfigure(2, weight=1)

    def save_hora() -> None:
        try:
            result = export_hora_packet(
                evidence_path=Path(hora_evidence_var.get()),
                reviewer=reviewer_var.get(),
                sunrise_lmt_hour=sunrise_var.get(),
                hora_lord=hora_lord_var.get(),
                awards={
                    planet: variable.get()
                    for planet, variable in hora_award_vars.items()
                },
            )
            status_var.set(
                "Verified Hora packet saved: " + str(result["output"])
            )
            messagebox.showinfo("Hora packet verified", status_var.get())
        except CaptureValidationError as exc:
            status_var.set("Hora packet rejected. Correct the listed conflicts.")
            messagebox.showerror(
                "Hora packet rejected",
                "\n".join(exc.issues[:18]),
            )
        except Exception as exc:
            messagebox.showerror("Hora capture failed", str(exc))

    ttk.Button(
        hora_tab,
        text="Validate and save Hora packet",
        command=save_hora,
    ).grid(row=13, column=0, columnspan=4, sticky="w", pady=(18, 0))

    ttk.Label(
        ayana_tab,
        text="Historical Ayana intermediates",
        style="Heading.TLabel",
    ).grid(row=0, column=0, columnspan=5, sticky="w")
    ttk.Label(
        ayana_tab,
        text=(
            "Fixture: 1889-02-11 00:00 Asia/Tokyo. Enter visible tropical "
            "longitude, visible Kranti, or both, plus visible Ayana for every "
            "planet. Do not copy values from this project's comparator."
        ),
        wraplength=980,
    ).grid(row=1, column=0, columnspan=5, sticky="w", pady=(2, 12))
    ttk.Label(ayana_tab, text="Uncropped evidence").grid(
        row=2, column=0, sticky="w"
    )
    ttk.Entry(
        ayana_tab,
        textvariable=ayana_evidence_var,
        state="readonly",
        width=76,
    ).grid(row=2, column=1, columnspan=3, sticky="ew", padx=8)
    ttk.Button(
        ayana_tab,
        text="Choose...",
        command=lambda: browse_evidence(ayana_evidence_var),
    ).grid(row=2, column=4, sticky="e")

    headings = (
        "Planet",
        "Tropical longitude",
        "Kranti",
        "Ayana virupa",
    )
    for column, heading in enumerate(headings):
        ttk.Label(
            ayana_tab,
            text=heading,
            style="Heading.TLabel",
        ).grid(row=3, column=column, sticky="w", pady=(16, 5), padx=(0, 10))
    for offset, planet in enumerate(PLANETS, start=4):
        ttk.Label(ayana_tab, text=planet.title()).grid(
            row=offset, column=0, sticky="w", pady=3
        )
        ttk.Entry(
            ayana_tab,
            textvariable=ayana_vars[planet]["tropical_longitude_deg"],
            width=20,
        ).grid(row=offset, column=1, sticky="w", pady=3)
        ttk.Entry(
            ayana_tab,
            textvariable=ayana_vars[planet]["kranti_deg"],
            width=20,
        ).grid(row=offset, column=2, sticky="w", pady=3)
        ttk.Entry(
            ayana_tab,
            textvariable=ayana_vars[planet]["ayana_virupa"],
            width=20,
        ).grid(row=offset, column=3, sticky="w", pady=3)
    ayana_tab.columnconfigure(3, weight=1)

    def save_ayana() -> None:
        try:
            result = export_ayana_packet(
                evidence_path=Path(ayana_evidence_var.get()),
                reviewer=reviewer_var.get(),
                values={
                    planet: {
                        field: variable.get()
                        for field, variable in planet_vars.items()
                    }
                    for planet, planet_vars in ayana_vars.items()
                },
            )
            status_var.set(
                "Verified Ayana packet saved: " + str(result["output"])
            )
            messagebox.showinfo("Ayana packet verified", status_var.get())
        except CaptureValidationError as exc:
            status_var.set("Ayana packet rejected. Correct the listed conflicts.")
            messagebox.showerror(
                "Ayana packet rejected",
                "\n".join(exc.issues[:18]),
            )
        except Exception as exc:
            messagebox.showerror("Ayana capture failed", str(exc))

    ttk.Button(
        ayana_tab,
        text="Validate and save Ayana packet",
        command=save_ayana,
    ).grid(row=12, column=0, columnspan=5, sticky="w", pady=(18, 0))

    ttk.Label(
        verify_tab,
        text="Certification packet status",
        style="Heading.TLabel",
    ).pack(anchor="w")
    ttk.Label(
        verify_tab,
        text=(
            "A complete packet only proves that the visible JHora inputs were "
            "captured consistently. It does not certify a formula, validate a "
            "trading rule, or unlock execution."
        ),
        wraplength=980,
    ).pack(anchor="w", pady=(2, 12))
    result_box = tk.Text(
        verify_tab,
        height=22,
        wrap="word",
        font=("Consolas", 10),
    )
    result_box.pack(fill="both", expand=True)

    def verify_packets() -> None:
        result = packet_status()
        rendered = json.dumps(result, indent=2)
        result_box.delete("1.0", "end")
        result_box.insert("1.0", rendered)
        status_var.set("Packet status: " + str(result["status"]))

    ttk.Button(
        verify_tab,
        text="Verify completed packet",
        command=verify_packets,
    ).pack(anchor="w", pady=(12, 0))

    footer = ttk.Frame(shell)
    footer.pack(fill="x", pady=(10, 0))
    ttk.Label(
        footer,
        textvariable=status_var,
        style="Status.TLabel",
        wraplength=1030,
    ).pack(anchor="w")
    ttk.Label(
        footer,
        text=(
            "Execution remains locked. The pending templates are never "
            "overwritten."
        ),
    ).pack(anchor="w", pady=(2, 0))

    root.mainloop()


def main() -> int:
    args = parse_args()
    if args.status:
        print(
            json.dumps(
                packet_status(
                    hora_path=args.hora_packet,
                    ayana_path=args.ayana_packet,
                    locked_kaala_path=args.kaala_witness,
                ),
                indent=2,
            )
        )
        return 0
    launch_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
