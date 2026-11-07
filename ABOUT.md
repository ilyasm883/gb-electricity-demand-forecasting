# About this project

**Multi-Horizon Electricity Demand Forecasting Using Classical Models and Deep Temporal Networks**

This project predicts how much electricity Great Britain will use in each of the **next 1 to 24 hours**.
It tests five different models on the same data, in the same way, and compares them.
The goal is not to make a new model. The goal is to find out **when a complex model is really better than a simple one**.

The numbers in square brackets, like [6], are sources. They are the same as in the research report and are listed at the end.

---

## Dataset

The data comes from **Open Power System Data (OPSD)**, a free website with energy data [19], [20].

| Dataset | Column we use | What it means |
|---|---|---|
| Time series, version 2020-10-06 [19] | `GB_GBN_load_actual_entsoe_transparency` | How much electricity Great Britain used in each hour, in MW (megawatts) |
| Weather data, version 2020-09-16 [20] | `GB_temperature` | The air temperature in Great Britain in each hour, in °C. Places where more people live count more |

- **Years used:** 2015 to 2019. That is 43,824 hours.
- **Why not 2020?** In 2020, COVID-19 lockdowns changed how people used electricity [3], and normal models did not work well [4]. We want to test normal years.
- **How the data is split:** the models learn from 2015-2017 (training), we choose their settings with 2018 (validation), and we test them on 2019 (test). We never mix the years.

### How we cleaned the data

Only 6 hours had no value. But some values were clearly wrong. We used three simple rules to find them:

1. **Too low:** below 10,000 MW. Great Britain never uses this little electricity.
2. **Sudden jump:** one hour is more than 5,000 MW different from both the hour before and the hour after.
3. **Block of low values:** below 65% of the normal value for that hour. "Normal" is the average of the same hour last week and next week. We skip bank holidays and Christmas to New Year, because demand is really low on those days.

We filled each missing or wrong hour:
- If the gap is 3 hours or less, we draw a straight line between the hour before and the hour after.
- If the gap is longer, we use the value from the same hour one week earlier.

In total we filled **115 hours (0.26%)** and marked each one. After cleaning, the data has **no missing and no wrong values**.

### Features (the information the models use)

Electricity use follows the hour of the day, the day of the week and the season. Temperature and holidays also change it a lot [1].
So we give the models 11 pieces of information:

| Group | Features | Why |
|---|---|---|
| Past use | `lag_1`, `lag_24`, `lag_168`, `rolling_mean_24`, `rolling_mean_168` | Use in the last hour, at the same hour yesterday and at the same hour last week, plus the average of the last day and last week |
| Calendar | `hour`, `day_of_week`, `month`, `is_weekend`, `is_holiday` | Use is different at night and in the day, at weekends, in winter and summer, and on bank holidays |
| Weather | `temperature` | People use more electricity when it is cold |

---

## Research questions

| | Question |
|---|---|
| **RQ1** | Which model gives the most accurate forecasts? |
| **RQ2** | How much does the accuracy of each model drop when it forecasts 24 hours ahead instead of 1 hour ahead? |
| **RQ3** | When do the models make their biggest mistakes? Is it at peak hours, at weekends or on public holidays? |
| **RQ4** | Do temperature and calendar information make the forecasts more accurate? |

---

## Research gap (what other studies are missing)

| Gap | The problem | What this project does | Question |
|---|---|---|---|
| **1. No strong simple models** | Many papers test new deep learning models, but they do not always compare them with simple, strong models [7], [8] | We include a very simple model and a strong tree model, and compare every model with them | RQ1 |
| **2. Only one average error** | Many papers give one error number for everything. You cannot see if a model is worse further ahead or on special days | We show the error for every hour ahead (1 to 24) and for peak hours, weekends and holidays | RQ2, RQ3 |
| **3. Inputs not tested fairly** | Papers do not often check, in the same way for every model, how much temperature helps | We train the models with and without temperature and calendar information | RQ4 |

---

## Why we chose these models

