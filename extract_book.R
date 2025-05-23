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

for (f in temp) {
  var_name <- tools::file_path_sans_ext(f)     # "book1"
  content <- get(var_name)                     # book1이라는 변수에서 가져옴
  txt_name <- paste0(var_name, ".txt")         # "book1.txt"
  writeLines(content, txt_name)
}


# get docx data in folder
doc <- read_docx("./book12.docx")
xml <- docx_summary(doc)
body_text <- subset(xml, content_type == "paragraph") # only paragraph
cat(paste(body_text$text, collapse = "\n"))
writeLines(body_text$text, "book12.txt")
