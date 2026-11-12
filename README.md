# Multi-Horizon Electricity Demand Forecasting (COM748)

This project predicts how much electricity Great Britain will use in the next 1 to 24 hours.
It compares five models: **seasonal naive, SARIMA, XGBoost, LSTM and PatchTST**.
The data comes from Open Power System Data, for the years 2015 to 2019.

- [ABOUT.md](ABOUT.md): the data, the research questions, the research gap, why we chose the models, and how we did it.
- [RESEARCH_QA.md](RESEARCH_QA.md): questions and answers about the research, including all results.

**Main result:** XGBoost makes the best forecasts for 2019. On average it is 1,080 MW (3.3%) away from the real value. This is 45% better than the simplest model.

---

## Folders and files

```
implementation/
├── datasets/
│   ├── raw/                     # gb_columns_raw.csv: the 3 original columns we use, and the official forecast
│   └── processed/               # clean data, features, and the train / validation / test files
├── notebooks/
│   ├── 01_download_dataset.ipynb      # download the original data (optional)
│   ├── 02_preprocessing.ipynb         # find and fix wrong values
│   ├── 03_eda.ipynb                   # look at the data and its patterns
│   ├── 04_feature_engineering.ipynb   # make 11 features and split the data by year
│   ├── 05_baselines.ipynb             # seasonal naive and SARIMA models
│   ├── 06_xgboost.ipynb               # XGBoost model, and save it for the web app
│   ├── 07_deep_models.ipynb           # LSTM and PatchTST models
│   ├── 08_evaluation.ipynb            # compare all models (RQ1, RQ2)
│   ├── 09_error_analysis.ipynb        # where the models go wrong, and which features help (RQ3, RQ4)
│   └── 10_extra_checks.ipynb          # compare with the official forecast, and train the deep models with 5 seeds
├── results/
│   ├── forecasts/               # the 2019 forecasts of every model
│   ├── tables/                  # result tables (CSV)
│   ├── figures/                 # charts (PNG)
│   └── models/                  # the saved XGBoost model used by the web app
├── app/                         # the web app (made with Streamlit)
│   ├── app.py                   # main file: page settings and the menu
│   ├── data_loader.py           # reads the data, the model and the results
│   ├── predictor.py             # makes a new 24-hour forecast with XGBoost
│   ├── tables.py                # makes tables with the best values in bold
│   ├── page_prediction.py       # page 1: Prediction
│   ├── page_compare.py          # page 2: Compare models
│   ├── page_results.py          # page 3: Results
│   ├── page_about.py            # page 4: About
│   └── requirements.txt         # packages for the web app only
├── ABOUT.md                     # about the research
├── RESEARCH_QA.md               # questions and answers about the research
├── FEATURES.md                  # the data and the features in detail
├── requirements.txt             # packages for the whole project
└── README.md
```

---

## 1. What you need

- **Python 3.11.** Download it from <https://www.python.org/downloads/>.
  On Windows, tick **"Add python.exe to PATH"** when you install it.
- About **3 GB** of free space on your computer, and internet.
- You do **not** need a GPU (graphics card). A GPU only makes notebooks 07 and 09 faster.

Open a terminal **in the `implementation` folder**:
- **Windows:** open the folder in File Explorer, click the address bar at the top, type `powershell` and press Enter.
- **Mac / Linux:** open Terminal and go to the folder with `cd`.

> If the folder path has spaces, put it in quotes, for example `cd "C:\Users\me\Desktop\my project"`.

---

## 2. Install the packages

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell says *"running scripts is disabled on this system"*, run this line once, then run the second line again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

(If you use Command Prompt instead of PowerShell, the second line is `.venv\Scripts\activate.bat`.)

### Mac / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The first line makes a separate space for this project's packages (called `.venv`). The second line turns it on.
When it is on, the line in the terminal starts with `(.venv)`. Turn it on again every time you open a new terminal.

### Optional: NVIDIA graphics card on Windows

On Windows, the steps above install the normal (CPU) version of PyTorch. If you have an NVIDIA graphics card, you can install the
faster GPU version of PyTorch 2.14.1 with the command from <https://pytorch.org/get-started/locally/>. The notebooks then use it automatically.

---

## 3. Run the notebooks

