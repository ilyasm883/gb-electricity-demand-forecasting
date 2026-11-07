# Multi-Horizon Electricity Demand Forecasting (COM748)

Hourly electricity demand forecasting for Great Britain, 1 to 24 hours ahead, comparing five models:
**seasonal naive, SARIMA, XGBoost, LSTM and PatchTST**. Data: Open Power System Data, 2015-2019.

See [ABOUT.md](ABOUT.md) for the dataset, research questions, research gap, models and methodology.

**Main result:** XGBoost is the most accurate model on the 2019 test year (MAE 1,080 MW, MAPE 3.3%, 45% better than the seasonal naive model).
See [RESEARCH_QA.md](RESEARCH_QA.md) for the research questions, method and all results.

---

## Folder structure

```
implementation/
├── datasets/
│   ├── raw/                     # gb_columns_raw.csv: the 3 original GB columns used (full OPSD files: notebook 01)
│   └── processed/               # clean data, features, train / validation / test files
├── notebooks/
│   ├── 01_download_dataset.ipynb      # download the raw files
│   ├── 02_preprocessing.ipynb         # select GB columns, find and fill wrong values
│   ├── 03_eda.ipynb                   # exploratory data analysis
│   ├── 04_feature_engineering.ipynb   # build 11 features, split train / validation / test
│   ├── 05_baselines.ipynb             # seasonal naive + SARIMA
│   ├── 06_xgboost.ipynb               # XGBoost (tuned on 2018), saves the model
│   ├── 07_deep_models.ipynb           # LSTM + PatchTST
│   ├── 08_evaluation.ipynb            # RQ1, RQ2: compare all models on 2019
│   └── 09_error_analysis.ipynb        # RQ3, RQ4: peaks, weekends, holidays, ablation
├── results/
│   ├── forecasts/               # 2019 forecasts of every model
│   ├── tables/                  # result tables (CSV)
│   ├── figures/                 # result figures (PNG)
│   └── models/                  # saved XGBoost model used by the dashboard
├── app/                         # Streamlit web app
│   ├── app.py                   # main file: page settings and sidebar menu
│   ├── data_loader.py           # reads the data, the saved model and the results
│   ├── predictor.py             # live 24-hour forecast with XGBoost
│   ├── tables.py                # tables with the best values in bold
│   ├── page_prediction.py       # page 1: Prediction
│   ├── page_compare.py          # page 2: Compare models
│   ├── page_results.py          # page 3: Results (RQ1-RQ4 tables and charts)
│   ├── page_about.py            # page 4: About the research
│   └── requirements.txt         # packages for the web app only
├── ABOUT.md                     # dataset, research questions, research gap, models, methodology
├── RESEARCH_QA.md               # questions and answers about the research
├── FEATURES.md                  # dataset, features and pipeline
├── requirements.txt             # packages for the whole project (exact versions)
└── README.md
```

---

## 1. What you need

- **Python 3.11** (tested with 3.11.11). Download it from <https://www.python.org/downloads/>.
  On Windows, tick **"Add python.exe to PATH"** during the installation.
- About **3 GB** of free disk space (PyTorch is large) and an internet connection.
- No GPU is needed. A GPU only makes the LSTM and PatchTST notebooks faster.

Open a terminal **inside the `implementation` folder**:
- **Windows:** open the folder in File Explorer, click the address bar, type `powershell` and press Enter.
- **Mac / Linux:** open Terminal and use `cd` to go to the folder.

> The folder path contains spaces, so always put it in quotes when you type it, for example
> `cd "C:\Users\me\Desktop\finalthesis sep 2026\Ilyas\implementation"`.

---

## 2. Set up the experiments (notebooks)

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

### Optional: NVIDIA GPU on Windows

`pip install -r requirements.txt` installs the CPU version of PyTorch on Windows. If you have an NVIDIA GPU, install the CUDA version
of PyTorch 2.14.1 with the command from <https://pytorch.org/get-started/locally/>. NeuralForecast uses the GPU automatically.

---

## 3. Run the experiments

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
| (optional) | `01_download_dataset.ipynb` | Downloads the two full OPSD files and saves the three GB columns in `gb_columns_raw.csv` |
| 1 | `02_preprocessing.ipynb` | Keeps GB load and temperature for 2015-2019, finds wrong values and fills them |
| 2 | `03_eda.ipynb` | Exploratory data analysis |
| 3 | `04_feature_engineering.ipynb` | Builds the 11 features and splits train / validation / test |
| 4 | `05_baselines.ipynb` | Seasonal naive and SARIMA |
| 5 | `06_xgboost.ipynb` | XGBoost, tuned on 2018, and saves the model for the web app |
| 6 | `07_deep_models.ipynb` | LSTM and PatchTST (faster with a GPU) |
| 7 | `08_evaluation.ipynb` | RQ1 and RQ2: compares all models on 2019 |
| 8 | `09_error_analysis.ipynb` | RQ3 and RQ4: peaks, weekends, holidays and feature ablation |

**How to run one notebook:**