We chose each model because of what other studies found (see the literature review in the report).
Together they go from the simplest to the most complex: statistics, machine learning and deep learning.

| Model | What other studies found | Why we use it |
|---|---|---|
| **Seasonal naive** | Experts say this is the simplest test every new model must pass [9]. Electricity use repeats every day and week, so even this simple idea works quite well | It just copies the value from the same hour last week. It needs no training. Every other model must be better than this one |
| **SARIMA** | A well-known statistics model. It is easy to explain and can set itself up automatically [9]. In a big forecasting competition (M4), statistics models did very well and most machine learning models did not [6]. Many companies still use them [5] | It is the classic statistics model. It can only learn one repeating pattern and is slow on long data, and we want to see how much this matters |
| **XGBoost** | A "tree" model: many small decision trees, each one fixing the mistakes of the ones before. In another big competition (M5), most of the best solutions used this kind of model [10]. On data in tables, tree models are often better than deep learning [11] | It is the strongest model that is not deep learning. Deep learning models must beat it to show they are worth it |
| **LSTM** | A deep learning model that remembers past values. It is one of the most used deep models for electricity forecasting and did well on open electricity data [12]. But its results depend a lot on how it is set up [13] | It is our memory-based deep learning model. It gets the same calendar and temperature information as XGBoost, so the comparison is fair |
| **PatchTST** | A "transformer" model. Transformers look at all past values at once to find patterns [15], [16]. A study found that a very simple model often beat them [7]. PatchTST cuts the data into short pieces ("patches") and did better than older transformers and that simple model [17] | It is our transformer model. We want to see if its good results also work for electricity in Great Britain |

**Models we looked at but did not use:**

| Model | Why not |
|---|---|
| N-BEATS [14] | Good results, but we kept the number of models small. It is a good idea for future work |
| Temporal Fusion Transformer [15], Informer [16] | Older transformers. PatchTST did better than them in its study [17] |
| LightGBM [10] | The same kind of tree model as XGBoost, so one is enough |

---

## Methodology (how we did it)

1. **Prepare the data:** take the electricity use and temperature for 2015-2019 [19], [20], then find and fix wrong values.
2. **Explore the data:** look at the patterns by hour, day, season, holiday and temperature. This tells us which features to use.
3. **Make the features:** build 11 features. They only use information we would already know at the time of the forecast. This way the models never "see the future", which is a common mistake [18].
4. **Train and tune:** the models learn from 2015-2017. We choose their settings using 2018 only.
5. **Test:** for every day of 2019, each model predicts the next 24 hours, using only the data known until that moment. We use the test year only once [18].
6. **Compare:** we measure the errors (MAE, RMSE, MAPE) [9] and compare each model with the simplest one. A statistics test (Diebold-Mariano) checks if a difference is real or just luck [8]. We also look at errors by hours ahead, peak hours, weekends and holidays.
7. **Test the features:** we train XGBoost and the LSTM with and without calendar and temperature information, to see how much they help.

This follows the advice of experts: open data, a full year for testing, splitting the data by time, a simple model to compare with, and a statistics test [8], [18].
All models use the same free tools (StatsForecast, MLForecast and NeuralForecast), so every model is trained and tested the same way.

---

## References

[1] T. Hong, P. Pinson, Y. Wang, R. Weron, D. Yang, and H. Zareipour, "Energy forecasting: A review and outlook," *IEEE Open Access J. Power Energy*, vol. 7, pp. 376-388, 2020, doi: 10.1109/OAJPE.2020.3029979.

[3] A. Bahmanyar, A. Estebsari, and D. Ernst, "The impact of different COVID-19 containment measures on electricity consumption in Europe," *Energy Res. Soc. Sci.*, vol. 68, Art. no. 101683, 2020, doi: 10.1016/j.erss.2020.101683.

[4] D. Obst, J. de Vilmarest, and Y. Goude, "Adaptive methods for short-term electricity load forecasting during COVID-19 lockdown in France," *IEEE Trans. Power Syst.*, vol. 36, pp. 4754-4763, 2021.

