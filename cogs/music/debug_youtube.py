#!/usr/bin/env python3
"""
Debug script for YouTube 403 errors
This script helps identify and fix YouTube streaming issues on VPC servers.
"""

import asyncio
import os
import sys
import yt_dlp
from pathlib import Path

# Add the parent directory to the path so we can import music_streamer
sys.path.append(str(Path(__file__).parent.parent.parent))

from cogs.music.music_streamer import MusicStreamer

async def test_youtube_stream(url):
    """Test YouTube streaming with detailed error reporting"""
    print(f"🔍 Testing YouTube stream for: {url}")
    print("="*60)
    
    # Check if cookies file exists
    cookies_file = "cogs/music/cookies.txt"
    if os.path.exists(cookies_file):
        print(f"✅ Cookies file found: {cookies_file}")
        streamer = MusicStreamer(cookies_file=cookies_file)
    else:
        print(f"⚠️  No cookies file found: {cookies_file}")
        streamer = MusicStreamer()
    
    try:
        # Step 1: Test info extraction
        print("\n📋 Step 1: Testing info extraction...")
        info = await streamer.extract_info(url, download=False)
        
        if not info:
            print("❌ Failed to extract video info")
            return False
        
        print(f"✅ Info extraction successful!")
        print(f"   Title: {info.get('title', 'Unknown')}")
        print(f"   Duration: {streamer.format_duration(info.get('duration', 0))}")
        
        # Step 2: Test audio source creation
        print("\n🎵 Step 2: Testing audio source creation...")
        audio_source = await streamer.get_audio_source(url)
        
        if audio_source:
            print("✅ Audio source created successfully!")
            print("🎉 Stream test PASSED!")
            return True
        else:
            print("❌ Failed to create audio source")
            
            # Step 3: Try alternative methods
            print("\n🔄 Step 3: Trying alternative methods...")
            
            # Method 1: Try different format
            print("   Trying different audio format...")
            try:
                alt_options = streamer.ytdl_format_options.copy()
                alt_options['format'] = 'worstaudio/worst'
                alt_ytdl = yt_dlp.YoutubeDL(alt_options)
                
                loop = asyncio.get_event_loop()
                alt_data = await loop.run_in_executor(
                    None,
                    lambda: alt_ytdl.extract_info(url, download=False)
                )
                
                if alt_data and 'url' in alt_data:
                    print("   ✅ Alternative format worked!")
                    return True
                else:
                    print("   ❌ Alternative format failed")
                    
            except Exception as e:
                print(f"   ❌ Alternative format error: {e}")
            
            # Method 2: Try without cookies
            print("   Trying without cookies...")
            try:
                no_cookie_streamer = MusicStreamer()
                no_cookie_source = await no_cookie_streamer.get_audio_source(url)
                
                if no_cookie_source:
                    print("   ✅ No-cookie method worked!")
                    print("   💡 Your cookies might be causing issues")
                    return True
                else:
                    print("   ❌ No-cookie method failed")
                    
            except Exception as e:
                print(f"   ❌ No-cookie method error: {e}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

async def test_multiple_videos():
    """Test multiple videos to see if it's a general issue"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    ]
    
    print("🧪 Testing multiple videos...")
    print("="*40)
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}/{len(test_urls)}:")
        success = await test_youtube_stream(url)
        results.append(success)
        
        if success:
            print(f"✅ Test {i} PASSED")
        else:
            print(f"❌ Test {i} FAILED")
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == 0:
        print("❌ All tests failed - This is likely a general issue")
        print("💡 Possible solutions:")
        print("   1. Update yt-dlp: pip install --upgrade yt-dlp")
        print("   2. Try different YouTube account")
        print("   3. Check VPC network configuration")
        print("   4. Use VPN or proxy (not recommended)")
    elif passed < total:
        print("⚠️  Some tests failed - This might be video-specific")
        print("💡 Try different videos or check video restrictions")
    else:
        print("🎉 All tests passed! Your setup should work fine.")

def check_system_info():
    """Check system information that might affect YouTube streaming"""
    print("🔧 System Information")
    print("="*30)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if yt-dlp is available
    try:
        import yt_dlp
        print(f"yt-dlp version: {yt_dlp.version.__version__}")
    except ImportError:
        print("❌ yt-dlp not installed")
    except Exception as e:
        print(f"⚠️  Could not get yt-dlp version: {e}")
    
    # Check if discord.py is available
    try:
        import discord
        print(f"discord.py version: {discord.__version__}")
    except ImportError:
        print("❌ discord.py not installed")
    except Exception as e:
        print(f"⚠️  Could not get discord.py version: {e}")
    
    # Check if FFmpeg is available
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"FFmpeg: {version_line}")
        else:
            print("❌ FFmpeg not working properly")
    except FileNotFoundError:
        print("❌ FFmpeg not found")
    except Exception as e:
        print(f"⚠️  Could not check FFmpeg: {e}")

def main():
    print("🐛 YouTube 403 Error Debug Tool")
    print("="*40)
    
    # Check system info first
    check_system_info()
    
    # Test specific video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"\n🎯 Testing specific video: {test_url}")
    success = asyncio.run(test_youtube_stream(test_url))
    
    if not success:
        print(f"\n🔄 Testing multiple videos to identify pattern...")
        asyncio.run(test_multiple_videos())
    
    print(f"\n📋 Debug completed!")
    print("If you're still having issues, try:")
    print("1. Updating yt-dlp: pip install --upgrade yt-dlp")
    print("2. Re-extracting cookies from your local machine")
    print("3. Using a different YouTube account")
    print("4. Checking your VPC's network configuration")

if __name__ == "__main__":
    main()
