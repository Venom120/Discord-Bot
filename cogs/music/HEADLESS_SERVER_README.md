# YouTube Authentication for Headless Ubuntu VPC Servers

This guide is specifically designed for setting up YouTube authentication on headless Ubuntu VPC servers where you cannot install desktop browsers.

## The Problem
On headless servers (like Oracle VPC), you cannot install desktop browsers, so the standard cookie extraction methods don't work. However, your bot still needs YouTube authentication to avoid sign-in prompts.

## Solutions for Headless Servers

### Method 1: Local Cookie Extraction (Recommended)

**Step 1: Extract cookies on your local machine**
1. Download `extract_cookies_local.py` to your local computer
2. Make sure you're logged into YouTube in your browser
3. Run the script:
   ```bash
   python extract_cookies_local.py
   ```
4. This will create `cookies.txt` on your local machine

**Step 2: Upload to your VPC server**
```bash
# Using SCP
scp cookies.txt username@your-vpc-ip:/path/to/bot/directory/

# Or using SFTP
sftp username@your-vpc-ip
cd /path/to/bot/directory/
put cookies.txt
```

**Step 3: Restart your bot**
The bot will automatically detect and use the cookies.

### Method 2: Manual Cookie Creation

**Step 1: Get cookies from browser extension**
1. Install "Cookie Editor" extension in Chrome/Firefox
2. Go to YouTube and log in
3. Open Cookie Editor and export in "Netscape" format
4. Save as `cookies.txt`

**Step 2: Upload to server**
Use SCP, SFTP, or your VPC provider's file manager to upload `cookies.txt`

### Method 3: Using yt-dlp on Local Machine

**Step 1: Install yt-dlp locally**
```bash
pip install yt-dlp
```

**Step 2: Extract cookies**
```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt
```

**Step 3: Upload to server**
Transfer the generated `cookies.txt` to your VPC server.

## File Structure on VPC Server

After setup, your VPC server should have:
```
Discord-Bot/
├── cogs/
│   └── music/
│       ├── Music.py
│       ├── music_streamer.py
│       └── cookies.txt          # Uploaded from local machine
├── main.py
├── config.json                  # Auto-generated
└── .gitignore                   # Updated to exclude cookies
```

## Testing on VPC Server

**Step 1: Run the headless cookie script**
```bash
cd /path/to/bot/directory/
python cogs/music/get_youtube_cookies.py
```

**Step 2: Test authentication**
```bash
python cogs/music/test_youtube_auth.py
```

**Step 3: Start your bot**
```bash
python main.py
```

## Troubleshooting

### Cookies Not Working?
1. **Check file location**: Ensure `cookies.txt` is in the correct directory
2. **Verify file format**: Should be in Netscape format
3. **Check permissions**: Make sure the bot can read the file
4. **Re-extract cookies**: Cookies expire, re-extract from local machine

### Still Getting Sign-in Prompts?
1. **Update yt-dlp**: `pip install --upgrade yt-dlp`
2. **Check bot logs**: Look for authentication messages
3. **Try different account**: Use a different YouTube account
4. **Verify cookies**: Run the test script to check if cookies are valid

### File Transfer Issues?
1. **SCP not working**: Check SSH key permissions
2. **SFTP issues**: Verify username and path
3. **Permission denied**: Check file permissions on server

## Security Best Practices

1. **Use dedicated account**: Create a YouTube account specifically for your bot
2. **Secure file transfer**: Use SSH/SCP for secure transfers
3. **Regular updates**: Re-extract cookies every few weeks
4. **Monitor usage**: Check bot logs for authentication issues

## Alternative Solutions

If cookie authentication continues to fail:

### Option 1: YouTube Data API
- Get API key from Google Cloud Console
- Modify bot to use API instead of yt-dlp
- More reliable but requires API key management

### Option 2: Different Music Sources
- Use Spotify, SoundCloud, or other sources
- May require different authentication methods

### Option 3: Proxy Service
- Use a proxy service (not recommended for production)
- May violate YouTube's terms of service

## Quick Commands Reference

```bash
# On local machine - extract cookies
python extract_cookies_local.py

# Upload to VPC
scp cookies.txt username@vpc-ip:/bot/directory/

# On VPC - test setup
python cogs/music/get_youtube_cookies.py
python cogs/music/test_youtube_auth.py

# Start bot
python main.py
```

## Support

If you're still having issues:
1. Check the bot logs for specific error messages
2. Verify your yt-dlp version is up to date
3. Try extracting cookies from a different browser
4. Consider using a different YouTube account
5. Check your VPC's network configuration

## File Locations

- **Local machine**: Run `extract_cookies_local.py` to create `cookies.txt`
- **VPC server**: Place `cookies.txt` in your bot's root directory
- **Configuration**: `config.json` is auto-generated on first run
- **Logs**: Check console output for authentication messages
