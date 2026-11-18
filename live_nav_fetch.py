from pathlib import Path
import time
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

SCHEMES = {
    "HDFC Top 100 Direct": "125497",
    "SBI Bluechip": "119551",
    "ICICI Bluechip": "120503",
    "Nippon Large Cap": "118632",
    "Axis Bluechip": "119092",
    "Kotak Bluechip": "120841",
}
API_URL = "https://api.mfapi.in/mf/{}"

def fetch_scheme(session, name, code):
    url = API_URL.format(code)
    response = session.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    meta = payload.get("meta", {})
    nav_rows = payload.get("data", [])
    if not nav_rows:
        raise ValueError(f"No NAV records returned for {name} ({code})")

    df = pd.DataFrame(nav_rows)
    if "date" not in df.columns or "nav" not in df.columns:
        raise ValueError(f"Unexpected API response structure for {name} ({code})")

    df["scheme_name_requested"] = name
    df["scheme_code"] = str(code)
    df["fund_house"] = meta.get("fund_house")
    df["scheme_type"] = meta.get("scheme_type")
    df["scheme_category"] = meta.get("scheme_category")
    df["scheme_name_api"] = meta.get("scheme_name")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    return df

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_frames = []

    with requests.Session() as session:
        session.headers.update({"User-Agent": "Day1-MutualFund-ETL/1.0"})
        for name, code in SCHEMES.items():
            try:
                frame = fetch_scheme(session, name, code)
                safe_name = name.lower().replace(" ", "_")
                out_file = RAW_DIR / f"nav_{safe_name}_{code}.csv"
                frame.to_csv(out_file, index=False)
                all_frames.append(frame)
                print(f"{name} ({code}): {len(frame)} NAV rows -> {out_file}")
            except (requests.RequestException, ValueError, KeyError) as exc:
                print(f"FAILED: {name} ({code}): {exc}")
            time.sleep(0.25)  # Be polite to the public API.

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined.to_csv(RAW_DIR / "live_nav_all_schemes.csv", index=False)
        print(f"\nSaved combined NAV file with {len(combined)} rows.")
    else:
        raise RuntimeError("No scheme NAV data could be fetched. Check internet/API availability.")

if __name__ == "__main__":
    main()
