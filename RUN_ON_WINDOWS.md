# Run the web app on a Windows computer

This guide shows how to download the project from GitHub and open the web app in your browser.
It starts with a Windows computer that has nothing installed.

You do not need to run the notebooks. All results and the trained model are already in the project.

**What you need**

- A computer with Windows 10 or Windows 11
- An internet connection (for the download and the install)
- About 1 GB of free disk space

**The steps in short**

| Step | What you do |
|---|---|
| 1 | Install Python 3.11 |
| 2 | Download the project from GitHub |
| 3 | Open PowerShell in the project folder |
| 4 | Install the packages (only the first time) |
| 5 | Start the web app |
| 6 | Use the web app |
| 7 | Stop the web app |

---

## Step 1. Install Python 3.11

1. Go to <https://www.python.org/downloads/windows/>.
2. Find **Python 3.11** and download the **Windows installer (64-bit)**.
3. Open the downloaded file.
4. On the first screen, tick the box **"Add python.exe to PATH"**. This is important.
5. Click **Install Now** and wait until it says the setup was successful.

**Check that it works.** Open **PowerShell** (click the Start menu, type `powershell`, press **Enter**) and type:

```powershell
py -3.11 --version
```

You should see `Python 3.11.x` (x can be any number).

---

## Step 2. Download the project from GitHub

The project is here:

<https://github.com/ilyasm883/gb-electricity-demand-forecasting>

If the page says "404" or "Not found", the repository is private. Sign in to GitHub with an account that has access, then open the link again.

Choose **one** of the two ways below.

### Way A. Download a ZIP file (easiest)

1. Open the link above in your browser.
2. Click the green **Code** button.
3. Click **Download ZIP**.
4. Open your **Downloads** folder. Right-click the ZIP file and click **Extract All**, then **Extract**.
5. You now have a folder named `gb-electricity-demand-forecasting-main`. This is the **project folder**.

### Way B. Use Git

Use this way only if Git is installed (<https://git-scm.com/download/win>).

Open PowerShell and type these lines, one at a time:

```powershell
cd $HOME\Documents
git clone https://github.com/ilyasm883/gb-electricity-demand-forecasting.git
```

If Git asks you to sign in, a browser window opens. Sign in to GitHub there.

You now have a folder named `gb-electricity-demand-forecasting` in **Documents**. This is the **project folder**.

---

## Step 3. Open PowerShell in the project folder

1. Open the project folder in File Explorer.
2. Check that you are in the right folder. You should see these inside it: `app`, `datasets`, `notebooks`, `results` and `README.md`.
   - If you only see one folder with the same name, open that one too.
3. Click the address bar at the top of File Explorer.
4. Type `powershell` and press **Enter**.

A blue window opens. It is already in the project folder.

---

## Step 4. Install the packages (only the first time)

Copy these lines into PowerShell, one at a time. Press **Enter** after each line and wait until it is finished.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r app\requirements.txt
```

What each line does:

| Line | What it does |
|---|---|
| `py -3.11 -m venv .venv` | Makes a private Python space for this project, in a folder named `.venv` |
| `.venv\Scripts\Activate.ps1` | Switches this private space on |
| `python -m pip install --upgrade pip` | Updates the tool that installs packages |
| `pip install -r app\requirements.txt` | Installs the five packages the web app needs |

When the second line works, the line in PowerShell starts with `(.venv)`.

**When to type `py` and when to type `python`**

| When | Type | Why |
|---|---|---|
| Before the `.venv` is on (only the first line) | `py -3.11` | `py` is the Python launcher of Windows. With `-3.11` it picks Python 3.11, even if other Python versions are installed |
| After the `.venv` is on (the line starts with `(.venv)`) | `python` | Now `python` always means the Python 3.11 of this project |

Do not type `py` after the `.venv` is on. It can pick the main Python of the computer, and then the packages are "not found".

**If `py` is not found**, type `python --version`. If it shows `Python 3.11.x`, use this as the first line instead:

```powershell
python -m venv .venv
```

Then go on with the second line as normal.

**If you see "running scripts is disabled on this system"** after the second line, type:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Type `Y` and press **Enter**. Then run `.venv\Scripts\Activate.ps1` again.

---

## Step 5. Start the web app

```powershell
streamlit run app\app.py
```

- The first time, Streamlit may ask for an email address. Just press **Enter** to skip it.
- If Windows Firewall asks a question, click **Allow**.
- Your browser opens the app at <http://localhost:8501>.
- If the browser does not open, copy the address `http://localhost:8501` into your browser yourself.

Keep the PowerShell window open while you use the app. If you close it, the app stops.

---

## Step 6. Use the web app

The app opens on the **Prediction** page.

To go to another page, click **"Menu: open another page"** on the left side and choose a page.

| Page | What you can do |
|---|---|
| **Prediction** | Choose a day in 2019. The XGBoost model makes a forecast for the 24 hours of that day and shows it next to the real demand. You can change the temperature or make the day a bank holiday, and see how the forecast changes |
| **Compare models** | Choose a day and see the forecasts of all five models, and the error of each model on that day |
| **Results** | Tables and charts for the four research questions. All the words are explained at the bottom of the page |
| **About** | Questions and answers about the research |

---

## Step 7. Stop the web app

1. Go back to the PowerShell window.
2. Press **Ctrl + C**.
3. Close the window.

---

## Next time

You do not need to install anything again. Open PowerShell in the project folder (step 3) and type only these two lines:

```powershell
.venv\Scripts\Activate.ps1
streamlit run app\app.py
```

---

## Problems and fixes

| Problem | Fix |
|---|---|
| `py` is not found | Type `python --version`. If it shows `Python 3.11.x`, use `python -m venv .venv` as the first line of step 4. If `python` is not found either, install Python 3.11 again and tick **"Add python.exe to PATH"** (step 1) |
| Packages are "not found" after the install | You typed `py` after the `.venv` was on. Use `python` instead (see step 4) |
| "running scripts is disabled on this system" | Type `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then `Y`, and try again (step 4) |
| `streamlit` is not found | The `.venv` is not on. Type `.venv\Scripts\Activate.ps1` and try again |
| `FileNotFoundError` when the app starts | PowerShell is in the wrong folder. It must be in the project folder, not inside the `app` folder (step 3) |
| `requirements.txt` is not found | Same as above: PowerShell is in the wrong folder (step 3) |
| "Port 8501 is already in use" | Another app is using this address. Type `streamlit run app\app.py --server.port 8502` and open <http://localhost:8502> |
| The install stops with an error about the Python version | Check that you installed Python **3.11** and typed `py -3.11` in step 4 |
| The page is empty or does not load | Wait a moment and press **F5** to load the page again |
