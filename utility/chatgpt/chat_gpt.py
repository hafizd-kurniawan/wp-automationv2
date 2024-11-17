from botasaurus.browser import Driver, Wait, browser
from botasaurus.window_size import WindowSize
from botasaurus.user_agent import UserAgent
import time

from utility.utils import Utils

DRIVER = None

DEFAULT_PROMPT = """
kamu adalah seorang ahli SEO dan copywriting, saat ini kamu sedang melakukan paraphrasing dari beberapa website berita lokal dan mancanegara untuk situs berita kamu sendiri.
Berikut adalah hasil scraping dari website berita lain dalam format JSON. Lakukan paraphrasing pada bagian content dengan bahasa yang baik menurut SEO.
Hasilkan output dalam format JSON tanpa tambahan noise teks, penjelasan, atau sejenisnya.
"""


def inject_text_with_js(driver: Driver, element_selector: str, text: str):
    """
    Inject teks langsung ke elemen dengan menggunakan JavaScript.
    """
    js_code = f"""
    document.querySelector("{element_selector}").innerText = `{text}`;
    """
    driver.run_js(js_code)


def send_prompt(driver: Driver, prompt: str):
    """
    Mengirim prompt ke ChatGPT melalui interaksi langsung dengan elemen input.
    """

    full_prompt = f"{DEFAULT_PROMPT} {prompt}"

    # Tunggu hingga elemen input tersedia
    driver.wait_for_element("div[id='prompt-textarea']", wait=60)

    # Inject teks ke elemen input
    inject_text_with_js(driver, "div[id='prompt-textarea']", full_prompt)

    # Klik tombol kirim
    driver.click("button[aria-label='Send prompt']", Wait.LONG)

    time.sleep(2)


def get_response(driver: Driver, prompt: str, timeout: int = 60) -> str:
    """
    Mengambil respons dari ChatGPT setelah prompt dikirim.
    """

    check_and_close_popup(driver)
    send_prompt(driver, prompt)
    hit_latest_response(driver)

    start_time = time.time()
    while time.time() - start_time < timeout:
        driver.select_all("button[aria-label='Copy']", wait=60)
        responses = driver.select_all(".markdown", wait=60)
        if responses:
            return responses[-1].text
        time.sleep(1)
    print("[Error]: Respons ChatGPT timeout.")
    return ""


@browser(
    reuse_driver=True,
    close_on_crash=True,
    user_agent=UserAgent.HASHED,
    window_size=WindowSize.HASHED,
    output=None,
)
def open_chatgpt(driver: Driver, data={}):
    """
    Membuka halaman ChatGPT menggunakan driver dan mengatur driver global.
    """
    driver.google_get("https://chatgpt.com/", bypass_cloudflare=True)
    global DRIVER
    DRIVER = driver


def check_and_close_popup(driver: Driver):
    """
    Memeriksa apakah popup muncul dan menutupnya jika ada.
    """
    try:
        popup = driver.wait_for_element(
            "a[class='mt-5 cursor-pointer text-sm font-semibold text-token-text-secondary underline']",
            wait=Wait.VERY_LONG,
        )
        if popup:
            popup.click()
    except Exception:
        pass


def hit_latest_response(driver: Driver):
    try:
        element = driver.wait_for_element(
            'button[class="cursor-pointer absolute z-10 rounded-full bg-clip-padding border text-token-text-secondary border-token-border-light right-1/2 translate-x-1/2 bg-token-main-surface-primary w-8 h-8 flex items-center justify-center bottom-5"]'
        )
        if element:
            element.click()
    except Exception:
        pass


def run_ai(text: str) -> str:
    """
    Menjalankan ChatGPT untuk memproses prompt yang diberikan.
    """
    try:
        response = get_response(DRIVER, text)
        return Utils.parseResponseGpt(response, text)
    except Exception as e:
        print(f"[Error]: {e}")
        return ""
