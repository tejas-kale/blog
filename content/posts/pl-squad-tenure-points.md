---
title: "Squad tenure and points"
date: "2026-09-23"
draft: true
description: "The median within-club correlation between senior-squad tenure and Premier League points is about zero, on both regular cuts."
---

Across the 31 completed 38-game seasons from 1995–96 through 2025–26, I asked whether clubs with a longer current senior-squad streak finish on more points. The answer below is descriptive.

A regular has at least 20 league starts, or, on the second cut, at least 20 league appearances. For each club-season I take the median tenure of those regulars. Tenure is the current streak in that club's senior squad, in any division. A full season on loan wipes the parent's streak. A mid-season split counts as half a season. The plotted total is results points: three for a win and one for a draw. The reconciliation records the four named deductions beside that total.

The lead number is the median of the within-club Pearson correlations, among clubs with at least 10 seasons in which every regular was matched. On the starts cut that median is 0.035. The 10% trimmed mean is 0.076, and the median of the Spearman correlations is 0.074. Redrawing each club's seasons 2,000 times, seed 2026, with that season's tenure and points kept together, the 95% interval runs from −0.093 to 0.244. Eighteen clubs enter.

On the appearances cut the median is 0.017. The trimmed mean is 0.097 and the median Spearman correlation is 0.048. The interval runs from −0.132 to 0.279, again with 18 clubs.

Every club that reaches 10 seasons has a defined correlation, so the write-up has no separate sentence for an undefined share. Tejas chooses which cut a chart shows. Both cuts are computed. The ten club plots for each cut stay with the notebook.

A club-season stays out when a regular name is unmatched or ambiguous. The resolution table is empty. On the starts cut, 172 club-seasons are out, and Barnsley, Bradford City, and Huddersfield Town have none left. Clubs with fewer than ten kept seasons are named in the notebook summary, and they stay out of the median. Filling a row in the resolution table is what lets that season back in.

{{< note href="https://github.com/tejas-kale/blog/tree/main/notebooks/pl-squad-tenure-points" >}}R sources{{< /note >}}
