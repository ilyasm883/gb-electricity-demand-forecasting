# Multi-Horizon Electricity Demand Forecasting (COM748)

Hourly electricity demand forecasting for Great Britain, 1 to 24 hours ahead, comparing five models:
**seasonal naive, SARIMA, XGBoost, LSTM and PatchTST**. Data: Open Power System Data, 2015-2019.

Illyas Matloob (B01050018) · MSc Computer Science, Ulster University · Supervisor: Dr Anwar Haq

**Current stage:** data download, pre-processing, exploratory data analysis and feature engineering (notebooks 01-04).
The model notebooks and the web app will be added next.

---

## Folder structure

```
├── datasets/
│   ├── raw/                     # original OPSD files (downloaded by notebook 01) + small GB extract
│   └── processed/               # clean data, features, train / validation / test files
├── notebooks/
│   ├── 01_download_dataset.ipynb      # download the raw files
│   ├── 02_preprocessing.ipynb         # select GB columns, find and fill wrong values
│   ├── 03_eda.ipynb                   # exploratory data analysis
│   └── 04_feature_engineering.ipynb   # build 11 features, split train / validation / test
├── results/
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
3. Open each notebook file **in this order** and run it:

| Order | Notebook file | What it does |
|---|---|---|
| 1 | `01_download_dataset.ipynb` | Downloads the two OPSD files (about 365 MB) into `datasets/raw/`. Skipped if the files are already there |
| 2 | `02_preprocessing.ipynb` | Keeps GB load and temperature for 2015-2019, finds wrong values with three rules and fills them |
| 3 | `03_eda.ipynb` | Exploratory data analysis: daily, weekly and yearly patterns, holidays, temperature, autocorrelation |
| 4 | `04_feature_engineering.ipynb` | Builds the 11 features and splits the data: train 2015-2017, validation 2018, test 2019 |

**How to run one notebook:**

1. Click the notebook file to open it.
2. In the menu, click **Kernel → Restart Kernel and Run All Cells** (or **Run → Run All Cells**).
3. Wait until every cell has finished. A cell that is still running shows `[*]`; when it is done it shows a number, such as `[5]`.
4. Close the notebook and open the next one.

Each notebook saves its output, which the next notebook reads, so always keep this order.
The full raw files are not stored on GitHub because they are bigger than 100 MB, so **always run notebook 01 first**.

---

## 4. Problems and fixes

| Problem | Fix |
|---|---|
| `py` or `python` is not recognised (Windows) | Python is not on PATH. Reinstall Python 3.11 and tick "Add python.exe to PATH" |
| `jupyter` is not recognised | The environment is not active. Run the activate command from step 2 |
| `FileNotFoundError` in notebook 02 | Run notebook 01 first, it downloads the raw files |
| `FileNotFoundError` in notebook 03 or 04 | Run the notebooks in order. Each one needs the files from the one before |

---

*Academic prototype for an MSc research project. Not a tool for real grid operation.*