[5] F. Petropoulos et al., "Forecasting: Theory and practice," *Int. J. Forecast.*, vol. 38, no. 3, pp. 705-871, 2022, doi: 10.1016/j.ijforecast.2021.11.001.

[6] S. Makridakis, E. Spiliotis, and V. Assimakopoulos, "The M4 competition: 100,000 time series and 61 forecasting methods," *Int. J. Forecast.*, vol. 36, no. 1, pp. 54-74, 2020, doi: 10.1016/j.ijforecast.2019.04.014.

[7] A. Zeng, M. Chen, L. Zhang, and Q. Xu, "Are transformers effective for time series forecasting?," in *Proc. AAAI Conf. Artif. Intell.*, vol. 37, no. 9, 2023, pp. 11121-11128, doi: 10.1609/aaai.v37i9.26317.

[8] J. Lago, G. Marcjasz, B. De Schutter, and R. Weron, "Forecasting day-ahead electricity prices: A review of state-of-the-art algorithms, best practices and an open-access benchmark," *Appl. Energy*, vol. 293, Art. no. 116983, 2021, doi: 10.1016/j.apenergy.2021.116983.

[9] R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed. Melbourne, Australia: OTexts, 2021. [Online]. Available: https://otexts.com/fpp3/

[10] S. Makridakis, E. Spiliotis, and V. Assimakopoulos, "M5 accuracy competition: Results, findings, and conclusions," *Int. J. Forecast.*, vol. 38, no. 4, pp. 1346-1364, 2022, doi: 10.1016/j.ijforecast.2021.11.013.

[11] L. Grinsztajn, E. Oyallon, and G. Varoquaux, "Why do tree-based models still outperform deep learning on typical tabular data?," in *Adv. Neural Inf. Process. Syst. (NeurIPS), Datasets and Benchmarks Track*, vol. 35, 2022.

[12] J. Lin, J. Ma, J. Zhu, and Y. Cui, "Short-term load forecasting based on LSTM networks considering attention mechanism," *Int. J. Electr. Power Energy Syst.*, vol. 137, Art. no. 107818, 2022, doi: 10.1016/j.ijepes.2021.107818.

[13] H. Hewamalage, C. Bergmeir, and K. Bandara, "Recurrent neural networks for time series forecasting: Current status and future directions," *Int. J. Forecast.*, vol. 37, no. 1, pp. 388-427, 2021.

[14] B. N. Oreshkin, D. Carpov, N. Chapados, and Y. Bengio, "N-BEATS: Neural basis expansion analysis for interpretable time series forecasting," in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2020.

[15] B. Lim, S. Ö. Arık, N. Loeff, and T. Pfister, "Temporal fusion transformers for interpretable multi-horizon time series forecasting," *Int. J. Forecast.*, vol. 37, no. 4, pp. 1748-1764, 2021, doi: 10.1016/j.ijforecast.2021.03.012.

[16] H. Zhou et al., "Informer: Beyond efficient transformer for long sequence time-series forecasting," in *Proc. AAAI Conf. Artif. Intell.*, vol. 35, no. 12, 2021, pp. 11106-11115, doi: 10.1609/aaai.v35i12.17325.

[17] Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, "A time series is worth 64 words: Long-term forecasting with transformers," in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2023.

[18] H. Hewamalage, K. Ackermann, and C. Bergmeir, "Forecast evaluation for data scientists: Common pitfalls and best practices," *Data Min. Knowl. Discov.*, vol. 37, no. 2, pp. 788-832, 2023.

[19] Open Power System Data, "Data package time series," Version 2020-10-06, 2020. [Online]. Available: https://doi.org/10.25832/time_series/2020-10-06

[20] Open Power System Data, "Data package weather data," Version 2020-09-16, 2020. [Online]. Available: https://doi.org/10.25832/weather_data/2020-09-16

---

*A student research project. Not for real use by electricity companies.*
