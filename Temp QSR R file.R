# Load packages
library(readxl)
library(dplyr)
library(purrr)

# Define your folder path
folder_path <- "C:/Users/SavannahSummers/Downloads/QSR Quality Check SKS/QSR 2024/Sch A & B 2024"

# List all Excel files in the folder
files <- list.files(folder_path, pattern = "\\.xlsx$", full.names = TRUE)

# Show filenames
print(files)

# Preview sheet names for the first file
sheet_names <- excel_sheets(files[1])
print(sheet_names)

# Load specific sheet to explore structure
# You can replace "Sch B" with whatever you want to test
sample_data <- read_excel(files[1], sheet = "Sch B")

# Peek at the top of the sheet
head(sample_data, 30)
