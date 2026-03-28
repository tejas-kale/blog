---
title: "Creating Data Visualisations with ReportLab"
date: "2026-03-28"
draft: false
---

At work, I have to generate hundreds of PDFs every two weeks with each file containing about 50 pages. Each page consists of a single stacked bar chart along with annotations. When the module to render these bar charts was written, the library of choice was Plotly, which allowed us to interact with the plots and understand and debug them effectively. 

While the package was ideal during the exploration and research phase of the project, continuing with it as we approached production turned out to be the wrong trade-off. Generating each PDF took about 3 minutes, which meant that an entire day had to be devoted to generating the PDFs to keep up with the schedule.

Since the layout and data schema of the stacked bar chart never changes, I looked for alternatives to speed up the PDF generation process. This is when I came across [ReportLab](https://pypi.org/project/reportlab/), a Python package that provides an API to draw directly into a PDF. It reminded me of the D3 package which allows developers to build data visualisations from scratch in JavaScript. 

When I started experimenting with it, I found that GitHub Copilot was useful for working with ReportLab's API. Within a couple of hours, it wrote the necessary code and also explained the API to me clearly. Each PDF now takes 2 seconds to generate, **roughly 90x faster**. 

If you wish to explore ReportLab and compare its performance to other plotting packages, check out [this notebook](https://github.com/tejas-kale/blog/blob/main/notebooks/pdf_generation_benchmark.ipynb).