# Parental Labor Force Participation Analysis

library(tidyverse)
library(ggplot2)
library(scales)
library(arrow)
library(modelsummary)
library(gt)
library(survey)
library(usmap)
library(showtext)
library(ggtext)


# 0. FONTS AND SHARED THEME
font_add_google("Roboto Slab", "roboto_slab")
font_add_google("Roboto", "roboto")
showtext_auto()

project_theme <- function() {
  theme_minimal(base_size = 24, base_family = "roboto") +
    theme(
      plot.title = element_text(
        family     = "roboto_slab",
        face       = "bold",
        size       = 28,
        lineheight = 1.1,
        margin     = margin(b = .3, unit = "cm")
      ),
      plot.subtitle = element_text(
        family = "roboto",
        color  = "gray45",
        size   = 18,
        margin = margin(b = .3, unit = "cm")
      ),
      plot.caption = element_text(
        family = "roboto",
        color  = "gray55",
        size   = 13,
        hjust  = 0,
        margin = margin(t = .3, unit = "cm")
      ),
      plot.title.position   = "plot",
      plot.caption.position = "plot",
      axis.title.x = element_text(
        margin = margin(t = .3, unit = "cm"),
        color  = "gray30",
        size   = 20
      ),
      axis.title.y = element_text(
        margin = margin(r = .3, unit = "cm"),
        color  = "gray30",
        size   = 20
      ),
      axis.text        = element_text(color = "gray40", size = 18),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(color = "gray92"),
      legend.position  = "top",
      legend.direction = "horizontal",
      legend.text      = element_text(family = "roboto", size = 18),
      legend.key.size  = unit(1.5, "lines"),
      plot.margin      = margin(1, .8, .8, .8, "cm")
    )
}

# Source notes
source_general  <- "Source: IPUMS CPS ASEC 2022–2025. Estimates weighted using ASECWT. Sample restricted to adults aged 25–54 with at least one own child under age 5."
source_mothers  <- "Source: IPUMS CPS ASEC 2022–2025. Estimates weighted using ASECWT. Sample restricted to female adults aged 25–54 with at least one own child under age 5."

# Color palettes
colors_sex <- c(
  "Female" = "#C1666B",
  "Male"   = "#4281A4"
)

colors_educ <- c(
  "Less than High School" = "#7B1D1D",
  "High School Diploma"   = "#B84040",
  "Some College"          = "#D98080",
  "Bachelor's or Higher"  = "#F2BFBF"
)


# 1. LOAD DATA
df <- read_parquet("data/clean/cps_clean.parquet")

cat("=== DATA LOADED ===\n")
cat(sprintf("Rows: %s\n", format(nrow(df), big.mark=",")))
cat(sprintf("Columns: %s\n", ncol(df)))
cat(sprintf("Years: %s\n", paste(sort(unique(df$YEAR)), collapse=", ")))

parents <- df %>% filter(has_young_child == 1)
cat(sprintf("Parents with child under 5: %s\n", format(nrow(parents), big.mark=",")))

# 2. SUMMARY TABLE
# table of weighted NILF rates by education level

nilf_by_educ <- read_csv("outputs/nilf_by_educ.csv")

table_data <- nilf_by_educ %>%
  mutate(
    educ_label = case_when(
      educ_cat == "1_less_than_hs"   ~ "Less than High School",
      educ_cat == "2_hs_diploma"     ~ "High School Diploma",
      educ_cat == "3_some_college"   ~ "Some College",
      educ_cat == "4_bachelors_plus" ~ "Bachelor's or Higher"
    ),
    weighted_nilf_pct = round(weighted_nilf_pct, 1)
  ) %>%
  select(educ_label, weighted_nilf_pct, n_records)

gt_table <- table_data %>%
  gt() %>%
  cols_label(
    educ_label        = "Educational Background",
    weighted_nilf_pct = "% Not in Labor Force",
    n_records         = "Sample Size"
  ) %>%
  fmt_number(columns = n_records, use_seps = TRUE, decimals = 0) %>%
  fmt_number(columns = weighted_nilf_pct, decimals = 1, sep_mark = "", dec_mark = ".") %>%
  cols_align(align = "left",   columns = educ_label) %>%
  cols_align(align = "center", columns = c(weighted_nilf_pct, n_records)) %>%
  tab_header(
    title    = "Labor Force Participation Among Parents with Young Children",
    subtitle = "Weighted % not in labor force by education level | IPUMS CPS 2022–2025"
  ) %>%
  tab_source_note(source_note = source_general) %>%
  tab_style(
    style     = cell_text(weight = "bold"),
    locations = cells_column_labels()
  ) %>%
  tab_style(
    style     = cell_fill(color = "#f0f4f8"),
    locations = cells_body(rows = seq(1, nrow(table_data), 2))
  ) %>%
  opt_table_font(font = "Georgia") %>%
  tab_options(
    table.width                = pct(80),
    heading.title.font.size    = 16,
    heading.subtitle.font.size = 13,
    column_labels.font.size    = 15,
    table.font.size            = 15
  )

