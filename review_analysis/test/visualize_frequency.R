# Load required packages
library(ggplot2)
library(dplyr)
library(tidyr)
library(purrr)
library(stringr)
library(showtext)  # Handles font rendering
library(tidytext)

# Ensure showtext is used for better font support
showtext_auto()

# Select a system font that supports Korean (adjust if needed)
korean_font <- ifelse(Sys.info()["sysname"] == "Windows", "Malgun Gothic", "AppleGothic")

# Apply the font to ggplot2
theme_update(text = element_text(family = korean_font))


# Sample data: Read the CSV file (Replace with actual file path)
data <- read.csv("frequency_test_df.csv", stringsAsFactors = FALSE)

# Select only relevant columns: '사업장명' and 'top_10_words'
data_selected <- data %>% select(사업장명, top_10_words)

# Function to clean and extract words from the string format
process_top_words <- function(사업장명, top_10_words) {
  # Remove square brackets and split the string
  clean_string <- str_replace_all(top_10_words, "\\[|\\]", "")  # Remove '[' and ']'
  
  # Extract words and frequencies using regex
  words_freq <- str_match_all(clean_string, "'([^']+)', ([0-9]+)")[[1]]
  
  # Convert to dataframe
  df <- data.frame(
    word = words_freq[, 2],  # Extract words
    freq = as.numeric(words_freq[, 3])  # Extract frequencies
  )
  df$사업장명 <- 사업장명  # Add business name column
  return(df)
}

# Apply function row-wise using pmap_df on selected columns
top_words_df <- pmap_df(data_selected, process_top_words)


top_words_df <- top_words_df %>%
  group_by(사업장명) %>%
  mutate(word = reorder_within(word, freq, 사업장명))  # Sort words by frequency per business

# Generate the bar plots with **sorted words inside each facet**
plots <- ggplot(top_words_df, aes(x = word, y = freq, fill = 사업장명)) +
  geom_bar(stat = "identity") +
  facet_wrap(~사업장명, scales = "free", ncol = 4) +  # Sort facets & set columns
  scale_x_reordered() +  # Fix the order but remove _사업장명 suffix
  labs(title = "Top 10 Words for Each Restaurant", x = "Words", y = "Frequency") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 6, angle = 40, hjust = 1),  # Reduce font size & rotate
    axis.text.y = element_text(size = 10),  # Adjust y-axis label size
    strip.text = element_text(size = 12, face = "bold"),  # Business name title size
    legend.position = "none"
  )

# Print the plots
print(plots)




# Sample data: Read the CSV file (Replace with actual file path)
data2 <- read.csv("frequency_test_adj_df.csv", stringsAsFactors = FALSE)

# Select only relevant columns: '사업장명' and 'top_10_words'
data_selected2 <- data2 %>% select(사업장명, top_10_words)


# Apply function row-wise using pmap_df on selected columns
top_words_df2 <- pmap_df(data_selected2, process_top_words)


top_words_df2 <- top_words_df2 %>%
  group_by(사업장명) %>%
  mutate(word = reorder_within(word, freq, 사업장명))  # Sort words by frequency per business
###
# 각 사업장별 가장 많이 등장한 단어 찾기 (1위 단어)
most_common_words <- top_words_df2 %>%
  group_by(사업장명) %>%
  slice_max(order_by = freq, n = 1) %>% pull(word) # 각 사업장에서 가장 높은 빈도의 단어 찾기

print(most_common_words)  # 확인용 출력

# 특정 단어 제외 (벡터 비교를 위해 `%in%` 사용)
top_words_df2 <- top_words_df2 %>%
  filter(!(word %in% most_common_words)) %>%  # 가장 많이 등장한 단어 제외
  group_by(사업장명) %>%
  mutate(word = reorder_within(word, freq, 사업장명))  # 다시 정렬


top_words_df2

# Generate the bar plots with **sorted words inside each facet**
plots2 <- ggplot(top_words_df2, aes(x = word, y = freq, fill = 사업장명)) +
  geom_bar(stat = "identity") +
  facet_wrap(~사업장명, scales = "free", ncol = 4) +  # Sort facets & set columns
  scale_x_reordered() +  # Fix the order but remove _사업장명 suffix
  labs(title = "Top 10 Words for Each Restaurant", x = "Words", y = "Frequency") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 6, angle = 40, hjust = 1),  # Reduce font size & rotate
    axis.text.y = element_text(size = 10),  # Adjust y-axis label size
    strip.text = element_text(size = 12, face = "bold"),  # Business name title size
    legend.position = "none"
  )

# Print the plots
print(plots2)




