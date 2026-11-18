git config --global user.name "Manne Sravan"# Day 1 – Project Setup + Data Ingestion (ETL)

## 1. Folder structure

```text
day1_mutual_fund_etl/
├── data/
│   ├── raw/          # Put the 10 supplied CSV files here
│   └── processed/
├── notebooks/
├── sql/
├── dashboard/
├── reports/
├── data_ingestion.py
├── live_nav_fetch.py
├── requirements.txt
└── README.md
```

## 2. Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Add the supplied data

Copy all 10 provided CSV datasets into `data/raw/`. The ingestion script prints each file's shape, data types and first five rows, and checks for empty files, missing values and duplicate rows.

For automatic AMFI code validation, make sure the filenames include `fund_master` and `nav_history` (for example, `fund_master.csv` and `nav_history.csv`). If your actual filenames differ, edit the keyword lists near the top of `data_ingestion.py`. The script also detects common scheme-code column names; adjust the candidate lists if your files use different column names.

## 4. Run the ETL scripts

```bash
python live_nav_fetch.py
python data_ingestion.py
```

The NAV script requests the six specified scheme codes from MFAPI and saves individual raw CSVs plus `data/raw/live_nav_all_schemes.csv`. API availability and returned history are controlled by MFAPI.

## 5. GitHub

Create an empty GitHub repository, then run:

```bash
git init
git add .
git commit -m "Day 1: Data ingestion complete"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Do not commit private credentials or virtual-environment folders.