gtsave(gt_table, "outputs/figures/nilf_table.png")


# 3. GENDER GAP TREND LINE
# Showcase gap between mothers and fathers 2022-2025

nilf_trend_sex <- read_csv("outputs/nilf_trend_by_sex.csv")

p_trend_sex <- ggplot(nilf_trend_sex,
                      aes(x = YEAR,
                          y = weighted_nilf_pct,
                          color = sex_label,
                          group = sex_label)) +
  geom_line(linewidth = 1.5) +
  geom_point(size = 5) +
  geom_text(
    aes(label = sprintf("%.1f%%", weighted_nilf_pct)),
    vjust = -1.3,
    size  = 7,
    fontface = "bold",
    show.legend = FALSE
  ) +
  scale_color_manual(values = colors_sex, name = NULL) +
  scale_x_continuous(breaks = c(2022, 2023, 2024, 2025)) +
  scale_y_continuous(
    limits = c(0, 42),
    labels = function(x) paste0(x, "%")
  ) +
  labs(
    x       = "Year",
    y       = "% Not in Labor Force",
    caption = source_general
  ) +
  project_theme()

ggsave("outputs/figures/nilf_trend_by_sex.png",
       plot = p_trend_sex, width = 13, height = 8, dpi = 150, bg = "white")
print(p_trend_sex)

# 4. Grouped Bar Chart
# NILF rate by education level and sex among parents with young children

summary_educ_sex <- parents %>%
  group_by(educ_cat, sex_label) %>%
  summarise(
    weighted_nilf_pct = sum(nilf * ASECWT) / sum(ASECWT) * 100,
    n = n(),
    .groups = "drop"
  ) %>%
  mutate(
    educ_label = case_when(
      educ_cat == "1_less_than_hs"   ~ "Less than\nHigh School",
      educ_cat == "2_hs_diploma"     ~ "High School\nDiploma",
      educ_cat == "3_some_college"   ~ "Some\nCollege",
      educ_cat == "4_bachelors_plus" ~ "Bachelor's\nor Higher"
    ),
    educ_label = factor(educ_label, levels = c(
      "Less than\nHigh School",
      "High School\nDiploma",
      "Some\nCollege",
      "Bachelor's\nor Higher"
    ))
  )

p_bar <- ggplot(summary_educ_sex,
                aes(x = educ_label,
                    y = weighted_nilf_pct,
                    fill = sex_label)) +
  geom_col(position = "dodge", width = 0.7) +
  geom_text(
    aes(label = sprintf("%.1f%%", weighted_nilf_pct)),
    position = position_dodge(width = 0.7),
    vjust    = -0.5,
    size     = 7,
    fontface = "bold"
  ) +
  scale_fill_manual(values = colors_sex, name = NULL) +
  scale_y_continuous(
    limits = c(0, 70),
    labels = function(x) paste0(x, "%"),
    expand = c(0, 0)
  ) +
  labs(
    x       = "Educational Background",
    y       = "% Not in Labor Force",
    caption = source_general
  ) +
  project_theme() +
  theme(panel.grid.major.x = element_blank())

ggsave("outputs/figures/nilf_by_educ_sex.png",
       plot = p_bar, width = 13, height = 8, dpi = 150, bg = "white")
print(p_bar)

# 5. MOTHERS BY EDUCATION TREND
# Showcasing trends for mothers by education level 2022-2025
# Dark red = least education + highest NILF
# Light pink = most education + lowest NILF

nilf_mothers_educ <- read_csv("outputs/nilf_trend_mothers_by_educ.csv") %>%
  mutate(
    educ_label = case_when(
      educ_cat == "1_less_than_hs"   ~ "Less than High School",
      educ_cat == "2_hs_diploma"     ~ "High School Diploma",
      educ_cat == "3_some_college"   ~ "Some College",
      educ_cat == "4_bachelors_plus" ~ "Bachelor's or Higher"
    ),
    educ_label = factor(educ_label, levels = c(
      "Less than High School",
      "High School Diploma",
      "Some College",
      "Bachelor's or Higher"
    ))
  )

