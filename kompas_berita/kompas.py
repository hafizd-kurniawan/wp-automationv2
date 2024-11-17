from dataclasses import dataclass
from selenium import webdriver
from typing import Optional
import time

from utility.chatgpt import run_ai, open_chatgpt, DEFAULT_PROMPT
from utility.selenium import ConvertWebElement, Wait
from utility.selenium import SeleniumDriver
from utility.utils import Utils


@dataclass
class Article:
    url: str
    category: str
    tag: str
    title: str
    featuredImage: str
    excerpt: Optional[str] = None
    content: Optional[str] = None


class ArtilceV2(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)


class ScrapingArtilceV1(SeleniumDriver):
    def __init__(self, driver: webdriver, scrapingPath: dict[str:str]):
        super().__init__(driver)
        self.sP = scrapingPath
        self.foundImageDescription = []

    def extractArticle(self, category: str) -> list[Article]:
        """
        method ini akan mengamabil semua sub artikel di halaman depan,
        kemudian akan mengambil url,title, dll
        """
        articles = self.getElementList(self.sP["xpArticlesV1"], "xpath")
        dataArticles = []
        print("---------------")
        print(category)
        for article in articles:
            innerHtml = article.get_attribute("innerHTML")
            articleElement = ConvertWebElement.toLxml(innerHtml)

            # Buat objek Article untuk menyimpan data
            articleData = Article(
                url=self.extractUrl(articleElement),
                category=category,
                tag=self.extractTag(articleElement),
                title=self.extractTitle(articleElement),
                featuredImage=self.extractFeaturedImage(articleElement),
                excerpt=self.extractExcerpt(articleElement),
                content=None,
            )
            dataArticles.append(articleData)
        return dataArticles

    #########################
    # ekstrak detail artikel
    #########################
    def extractDetailArticleHeaderH1(self, element) -> dict[str:str]:
        h1Elements = element.xpath(self.sP["xpDetailArticleTitle"])
        if h1Elements:
            return {"tag": "h1", "content": h1Elements[0]}

    def extractDetailArticleHeaderImage(self, element) -> dict[str:str]:
        imgElements = element.xpath(self.sP["xpDetailArticleImage"])
        if imgElements:
            img_src = imgElements[0].get("src", "")
            img_alt = imgElements[0].get("alt", "")
            return {"tag": "img", "src": img_src, "alt": img_alt}

    def extractDetailArticleParagraph(self, tag, text) -> dict[str:str]:
        text = text.replace("KOMPAS.com", "PT. XYZ")
        if text:
            return {"tag": tag, "content": text}

    def extractDetailArticleImage(self, element) -> dict[str:str]:
        imgSrc = element.get("src", "")
        if imgSrc:
            return {"tag": "img", "src": imgSrc, "alt": element.get("alt", "")}

    def extractDetailArticleLi(self, tag, text) -> dict[str:str]:
        return {"tag": tag, "content": text}

    def extractDetailArticleDiv(self, element) -> dict[str:str]:
        el = element.xpath(self.sP["xpPhotoWrap"])
        if len(el) != 0:
            imgElement = el[0].xpath(self.sP["xpImageDescription"])
            if imgElement is not None:
                imgElement = imgElement[0]
                imgSrc = imgElement.get("src", "")
                # if imgSrc in self.foundImageDescription:
                #     print("found return")
                #     return

                return {
                    "tag": "img",
                    "src": imgSrc,
                    "alt": imgElement.get("alt", ""),
                }

    def extractDetailArticleHeading(self, tag, text) -> dict[str:str]:
        return {"tag": tag, "content": text}

    def extractDetailArticleContent(self, pageTree) -> list[str]:
        divArticles = pageTree.xpath(self.sP["xpDetailArticles"])
        content = []
        foundImageContent = []

        # header H1 and header img
        content.append(self.extractDetailArticleHeaderH1(pageTree))
        content.append(self.extractDetailArticleHeaderImage(pageTree))

        if not divArticles:
            print("Div utama artikel tidak ditemukan.")

        # Mendapatkan konten artikel dengan
        # mengiterasi semua element
        for element in divArticles[0].iter():
            tag = element.tag

            # Mengabaikan elemen yang memiliki tag selain yg sudah ditenukan
            if tag not in self.sP["targetTag"]:
                continue
            # Mengabaikan elemen yang memiliki atribut tertentu
            if any(attr in element.attrib for attr in self.sP["xpIgnoreAttrib"]):
                continue

            text = element.text_content().strip()
            if tag == "img":
                elImg = self.extractDetailArticleImage(element)
                srcImg = elImg.get("src", "") if elImg is not None else None
                if elImg is not None and srcImg not in foundImageContent:
                    content.append(elDiv)
                    foundImageContent.append(srcImg)
                continue
            if tag == "p":
                elP = self.extractDetailArticleParagraph(tag, text)
                if elP is not None:
                    content.append(elP)
                continue
            if tag == "div":
                elDiv = self.extractDetailArticleDiv(element)
                srcImg = elDiv.get("src", "") if elDiv is not None else None
                if elDiv is not None and srcImg not in foundImageContent:
                    content.append(elDiv)
                    foundImageContent.append(srcImg)
                continue
            if tag in ["h2", "h3", "h4", "h5", "h6"]:
                elHeading = self.extractDetailArticleHeading(tag, text)
                if elHeading is not None:
                    content.append(elHeading)
                continue
            if tag == "li":
                elLi = self.extractDetailArticleLi(tag, text)
                if elLi is not None:
                    content.append(elLi)
                continue
        # hapus daftar image di artikel
        # self.foundImageDescription.clear()
        return content

    ##############################
    # ekstrak artikel di dasboard halaman utama
    ##############################
    def extractUrl(self, element) -> list[str]:
        url = element.xpath(self.sP["xpArticleLink"])
        return Utils.joinText(url)

    def extractTag(self, element):
        tag = element.xpath(self.sP["xpArticleTag"])
        return Utils.joinText(tag)

    def extractTitle(self, element):
        title = element.xpath(self.sP["xpArticleTitle"])
        title = Utils.joinText(title)
        return Utils.cleanText(title)

    def extractFeaturedImage(self, element):
        image = element.xpath(self.sP["xpArticleFeaturedImage"])
        return Utils.joinText(image)

    def extractExcerpt(self, element):
        text = element.xpath(self.sP["xpArticleExcerpt"])
        if text is not None:
            return Utils.joinText(text)
        return None

    ################################
    # Runner
    ################################
    def extractDetailArticle(self, url: str):
        if "https://video.kompas.com" in url:
            return
        print(url)
        self.driver.get(url)
        Wait.waitMedium()
        pageTree = ConvertWebElement.toLxml(self.driver.page_source)
        content = self.extractDetailArticleContent(pageTree)
        print("Content Scraping")
        print("------------------")
        print(content)
        print("\n")
        return content

    def saveToDatabse(self, category: str):
        # articles adalah sebuah list of @dataclass
        articles = self.extractArticle(category)
        for article in articles:
            content = self.extractDetailArticle(article.url)
            #################################
            # parapasing content
            #################################
            article.content = run_ai(content)
            print("Content praphasing")
            print("------------------")
            print(article.content)
            print("\n")
            print(article)
            print("\n\n")


class Kompas(SeleniumDriver):
    def __init__(
        self,
        driver: webdriver,
        sourceUrl: dict[str:str],
        scrapingPath: dict[str:str],
    ):
        super().__init__(driver)
        self.driver = driver
        self.sourceUrl = sourceUrl
        self.scrapingPath = scrapingPath
        self.articleV1 = ScrapingArtilceV1(driver, scrapingPath)

    def parse(self, category):
        done = 0
        if category in ["otomotif", "teknologi", "traveling"]:
            self.articleV1.saveToDatabse(category)

    def startParse(self):
        ##############
        # mulai bukan chatgpt agar terhindar dari cloudflare
        ##############
        open_chatgpt()
        for category, url in self.sourceUrl.items():
            self.driver.get(url)
            self.parse(category)
