#!/usr/bin/env python3
"""Inspecciona el contenido de un ZIP grande sin extraerlo ni requerir claves.

Ejemplo:
  python scripts/inspect_factor_model.py 'KN_US_Equity_Factor_Model.zip' \
    --output research/factor_model_manifest.json
"""
import argparse
import csv
import io
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile

SPECIAL = {
    "market": "f_market", "f_market": "f_market",
    "total_factor_returns": "f_total_factor_returns",
    "f_total_factor_returns": "f_total_factor_returns",
    "total_excess_returns": "f_total_excess_returns",
    "f_total_excess_returns": "f_total_excess_returns",
    "idyo_returns": "f_idyo_returns", "f_idyo_returns": "f_idyo_returns",
}
RESERVED = {"f_total_factor_returns", "f_total_excess_returns", "f_idyo_returns"}


def inspect(path, max_entries=5000):
    """Lee directorio ZIP y cabeceras CSV sin descomprimir archivos completos."""
    if not path.is_file():
        raise FileNotFoundError(f"No encontré: {path}")
    result = {"source_zip": path.name, "verified_from_zip": True,
              "all_entry_count": 0, "csv_count": 0, "truncated": False,
              "entries": [], "warnings": [],
              "caveat": "No valida fechas totales, contribuciones, retornos ni cobertura."}
    try:
        with ZipFile(path) as z:
            entries = z.infolist()
            result["all_entry_count"] = len(entries)
            result["truncated"] = len(entries) > max_entries
            for info in entries[:max_entries]:
                if info.is_dir():
                    continue
                ext = Path(info.filename).suffix.lower()
                row = {"path": info.filename, "ext": ext,
                       "compressed_bytes": info.compress_size,
                       "uncompressed_bytes": info.file_size}
                if ext == ".csv":
                    result["csv_count"] += 1
                    factor_name = Path(info.filename).stem.lower().strip()
                    canonical = SPECIAL.get(factor_name, factor_name)
                    row["factor_name_from_filename"] = canonical
                    row["reserved_aggregate"] = canonical in RESERVED
                    try:
                        with z.open(info) as binary:
                            with io.TextIOWrapper(binary, encoding="utf-8-sig",
                                                      errors="replace", newline="") as txt:
                                reader = csv.reader(txt)
                                header = next(reader, [])
                                row["first_column"] = header[0] if header else None
                                row["column_count"] = len(header)
                                row["sample_security_columns"] = header[1:9]
                                row["sample_first_column_values"] = []
                                for _, values in zip(range(3), reader):
                                    if values:
                                        row["sample_first_column_values"].append(values[0])
                    except (UnicodeError, OSError, csv.Error) as e:
                        row["read_error"] = type(e).__name__
                result["entries"].append(row)
    except BadZipFile as e:
        raise ValueError("No es un ZIP válido o está corrupto") from e
    if result["truncated"]:
        result["warnings"].append("Directorio truncado por max_entries")
    if any(e["ext"] in (".zip", ".7z", ".rar") for e in result["entries"]):
        result["warnings"].append("Hay comprimidos anidados no inspeccionados")
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("zip_path", type=Path)
    cli.add_argument("--output", type=Path,
                     default=Path("research/factor_model_manifest.json"))
    args = cli.parse_args()
    out = inspect(args.zip_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Manifiesto generado:", args.output)
    print("Entradas:", out["all_entry_count"], "| CSV:", out["csv_count"])
    print("No se ejecutó ningún cálculo de inversión.")


if __name__ == "__main__":
    main()
