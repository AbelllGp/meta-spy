import logging
from time import sleep
from typing import List

from ...config import Config
from selenium.webdriver.common.by import By
from ..facebook_base import BaseFacebookScraper
from rich import print as rprint
from ...repository import create_person, get_person, person_exists, create_reels


# Logging setup
logging.basicConfig(
    filename=Config.LOG_FILE_PATH,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FacebookReelsScraper(BaseFacebookScraper):
    """
    Scrape user's pictures
    """

    def __init__(self, user_id) -> None:
        super().__init__(user_id, base_url=f"https://www.facebook.com/{user_id}/reels")
        self.success = False

    def scroll_page(self) -> None:
        """
        Scrolls the page to load more friends from a list
        """
        try:
            last_height = self._driver.execute_script(
                "return document.body.scrollHeight"
            )
            consecutive_scrolls = 0

            while consecutive_scrolls < Config.MAX_CONSECUTIVE_SCROLLS:
                self._driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )

                sleep(Config.SCROLL_PAUSE_TIME)
                new_height = self._driver.execute_script(
                    "return document.body.scrollHeight"
                )

                if new_height == last_height:
                    consecutive_scrolls += 1
                else:
                    consecutive_scrolls = 0

                last_height = new_height

        except Exception as e:
            logging.error(f"Error occurred while scrolling: {e}")

    def extract_reels_urls(self) -> List[str]:
        """
        Return a list of all the image urls
        """
        extracted_reels_urls = []
        try:
            reels_elements = self._driver.find_elements(
                By.CSS_SELECTOR,
                "a.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1lliihq.xqitzto.x1n2onr6.xh8yej3",
            )
            for reel_element in reels_elements:
                src_attribute = reel_element.get_attribute("href")
                if src_attribute:
                    extracted_reels_urls.append(src_attribute)

        except Exception as e:
            logging.error(f"Error extracting reels URLs: {e}")

        return extracted_reels_urls

    @property
    def is_pipeline_successful(self) -> bool:
        return self.success

    def pipeline(self) -> None:
        """
        Pipeline to run the scraper
        """
        try:
            self._load_cookies()
            self._driver.refresh()
            self.scroll_page()
            reels = self.extract_reels_urls()
            rprint(reels)

            if not person_exists(self._user_id):
                create_person(self._user_id)

            person_id = get_person(self._user_id).id

            for reel in reels:
                create_reels(reel, person_id)

            self._driver.quit()
            self.success = True

        except Exception as e:
            logging.error(f"An error occurred: {e}")
