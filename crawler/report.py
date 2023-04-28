class Report:
    allTokens = dict()
    scraped = set()  # set of urls we've extracted from or are blacklisted
    unique_urls = set()
    maxWords = ["", 0] # maxWords[0] is URL, maxWords[1] is number of words

    def __init__(self):
        self.allTokens = dict()
        self.scraped = set()
        self.unique_urls = set()
        self.maxWords = ["", 0]

    @staticmethod
    def printReport():
        f = open("report.txt", "a")

        for word in Report.scraped:
            f.write(word + "\n")

        f.write("\n\n\n\nUNIQUE URLS")

        for word in Report.unique_urls:
            f.write(word + "\n")


        f.write("\n\n\n\nLONGEST PAGE(IN TERMS OF NUMBER OF WORDS)\n")
        f.write("Website URL: " + str(Report.maxWords[0]) + "\n")
        f.write("Number of words: " + str(Report.maxWords[1]) + "\n")

        f.close()

    