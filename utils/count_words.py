from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from crawler.report import Report

def tokenize_and_count_max(text, word_freq):
    stop_words = set(stopwords.words("english"))
    #nltk to tokenize the text provided
    

    #update the word_frequency dictionary and give the word count of this page
    for token in tokens:
        word = token.lower()
        if word.isalnum() and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    return len(tokens), word_freq




def tokenize(url, texts):
    tokens = word_tokenize(texts)
    for token in tokens:
        word = token.lower()
        if word.isalnum() and word not in stop_words:
            Report.allTokens[word] = Report.allTokens.get(word, 0) + 1
 
    if len(tokens) > Report.maxWords[1]:
        Report.maxWords[0] = url
        Report.maxWords[1] = len(tokens)
        

stop_words = set(stopwords.words("english"))

# This function answers problem 3, and writes it to a file.
def count_common():
    f = open("common_words.txt", "w+")
    counter = 0
    for k, v in sorted(Report.allTokens.items(), key = lambda x: -x[1]):
        if k not in stop_words:
            f.write(k + "=" + str(v))
            f.write("\n")
            counter += 1
        if counter == 50:
            break
    f.close()