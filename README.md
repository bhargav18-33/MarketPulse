# Systematic Momentum Equity Strategy

## Strategy Documentation

---

## Executive Summary

This document describes a systematic, multi-factor momentum equity strategy applied to a universe of 900+ U.S. equities. The strategy combines five independent momentum and strength factors, a benchmark-relative regime filter, and an adaptive factor-weighting mechanism that re-evaluates factor efficacy on a rolling basis rather than relying on static weights fixed at design time.

Backtested performance over the evaluation period shows a 38.14% CAGR against a 19.48% CAGR for the QQQ benchmark, a Sharpe ratio of 1.62, and a downside capture ratio of 65.4%, indicating outperformance driven substantially by risk mitigation rather than elevated volatility (beta 0.99). Full methodology, parameters, and limitations are documented below.

- 📄 **[Portfolio Analysis Report](Results/Portfolio_report.pdf)**

- 📊 **[Trade Analysis Results](Results/USA_TOP_20_trade_analysis.csv)**

---

## 1. Architecture

The system is organized into three layers, each independently maintainable:

| Layer | Function |
|---|---|
| Data and Resampling | Loads daily closing price history from a local data store into an in-memory master table. Produces two independent resampling frequencies (weekly and a faster secondary cadence), each anchored to the most recent trading day in the analysis window. |
| Factor Library | A set of parameterized, stateless functions computing RSI, relative strength, rate of change, CAGR, price distance, robust z-scores, and streak counters. No function is hardcoded to a specific ticker, date, or universe size. |
| Screening Pipeline | Orchestrates the factor library into a complete run: benchmark regime determination, per-security factor computation, cross-sectional ranking, adaptive weight discovery, multi-stage filtering, and final candidate selection. |

---

## 2. Data Methodology

Price history (adjusted close) is sourced from a local, version-controlled data file rather than a live market data API. This design choice removes dependency on external rate limits and guarantees that any given run is fully reproducible.

Two resampling frequencies are derived from the same underlying daily series:

- **Weekly frequency.** Used for RSI, relative strength, and the benchmark regime determination.
- **Secondary (faster) frequency.** Used for rate of change, CAGR, and price-distance/streak measures.

Resampling is performed by index position, anchored at the analysis end date, rather than by calendar date. Sample dates are selected by counting backward a fixed number of trading days from the most recent observation. This ensures every security, and the benchmark, share an identical comparison calendar regardless of individual listing history or data gaps.

A benchmark-relative price series (security price divided by benchmark price) is constructed alongside the raw price series for each security, supporting the relative-strength and relative-RSI factors described below.

---

## 3. Factor Construction

Five independent factors are computed per security. Each factor blends multiple lookback periods rather than relying on a single arbitrary window.

**3.1 Relative Strength Index (RSI).** Multi-period Wilder RSI, computed on both the security's own price and its benchmark-relative price, combined via weighted average.

**3.2 Relative Strength versus Benchmark.** A momentum-ratio measure (smoothed price now divided by smoothed price N periods prior) computed for the security and divided by the identical ratio computed for the benchmark, across three lookback horizons.

**3.3 Rate of Change (ROC).** Percentage price change measured over two lookback windows on the secondary frequency.

**3.4 Compound Annual Growth Rate (CAGR).** Two lookback periods, of differing length, each annualized independently prior to blending. Annualizing before combination places windows of unequal length on a comparable scale.

**3.5 Price Distance and Persistence.** A weighted blend of exponential-moving-average distance measures on benchmark-relative price, combined with a consecutive-period "streak" counter measuring sustained trend persistence. Both are evaluated using median and median-absolute-deviation based statistics, in preference to mean and standard deviation, to reduce sensitivity to individual outlier observations.

Each factor additionally produces a binary signal indicating proximity to its own rolling historical peak, used both as a ranking adjustment and as an independent filter condition.

---

## 4. Ranking Methodology and Adaptive Weighting

Each factor is ranked cross-sectionally across the eligible universe. The five factor ranks are combined into a single composite rank via weighted summation.

**4.1 Base allocation.** Each factor is assigned a fixed 10% weight, accounting for 50% of total weight.

**4.2 Dynamic allocation.** The remaining 50% is allocated to the three best-performing factors, determined through the following walk-forward procedure:

1. The complete pipeline, including universe screening and ranking, is independently re-executed as of two historical reference dates: one month and two months prior to the current analysis date.
2. For each factor and each historical date, the top-ranked securities as of that date are identified, and their subsequent median price return through the current date is measured.
3. Factors are ranked by realized median forward return, independently for each historical window.
4. The two windows' factor rankings are combined, with 60% weight to the more recent one-month window and 40% weight to the two-month window.
5. The three highest-ranked factors receive additional weight of 20%, 17%, and 13% respectively, added to their fixed 10% base.

