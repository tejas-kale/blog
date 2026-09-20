library(dplyr)
library(readr)
library(ggplot2)
library(scales)
library(tidyr)

notebook_dir <- {
  csv <- "oews_occupations.csv"
  ofile <- Filter(Negate(is.null), lapply(sys.frames(), `[[`, "ofile"))
  candidates <- c(
    getwd(),
    file.path(getwd(), "notebooks", "data_scientist_employment"),
    if (length(ofile)) dirname(ofile[[1]])
  )
  found <- candidates[file.exists(file.path(candidates, csv))]
  if (!length(found)) {
    stop("Cannot find oews_occupations.csv from ", getwd())
  }
  normalizePath(found[[1]])
}
setwd(notebook_dir)
dir.create("plots", showWarnings = FALSE)

occupations <- c(
  "Data scientists",
  "Financial analysts",
  "Paralegals",
  "Info-security analysts",
  "Market-research analysts",
  "Lawyers",
  "Translators",
  "Writers & authors",
  "Graphic designers",
  "Bookkeeping clerks",
  "Customer-service reps",
  "Data-entry keyers"
)

oews <- read_csv("oews_occupations.csv", show_col_types = FALSE) |>
  filter(occupation %in% occupations) |>
  mutate(occupation = factor(occupation, levels = occupations))

# Insert NA years so ggplot does not draw a line across classification gaps.
oews_plot <- oews |>
  complete(occupation, year = min(year):max(year))

ink <- "#2C2A28"
teal <- "#3E6D7A"
muted <- "#6B6560"

theme_note <- function() {
  theme_minimal(base_family = "Avenir Next", base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", colour = ink, hjust = 0),
      plot.subtitle = element_text(colour = muted, hjust = 0),
      plot.caption = element_text(colour = muted, hjust = 0, size = 9),
      panel.grid.minor = element_blank(),
      strip.text = element_text(hjust = 0, colour = ink),
      axis.text = element_text(colour = ink),
      axis.title = element_text(colour = ink)
    )
}

oews

change <- oews |>
  filter(year %in% c(2023, 2025)) |>
  select(occupation, year, employment) |>
  pivot_wider(names_from = year, values_from = employment, names_prefix = "y") |>
  mutate(change_pct = 100 * (y2025 / y2023 - 1)) |>
  arrange(desc(change_pct))

change

ds <- oews |> filter(occupation == "Data scientists")
y2023 <- ds$employment[ds$year == 2023]
y2025 <- ds$employment[ds$year == 2025]

p_ds <- ggplot(ds, aes(year, employment)) +
  geom_line(colour = teal, linewidth = 0.9) +
  geom_point(colour = teal, size = 2.2) +
  scale_x_continuous(breaks = ds$year) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale()),
                     limits = c(0, NA)) +
  labs(
    title = sprintf(
      "OEWS data-scientist jobs rose %.0f%% from May 2023 to May 2025",
      100 * (y2025 / y2023 - 1)
    ),
    subtitle = "SOC 15-2051, national May estimates. First published as a standalone occupation in 2021.",
    x = NULL,
    y = "Employment",
    caption = "BLS Occupational Employment and Wage Statistics."
  ) +
  theme_note()
ggsave(file.path(notebook_dir, "plots", "data_scientists.png"), p_ds,
       width = 9.2, height = 5.2, dpi = 150)

p_facet <- ggplot(oews_plot, aes(year, employment)) +
  geom_line(colour = teal, linewidth = 0.75) +
  geom_point(colour = teal, size = 1.3, na.rm = TRUE) +
  facet_wrap(~occupation, scales = "free_y", ncol = 3) +
  scale_x_continuous(breaks = c(2000, 2005, 2010, 2015, 2020, 2025)) +
  scale_y_continuous(labels = label_number(scale_cut = cut_short_scale())) +
  labs(
    title = "OEWS May employment for The Economist Chart 3 occupations",
    subtitle = "Gaps are years BLS did not publish a comparable detail code, or pages not retrieved.",
    x = NULL,
    y = NULL,
    caption = "BLS Occupational Employment and Wage Statistics, national estimates."
  ) +
  theme_note()
ggsave(file.path(notebook_dir, "plots", "facet.png"), p_facet,
       width = 9.5, height = 8.8, dpi = 150)

p_change <- change |>
  mutate(occupation = factor(occupation, levels = rev(occupation))) |>
  ggplot(aes(change_pct, occupation, fill = change_pct > 0)) +
  geom_col(width = 0.72) +
  geom_vline(xintercept = 0, colour = ink, linewidth = 0.35) +
  scale_fill_manual(values = c("#B85C4A", teal), guide = "none") +
  scale_x_continuous(labels = label_number(suffix = "%")) +
  labs(
    title = "May 2023 to May 2025: data scientists are the outlier",
    subtitle = "Paralegals +11% and market-research analysts +6%, as in Chart 3.",
    x = "Change in OEWS employment",
    y = NULL,
    caption = "BLS OEWS national May estimates. US employment rose about 2.5% over the same window."
  ) +
  theme_note()
ggsave(file.path(notebook_dir, "plots", "change_2023_2025.png"), p_change,
       width = 9.2, height = 5.6, dpi = 150)
