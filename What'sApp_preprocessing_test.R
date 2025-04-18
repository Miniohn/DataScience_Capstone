### TEST
## what's app preprocessing
library(stringr)
library(dplyr)
library(tidyverse)

# get data
getwd()

wa<-readLines("./preprocessing/what's_app/_chat 3.txt", 
          encoding="UTF-8")
wa

# glimpse

# delete date data
wa2 <- 
  wa %>% str_remove_all("\\[[:print:]+\\]")
wa2

# seperate name and text
# "name" : "text"
test<-wa2 %>% str_split(": ",n=2)

test[[1]][2]

name <- vector()
text <- vector()
for (i in 1:length(test)){
  name[i]<-test[[i]][1]
  text[i]<-test[[i]][2]
}

test_df <- data.frame(name, text)
test_df

## preprocessing
test_df$name<-str_trim(test_df$name)
test_df$text<-str_trim(test_df$text)

# duplicated word delete

# 1) "Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them."
test_df<-
  test_df %>% 
  filter(!str_detect(text, "encrypted"))

# delete emogi
emoji_pattern <- "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF]"
test_df$text<-str_remove_all(test_df$text, emoji_pattern)

# fin) if nchar == 0 --> delete this row
test_df %>% filter(!nchar(text)==0)

test_df %>% head(20)
