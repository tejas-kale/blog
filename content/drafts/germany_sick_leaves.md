---
title: Diving into Germany's Sickness Statistics
date: 2026-09-02
draft: true
---

BBC More or Less' recent [podcast episode](https://www.bbc.co.uk/sounds/play/w3ct9995) on the statistic that Germans take roughly 19.5 days of sick leave every year was interesting. It told that the number comes from the statutory insurer DAK's [report](https://www.dak.de/dak/unternehmen/reporte-forschung/gesundheitsreport-2026_223108), which counts all calendar days (including weekends) and excludes child-sickness and maternity leave. Given that Germany has 93 statutory health insurers, and the claim from an expert in the episode that the average is skewed by a handful of long-term absences, I wanted to answer two questions:

1. How representative are the people insured by DAK for the whole of Germany?
2. How skewed is the headline statistic of 19.5, and what is the median number of sick days taken by employees in Germany?

To answer the first question, we can look at a similar [report](https://www.tk.de/resource/blob/2214302/9c99dbb2cea6422e50c6009c50e57e37/gesundheitsreport-au-2026-data.pdf) published by another statutory insurer, Techniker Krankenkasse (TK), which is quite popular among the immigrant and tech community in Germany. TK is substantially larger than DAK: about 12.3 million people insured versus DAK's 5.4 million, or roughly 16% versus 7% of the statutory system. Their study estimates the average sick leave per year from their insurees at 18.5 days (age-standardised; 18.6 without that adjustment). Thus, while not conclusive, the TK report provides further evidence that the DAK mean is not a quirk of one fund.

While neither report publishes the median sick days per person per year, it is instructive to look at DAK's data grouped by the duration of each absence. As seen from the chart below, absences of 43 days or more account for only 2.5% of sick absences but 37.9% of sick days. Conversely, 40.1% of absences last 1–3 days but account for only 8.3% of sick days.

![Long absences are rare but dominate total sick days]({{< relURL "charts/dak-absence-duration.png" >}})

That 19.5 figure is a person-year mean: total certified calendar days divided by insured years, including the 37.5% of DAK members with no absence at all. It is not the average length of an episode (that is 9.8 days) and not a typical worker's year. DAK's duration table is also at the episode level, not the person level, so we still cannot say what the median or modal employee experienced. The honest conclusion is narrower: 19.5 is a valid insurer-level mean, and it is pulled up by a small share of very long cases — but without a person-level distribution, it should not be read as "what Germans typically take".
