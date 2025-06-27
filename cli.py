from core import AparatDownloader

if __name__ == "__main__":
    playlist_id = input("Give me a Aparat playlist id: ")
    quality = input(
        "Give me the quality: (Examples: 144 , 240 , 360 , 480 , 720 , 1080) :"
    )
    for_download_manager = (
        input(
            'Type "y" if you want to create a .txt file that contain all the videos link otherwise '
            'type "n" to start download now:'
        )
        == "y"
    )
    destination_path = input("Give me the destination path (default: ./Downloads):")

    downloader = AparatDownloader(
        playlist_id=playlist_id,
        quality=quality,
        for_download_manager=for_download_manager,
        destination_path=destination_path,
    )
    downloader.download_playlist()
