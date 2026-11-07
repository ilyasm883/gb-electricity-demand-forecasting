# Multi-Horizon Electricity Demand Forecasting (COM748)

Hourly electricity demand forecasting for Great Britain, 1 to 24 hours ahead, comparing five models:
**seasonal naive, SARIMA, XGBoost, LSTM and PatchTST**. Data: Open Power System Data, 2015-2019.

---

## Folder structure

```
├── datasets/
│   ├── raw/                     # gb_columns_raw.csv: the 3 original GB columns used (full OPSD files: notebook 01)
│   └── processed/               # clean data, features, train / validation / test files
├── notebooks/
│   ├── 01_download_dataset.ipynb      # download the raw files
│   ├── 02_preprocessing.ipynb         # select GB columns, find and fill wrong values
│   ├── 03_eda.ipynb                   # exploratory data analysis
│   ├── 04_feature_engineering.ipynb   # build 11 features, split train / validation / test
│   └── 05_baselines.ipynb             # seasonal naive + SARIMA
├── results/
│   ├── forecasts/               # 2019 forecasts of each model
│   ├── tables/                  # result tables (CSV)
│   └── figures/                 # figures from the notebooks (PNG)
├── FEATURES.md                  # dataset, features and pipeline
├── requirements.txt             # packages for the whole project (exact versions)
└── README.md
```

---

## 1. What you need

- **Python 3.11** (tested with 3.11.11). Download it from <https://www.python.org/downloads/>.
  On Windows, tick **"Add python.exe to PATH"** during the installation.
- About **3 GB** of free disk space (PyTorch, needed for the later deep learning notebooks, is large) and an internet connection.

Open a terminal **inside the project folder** (the folder that contains `notebooks` and `README.md`):
- **Windows:** open the folder in File Explorer, click the address bar, type `powershell` and press Enter.
- **Mac / Linux:** open Terminal and use `cd` to go to the folder.

> If the folder path contains spaces, put it in quotes when you type it, for example
> `cd "C:\Users\me\Desktop\my project"`.

---

## 2. Set up the environment

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell says *"running scripts is disabled on this system"*, run this once and try the activate command again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

(Using the old Command Prompt instead? Activate with `.venv\Scripts\activate.bat`.)

### Mac / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You will see `(.venv)` at the start of the line when the environment is active. Activate it again every time you open a new terminal.

---

## 3. Run the notebooks

1. Start Jupyter (with the environment active):

   ```bash
   jupyter notebook
   ```

2. Jupyter opens in your browser. Click the **`notebooks`** folder.
3. Open each notebook file **in this order** and run it.

**Start from notebook 02.** The raw data it needs, `datasets/raw/gb_columns_raw.csv`, is already in the repository.
Notebook 01 is optional: it downloads the full original files from OPSD (about 365 MB) and makes `gb_columns_raw.csv` again.

| Order | Notebook file | What it does |
|---|---|---|
| (optional) | `01_download_dataset.ipynb` | Downloads the two full OPSD files into `datasets/raw/` and saves the three GB columns in `gb_columns_raw.csv` |
| 1 | `02_preprocessing.ipynb` | Keeps GB load and temperature for 2015-2019, finds wrong values with three rules and fills them |
| 2 | `03_eda.ipynb` | Exploratory data analysis: daily, weekly and yearly patterns, holidays, temperature, autocorrelation |
| 3 | `04_feature_engineering.ipynb` | Builds the 11 features and splits the data: train 2015-2017, validation 2018, test 2019 |
| 4 | `05_baselines.ipynb` | Seasonal naive and SARIMA models: forecasts every day of 2019, 24 hours ahead |

**How to run one notebook:**

1. Click the notebook file to open it.
2. In the menu, click **Kernel → Restart Kernel and Run All Cells** (or **Run → Run All Cells**).
3. Wait until every cell has finished. A cell that is still running shows `[*]`; when it is done it shows a number, such as `[5]`.
4. Close the notebook and open the next one.

Each notebook saves its output, which the next notebook reads, so always keep this order.

---

## 4. Problems and fixes

| Problem | Fix |
|---|---|
| `py` or `python` is not recognised (Windows) | Python is not on PATH. Reinstall Python 3.11 and tick "Add python.exe to PATH" |
| `jupyter` is not recognised | The environment is not active. Run the activate command from step 2 |
| `FileNotFoundError` in notebook 02 | Check that `datasets/raw/gb_columns_raw.csv` is there. If not, run notebook 01 to make it |
| `FileNotFoundError` in notebook 03, 04 or 05 | Run the notebooks in order (02, 03, 04, 05). Each one needs the files from the one before |

---

*Academic prototype for an MSc research project. Not a tool for real grid operation.*
