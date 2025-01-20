# R version 4.4.0 (2024-04-24)
# data.table_1.15.4  kableExtra_1.4.0.4 knitr_1.47
library(knitr)
library(kableExtra)
library(data.table)
options(knitr.kable.NA = "")

# Table 1
table_1 <- fread("./plos-minimum-data-set/tables_clean/table_1.csv")
table_1 |>
    kbl(booktabs = T) |>
    kable_styling() |>
    add_header_above(
        c(
            " " = 1, "Case notes" = 2, "Assessment" = 2, "Total" = 1
        )
    )

# Table 2
table_2 <- fread("./plos-minimum-data-set/tables_clean/table_2.csv")

table_2 |>
    kbl(booktabs = T) |>
    kable_styling(latex_options = c("scale_down")) |>
    footnote("F: Female. WB: White British. YOB: Median year of birth. Service length: Median time receiving statutory care services. Sentences (classified) is the number of sentences manually classified for model evaluation.", threeparttable = TRUE)


# Table 3
table_3 <- fread("./plos-minimum-data-set/tables_clean/table_3.csv", header = TRUE)
setnames(table_3, c("V1", "V2", "V4"), c("", "", ""))
table_3 |>
    kbl(booktabs = T) |>
    column_spec(1, border_right = TRUE) |>
    kable_styling()

# Table 4
table_4 <- fread("./plos-minimum-data-set/tables_clean/table_4.csv")
table_4 |>
    kbl(booktabs = TRUE) |>
    kable_styling() |>
    pack_rows("Transformers", 1, 2, hline_after = TRUE) |>
    pack_rows("Pre-trained embeddings", 3, 7, hline_after = TRUE) |>
    pack_rows("Document-term matrix", 13, 17, hline_after = TRUE) |>
    pack_rows("Tf-idf", 8, 12, hline_after = TRUE)

# Table 5
table_5 <- fread("./plos-minimum-data-set/tables_clean/table_5.csv")
setnames(table_5, "V1", "")
table_5 |>
    kbl(
        booktabs = TRUE,
        label = "comparison",
        caption = "Comparison of demographic and ADL needs between ELSA waves 6-9 and administrative data"
    ) |>
    kable_styling(
        latex_options = c("striped", "scale_down")
    ) |>
    add_header_above(
        c(
            " " = 1, "Administrative" = 2, "ELSA" = 2
        )
    ) |>
    kableExtra::footnote(
        "ELSA: English Longitudinal Study of Ageing waves 6-9 (limited to the subset of individuals who report they receive statutory care). N Unique: number of unique individuals (as data is pooled). Administrative values are recorded by care managers in structured data. ELSA values are from the variables: raracem, toilta, hhres, slfmem, sex, dangera, rcaany_e, dressing, mealsa, shopa.",
        threeparttable = TRUE, general_title = ""
    )


# Table 6
table_6 <- fread("./plos-minimum-data-set/tables_clean/table_6.csv", header = TRUE)
setnames(table_6, "V1", "")
table_6 |>
    kbl(
        booktabs = TRUE,
        caption = "Factors in structured data associated with loneliness and social isolation: Administrative data and ELSA",
        label = "logregchisqelsa"
    ) |>
    kable_styling(latex_options = c(
        "HOLD_position",
        "scale_down"
    )) |>
    pack_rows(
        "Chi-sq test", 1, 11
    ) |>
    pack_rows(
        "Logistic regression", 12, nrow(table_6)
    ) |>
    add_header_above(
        c(
            " " = 1, "Administrative records" = 4, "ELSA" = 2
        )
    ) |>
    footnote("*** < 0.001; ** <0.01; * <0.05; . <0.1", general_title = "") |>
    footnote(
        "ELSA: English Longitudinal Study of Ageing. CES-D: Center for Epidemiological Studies Depression. Chi-sq results are p-values. Logistic regression results are coefficients (0.95 CI).",
        threeparttable = TRUE, general_title = ""
    )

# Table 7
table_7 <- fread("./plos-minimum-data-set/tables_clean/table_7.csv", header = TRUE)
setnames(table_7, "V1", "")
table_7 |>
    kbl(
        booktabs = TRUE,
        label = "daycentrelogreg",
        caption = "Logistic regression: association of loneliness extracted from free text with services received for loneliness",
    ) |>
    kable_styling(latex_options = c(
        "HOLD_position",
        "scale_down"
    )) |>
    add_header_above(
        c(
            " " = 1,
            "Odds ratio (RoBERTa model)" = 4
        )
    ) |>
    footnote("*** < 0.001; ** <0.01; * <0.05; . <0.1")

# Figure 4 data (Table in Appendix)
figure_4 <- fread("./plos-minimum-data-set/tables_clean/figure_4.csv")
figure_4 |>
    kbl(
        booktabs = TRUE,
        caption = "Comparison of free text extraction with ELSA",
        label = "elsacomparison"
    ) |>
    kable_styling(latex_options = c("scale_down")) |>
    add_header_above(
        c(" " = 2, "ELSA" = 2, "Administrative data" = 2)
    )
