library(tidyverse)
library(data.table)
library(readr)
df <- read.csv("restaurant.csv", fileEncoding = "ISO-8859-1", stringsAsFactors = FALSE)
df <- read_csv("restaurant.csv", locale = locale(encoding = "ISO-8859-1"))


df %>% nrow()
df %>% head() 
df %>% colnames()

df %>% select(c("개방자치단체코드", "영업상태명","상세영업상태명","전화번호", 
                "소재지면적","소재지우편번호","지번주소","도로명주소", 
                "도로명우편번호", "사업장명","업태구분명", "좌표정보.X.", "좌표정보.Y.")) -> df_new


df <- fread("restaurant.csv")
df


df <- read.csv("restaurant.csv", fileEncoding = "CP949", stringsAsFactors = FALSE)
df %>% head()
df %>% nrow


df <- fread("restaurant.csv", encoding = "UTF-8", fill = TRUE)
df %>% head()


library(tidyverse)
df <- read.csv("restaurant.csv", fileEncoding = "CP949", stringsAsFactors = FALSE)
df %>% nrow()
