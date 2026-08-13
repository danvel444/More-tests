# Lottery Strategy Simulation -- Results


## Lotto 6/49

### Official odds by tier

| tier              |   probability |       one_in | prize_type   |   amount |
|:------------------|--------------:|-------------:|:-------------|---------:|
| Match 6 (Jackpot) |           0.0 | 13,983,816.0 | jackpot      |    nan   |
| Match 5 + Bonus   |           0.0 |  2,330,636.0 | parimutuel   |    nan   |
| Match 5           |           0.0 |     55,491.3 | parimutuel   |    nan   |
| Match 4           |           0.0 |      1,032.4 | fixed        |     25.0 |
| Match 3           |           0.0 |         56.7 | fixed        |     10.0 |
| Match 2 + Bonus   |           0.0 |         81.2 | fixed        |      5.0 |

### A. Fixed numbers vs. Quick Pick -- empirical hit rate per tier

(n = 2,000,000 simulated draws, 25 independent fixed players averaged)

| tier              |   Fixed Numbers |   Quick Pick |   theoretical |
|:------------------|----------------:|-------------:|--------------:|
| Match 2 + Bonus   |        0.012344 |     0.012391 |      0.012314 |
| Match 3           |        0.017658 |     0.017874 |      0.017650 |
| Match 4           |        0.000968 |     0.000991 |      0.000969 |
| Match 5           |        0.000018 |     0.000019 |      0.000018 |
| Match 5 + Bonus   |        0.000000 |     0.000000 |      0.000000 |
| Match 6 (Jackpot) |        0.000000 |     0.000000 |      0.000000 |

### B. Jackpot-sharing risk (assuming ~6,000,000 other tickets in play, 12% of all players restricted to numbers 1-31, illustrative jackpot $12,000,000)

| scenario                                      |   expected_co_winners |   mean_co_winners_sim |   mean_payout_sim |   median_payout_sim |   p_share_with_anyone |   game |
|:----------------------------------------------|----------------------:|----------------------:|------------------:|--------------------:|----------------------:|-------:|
| Popular / calendar numbers (all ≤ 31)         |                 1.355 |                 1.350 |     6,581,662.524 |       6,000,000.000 |                 0.741 |    649 |
| Quick pick / spread numbers (≥ 1 number > 31) |                 0.378 |                 0.377 |     9,999,006.000 |      12,000,000.000 |                 0.314 |    649 |

### C. Wheeling system vs. same number of random lines

| method                           |   lines |   cost_per_draw |   mean_return_per_draw |   return_per_dollar |   game |
|:---------------------------------|--------:|----------------:|-----------------------:|--------------------:|-------:|
| Full wheel (9 numbers, 84 lines) |      84 |       252.00000 |               21.96620 |             0.08717 |    649 |
| 84 independent random lines      |      84 |       252.00000 |               22.03275 |             0.08743 |    649 |

### D. Return per dollar vs. number of lines played per draw

|   lines_per_draw |   cost_per_draw |   mean_fixed_prize_return_per_draw |   return_per_dollar |   std_return_per_draw |   game |
|-----------------:|----------------:|-----------------------------------:|--------------------:|----------------------:|-------:|
|                1 |         3.00000 |                            0.26213 |             0.08738 |               1.62289 |    649 |
|                5 |        15.00000 |                            1.29832 |             0.08655 |               3.58757 |    649 |
|               20 |        60.00000 |                            5.25617 |             0.08760 |               7.23044 |    649 |
|               50 |       150.00000 |                           13.10752 |             0.08738 |              11.42829 |    649 |

### E. Rollover chasing -- only play when the jackpot clears a threshold

(simulated 1,000,000-draw jackpot trajectory; reset $5,000,000, cap none, +$3,000,000/unwon draw, sales scale as (J/reset)^1.3 off a base of 6,000,000 tickets)

|   threshold |   fraction_of_draws_played |   mean_jackpot_when_played |   mean_other_tickets_when_played |   jackpot_ev_per_line |   fixed_tier_ev_per_line |   total_ev_per_line |   return_per_dollar |   game |
|------------:|---------------------------:|---------------------------:|---------------------------------:|----------------------:|-------------------------:|--------------------:|--------------------:|-------:|
|     5000000 |                     1.0000 |             7,322,456.0000 |                  10,108,897.4741 |                0.3737 |                   0.2623 |              0.6360 |              0.2120 |    649 |
|    12000000 |                     0.0532 |            14,609,404.0706 |                  24,222,580.8187 |                0.5348 |                   0.2623 |              0.7971 |              0.2657 |    649 |
|    20000000 |                     0.0011 |            20,209,039.5480 |                  36,882,776.3629 |                0.5614 |                   0.2623 |              0.8237 |              0.2746 |    649 |


