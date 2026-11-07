# Raw data

**`gb_columns_raw.csv`** is the data this project starts from. **Notebook 02 reads this file.**
It has the 3 original columns we need from Open Power System Data. The values are not changed.

| Column | Where it comes from |
|---|---|
| `utc_timestamp` | the date and hour (UTC) |
| `GB_GBN_load_actual_entsoe_transparency` | how much electricity Great Britain used (MW), from the time series file |
| `GB_temperature` | the temperature in Great Britain (°C), from the weather file |

It goes from 31 December 2014 to 30 September 2020. The temperature is empty after 2019, because the weather file ends there.

## The full original files (optional)

Notebook `01_download_dataset.ipynb` downloads the two full files into this folder, and makes `gb_columns_raw.csv` from them:

| File | Size | Source |
|---|---|---|
| `time_series_60min_singleindex.csv` | 130 MB | OPSD Time Series, version 2020-10-06 |
| `weather_data.csv` | 234 MB | OPSD Weather Data, version 2020-09-16 |

These files are too big for GitHub (the limit is 100 MB), so they are not in the project. You only need them if you want to check where the data comes from.