p_mothers_educ <- ggplot(nilf_mothers_educ,
                         aes(x = YEAR,
                             y = weighted_nilf_pct,
                             color = educ_label,
                             group = educ_label)) +
  geom_line(linewidth = 1.5) +
  geom_point(size = 5) +
  geom_text(
    data = nilf_mothers_educ %>% filter(YEAR == 2025),
    aes(label = sprintf("%.1f%%", weighted_nilf_pct)),
    hjust = -0.15,
    size  = 7,
    fontface = "bold",
    show.legend = FALSE
  ) +
  scale_color_manual(values = colors_educ, name = NULL) +
  scale_x_continuous(
    breaks = c(2022, 2023, 2024, 2025),
    limits = c(2022, 2026)
  ) +
  scale_y_continuous(
    limits = c(0, 75),
    labels = function(x) paste0(x, "%")
  ) +
  labs(
    x       = "Year",
    y       = "% Not in Labor Force",
    caption = source_mothers
  ) +
  project_theme()

ggsave("outputs/figures/nilf_mothers_by_educ.png",
       plot = p_mothers_educ, width = 13, height = 8, dpi = 150, bg = "white")
print(p_mothers_educ)

# 6. GEOGRAPHIC MAP
# State-level NILF rates among bachelor's degree mothers with young children
# Purple gradient: light lavender (low NILF) to deep plum (high NILF)

nilf_state <- read_csv("outputs/nilf_bachelors_mothers_by_state.csv") %>%
  rename(fips = STATEFIP) %>%
  mutate(
    fips     = sprintf("%02d", fips),
    reliable = n_records >= 100
  )

p_map <- plot_usmap(
  data      = nilf_state,
  values    = "weighted_nilf_pct",
  color     = "white",
  linewidth = 0.3
) +
  scale_fill_gradient(
    low    = "#EDE0F5",
    high   = "#3B0764",
    name   = "% Not in\nLabor Force",
    labels = function(x) paste0(x, "%"),
    guide  = guide_colorbar(
      barwidth  = 1.5,
      barheight = 12,
      ticks     = TRUE
    )
  ) +
  labs(
    caption = source_mothers
  ) +
  theme(
    text         = element_text(family = "roboto", size = 18),
    plot.title   = element_text(
      family     = "roboto_slab",
      face       = "bold",
      size       = 26,
      lineheight = 1.1,
      margin     = margin(b = .3, unit = "cm")
    ),
    plot.caption = element_text(
      family = "roboto",
      color  = "gray55",
      size   = 13,
      hjust  = 0,
      margin = margin(t = .3, unit = "cm")
    ),
    plot.title.position   = "plot",
    plot.caption.position = "plot",
    legend.position       = "right",
    legend.text           = element_text(size = 16),
    legend.title          = element_text(size = 16),
    plot.margin           = margin(1, .8, .8, .8, "cm")
  )

ggsave("outputs/figures/nilf_map_bachelors_mothers.png",
       plot = p_map, width = 14, height = 9, dpi = 150, bg = "white")
print(p_map)

# 7. OVERALL TREND LINE
# Overall NILF rate among parents with young children 2022-2025

nilf_trend <- read_csv("outputs/nilf_trend.csv")

p_trend <- ggplot(nilf_trend, aes(x = YEAR, y = weighted_nilf_pct)) +
  geom_line(color = "#4281A4", linewidth = 1.5) +
  geom_point(color = "#4281A4", size = 5) +
  geom_text(
    aes(label = sprintf("%.1f%%", weighted_nilf_pct)),
    vjust    = -1.3,
    size     = 7,
    fontface = "bold",
    color    = "#4281A4"
  ) +
  scale_x_continuous(breaks = c(2022, 2023, 2024, 2025)) +
  scale_y_continuous(
    limits = c(15, 22),
    labels = function(x) paste0(x, "%")
  ) +
  labs(
    x       = "Year",
    y       = "% Not in Labor Force",
    caption = source_general
  ) +
  project_theme()

ggsave("outputs/figures/nilf_trend.png",
       plot = p_trend, width = 13, height = 8, dpi = 150, bg = "white")
print(p_trend)