## Lotto Max

### Official odds by tier

| tier              |   probability |        one_in | prize_type   |   amount |
|:------------------|--------------:|--------------:|:-------------|---------:|
| Match 7 (Jackpot) |           0.0 | 133,784,560.0 | jackpot      |    nan   |
| Match 6 + Bonus   |           0.0 |  19,112,080.0 | parimutuel   |    nan   |
| Match 6           |           0.0 |     434,365.5 | parimutuel   |    nan   |
| Match 5 + Bonus   |           0.0 |     144,788.5 | parimutuel   |    nan   |
| Match 5           |           0.0 |       6,734.3 | parimutuel   |    nan   |
| Match 4 + Bonus   |           0.0 |       4,040.6 | parimutuel   |    nan   |
| Match 4           |           0.0 |         288.6 | fixed        |     20.0 |
| Match 3 + Bonus   |           0.0 |         288.6 | fixed        |     20.0 |
| Match 3           |           0.0 |          28.2 | fixed        |      5.0 |

### A. Fixed numbers vs. Quick Pick -- empirical hit rate per tier

(n = 2,000,000 simulated draws, 25 independent fixed players averaged)

| tier              |   Fixed Numbers |   Quick Pick |   theoretical |
|:------------------|----------------:|-------------:|--------------:|
| Match 3           |        0.035523 |     0.035658 |      0.035514 |
| Match 3 + Bonus   |        0.003456 |     0.003449 |      0.003465 |
| Match 4           |        0.003467 |     0.003459 |      0.003465 |
| Match 4 + Bonus   |        0.000248 |     0.000247 |      0.000247 |
| Match 5           |        0.000151 |     0.000162 |      0.000148 |
| Match 5 + Bonus   |        0.000006 |     0.000007 |      0.000007 |
| Match 6           |        0.000003 |     0.000003 |      0.000002 |
| Match 6 + Bonus   |        0.000000 |     0.000000 |      0.000000 |
| Match 7 (Jackpot) |        0.000000 |     0.000000 |      0.000000 |

### B. Jackpot-sharing risk (assuming ~10,000,000 other tickets in play, 12% of all players restricted to numbers 1-31, illustrative jackpot $40,000,000)

| scenario                                      |   expected_co_winners |   mean_co_winners_sim |   mean_payout_sim |   median_payout_sim |   p_share_with_anyone | game   |
|:----------------------------------------------|----------------------:|----------------------:|------------------:|--------------------:|----------------------:|:-------|
| Popular / calendar numbers (all ≤ 31)         |                 0.522 |                 0.523 |    31,151,355.714 |      40,000,000.000 |                 0.407 | max    |
| Quick pick / spread numbers (≥ 1 number > 31) |                 0.066 |                 0.065 |    38,725,950.000 |      40,000,000.000 |                 0.063 | max    |

### C. Wheeling system vs. same number of random lines

| method                             |   lines |   cost_per_draw |   mean_return_per_draw |   return_per_dollar | game   |
|:-----------------------------------|--------:|----------------:|-----------------------:|--------------------:|:-------|
| Full wheel (10 numbers, 120 lines) |     120 |       180.00000 |               37.95717 |             0.21087 | max    |
| 120 independent random lines       |     120 |       180.00000 |               37.91812 |             0.21066 | max    |

### D. Return per dollar vs. number of lines played per draw

|   lines_per_draw |   cost_per_draw |   mean_fixed_prize_return_per_draw |   return_per_dollar |   std_return_per_draw | game   |
|-----------------:|----------------:|-----------------------------------:|--------------------:|----------------------:|:-------|
|                1 |         1.50000 |                            0.31532 |             0.21021 |               1.88233 | max    |
|                5 |         7.50000 |                            1.57900 |             0.21053 |               4.21761 | max    |
|               20 |        30.00000 |                            6.29898 |             0.20997 |               8.39709 | max    |
|               50 |        75.00000 |                           15.81887 |             0.21092 |              13.32302 | max    |

### E. Rollover chasing -- only play when the jackpot clears a threshold

(simulated 1,000,000-draw jackpot trajectory; reset $10,000,000, cap $90,000,000, +$4,000,000/unwon draw, sales scale as (J/reset)^1.3 off a base of 10,000,000 tickets)

