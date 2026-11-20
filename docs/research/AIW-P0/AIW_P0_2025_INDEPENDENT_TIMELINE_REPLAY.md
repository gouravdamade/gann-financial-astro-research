# Independent replay of the 2025 Sun marks

**Result.** Every transition, both charts' counts and the complete range −5 to +3 agree with the ledger pinned to b27ba87434ecd0fd491990d8516349487d526630. The first whole UTC second in each new sign matched in all 12 cases.

I read the two chart hypotheses from the founder registry. Using their registered UTC epochs and coordinates, I recalculated all seven natal longitudes and the ascendant. I then scored signs from the freshly transcribed table. For the Sun's crossings I called Swiss Ephemeris 2.10.03 solcross_ut for each target longitude 0°,30°,…,330° starting at 1 January. This uses a different event-finding path from the previous daily bracket and bisection, with the same Raman and explicit Moshier model. At each reported ingress I checked calc_ut at the stated second and one second earlier. This verifies the computational boundary at one-second sampling. UTC approximates UT for this research replay. It does not supply observatory validation or new evidence about the historical founding dates.

| Subject | Birth input | Natal reference signs, Sun / Moon / Mars / Mercury / Jupiter / Venus / Saturn / Lagna |
|---|---|---|
| USD | 1776-07-04T16:56:02Z, 39.9526°, -75.1652° | Gemini / Aquarius / Gemini / Cancer / Gemini / Gemini / Virgo / Virgo |
| JPY | 1889-02-10T15:00:00Z, 35.6762°, 139.6503° | Aquarius / Gemini / Pisces / Aquarius / Sagittarius / Pisces / Cancer / Libra |

The natal seven planets use geocentric sidereal positions. The ascendant is the ascendant returned by houses_ex with sidereal flag and whole-sign convention. Zero-based signs use floor(longitude/30) after normalizing longitude. The JSON includes the newly computed degrees and registry hash. All sixteen signs match the archived chart inputs. This comparison concerns signs, with no claim of identical longitudes between ephemeris backends.

| Effective UTC | Sun | USD marks | JPY marks | USD − JPY |
|---|---|---:|---:|---:|
| 2025-01-01 00:00:00 | Sagittarius | 7 | 4 | 3 |
| 2025-01-12 17:20:28 | Capricorn | 2 | 4 | -2 |
| 2025-02-11 06:06:05 | Aquarius | 4 | 3 | 1 |
| 2025-03-13 02:31:24 | Pisces | 4 | 5 | -1 |
| 2025-04-12 10:25:58 | Aries | 6 | 5 | 1 |
| 2025-05-13 06:42:57 | Taurus | 3 | 3 | 0 |
| 2025-06-13 12:53:51 | Gemini | 5 | 2 | 3 |
| 2025-07-14 23:38:49 | Cancer | 5 | 3 | 2 |
| 2025-08-15 08:15:51 | Leo | 1 | 6 | -5 |
| 2025-09-15 08:41:32 | Virgo | 4 | 4 | 0 |
| 2025-10-15 21:16:46 | Libra | 2 | 5 | -3 |
| 2025-11-14 21:40:30 | Scorpio | 5 | 4 | 1 |
| 2025-12-14 12:43:01 | Sagittarius | 7 | 4 | 3 |
| 2026-01-01 00:00:00 | Sagittarius | 7 | 4 | 3 |

The first row is the initial state, and the 1 January 2026 row closes the display. Source intervals are left-closed and right-open. The source state changes at the astronomical ingress. The recorded instant is the first whole second sampling the new state. A crossing at which one side’s count stays constant still changes the underlying sign.

**Timeframe check.** For M1, H1, D1 and W1 I reconstructed the state from the beginning of the containing time bin plus every ingress through the requested instant. I compared it with direct longitude-based lookup at all 365 daily checkpoints and immediately before, at and after all 12 crossings. All **1,604 comparisons at 401 distinct instants** agreed. Bins were anchored at the start of the test year. This tests view-invariant evaluation rather than the project UI. Sampling only a bar’s opening or closing value can hide a within-bar change.

**Reproduction recipe.** Set Raman once in an isolated process. Generate the 12 crossings, convert Julian day to UTC seconds and round upward for the first whole-second display value. Find each side's new count by relative-place membership. Keep exact membership on each side of every boundary. Compare the resulting ordered rows, including sign, both counts and signed difference, with the baseline. No interpolation or price input is needed.

