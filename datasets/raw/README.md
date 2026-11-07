# Raw data

**`gb_columns_raw.csv`** is the raw data used by the project. It has the three original columns from Open Power System Data,
with the values unchanged. **Notebook 02 starts from this file.**

| Column | File it comes from |
|---|---|
| `utc_timestamp` | both files |
| `GB_GBN_load_actual_entsoe_transparency` | time series file (Great Britain load, MW) |
| `GB_temperature` | weather file (temperature, °C) |

It covers 31 Dec 2014 to 30 Sep 2020 (the time series file). Temperature is empty after 2019 because the weather file ends there.

## Full original files (optional)

Notebook `01_download_dataset.ipynb` downloads the two full files into this folder and makes `gb_columns_raw.csv` from them:

| File | Size | Source |
|---|---|---|
| `time_series_60min_singleindex.csv` | 130 MB | OPSD Time Series, version 2020-10-06 |
| `weather_data.csv` | 234 MB | OPSD Weather Data, version 2020-09-16 |

They are bigger than GitHub's 100 MB limit, so they are not stored in the repository.
