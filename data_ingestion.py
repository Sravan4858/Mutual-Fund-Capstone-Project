from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"

def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

    datasets = {}
    anomalies = []
    print(f"Found {len(files)} CSV files in {RAW_DIR}")
    for path in files:
        df = pd.read_csv(path, low_memory=False)
        datasets[path.name] = df
        print("\n" + "=" * 80)
        print(f"FILE: {path.name}")
        print("Shape:", df.shape)
        print("\\nData types:\\n", df.dtypes.to_string())
        print("\\nFirst five rows:\\n", df.head().to_string(index=False))
        missing = int(df.isna().sum().sum())
        duplicates = int(df.duplicated().sum())
        if df.empty or missing or duplicates:
            anomalies.append(
                f"{path.name}: empty={df.empty}, missing_cells={missing}, duplicate_rows={duplicates}"
            )

    master = datasets.get("01_fund_master.csv")
    nav = datasets.get("02_nav_history.csv")
    summary = ["DAY 1 DATA QUALITY SUMMARY", "=========================="]
    if master is not None:
        for col in ["fund_house", "category", "sub_category", "risk_category"]:
            if col in master.columns:
                vals = sorted(master[col].dropna().astype(str).unique().tolist())
                summary.append(f"{col} ({len(vals)} unique): {vals}")
    if master is not None and nav is not None:
        master_codes = set(master["amfi_code"].dropna().astype(str).str.strip())
        nav_codes = set(nav["amfi_code"].dropna().astype(str).str.strip())
        missing_codes = sorted(master_codes - nav_codes)
        summary += [
            f"Unique fund master AMFI codes: {len(master_codes)}",
            f"Unique NAV history AMFI codes: {len(nav_codes)}",
            f"Fund master codes missing from NAV history: {len(missing_codes)}",
            f"Missing codes: {missing_codes}",
        ]
    summary.append(
        "AMFI scheme codes are numeric identifiers; do not assume their digits encode fund house, "
        "category, or plan. Use fund_master metadata for those attributes."
    )
    summary.append("Potential anomalies:")
    summary.extend([f"- {x}" for x in anomalies] or ["- No basic anomalies detected."])
    output = REPORT_DIR / "day1_data_quality_summary.txt"
    output.write_text("\n".join(summary), encoding="utf-8")
    print("\n" + "\n".join(summary))
    print(f"\\nSaved report: {output}")

if __name__ == "__main__":
    main()
