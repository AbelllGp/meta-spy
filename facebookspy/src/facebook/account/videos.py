import logging
from time import sleep
from typing import List

from ...config import Config
from selenium.webdriver.common.by import By
from rich import print as rprint
from ..facebook_base import BaseFacebookScraper
from ...repository import create_person, get_person, person_exists, create_videos


# Logging setup
logging.basicConfig(
    filename=Config.LOG_FILE_PATH,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FacebookVideoScraper(BaseFacebookScraper):
    """
    Scrape user's pictures
    """

    def __init__(self, user_id) -> None:
        super().__init__(user_id, base_url=f"https://www.facebook.com/{user_id}/videos")
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

    def extract_videos_urls(self) -> List[str]:
        """
        Return a list of all the image urls
        """
        extracted_videos_urls = []
        try:
            videos_elements = self._driver.find_elements(
                By.CSS_SELECTOR,
                "a.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv",
            )
            for video_element in videos_elements:
                src_attribute = video_element.get_attribute("href")
                if src_attribute:
                    extracted_videos_urls.append(src_attribute)

        except Exception as e:
            logging.error(f"Error extracting reels URLs: {e}")

        return extracted_videos_urls

    @property
    def is_pipeline_successful(self) -> bool:
        return self.success

    def pipeline(self) -> None:
        """
        Pipeline to run the scraper
        """
        try:
            rprint("[bold]Step 1 of 4 - Load cookies[/bold]")
            self._load_cookies()
            rprint("[bold]Step 2 of 4 - Refresh driver[/bold]")
            self._driver.refresh()
            rprint("[bold]Step 3 of 4 - Scrolling page[/bold]")
            self.scroll_page()
            rprint("[bold]Step 4 of 4 - Extract videos urls[/bold]")
            videos = self.extract_videos_urls()
            rprint(videos)

            if not person_exists(self._user_id):
                create_person(self._user_id)

            person_id = get_person(self._user_id).id
            for video in videos:
                create_videos(video, person_id)

            self._driver.quit()
            self.success = True

        except Exception as e:
            logging.error(f"An error occurred: {e}")