1. Start Jupyter (the `.venv` must be on):

   ```bash
   jupyter notebook
   ```

2. Jupyter opens in your web browser. Click the **`notebooks`** folder.
3. Open the notebooks **in this order** and run each one.

**Start with notebook 02.** The data it needs (`datasets/raw/gb_columns_raw.csv`) is already in the project.
Notebook 01 is only needed if you want to download the original data again (about 365 MB).

| Order | Notebook | What it does |
|---|---|---|
| (optional) | `01_download_dataset.ipynb` | Downloads the two original data files and saves the 3 columns we use |
| 1 | `02_preprocessing.ipynb` | Keeps the data for 2015-2019, and finds and fixes wrong values |
| 2 | `03_eda.ipynb` | Looks at the data: patterns by hour, day, season, holiday and temperature |
| 3 | `04_feature_engineering.ipynb` | Makes the 11 features and splits the data into train, validation and test |
| 4 | `05_baselines.ipynb` | Seasonal naive and SARIMA models |
| 5 | `06_xgboost.ipynb` | XGBoost model. Saves the model for the web app |
| 6 | `07_deep_models.ipynb` | LSTM and PatchTST models (faster with a GPU) |
| 7 | `08_evaluation.ipynb` | Compares all models on 2019 (RQ1 and RQ2) |
| 8 | `09_error_analysis.ipynb` | Finds where the models make mistakes and which features help (RQ3 and RQ4) |
| 9 | `10_extra_checks.ipynb` | Compares the models with the official forecast, and trains LSTM and PatchTST 5 times with different seeds (faster with a GPU) |

**How to run a notebook:**

1. Click the notebook to open it.
2. In the menu, click **Kernel → Restart Kernel and Run All Cells** (or **Run → Run All Cells**).
3. Wait until all cells are finished. A cell that is still running shows `[*]`. A finished cell shows a number, like `[5]`.
4. Close the notebook and open the next one.

Each notebook saves files that the next notebook needs, so always keep this order.
All results are already saved in `results/`, so you can also skip the notebooks and go straight to the web app.

---

## 4. Run the web app

In the `implementation` folder, with the `.venv` on:

```bash
streamlit run app/app.py
```

On Windows you can also type `streamlit run app\app.py`. The app opens in your browser at <http://localhost:8501>.
To stop it, press **Ctrl + C** in the terminal.

> Only want the web app? Install fewer packages: follow step 2, but use `pip install -r app/requirements.txt`.

The app has four pages. Use the menu on the left:

| Page | What you can do |
|---|---|
| **Prediction** | Choose a day in 2019, one of the latest days up to yesterday, or a future day (today and the next 6 days). XGBoost makes a forecast for the 24 hours of that day, next to the real values. You can change the temperature or make the day a bank holiday, and see how the forecast changes |
| **Compare models** | Choose a day and see the forecasts of all five models, and the error of each model on that day |
| **Results** | Tables and charts for the four research questions. The best results are in bold |
| **About** | Questions and answers about the research |

### How the real demand after 2019 is collected

The saved data of this project stops on 31 December 2019. The **Prediction** page can also forecast the latest days, up to yesterday.
It can also forecast future days: today and the next 6 days.
For these days the app downloads the data from the internet when you choose **Latest and future days (live data)**.

| What | Where it comes from | How |
|---|---|---|
| Real demand | **Elexon**, the official data service of the GB electricity market. Dataset: Actual Total Load. Address: `https://data.elexon.co.uk/bmrs/api/v1/demand/actual/total` | The app asks for the last 42 days, ending yesterday. It is free and needs no account. The two half-hour values of each hour are averaged into one hourly value |
| Temperature | **Open-Meteo**, a free weather data service | Hourly temperature, average of eight big cities (London, Birmingham, Manchester, Leeds, Glasgow, Bristol, Newcastle, Cardiff) |
| Bank holidays | Python package `holidays` (England) | The same as in notebook 04 |

Cleaning of the live demand:

- Values that are clearly wrong are removed (below 12,000 MW, or a one-hour spike of more than 5,000 MW, the same spike rule as in notebook 02).
- Missing hours are filled with a straight line between the hours around them. The page says how many hours of the chosen day were filled.

Future days (today and the next 6 days):

