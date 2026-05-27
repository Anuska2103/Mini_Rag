from src.txt_processing import read_text_file, basic_clean_text, count_text_stats, keyword_search,split_into_paragraphs

text=read_text_file("data/Artificial Intelligence is transfor.txt")

##print("cleaned text:\n", basic_clean_text(text))
print("\ntext summary:\n", count_text_stats(text))
print("\nparagraphs:\n", split_into_paragraphs(text))
print("\nkeyword search:\n", keyword_search(text, "Python is one of the most popular programming languages"))