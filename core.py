
import logging
import os
import re
import requests


def sanitize_filename(name, max_length=150):
    """Make a filename or folder name safe for Windows."""
    name = str(name or "").strip()

    # Replace characters that Windows does not allow.
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "-", name)

    # Remove trailing spaces and dots.
    name = name.rstrip(" .")

    # Avoid empty names.
    if not name:
        name = "Aparat"

    # Windows reserved device names.
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    first_part = name.split(".")[0].upper()
    if first_part in reserved:
        name = "_" + name

    # Avoid excessively long path components.
    name = name[:max_length].rstrip(" .")

    return name or "Aparat"


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
        self.destination_path = os.path.abspath(destination_path)
        self.current_directory = os.getcwd()

        self.logger = self.setup_logger()

        os.makedirs(self.destination_path, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            )
        })

    @staticmethod
    def setup_logger():
        logger = logging.getLogger("AparatDownloader")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # Prevent duplicate log messages.
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - "
                "%(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def download_video(self, video_url, output_path):
        """Download one video to the specified path."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Stream to a temporary file so failed downloads do not
            # leave an apparently complete video behind.
            temp_path = output_path + ".part"

            with self.session.get(
                video_url,
                stream=True,
                timeout=(20, 60),
            ) as response:
                response.raise_for_status()

                with open(temp_path, "wb") as file:
                    for chunk in response.iter_content(
                        chunk_size=1024 * 256
                    ):
                        if chunk:
                            file.write(chunk)

            os.replace(temp_path, output_path)

            self.logger.info("Downloaded to %s", output_path)
            return True

        except requests.RequestException:
            self.logger.exception(
                "Network error while downloading: %s",
                output_path,
            )
        except OSError:
            self.logger.exception(
                "File system error while saving: %s",
                output_path,
            )
        except Exception:
            self.logger.exception(
                "Unexpected download error: %s",
                output_path,
            )

        return False

    def get_video_download_urls(self, video_uid):
        """Retrieve available download links for a video."""
        video_url = (
            "https://www.aparat.com/api/fa/v1/video/video/show/"
            f"videohash/{video_uid}"
        )

        response = self.session.get(video_url, timeout=(20, 30))
        response.raise_for_status()

        video_data = response.json()
        return (
            video_data.get("data", {})
            .get("attributes", {})
            .get("file_link_all", [])
        )

    @staticmethod
    def _get_direct_url(link):
        """Return a usable direct URL from an API link entry."""
        if not isinstance(link, dict):
            return None

        urls = link.get("urls")

        if isinstance(urls, str):
            return urls or None

        if isinstance(urls, list):
            for url in urls:
                if isinstance(url, str) and url.strip():
                    return url.strip()

        # Some API responses may provide a direct URL differently.
        for key in ("url", "link"):
            value = link.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        return None

    def download_playlist(self):
        """Download all videos in an Aparat playlist."""
        if not self.playlist_id:
            self.logger.error("Playlist ID is missing.")
            return

        if self.quality is None:
            self.logger.error("Video quality is missing.")
            return

        quality = str(self.quality).strip().lower()
        if quality.endswith("p"):
            quality = quality[:-1]

        api_url = (
            "https://www.aparat.com/api/fa/v1/video/playlist/one/"
            f"playlist_id/{self.playlist_id}"
        )

        try:
            response = self.session.get(
                api_url,
                timeout=(20, 30),
            )

            self.logger.info(
                "Playlist API status: %s",
                response.status_code,
            )

            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict):
                self.logger.error(
                    "Unexpected playlist API response: "
                    "expected a JSON object."
                )
                return

            self.logger.info(
                "Playlist API response keys: %s",
                list(data.keys()),
            )

            playlist_data = data.get("data", {})
            attributes = playlist_data.get("attributes", {})
            playlist_title = attributes.get("title", "Aparat_Playlist")

            safe_playlist_title = sanitize_filename(playlist_title)

            videos = data.get("included", [])
            if not isinstance(videos, list):
                self.logger.error(
                    "Unexpected playlist structure: "
                    "'included' is not a list."
                )
                return

            playlist_path = os.path.join(
                self.destination_path,
                safe_playlist_title,
            )

            if not self.for_download_manager:
                os.makedirs(playlist_path, exist_ok=True)
            else:
                os.makedirs(self.destination_path, exist_ok=True)

            txt_path = os.path.join(
                self.destination_path,
                safe_playlist_title + ".txt",
            )

            if self.for_download_manager:
                self.logger.info(
                    "Creating download links file: %s",
                    txt_path,
                )
            else:
                self.logger.info(
                    "Downloading playlist: %s",
                    playlist_title,
                )

            video_items = [
                item for item in videos
                if isinstance(item, dict)
                and item.get("type") == "Video"
            ]

            if not video_items:
                self.logger.warning(
                    "No video entries were found in the playlist API response."
                )
                return

            self.logger.info(
                "Found %s video entries.",
                len(video_items),
            )

            successful = 0
            failed = 0
            skipped = 0

            # Write a fresh link list for each new run.
            links_file = (
                open(txt_path, "w", encoding="utf-8")
                if self.for_download_manager
                else None
            )

            try:
                for index, video in enumerate(video_items, start=1):
                    video_attributes = video.get("attributes", {})
                    video_uid = video_attributes.get("uid")
                    video_title = video_attributes.get(
                        "title", f"video_{index}"
                    )

                    if not video_uid:
                        self.logger.warning(
                            "[%s/%s] Missing video UID; skipping.",
                            index,
                            len(video_items),
                        )
                        skipped += 1
                        continue

                    safe_video_title = sanitize_filename(video_title)

                    self.logger.info(
                        "[%s/%s] Processing: %s",
                        index,
                        len(video_items),
                        video_title,
                    )

                    try:
                        available_links = self.get_video_download_urls(
                            video_uid
                        )

                        if not isinstance(available_links, list):
                            raise ValueError(
                                "Unexpected video download-link structure."
                            )

                        if not available_links:
                            self.logger.warning(
                                "No download links found for %s.",
                                video_title,
                            )
                            failed += 1
                            continue

                        # Match the requested quality, such as 720p.
                        target_profile = quality + "p"
                        selected_link = next(
                            (
                                item for item in available_links
                                if isinstance(item, dict)
                                and str(item.get("profile", "")).lower()
                                == target_profile
                                and self._get_direct_url(item)
                            ),
                            None,
                        )

                        if selected_link is None:
                            # Preserve the original fallback behavior:
                            # use the last usable link if possible.
                            selected_link = next(
                                (
                                    item for item in reversed(available_links)
                                    if self._get_direct_url(item)
                                ),
                                None,
                            )

                            if selected_link is None:
                                self.logger.warning(
                                    "No usable download URL for %s.",
                                    video_title,
                                )
                                failed += 1
                                continue

                            self.logger.warning(
                                "Quality %s unavailable for %s; "
                                "using another available quality.",
                                target_profile,
                                video_title,
                            )

                        download_url = self._get_direct_url(selected_link)

                        if self.for_download_manager:
                            links_file.write(download_url + "\n")
                            links_file.flush()
                            successful += 1
                            continue

                        output_filename = (
                            f"{index:03d} - {safe_video_title} - "
                            f"{quality}p.mp4"
                        )
                        output_path = os.path.join(
                            playlist_path,
                            output_filename,
                        )

                        if self.download_video(download_url, output_path):
                            successful += 1
                        else:
                            failed += 1

                    except Exception:
                        # A single bad video should not stop the playlist.
                        self.logger.exception(
                            "Failed to process video: %s",
                            video_title,
                        )
                        failed += 1
                        continue

            finally:
                if links_file is not None:
                    links_file.close()

            self.logger.info(
                "Playlist finished. Total: %s, successful: %s, "
                "failed: %s, skipped: %s",
                len(video_items),
                successful,
                failed,
                skipped,
            )

            if self.for_download_manager:
                self.logger.info(
                    "Download links saved to: %s",
                    txt_path,
                )

        except requests.RequestException:
            self.logger.exception(
                "Could not retrieve playlist information. "
                "Check your connection or the API response."
            )
        except (ValueError, TypeError):
            self.logger.exception(
                "Could not parse the playlist API response."
            )
        except Exception:
            self.logger.exception(
                "Unexpected playlist processing error."
            )
