
import requests
import os
import logging
import asyncio
import aiohttp
import json
import hashlib
from typing import Optional, Callable, Dict, List
from concurrent.futures import ThreadPoolExecutor
import time


class AparatDownloader:
    def __init__(
        self,
        playlist_id=None,
        quality=None,
        for_download_manager=False,
        destination_path="Downloads",
        progress_callback: Optional[Callable] = None,
        max_concurrent_downloads=3,
        auto_quality=False,
    ):
        self.playlist_id = playlist_id
        self.quality = quality
        self.for_download_manager = for_download_manager
        self.destination_path = destination_path
        self.progress_callback = progress_callback
        self.max_concurrent_downloads = max_concurrent_downloads
        self.auto_quality = auto_quality
        self.current_directory = os.getcwd()
        self.logger = self.setup_logger()
        self.history_file = os.path.join(destination_path, ".download_history.json")
        self.download_history = self.load_download_history()

        if not os.path.exists(destination_path):
            os.makedirs(destination_path, exist_ok=True)

    def setup_logger(self, log_level=logging.INFO, log_to_file=True):
        logger = logging.getLogger("AparatDownloader")
        logger.setLevel(log_level)
        
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_to_file:
            log_file = os.path.join(self.destination_path, "downloader.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def load_download_history(self) -> Dict:
        """Load download history to avoid duplicates"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load download history: {e}")
        return {}

    def save_download_history(self):
        """Save download history"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save download history: {e}")

    def get_file_hash(self, file_path: str) -> str:
        """Generate hash for partial download tracking"""
        return hashlib.md5(file_path.encode()).hexdigest()

    def is_download_complete(self, file_path: str, expected_size: int) -> bool:
        """Check if download is complete"""
        if not os.path.exists(file_path):
            return False
        return os.path.getsize(file_path) == expected_size

    def download_video_with_resume(self, video_url: str, output_path: str, video_title: str = ""):
        """Download video with resume capability"""
        try:
            # Get file size first
            head_response = requests.head(video_url)
            total_size = int(head_response.headers.get('content-length', 0))
            
            # Check if already downloaded
            if self.is_download_complete(output_path, total_size):
                self.logger.info(f"File already downloaded: {video_title}")
                return True

            # Check for partial download
            resume_pos = 0
            if os.path.exists(output_path):
                resume_pos = os.path.getsize(output_path)
                if resume_pos >= total_size:
                    self.logger.info(f"File already complete: {video_title}")
                    return True

            # Set up headers for resume
            headers = {}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'
                self.logger.info(f"Resuming download from byte {resume_pos}: {video_title}")

            # Download with resume
            response = requests.get(video_url, headers=headers, stream=True)
            
            if response.status_code in [200, 206]:  # 206 is partial content
                mode = 'ab' if resume_pos > 0 else 'wb'
                
                with open(output_path, mode) as file:
                    downloaded = resume_pos
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress callback
                            if self.progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                self.progress_callback(video_title, progress, downloaded, total_size)

                full_output_path = os.path.join(self.current_directory, output_path)
                self.logger.info(f"Downloaded: {video_title} -> {full_output_path}")
                return True
            else:
                self.logger.error(f"Failed to download {video_title}: HTTP {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error downloading {video_title}: {e}")
            return False

    @staticmethod
    def get_video_download_urls(video_uid):
        """Get video download URLs"""
        video_url = (
            f"https://www.aparat.com/api/fa/v1/video/video/show/videohash/{video_uid}"
        )

        video_response = requests.get(video_url)
        video_data = video_response.json()
        return video_data["data"]["attributes"]["file_link_all"]

    def get_best_quality(self, video_download_links: List[Dict]) -> Dict:
        """Auto-select best available quality"""
        if not video_download_links:
            return None
            
        # Sort by quality (highest first)
        quality_order = ['1080', '720', '480', '360', '240', '144']
        
        for quality in quality_order:
            for link in video_download_links:
                if link["profile"] == f"{quality}p":
                    return link
        
        # Fallback to last available
        return video_download_links[-1]

    def get_playlist_info(self) -> Dict:
        """Get playlist information before downloading"""
        api_url = f"https://www.aparat.com/api/fa/v1/video/playlist/one/playlist_id/{self.playlist_id}"
        
        try:
            response = requests.get(api_url)
            data = response.json()
            
            videos = data["included"]
            playlist_title = data["data"]["attributes"]["title"]
            
            video_count = len([v for v in videos if v["type"] == "Video"])
            
            return {
                "title": playlist_title,
                "video_count": video_count,
                "videos": videos,
                "raw_data": data
            }
        except Exception as e:
            self.logger.error(f"Error getting playlist info: {e}")
            return None

    async def download_playlist_async(self):
        """Async version of download_playlist for better performance"""
        playlist_info = self.get_playlist_info()
        if not playlist_info:
            return False

        playlist_title = playlist_info["title"]
        videos = playlist_info["videos"]
        
        # Check if playlist was already downloaded
        playlist_hash = hashlib.md5(f"{self.playlist_id}_{self.quality}".encode()).hexdigest()
        if playlist_hash in self.download_history:
            self.logger.info(f"Playlist '{playlist_title}' was already downloaded")
            return True

        self.logger.info(f"Starting download of playlist: {playlist_title} ({playlist_info['video_count']} videos)")

        if not os.path.exists(f"{self.destination_path}/{playlist_title}"):
            os.makedirs(f"{self.destination_path}/{playlist_title}", exist_ok=True)

        # Prepare download tasks
        download_tasks = []
        
        for video in videos:
            if video["type"] == "Video":
                video_uid = video["attributes"]["uid"]
                video_title = video["attributes"]["title"]
                
                try:
                    video_download_links = self.get_video_download_urls(video_uid)
                    
                    # Select quality
                    selected_link = None
                    if self.auto_quality:
                        selected_link = self.get_best_quality(video_download_links)
                        actual_quality = selected_link["profile"].replace("p", "") if selected_link else self.quality
                    else:
                        # Find requested quality
                        for link in video_download_links:
                            if link["profile"] == f"{self.quality}p":
                                selected_link = link
                                actual_quality = self.quality
                                break
                        
                        # Fallback to best available
                        if not selected_link:
                            selected_link = self.get_best_quality(video_download_links)
                            actual_quality = selected_link["profile"].replace("p", "") if selected_link else "unknown"
                            self.logger.warning(f"Quality {self.quality}p not found for '{video_title}', using {actual_quality}p")

                    if selected_link:
                        if self.for_download_manager:
                            # Save to text file
                            with open(f"{self.destination_path}/{playlist_title}.txt", "a", encoding='utf-8') as links_txt:
                                links_txt.write(f"{selected_link['urls'][0]}\n")
                        else:
                            # Prepare for download
                            download_url = selected_link["urls"][0]
                            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
                            output_path = f"{self.destination_path}/{playlist_title}/{safe_title}-{actual_quality}p.mp4"
                            
                            download_tasks.append({
                                'url': download_url,
                                'path': output_path,
                                'title': video_title
                            })

                except Exception as e:
                    self.logger.error(f"Error processing video '{video_title}': {e}")

        # Execute downloads with concurrency limit
        if download_tasks and not self.for_download_manager:
            semaphore = asyncio.Semaphore(self.max_concurrent_downloads)
            
            async def download_with_semaphore(task):
                async with semaphore:
                    return await asyncio.get_event_loop().run_in_executor(
                        None, 
                        self.download_video_with_resume,
                        task['url'],
                        task['path'],
                        task['title']
                    )
            
            # Run downloads
            results = await asyncio.gather(*[download_with_semaphore(task) for task in download_tasks])
            
            successful = sum(1 for r in results if r)
            self.logger.info(f"Downloaded {successful}/{len(download_tasks)} videos successfully")

        # Save to history
        self.download_history[playlist_hash] = {
            "playlist_id": self.playlist_id,
            "title": playlist_title,
            "quality": self.quality,
            "download_date": time.time(),
            "video_count": len(download_tasks) if not self.for_download_manager else len([v for v in videos if v["type"] == "Video"])
        }
        self.save_download_history()

        if self.for_download_manager:
            self.logger.info(f"Links file created: {playlist_title}.txt")
        else:
            self.logger.info(f"Playlist download completed: {playlist_title}")

        return True

    def download_playlist(self):
        """Synchronous wrapper for async download"""
        try:
            if asyncio.get_event_loop().is_running():
                # If already in an event loop, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.download_playlist_async())
                    return future.result()
            else:
                return asyncio.run(self.download_playlist_async())
        except Exception as e:
            self.logger.error(f"Error in download_playlist: {e}")
            return False
