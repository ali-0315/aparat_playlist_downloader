import requests
import os
import logging


class AparatDownloader:
    def __init__(
        self,
        playlist_id=None,
        quality=None,
        for_download_manager=False,
        destination_path="Downloads",
    ):
        self.playlist_id = playlist_id
        self.quality = quality
        self.for_download_manager = for_download_manager
        self.destination_path = destination_path
        self.current_directory = os.getcwd()
        self.logger = self.setup_logger()

        if not os.path.exists(destination_path):
            os.mkdir(destination_path)

    @staticmethod
    def setup_logger():
        logger = logging.getLogger("AparatDownloader")
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        return logger

    def download_video(self, video_url, output_path):
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            full_output_path = os.path.join(self.current_directory, output_path)
            self.logger.info(f"Downloaded to {full_output_path}")
        else:
            self.logger.error("Failed to download the video.")

    @staticmethod
    def get_video_download_urls(video_uid):
        video_url = (
            f"https://www.aparat.com/api/fa/v1/video/video/show/videohash/{video_uid}"
        )

        video_response = requests.get(video_url)
        video_data = video_response.json()
        return video_data["data"]["attributes"]["file_link_all"]

    def download_playlist(self):
        assert self.playlist_id is not None
        assert self.quality is not None

        api_url = f"https://www.aparat.com/api/fa/v1/video/playlist/one/playlist_id/{self.playlist_id}"
        try:
            response = requests.get(api_url)
            data = response.json()
            videos = data["included"]
            play_list_title = data["data"]["attributes"]["title"]

            if self.for_download_manager:
                self.logger.info(f"Start creating {play_list_title}.txt file")
            else:
                self.logger.info(f"Downloading Playlist {play_list_title} ...")

            if not os.path.exists(f"{self.destination_path}/{play_list_title}"):
                os.mkdir(f"{self.destination_path}/{play_list_title}")

            for video in videos:
                if video["type"] == "Video":
                    video_uid = video["attributes"]["uid"]
                    video_title = video["attributes"]["title"]
                    video_download_link_all = self.get_video_download_urls(video_uid)
                    found_flag = False
                    for video_download_link in video_download_link_all:
                        if video_download_link["profile"] == self.quality + "p":
                            found_flag = True

                            if self.for_download_manager:
                                with open(
                                    f"{self.destination_path}/{play_list_title}.txt",
                                    "a",
                                ) as links_txt:
                                    links_txt.write(
                                        f"{video_download_link['urls'][0]}\n"
                                    )
                            else:
                                download_url = video_download_link["urls"][0]
                                output_path = f"{self.destination_path}/{play_list_title}/{video_title}-{self.quality}p.mp4"
                                self.download_video(download_url, output_path)

                    if not found_flag:
                        video_download_link = video_download_link_all[-1]

                        if self.for_download_manager:
                            self.logger.warning(
                                f"Failed to find video ({video_title}) with selected quality; Add another quality link inside"
                            )
                            with open(f"{play_list_title}.txt", "a") as links_txt:
                                links_txt.write(f"{video_download_link['urls'][0]}\n")
                        else:
                            self.logger.warning(
                                f"Failed to find video ({video_title}) with selected quality; Download another quality inside"
                            )
                            download_url = video_download_link["urls"][0]
                            output_path = f"{self.destination_path}/{play_list_title}/{video_title}-{self.quality}p.mp4"
                            self.download_video(download_url, output_path)

            if self.for_download_manager:
                self.logger.info(f"{play_list_title}.txt created")

        except KeyError:
            self.logger.error("We have some errors in getting API data!")

        except ConnectionError:
            self.logger.error("Please check your internet connection.")

        except Exception as e:
            self.logger.error(e)
