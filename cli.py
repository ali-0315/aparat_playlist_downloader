
import argparse
import sys
import asyncio
from core import AparatDownloader


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Aparat Playlist Downloader - دانلودر پلی‌لیست آپارات",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py -p 822374 -q 720 -o ./Downloads
  python cli.py --playlist-id 822374 --quality auto --destination ./MyVideos --links-only
  python cli.py -p 822374 -q 480 --concurrent 5 --preview
        """
    )
    
    parser.add_argument(
        '-p', '--playlist-id',
        type=str,
        help='Aparat playlist ID or full URL'
    )
    
    parser.add_argument(
        '-q', '--quality',
        type=str,
        default='720',
        help='Video quality (144, 240, 360, 480, 720, 1080) or "auto" for best available'
    )
    
    parser.add_argument(
        '-o', '--destination',
        type=str,
        default='./Downloads',
        help='Output directory path (default: ./Downloads)'
    )
    
    parser.add_argument(
        '-l', '--links-only',
        action='store_true',
        help='Create a .txt file with download links instead of downloading'
    )
    
    parser.add_argument(
        '-c', '--concurrent',
        type=int,
        default=3,
        help='Number of concurrent downloads (default: 3, max: 10)'
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Show playlist information without downloading'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--no-log-file',
        action='store_true',
        help='Disable logging to file'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume interrupted downloads (enabled by default)'
    )
    
    return parser


def validate_args(args):
    """Validate command line arguments"""
    errors = []
    
    # Validate playlist ID
    if not args.playlist_id:
        errors.append("Playlist ID is required")
    else:
        # Extract ID from URL if necessary
        if args.playlist_id.startswith('http'):
            try:
                args.playlist_id = args.playlist_id.split('/')[-1]
            except:
                errors.append("Invalid playlist URL format")
        
        if not args.playlist_id.isdigit():
            errors.append("Playlist ID must be numeric")
    
    # Validate quality
    if args.quality != 'auto' and not args.quality.isdigit():
        errors.append("Quality must be a number or 'auto'")
    
    # Validate concurrent downloads
    if args.concurrent < 1 or args.concurrent > 10:
        errors.append("Concurrent downloads must be between 1 and 10")
    
    return errors


def progress_callback(title, progress, downloaded, total):
    """Progress callback for CLI"""
    downloaded_mb = downloaded / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    print(f"\r{title}: {progress:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)


async def main():
    """Main async function"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Interactive mode if no playlist ID provided
    if not args.playlist_id:
        print("🎬 Aparat Playlist Downloader")
        print("=" * 40)
        
        args.playlist_id = input("Enter Aparat playlist ID or URL: ").strip()
        if not args.playlist_id:
            print("❌ Playlist ID is required")
            sys.exit(1)
        
        # Extract ID from URL if necessary
        if args.playlist_id.startswith('http'):
            args.playlist_id = args.playlist_id.split('/')[-1]
        
        # Interactive quality selection
        quality_input = input(f"Enter quality (144, 240, 360, 480, 720, 1080, auto) [default: {args.quality}]: ").strip()
        if quality_input:
            args.quality = quality_input
        
        # Interactive path selection
        path_input = input(f"Enter destination path [default: {args.destination}]: ").strip()
        if path_input:
            args.destination = path_input
        
        # Interactive mode selection
        mode_input = input('Create links file only? (y/N): ').strip().lower()
        args.links_only = mode_input == 'y'
        
        # Preview option
        preview_input = input('Show preview first? (y/N): ').strip().lower()
        args.preview = preview_input == 'y'
    
    # Validate arguments
    errors = validate_args(args)
    if errors:
        print("❌ Validation errors:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    
    # Set up logging level
    import logging
    log_level = getattr(logging, args.log_level)
    
    # Create downloader instance
    auto_quality = args.quality == 'auto'
    quality = '720' if auto_quality else args.quality
    
    downloader = AparatDownloader(
        playlist_id=args.playlist_id,
        quality=quality,
        for_download_manager=args.links_only,
        destination_path=args.destination,
        progress_callback=progress_callback,
        max_concurrent_downloads=args.concurrent,
        auto_quality=auto_quality,
    )
    
    # Configure logging
    downloader.logger = downloader.setup_logger(
        log_level=log_level,
        log_to_file=not args.no_log_file
    )
    
    try:
        # Preview mode
        if args.preview:
            print("\n🔍 Getting playlist information...")
            info = downloader.get_playlist_info()
            
            if info:
                print(f"\n📋 Playlist: {info['title']}")
                print(f"📊 Videos: {info['video_count']}")
                print(f"🆔 ID: {args.playlist_id}")
                
                if info['video_count'] > 0:
                    print(f"\n📹 Video list (showing first 10):")
                    video_count = 0
                    for video in info['videos']:
                        if video['type'] == 'Video' and video_count < 10:
                            print(f"   {video_count + 1}. {video['attributes']['title']}")
                            video_count += 1
                    
                    if info['video_count'] > 10:
                        print(f"   ... and {info['video_count'] - 10} more videos")
                
                if not args.links_only:
                    proceed = input(f"\n⚡ Proceed with download? (Y/n): ").strip().lower()
                    if proceed == 'n':
                        print("👋 Download cancelled")
                        return
            else:
                print("❌ Could not get playlist information")
                return
        
        # Start download
        if args.links_only:
            print(f"\n📄 Creating links file...")
        else:
            print(f"\n⬇️  Starting download...")
            print(f"   Quality: {args.quality}")
            print(f"   Concurrent: {args.concurrent}")
            print(f"   Destination: {args.destination}")
        
        # Execute download
        result = await downloader.download_playlist_async()
        
        if result:
            if args.links_only:
                print(f"\n✅ Links file created successfully!")
            else:
                print(f"\n✅ Playlist downloaded successfully!")
        else:
            print(f"\n❌ Download failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Download interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        downloader.logger.error(f"CLI Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
