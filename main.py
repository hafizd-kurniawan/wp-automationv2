"""
TODO:
1. kita bikin konten/web scrapaing dulu
   - kemungkinan excerpt sudah di generate atau sudah di scraping
   - featured_images sudah tergenerate atau sudah di scraping
   - images sudah tergenerate atau sudah di scraping
   - featured_images, images perlu di download
2. kita buat post
   - setelah done untuk poin diatas buat sebuah json dan upload
    - simpan nama title dan template path nya
   - membuat sebuh post dengan rest api wordpress
   - open selenium, open as elementor untuk post nya
   - masukkan template ke post


#    buat post dulu tapi kita

"""

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from kompas_berita import Kompas
from database import migrate
from config import Config


def main():
    # define config
    configFile = "./config/config.toml"
    config = Config(configFile)
    dataConfig = config.loadConfig()

    # define database
    DATABASE_URL = f"sqlite:///{dataConfig.databaseName}"
    session = migrate(DATABASE_URL)

    # define selenium driver
    options = Options()
    options.headless = True
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disk-cache-size=4096")
    options.add_argument("window-size=800x600")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(), options=options)

    # define webscraping kompas
    kompas = Kompas(
        driver,
        dataConfig.KompasArticles,
        dataConfig.KompasScraping,
    )
    kompas.startParse()


if __name__ == "__main__":
    main()
