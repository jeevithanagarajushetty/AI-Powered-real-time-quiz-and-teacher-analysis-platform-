from newspaper import Article


def extract_link(url):

    article = Article(url)

    article.download()
    article.parse()

    return article.text