# load library
library(pdftools)
library(dplyr)
library(officer)
library(xml2)

# current location
getwd()
setwd("./raw_data_book/")

# try
# PDF 파일 리스트
temp <- list.files(pattern = "*.pdf")

for (f in temp) {
  var_name <- tools::file_path_sans_ext(f)  # "book1.pdf" → "book1"
  assign(var_name, pdf_text(f))
}

out_dir <- "/Users/haley/Desktop/2025-1/DS1/code/need_preprocessing/Book/"

for (f in temp) {
  var_name <- tools::file_path_sans_ext(f)         # 예: "book1"
  content <- get(var_name)                         # 변수에서 내용 불러오기
  txt_name <- paste0(var_name, ".txt")             # 예: "book1.txt"
  out_path <- file.path(out_dir, txt_name)         # 전체 경로 만들기
  writeLines(content, out_path)                    # 해당 경로에 저장
}


# get docx data in folder
doc <- read_docx("./book12.docx")
xml <- docx_summary(doc)
body_text <- subset(xml, content_type == "paragraph") # only paragraph
cat(paste(body_text$text, collapse = "\n"))
writeLines(body_text$text, "/Users/haley/Desktop/2025-1/DS1/code/need_preprocessing/Book/book12.txt")
