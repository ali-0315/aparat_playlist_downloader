import requests
import os

dir_path = os.getcwd() + '/Downloads'
os.makedirs(dir_path, exist_ok=True)

def download_video(video_url, output_path):
    response = requests.get(video_url, stream=True)

    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f'{output_path} Downloaded!')
    else:
        print('Failed to download the video.')

playlist_id = input('Give me a Aparat playlist id: ')
api_url = f'https://www.aparat.com/api/fa/v1/video/playlist/one/playlist_id/{playlist_id}'
quality = input('Give me the quality: (Examples: 144 , 240 , 360 , 480 , 720 , 1080) :')
for_download_manager = input('Type "y" to create a .txt file for videos links or '
                             '"n" to download videos:') == 'y'
response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()
    videos = data['included']
    play_list_title = data['data']['attributes']['title']
    if for_download_manager:
        print(f'start creating {play_list_title}.txt file')
    else:
        print(f'Downloading Playlist {play_list_title} ...')

    os.makedirs(f'{dir_path}/{play_list_title}', exist_ok=True)
    if os.path.isfile(f'{dir_path}/{play_list_title}/{play_list_title}.txt'):
        os.remove(f'{dir_path}/{play_list_title}/{play_list_title}.txt')

    for video in videos:
        if video['type'] == 'Video':
            video_id = video['attributes']['uid']
            video_title = video['attributes']['title']
            video_url = f'https://www.aparat.com/api/fa/v1/video/video/show/videohash/{video_id}'
            video_response = requests.get(video_url)
            if video_response.status_code == 200:
                video_data = video_response.json()
                video_download_link_all = video_data['data']['attributes']['file_link_all']
                found_flag = False
                for video_download_link in video_download_link_all:
                    if video_download_link['profile'] == quality + 'p':
                        found_flag = True
                        if for_download_manager:
                            with open(f'{dir_path}/{play_list_title}/{play_list_title}.txt', 'a') as links_txt:
                                links_txt.write(f'{video_download_link["urls"][0]}\n')
                        else:
                            download_url = video_download_link['urls'][0]
                            output_path = f'{dir_path}/{play_list_title}/{video_title}-{quality}p.mp4'
                            download_video(download_url, output_path)
                if not found_flag:
                    video_download_link = video_download_link_all[-1]
                    if for_download_manager:
                        print(f'Failed to find video ({video_title}) with selected quality; use another quality link inside')
                        with open(f'{dir_path}/{play_list_title}/{play_list_title}.txt', 'a') as links_txt:
                            links_txt.write(f'{video_download_link["urls"][0]}\n')
                    else:
                        print(f'Failed to find video ({video_title}) with selected quality; Download another quality inside')
                        download_url = video_download_link['urls'][0]
                        output_path = f'{dir_path}/{play_list_title}/{video_title}-{quality}p.mp4'
                        download_video(download_url, output_path)
    if for_download_manager:
        print(f'{play_list_title}.txt created')
else:
    print('We have some errors in getting API data!')
