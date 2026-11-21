# Replaying Ketu–Venus from the birth balance

**Raman’s printed balance yields a 14-month Venus subperiod starting at age 49 years, 6 months, 17 days.** The period arithmetic is exact conditional on the printed input. A boundary in civil time requires the almanac and conversion convention. [Chart 44, pp. 102–103](https://elibraryofyoga.com/server/api/core/bitstreams/2271a6e2-f4ca-49bd-9706-89cec2d6f5f5/content#page=111)

## From the Moon to the opening ruler

Raman’s companion manual gives both the proportion of the star's passage elapsed in time and a longitude method. For the latter, number equal 13°20′ nakṣatras from Aśvinī at 0° of sidereal Aries. Start the repeating lord sequence Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury. Years are 7, 20, 6, 10, 7, 18, 16, 19, 17. Punarvasu covers [80°, 93⅓°) and gives Jupiter. Its remaining years equal 16 × (93⅓° − lunar longitude)/(13⅓°). The printed Jupiter balance is 13y 1m 20d. On the angular method that implies 82.384259° sidereal. This is an inversion of the printed balance, not an observed longitude. [Raman, Hindu Predictive Astrology, XII, tables of daśās and bhuktis and two methods of finding the balance](https://lib.wildla.in/book/B.%20V.%20Raman%20Hindu%20Predictive%20Astrology%20%201996%20%281%29.pdf)

I evaluated **both** candidate mornings using the caption coordinates. Interpreting L.T. as local mean time subtracts 4h59m, giving 23:36 UT on the preceding civil day. This is a declared reconstruction assumption. Swiss Ephemeris 2.10.03, Moshier, geocentric sidereal Raman, mean node, Gregorian input, UT, whole-sign houses. The two dates were compared to the printed horoscope before using either for timing.

| Local morning | Lunar longitude | Birth star and ruler | Comparison |
|---|---:|---|---|
| 29 September | 82.412215° | Punarvasu, Jupiter | All seven planets, both nodes and ascendant match the rāśi diagram. In D9 the modern calculation puts Venus in Sagittarius and Saturn in Aquarius where the plate gives Scorpio and Pisces. |
| 30 September | 94.780184° | Puṣya, Saturn | Moon in Cancer conflicts with the printed Gemini Moon and the Jupiter balance. |

On 29 September the angular calculation gives 13.105342 years, about 12.08 period-accounting days less than printed. I also bracketed the Moon’s 80° entry and 93⅓° exit and bisected actual longitude. The crossings were JD(UT) 2410909.285556703 and 2410910.367660084. Birth is JD 2410909.4833333334. Applying 16 × remaining crossing time / total crossing time gives 13.075671 years, about 22.76 accounting days less than printed. The two methods can differ because the Moon's speed varies. Neither calculation recovers Raman's exact source tables. The node choice has no bearing on this lunar discrepancy.

## Major and subsidiary boundaries

Use 12 months/year and 30 days/month as **period arithmetic**. For parent length L and next ruler's allotment Y, child length = L × Y/120. Children start with the parent ruler and continue cyclically. Preserve a partial first major period by measuring from its original start. Never restart its first bhukti at birth. The ledger below measures age from birth using a left-closed, right-open interval convention.

| Major ruler | Start age (y m d) | End age (y m d) |
|---|---|---|
| Jupiter, remaining | 0 0 0 | 13 1 20 |
| Saturn | 13 1 20 | 32 1 20 |
| Mercury | 32 1 20 | 49 1 20 |
| Ketu | 49 1 20 | 56 1 20 |

Ketu–Ketu lasts 7 × 7/120 years = 4m 27d. Add it to age 49y 1m 20d to get 49y 6m 17d. Ketu–Venus lasts 7 × 20/120 years = 1y 2m 0d, ending at 50y 8m 17d when Ketu–Sun begins. All nine Ketu subdivisions are tabulated in the JSON. For any query age, choose the interval containing it. At an end boundary select the incoming ruler.

**Resolution.** The source supports a seven-year parent, a fourteen-month child and a statement that the crisis occurred within the period. It identifies neither a pratyantardaśā nor a transit trigger nor a day. A smaller calendar unit in the arithmetic supplies no event observation. The evidence does not establish which civil-year conversion Raman used in this case. The fixture therefore carries native ages and null UTC bounds. An original daśā worksheet would allow the printed balance, conversion and civil dates to be independently checked.