This mechanism allows factor weighting to respond to which factors have recently demonstrated predictive value, rather than relying exclusively on a fixed weighting scheme determined at design time.

---

## 5. Filtering Criteria

Following ranking, a sequential set of filters is applied to narrow the eligible universe:

- **Common filter.** Applied first, establishing the base eligible universe prior to any rank-dependent filtering.
- **RSI filter.** Threshold and trend-confirmation conditions on both raw and benchmark-blended RSI.
- **Rate of Change filter.** Dual-period upper bound on rate of change.
- **CAGR filter.** Requires CAGR trending above its own smoothed average, with an upper bound to exclude extreme outliers.
- **Distance and persistence filter.** Upper bounds on both price extension and consecutive trend duration.
- **Relative strength filter.** Requires smoothed relative strength to exceed a defined fraction of its own smoothed average.
- **Composite rank filter.** Each of the five ranking components must satisfy an individually configured rank threshold.

The final candidate list is the intersection of all filter conditions, ordered by composite rank.

---

## 6. Diagnostics and Auditability

Two diagnostic tools support full traceability of selection decisions:

- **Filter attribution report.** A complete record, for every security in the universe, of pass or fail status on each individual filter, together with the aggregate result and composite rank. Supports audit of any selection or exclusion decision.
- **Security-level diagnostic function.** An on-demand lookup providing, for a single security, each rank component measured against its threshold, and the pass or fail status of every individual filter.

---

## 7. Backtest Performance

| Metric | Strategy | Benchmark (QQQ) | Difference |
|---|---:|---:|---:|
| CAGR | 38.14% | 19.48% | +18.66% |
| Total Return | 1860.8% | 415.2% | +1445.6% |
| Annualized Volatility | 23.75% | n/a | n/a |
| Maximum Drawdown | -19.16% | -35.12% | +15.96% |
| Sharpe Ratio | 1.62 | n/a | n/a |
| Sortino Ratio | 2.21 | n/a | n/a |
| Calmar Ratio | 1.99 | n/a | n/a |
| Beta | 0.99 | 1.00 | -0.01 |
| Jensen's Alpha | 18.76% (p < 0.0001) | n/a | n/a |
| Information Ratio | 0.91 | n/a | n/a |
| Up Capture | 81.3% | 100.0% | -18.7% |
| Down Capture | 65.4% | 100.0% | -34.6% |

Results indicate outperformance attributable primarily to superior downside protection, evidenced by an asymmetric capture profile (81.3% upside capture against 65.4% downside capture), rather than to elevated portfolio risk relative to benchmark.

---

## 8. Implementation

**Data requirement.** A local file containing daily adjusted closing prices in wide format (date by ticker), including the benchmark series.

**Execution.**
```python
today = run_pipeline(end_date)
```

**Adaptive weighting** is executed by re-running the pipeline against two historical reference dates and deriving composite weights prior to the final ranking and filtering stage.

**Outputs.** A ranked candidate list and a complete filter attribution report, both exported to file for downstream review.

---

## 9. Parameters Reference

| Category | Parameters |
|---|---|
| Resampling | Weekly and secondary sampling intervals |
| RSI | Lookback periods (weekly, secondary, relative), blend weights, smoothing windows |
| Relative Strength | Lookback periods, blend weights, benchmark smoothing parameters |
| Rate of Change / CAGR | Lookback periods, blend weights, smoothing window |
| Distance / Persistence | Lookback periods, blend weights, smoothing span |
| Peak Proximity Signals | Rolling window lengths, threshold multipliers |
| Filter Thresholds | Per-factor filter bounds, composite rank cutoffs |

Full parameter values are maintained in the strategy configuration and are subject to periodic review.

---

## 10. Limitations and Risk Disclosures

The following limitations are disclosed in the interest of methodological transparency and should be considered when evaluating the results presented above.

**Overfitting risk.** Filter thresholds were refined iteratively during development with reference to their effect on candidate composition. In the absence of a strict, documented train and test partition, reported backtest performance may reflect partial in-sample fitting and should not be assumed to generalize without independent out-of-sample validation.

**Transaction costs.** Reported performance figures do not incorporate transaction costs, market impact, or slippage. Realized performance under live execution would be expected to be lower.

**Universe composition.** The extent to which the backtest universe reflects historical constituents, including securities subsequently delisted, has not been independently confirmed. A universe limited to currently listed securities would be expected to overstate historical performance.

**Computational scaling.** Runtime scales with universe size and is approximately tripled when adaptive weight discovery is enabled, owing to the requirement of two additional full historical pipeline executions.

**Numerical sensitivity.** Certain composite calculations, including weighted z-scores and blended CAGR, sum multiple sub-components. A single missing observation in any sub-component can invalidate the composite result for the affected observation. Adequate historical depth per security is required for all rolling-window calculations to be fully populated.

---

*This document describes a research methodology and backtested strategy. It does not constitute investment advice, and past performance is not indicative of future results.*
