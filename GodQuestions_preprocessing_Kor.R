## GodQuestions_preprocessing_Kor

# import library
library(stringr)
library(dplyr)
library(tidyverse)
library(openxlsx)

# load data
df <-read.xlsx("./preprocessing/GodQuestions/GodQuestions_test_Kor_2025-04-25.xlsx") %>% as.data.frame()
df$crawling_date <- as.Date(df$crawling_date, origin = "1899-12-30")
df %>% head()
nrow(df)

##duplicate check
df$URL_KOR_remove<-str_remove_all(df$URL_KOR, "https://www.gotquestions.org/Korean/Korean-")
df$URL_KOR_remove<-str_remove_all(df$URL_KOR_remove, ".html")

dup_df<-df[duplicated(df$URL_KOR_remove),]
names(dup_df)
dup_df$order<-row.names(dup_df)
dup_df

# all duplicated row
all_dup_df<-df[duplicated(df$URL_KOR_remove) | duplicated(df$URL_KOR_remove, fromLast = TRUE),]
all_dup_df$order<-row.names(all_dup_df)
all_dup_df %>% select(URL_KOR_remove, order) %>%arrange(URL_KOR_remove)

## case when english context--> X ?
df[df$Question_ENG =="NA",] # nothing

## ENG Answer Preprocessing 
# ex : ~ Copyright Got Questions Ministries ~
df$Answer_ENG %>% head()

# 1 : "Have you made a decision for Christ"~ remove

df$Answer_ENG %>% str_extract_all("\\nHave you[\\s\\S]*?button below[\\s\\S]+") %>% head(20)

df$Answer_ENG<-df$Answer_ENG %>% str_remove_all("\\nHave you[\\s\\S]*?button below[\\s\\S]+") %>% unlist()
df$Answer_ENG %>% head(15)

# 2 : "For Further Study" ~ remove
df$Answer_ENG %>% str_extract_all("\\nFor Further Study[\\s\\S]+")

df$Answer_ENG<-df$Answer_ENG %>% str_remove_all("\\nFor Further Study[\\s\\S]+") %>% unlist()
df$Answer_ENG %>% tail(15)

# 3 : "Related Articles" ~ remove
df$Answer_ENG %>% str_extract_all("\\nRelated Articles[\\s\\S]+")

df$Answer_ENG<-df$Answer_ENG %>% str_remove_all("\\nRelated Articles[\\s\\S]+") %>% unlist()
df$Answer_ENG

# anything else,,,?