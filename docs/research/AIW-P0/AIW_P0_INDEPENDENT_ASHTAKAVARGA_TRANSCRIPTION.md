# Independent transcription of Bṛhat Jātaka IX

The controlling edition is N. Chidambaram Aiyar’s 1905 *Bṛhat Jātaka*. I read the page images for IX.1–7 (printed pp97–99), recorded the seven recipient tables, then compared the new Sun/Mars table with the earlier ledger. The earlier research was visible in the conversation. This is a fresh transcription and an independent calculation by the same reviewer, rather than a blinded second-person audit. The scan’s SHA-256 is CEAFC2FE3E385FB834B94FA4F464406DA3BA42AB01B3A2AC42A2749ABDA9F1D9. [1905 scan, PDF p141](https://upload.wikimedia.org/wikipedia/commons/c/c2/The_Brihat_jataka_%28IA_brihatjataka00varaiala%29.pdf#page=141)

The left column names the natal contributor. Each number is an inclusive sign distance at which that contributor marks the recipient’s transit favorable. Two planets in one natal sign remain two contributors. An entry of 1 means that the transit and the reference occupy the same sign.

| Natal contributor | Sun · IX.1, p97 | Mars · IX.3, p98 |
|---|---|---|
| Sun | 1, 2, 4, 7, 8, 9, 10, 11 | 3, 5, 6, 10, 11 |
| Moon | 3, 6, 10, 11 | 3, 6, 11 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 | 1, 2, 4, 7, 8, 10, 11 |
| Mercury | 3, 5, 6, 9, 10, 11, 12 | 3, 5, 6, 11 |
| Jupiter | 5, 6, 9, 11 | 6, 10, 11, 12 |
| Venus | 6, 7, 12 | 6, 8, 11, 12 |
| Saturn | 1, 2, 4, 7, 8, 9, 10, 11 | 1, 4, 7, 8, 9, 10, 11 |
| Lagna | 3, 4, 6, 10, 11, 12 | 1, 3, 6, 10, 11 |

**Reconstructing the p100 figure.** The top-left box is Pisces, followed clockwise by Aries. The chart puts Venus and Lagna in Pisces, Sun in Aries, Mercury and Moon in Taurus, Jupiter in Cancer, Saturn in Libra and Mars in Capricorn. For Mars in Aries the places in table order are 1,12,4,12,10,2,7,2. The contributing marks come from natal Mars, Jupiter and Saturn. Proceeding around the zodiac yields **3, 3, 3, 4, 5, 2, 5, 1, 2, 5, 3, 3**. All twelve cells match both the p100 double-entry diagram and p101 favorable-only table. The JSON gives each of the 96 membership decisions. [1905 diagram and notes](https://upload.wikimedia.org/wikipedia/commons/c/c2/The_Brihat_jataka_%28IA_brihatjataka00varaiala%29.pdf#page=144)

**Published comparison.** At commit b27ba87434ecd0fd491990d8516349487d526630, the local comparison file hashed to published Git blob 7f1085a2b77c6e9d2698d6a06cceb8ae2da829b6. All 16 Sun/Mars masks, all twelve printed Mars favorable counts, all four 12-sign project chart/planet arrays and all four active eight-bit contributor vectors agreed. No numeric discrepancy in those fields. The 1905 adverse complement has a material edition limit for Mars, explained in the phala report. [Published comparison file](https://github.com/gouravdamade/gann-financial-astro-research/blob/b27ba87434ecd0fd491990d8516349487d526630/docs/research/AIW-MASTER-02/AIW_MASTER_02_RESEARCH_CANDIDATES.json)

**Acceptance invariant.** As a recipient traverses 12 signs, each contributor visits each relative place exactly once. The total of the favorable counts must therefore equal the total size of its eight masks, 48 for Sun and 39 for Mars. This checksum detects omissions but can miss an exchanged place. The twelve-cell figure and individual entries supply the stronger controls.