|   threshold |   fraction_of_draws_played |   mean_jackpot_when_played |   mean_other_tickets_when_played |   jackpot_ev_per_line |   fixed_tier_ev_per_line |   total_ev_per_line |   return_per_dollar | game   |
|------------:|---------------------------:|---------------------------:|---------------------------------:|----------------------:|-------------------------:|--------------------:|--------------------:|:-------|
|    10000000 |                     1.0000 |            21,842,904.0000 |                  28,774,248.9606 |                0.1452 |                   0.3162 |              0.4613 |              0.3076 | max    |
|    40000000 |                     0.0648 |            46,776,371.0474 |                  74,523,391.6454 |                0.2754 |                   0.3162 |              0.5916 |              0.3944 | max    |
|    60000000 |                     0.0024 |            64,840,385.4210 |                 113,691,697.8884 |                0.3409 |                   0.3162 |              0.6571 |              0.4380 | max    |
|    80000000 |                     0.0000 |            83,250,000.0000 |                 157,232,146.6706 |                0.3877 |                   0.3162 |              0.7039 |              0.4693 | max    |


## Daily Grand

### Official odds by tier

| tier                                           |   probability |       one_in | prize_type   |      amount |
|:-----------------------------------------------|--------------:|-------------:|:-------------|------------:|
| Match 5 + Grand (Jackpot: $1,000/day for life) |           0.0 | 13,348,188.0 | jackpot      | 7,000,000.0 |
| Match 5 ($25,000/year for life)                |           0.0 |  2,224,698.0 | fixed        |   500,000.0 |
| Match 4 + Grand                                |           0.0 |     60,673.6 | fixed        |     1,000.0 |
| Match 4                                        |           0.0 |     10,112.3 | fixed        |       500.0 |
| Match 3 + Grand                                |           0.0 |      1,411.0 | fixed        |       100.0 |
| Match 3                                        |           0.0 |        235.2 | fixed        |        20.0 |
| Match 2 + Grand                                |           0.0 |        100.8 | fixed        |        10.0 |
| Match 1 + Grand                                |           0.1 |         19.7 | fixed        |         4.0 |
| Grand Number only                              |           0.1 |         12.3 | fixed        |         4.0 |

### A. Fixed numbers vs. Quick Pick -- empirical hit rate per tier

(n = 2,000,000 simulated draws, 25 independent fixed players averaged)

| tier                                           |   Fixed Numbers |   Quick Pick |   theoretical |
|:-----------------------------------------------|----------------:|-------------:|--------------:|
| Grand Number only                              |        0.081386 |     0.080955 |      0.081360 |
| Match 1 + Grand                                |        0.050810 |     0.050778 |      0.050850 |
| Match 2 + Grand                                |        0.009916 |     0.009886 |      0.009922 |
| Match 3                                        |        0.004239 |     0.004280 |      0.004252 |
| Match 3 + Grand                                |        0.000712 |     0.000726 |      0.000709 |
| Match 4                                        |        0.000098 |     0.000085 |      0.000099 |
| Match 4 + Grand                                |        0.000017 |     0.000019 |      0.000016 |
| Match 5 ($25,000/year for life)                |        0.000000 |     0.000000 |      0.000000 |
| Match 5 + Grand (Jackpot: $1,000/day for life) |        0.000000 |     0.000000 |      0.000000 |

### B. Jackpot-sharing risk (assuming ~1,000,000 other tickets in play, 12% of all players restricted to numbers 1-31, illustrative jackpot $7,000,000)

| scenario                                      |   expected_co_winners |   mean_co_winners_sim |   mean_payout_sim |   median_payout_sim |   p_share_with_anyone | game   |
|:----------------------------------------------|----------------------:|----------------------:|------------------:|--------------------:|----------------------:|:-------|
| Popular / calendar numbers (all ≤ 31)         |                 1.168 |                 1.167 |     4,130,325.458 |       3,500,000.000 |                 0.689 | grand  |
| Quick pick / spread numbers (≥ 1 number > 31) |                 0.461 |                 0.460 |     5,612,500.000 |       7,000,000.000 |                 0.368 | grand  |

### C. Wheeling system vs. same number of random lines

| method                           |   lines |   cost_per_draw |   mean_return_per_draw |   return_per_dollar | game   |
|:---------------------------------|--------:|----------------:|-----------------------:|--------------------:|:-------|
| Full wheel (8 numbers, 56 lines) |      56 |       168.00000 |              311.65096 |             1.85507 | grand  |
| 56 independent random lines      |      56 |       168.00000 |              309.27057 |             1.84090 | grand  |

### D. Return per dollar vs. number of lines played per draw

|   lines_per_draw |   cost_per_draw |   mean_fixed_prize_return_per_draw |   return_per_dollar |   std_return_per_draw | game   |
|-----------------:|----------------:|-----------------------------------:|--------------------:|----------------------:|:-------|
|                1 |         3.00000 |                            5.16406 |             1.72135 |              17.35662 | grand  |
|                5 |        15.00000 |                           27.58600 |             1.83907 |             913.82092 | grand  |
|               20 |        60.00000 |                          109.90841 |             1.83181 |           1,827.41283 | grand  |
|               50 |       150.00000 |                          268.45594 |             1.78971 |           2,239.56878 | grand  |
