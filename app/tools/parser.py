from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):

    def initialize(self):
        self.users = []
        self.scores = []
        self.nextDataIsUser = False
        self.nextDataIsScore = False

    def handle_starttag(self, tag, attrs):
        if (tag == "section"):
            for attr in attrs:
                if ("highscore__user-nick" in attr[1]):
                    self.nextDataIsUser = True

        if (tag == "span"):
            for attr in attrs:
                if ("highscore__score" in attr[1]):
                    self.nextDataIsScore = True

    def handle_data(self, data):
        if (self.nextDataIsUser):
            self.nextDataIsUser = False
            self.users.append(data)

        if (self.nextDataIsScore):
            self.nextDataIsScore = False
            score = str(data).replace(u"\xa0", "").replace("points","").replace(",","").strip()
            self.scores.append(score)
 
    def results(self):
        results = []
        for entry in zip(self.users, self.scores):
            results.append(entry)
        return results
                    

# with open ("pag2.html", "r") as f:
#     parser = MyHTMLParser()
#     parser.initialize()
#     content = f.read()
#     parser.feed(content)
#     print(parser.users)
#     for score in parser.scores:
#         print(int(score))