- There is no real demand for these days yet. The page shows **only the forecast**: no actual line and no error.
- The temperature is the weather forecast from Open-Meteo for the same eight cities.
- For today, XGBoost starts from the real demand up to yesterday. For a later day, it first forecasts the days in between and uses these forecasts in place of the real demand. So the further ahead the day, the less exact the forecast.

Important:

- The live days are **not** part of the tested results. All results in this project are for the test year 2019.
- XGBoost was trained on 2015-2017 and is not trained again, so the error on the latest days is usually bigger than in 2019.
- Only the last 42 days are downloaded and nothing is saved in the project. Without internet, only the 2019 option works.
- The code is in `app/live_data.py`.

### Put the web app online (free)

1. Upload the `implementation` folder to GitHub. (The large original data files are left out on purpose.)
2. Go to <https://share.streamlit.io>, sign in with GitHub and click **Create app**.
3. Choose the repository. Set the main file to `app/app.py` and Python to **3.11**. Click **Deploy**.

Streamlit installs the packages in `app/requirements.txt` by itself.

---

## 5. Problems and fixes

| Problem | Fix |
|---|---|
| `py` or `python` is not found (Windows) | Python is not on PATH. Install Python 3.11 again and tick "Add python.exe to PATH" |
| `streamlit` or `jupyter` is not found | The `.venv` is not on. Run the second line of step 2 again |
| `FileNotFoundError` in the web app | Start the app from the `implementation` folder, not from inside the `app` folder |
| `FileNotFoundError` in a notebook | Run the notebooks in order, starting with 02. Each one needs files from the one before |
| A notebook with XGBoost and PyTorch stops and does not finish | This is already fixed in notebook 09 (`OMP_NUM_THREADS=1`). Restart the kernel and run it again |
| Deep learning results are a little different from the saved ones | This is normal. Training on a GPU is not exactly the same every time. The random seeds are fixed (XGBoost 42, LSTM and PatchTST 1) |

---

## 6. Run the web app on a Windows computer (step by step)

These steps start with a Windows computer that has nothing installed. At the end, the web app is open in your browser.
You only install what the web app needs. All results are already in the project.

**Step 1. Install Python 3.11**

1. Go to <https://www.python.org/downloads/windows/> and download the **Windows installer (64-bit)** for **Python 3.11**.
2. Open it. On the first screen, tick **"Add python.exe to PATH"**, then click **Install Now**.
3. Check that it works: open **PowerShell** (Start menu → type `powershell` → Enter) and type:

   ```powershell
   py -3.11 --version
   ```

   You should see `Python 3.11.x`.

**Step 2. Get the project**

- From GitHub: click the green **Code** button → **Download ZIP**. Then right-click the ZIP file → **Extract All**.
- Or copy the `implementation` folder from a USB stick or OneDrive.

**Step 3. Open PowerShell in the project folder**

Open the `implementation` folder in File Explorer (the folder with `app`, `results` and `README.md` in it).
Click the address bar at the top, type `powershell` and press **Enter**. A blue window opens in that folder.

**Step 4. Install the packages (only the first time)**

Copy these lines into PowerShell, one at a time, and press **Enter** after each one:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r app\requirements.txt
```

- If you see *"running scripts is disabled on this system"* after the second line, type
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then `Y`, and run `.venv\Scripts\Activate.ps1` again.
- When it works, the line starts with `(.venv)`.

**Step 5. Start the web app**

```powershell
streamlit run app\app.py
```

- The first time, Streamlit may ask for an email address. Just press **Enter** to skip.
- If Windows Firewall asks, click **Allow**.
- The app opens in your browser at <http://localhost:8501>. If it does not open, copy this address into your browser.

**Step 6. Use the web app**

Use the menu on the left to open **Prediction**, **Compare models**, **Results** or **About** (see section 4).

**Step 7. Stop the web app**

Go back to the PowerShell window and press **Ctrl + C**. Then you can close the window.

**Next time**

Open PowerShell in the `implementation` folder again (step 3) and type only:

```powershell
.venv\Scripts\Activate.ps1
streamlit run app\app.py
```

> Do you also want to run the notebooks on Windows? In step 4, type `pip install -r requirements.txt`
> instead of `app\requirements.txt` (this also installs PyTorch). Then follow sections 3 and 4.

---

*A student research project. Not for real use by electricity companies.*
