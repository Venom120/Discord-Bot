#!/usr/bin/env python3
"""
Local Cookie Extractor for YouTube
Run this script on your local machine (with browser) to extract cookies for your VPC server.
"""

import subprocess
import sys
import os
import json

def check_yt_dlp_local():
    """Check if yt-dlp is installed locally"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_yt_dlp_local():
    """Install yt-dlp locally"""
    print("📦 Installing yt-dlp locally...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], check=True)
        print("✅ yt-dlp installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install yt-dlp: {e}")
        return False

def extract_cookies_local():
    """Extract cookies from local browser"""
    print("🔍 Extracting cookies from your local browser...")
    print("Make sure you're logged into YouTube in your browser!")
    
    browsers = ['chrome', 'firefox', 'edge', 'safari', 'opera', 'brave']
    
    for browser in browsers:
        print(f"\nTrying {browser}...")
        try:
            result = subprocess.run([
                'yt-dlp', 
                '--cookies-from-browser', browser,
                '--cookies', 'cookies.txt',
                '--print', 'cookies'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists('cookies.txt'):
                print(f"✅ Successfully extracted cookies from {browser}!")
                
                # Test the cookies
                if test_cookies_local():
                    print("\n🎉 Cookie extraction successful!")
                    print("📁 cookies.txt has been created")
                    print("\n📋 Next steps:")
                    print("1. Upload cookies.txt to your VPC server")
                    print("2. Place it in your bot's directory")
                    print("3. Restart your bot")
                    return True
                else:
                    print("⚠️  Cookies extracted but may be invalid")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout trying {browser}")
        except Exception as e:
            print(f"❌ Error with {browser}: {e}")
    
    return False

def test_cookies_local():
    """Test if extracted cookies are valid"""
    if not os.path.exists('cookies.txt'):
        return False
    
    try:
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        valid_lines = [line for line in lines if line.strip() and not line.startswith('#')]
        
        if len(valid_lines) > 0:
            print(f"✅ Found {len(valid_lines)} cookie entries")
            return True
        else:
            print("❌ No valid cookie entries found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading cookies: {e}")
        return False

def create_upload_instructions():
    """Create instructions for uploading to VPC"""
    print("\n📤 Upload Instructions for VPC")
    print("="*40)
    print("To upload cookies.txt to your VPC server:")
    print()
    print("METHOD 1: Using SCP")
    print("scp cookies.txt username@your-vpc-ip:/path/to/bot/directory/")
    print()
    print("METHOD 2: Using SFTP")
    print("1. Connect to your VPC: sftp username@your-vpc-ip")
    print("2. Navigate to bot directory: cd /path/to/bot/directory/")
    print("3. Upload: put cookies.txt")
    print()
    print("METHOD 3: Using File Manager (if available)")
    print("1. Use your VPC provider's file manager")
    print("2. Navigate to your bot directory")
    print("3. Upload cookies.txt")
    print()
    print("METHOD 4: Copy and Paste")
    print("1. Open cookies.txt in a text editor")
    print("2. Copy all content")
    print("3. On VPC: nano cookies.txt")
    print("4. Paste the content and save")

def main():
    print("🍪 Local YouTube Cookie Extractor")
    print("="*35)
    print("This script extracts YouTube cookies from your local browser")
    print("for use on your headless VPC server.")
    print()
    
    # Check if yt-dlp is installed
    if not check_yt_dlp_local():
        print("❌ yt-dlp not found locally")
        if not install_yt_dlp_local():
            print("❌ Failed to install yt-dlp")
            return
    
    # Extract cookies
    if extract_cookies_local():
        create_upload_instructions()
    else:
        print("\n❌ Failed to extract cookies from any browser")
        print("Make sure you're logged into YouTube in at least one browser")
        print("Try logging into YouTube and running this script again")

if __name__ == "__main__":
    main()
