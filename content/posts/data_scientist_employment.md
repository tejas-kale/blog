---
title: "Data Science Jobs and the AI boom"
date: "2026-09-20"
draft: false
description: "The 2023–2025 jump in US data-scientist jobs started in 2021, before generative AI became a household name."
---

While reading an article on The Economist arguing that [AI has increased overall employment](https://www.economist.com/finance-and-economics/2026/09/04/the-jobs-apocalypse-is-postponed-an-ai-jobs-boom-is-here), the following chart caught my attention. It shows the change in employment in select professions in the US between 2023 and 2025. These professions were chosen as they have been hypothesised to be ripe for disruption with the arrival of agentic AI applications. I had two questions pop up in my head: (1) how exactly is the data compiled and (2) does the 2023-25 window create an arbitrary effect for some professions?

![The Economist Chart 3: US employment, % change May 2023–25]({{< relURL "data_scientist_employment/economist-chart3.png" >}})

Ironically, with the help of an agentic AI system (Cursor to be specific), I found out that the numbers come from the Bureau of Labor Statistics’ Occupational Employment and Wage Statistics (OEWS) survey. OEWS [samples](https://www.bls.gov/opub/hom/oews/design.htm) establishments including private sector, local government, and state government and hospitals in 3-year cycles. Based on the lists available from the state unemployment insurance agencies, there are approximately 8.7 million establishments in the country. About 186,000 workplaces are contacted each May and each November and an estimate published every May pools six of those panels, roughly 1.1 million establishments over three years. Sampled employers send, for a reference payroll, each employee’s job title, a brief description of duties, and the wage. The [form](https://www.bls.gov/respondents/oes/pdf/forms/uuuuuu_fillable.pdf) makes it explicit to report the description and not just the job title.

State workforce agencies and BLS then [assign](https://www.bls.gov/oes/oes_ques.htm) a Standard Occupational Classification code from the work performed. For example, “Data scientist” as a title is meant to be tagged as [SOC 15-2051](https://www.bls.gov/soc/2018/soc_2018_definitions.pdf). “Machine learning engineer” is not a unique match, so the coder is supposed to use the duties. In other words, two people with the same title can go to different codes and two people with different titles can go to the same one. After the classification, the count of wage-and-salary jobs for each code is [estimated based on the MB3 methodology](https://www.bls.gov/opub/hom/oews/calculation.htm), scaled to the Quarterly Census of Employment and Wages. These estimates exclude the self-employed.

An important point to remember is that the definition of individual SOC codes changes over time and they also get added or removed. Hence, the OEWS estimates are not perfectly comparable over time.

Having understood the provenance of the data, I fetched it for the professions listed in the chart above from the BLS's website and plotted it for all available years, as shown below. To my understanding, this visualisation makes the link between job growth and generative AI less obvious. For example, since it appeared as a standalone code in 2021, data scientist employment has risen sharply every year. Employment in the other professions also seems to have continued its pre-AI trend. Jobs for translators have tended to plateau since about 2012 except for a brief peak from 2018 to 2020.

![OEWS May employment for The Economist Chart 3 occupations]({{< relURL "data_scientist_employment/facet.png" >}})

Jobs as Bookkeeping clerks and data-entry keyers have been declining since 2010 and the start of the millennium respectively and it is hard to argue that AI has impacted the trend in any way. Customer service representative roles are the only ones where the decline (about 10%) coincides with the period when agentic AI systems proliferated.

Some trends from the plots are definitely worth following up in the future. For example, Writers and authors, which includes roles like copy editors, documentation writers, playwrights and television writers, saw a large spike in employment from 2020 to 2022 and a near equal fall from 2022 to 2024. Employment then stabilised in 2025 so we will need to see what the future holds for these roles.

I wanted to understand the increase in data science roles, hence I also looked at roles adjacent to them as shown in the chart below. What I infer from it is that the growth of data science roles is not unique among occupations associated with AI adoption. Software developers, project management specialists, analysts, and computer science researchers have all shown an increase in employment to varying degrees over the past few years. This is not surprising as data science work usually needs (1) data collection and curation which data management experts like data engineers often perform and (2) informs critical business decisions which are taken by project managers, product owners, or key executives.

![OEWS May employment for occupations adjacent to Chart 3]({{< relURL "data_scientist_employment/facet_adjacent.png" >}})

To conclude, the data do not show a link between generative AI and the rise of data science roles. It shows that data science as a profession was already on the ascendant and that the next few years will reveal whether AI changes its slope.

{{< note href="https://github.com/tejas-kale/blog/blob/main/notebooks/data_scientist_employment/data_scientist_employment.org" >}}Org notebook with code and additional data{{< /note >}}