1. Click the notebook file to open it.
2. In the menu, click **Kernel → Restart Kernel and Run All Cells** (or **Run → Run All Cells**).
3. Wait until every cell has finished. A cell that is still running shows `[*]`; when it is done it shows a number, such as `[5]`.
4. Close the notebook and open the next one.

Each notebook saves its output, which the next notebook reads, so always keep this order.
All results are already saved in `results/`, so you can also skip the notebooks and go straight to the web app.

---

## 4. Run the web app (dashboard)

From the `implementation` folder, with the environment active:

```bash
streamlit run app/app.py
```

On Windows you can also write `streamlit run app\app.py`. The app opens at <http://localhost:8501>. Stop it with **Ctrl + C**.

> Only want the web app? It needs far fewer packages. Make an environment as in step 2, but install
> `pip install -r app/requirements.txt` instead (no PyTorch needed).

The app has four pages (menu on the left):

| Page | What you can do |
|---|---|
| **Prediction** | Pick a day in 2019. The saved XGBoost model forecasts the 24 hours of that day live, next to the real demand. Change the temperature or mark the day as a bank holiday to see how the forecast reacts |
| **Compare models** | Pick a day and see the saved forecasts of all five models, with each model's error on that day |
| **Results** | Tables and charts for all four research questions (RQ1-RQ4), with the best results in bold |
| **About** | The research explained: problem, research gap, data, features, models, results, limitations and future work |

### Put the web app online (free)

1. Upload the `implementation` folder to a GitHub repository (the `.gitignore` leaves out the large raw data).
2. Go to <https://share.streamlit.io>, sign in with GitHub and click **Create app**.
3. Choose the repository, set the main file to `app/app.py` and Python version **3.11**, then click **Deploy**.

Streamlit Cloud installs `app/requirements.txt` automatically.

---

## 5. Problems and fixes

| Problem | Fix |
|---|---|
| `py` or `python` is not recognised (Windows) | Python is not on PATH. Reinstall Python 3.11 and tick "Add python.exe to PATH" |
| `streamlit` or `jupyter` is not recognised | The environment is not active. Run the activate command from step 2 |
| `FileNotFoundError` in the web app | Start it from the `implementation` folder, not from inside `app` |
| `FileNotFoundError` in a notebook | Run the notebooks in order, starting from 02. Each one needs the files from the one before |
| A notebook with XGBoost and PyTorch freezes | Already handled in notebook 09 (`OMP_NUM_THREADS=1`). Restart the kernel and run again |
| Deep model results differ slightly from the saved ones | Normal. GPU training is not exactly the same every time. Seeds are fixed (XGBoost 42, LSTM and PatchTST 1) |

---

## 6. Run the application on a Windows computer (step by step)

These steps start from a Windows computer with nothing installed and end with the web app open in the browser.
They only install what the web app needs. All results are already saved in the project.

**Step 1. Install Python 3.11**

1. Go to <https://www.python.org/downloads/windows/> and download the **Windows installer (64-bit)** for **Python 3.11**.
2. Run it. On the first screen, tick **"Add python.exe to PATH"**, then click **Install Now**.
3. Check it worked: open **PowerShell** (Start menu → type `powershell` → Enter) and type:

   ```powershell
   py -3.11 --version
   ```

   It should show `Python 3.11.x`.

**Step 2. Get the project**

- From GitHub: click the green **Code** button → **Download ZIP**, then right-click the ZIP → **Extract All**.
- Or copy the `implementation` folder from a USB stick or OneDrive.

**Step 3. Open PowerShell in the project folder**

Open the `implementation` folder in File Explorer (the one that contains `app`, `results` and `README.md`).
Click the address bar at the top, type `powershell` and press **Enter**. A blue window opens in that folder.

**Step 4. Create the environment and install the packages (only the first time)**

Copy these lines into PowerShell one by one and press **Enter** after each:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r app\requirements.txt
```

- If you see *"running scripts is disabled on this system"* after the second line, run
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, type `Y`, and run `.venv\Scripts\Activate.ps1` again.
- When the environment is active, the line starts with `(.venv)`.

**Step 5. Start the application**

```powershell
streamlit run app\app.py
```

- The first time, Streamlit may ask for an email address. Just press **Enter** to skip.
- If Windows Firewall asks for permission, click **Allow**.
- The app opens in your browser at <http://localhost:8501>. If it does not open, copy that address into the browser.

**Step 6. Use the application**

Use the menu on the left to switch between **Prediction**, **Compare models**, **Results** and **About** (see the table in section 4).

**Step 7. Stop the application**

Go back to the PowerShell window and press **Ctrl + C**. You can then close the window.

**Next time you want to run it**

Open PowerShell in the `implementation` folder again (step 3), then run only:

```powershell
.venv\Scripts\Activate.ps1
streamlit run app\app.py
```

> Want to run the notebooks (experiments) on Windows as well? In step 4, use `pip install -r requirements.txt`
> instead of `app\requirements.txt` (this also installs PyTorch), then follow sections 3 and 4.

---

*Academic prototype for an MSc research project. Not a tool for real grid operation.*
