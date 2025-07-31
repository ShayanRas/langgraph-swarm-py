# Xvfb Setup for Headed Browsers in Docker

## Understanding Headed Mode on Servers

### Key Concept: "Headed" Doesn't Mean "Visible"

When running on a server/API:
- **Headless mode**: Browser runs without GUI capabilities (detectable by bots)
- **Headed mode + Xvfb**: Browser runs with FULL GUI capabilities but renders to virtual memory (harder to detect)
- **No monitor or desktop needed**: Everything happens in memory

### Why This Matters for Bot Detection

```
Headless Browser              vs    Headed Browser + Xvfb
├─ Missing window.chrome             ├─ Has window.chrome ✓
├─ navigator.webdriver = true        ├─ navigator.webdriver = undefined ✓
├─ No media codecs                   ├─ Full media codecs ✓
├─ Different JS behavior             ├─ Identical to desktop Chrome ✓
└─ Easy to detect                    └─ Very hard to detect ✓
```

## Problem Solved

Previously, when trying to run non-headless browsers in Docker for better bot detection evasion, you would get:
```
Looks like you launched a headed browser without having a XServer running.
```

## Solution

The Docker container now includes:
1. **Xvfb** (X Virtual Framebuffer) - A virtual display server that runs in memory
2. **Automatic detection** - Starts Xvfb when needed
3. **Smart fallback** - Uses headless if display unavailable
4. **No GUI infrastructure needed** - Perfect for servers/APIs

## How It Works

### Visual Flow
```
API Request → Your Server (No Monitor)
                    ↓
            Docker Container
                    ↓
         [Xvfb Virtual Display :99]
                    ↓
         Chromium (Headed Mode)
                    ↓
    Renders to Memory Buffer (Invisible)
                    ↓
            TikTok Sees: Real Browser ✓
                    ↓
            Data Returned to API
```

### Technical Details

1. **On Container Start**: 
   - If `TIKTOK_HEADLESS=false`, the entrypoint script starts Xvfb
   - Creates virtual display at `DISPLAY=:99` (1920x1080 resolution)
   - Browsers render to this virtual display (invisible to you)

2. **Smart Detection**:
   - Detects container environment
   - Checks for existing DISPLAY
   - Falls back to headless if needed

## Quick Start

### For Headless (Default, Recommended for Docker):
```bash
# .env
TIKTOK_HEADLESS=true
```

### For Headed Mode (Better Stealth):
```bash
# .env
TIKTOK_HEADLESS=false
TIKTOK_BROWSER=chromium  # Works best with Xvfb
```

Then rebuild and run:
```bash
docker-compose down
docker-compose up --build
```

## Verification

Check the logs for:
- `🖥️  Starting Xvfb virtual display...` - Xvfb is starting
- `✅ Virtual display started on DISPLAY=:99` - Ready for headed browsers
- `🔲 Running in headless mode` - Using headless (if TIKTOK_HEADLESS=true)

## Resource Usage

- **Xvfb Process**: ~10MB RAM, minimal CPU
- **Headed Browser**: ~400MB per session
- **Headless Browser**: ~300MB per session

## Common Questions

### Q: Do I need a GUI, remote desktop, or VNC?
**A: No!** Xvfb handles everything in memory. The browser renders to a virtual buffer, not a real screen. Your API works exactly the same.

### Q: What's the difference between headless and headed+Xvfb?
**A:**
- **Headless**: Browser runs in limited mode, missing features that websites can detect
- **Headed+Xvfb**: Browser runs in full mode but displays to virtual memory instead of a screen

### Q: Why not just use headless mode?
**A:** TikTok and other sites can detect headless browsers through:
- JavaScript API differences
- Missing browser features
- Behavioral patterns
- Browser fingerprinting

Headed mode with Xvfb is much harder to detect.

### Q: Can I see what the browser is doing?
**A:** Not by default (it's invisible). But you can:
- Take screenshots via Playwright API
- Connect VNC to Xvfb (advanced, rarely needed)
- Check logs for browser activity

## Troubleshooting

1. **Still getting display errors?**
   - Ensure you rebuilt the image: `docker-compose build --no-cache`
   - Check if Xvfb started: `docker-compose logs | grep Xvfb`

2. **Want to force headless?**
   - Set `TIKTOK_HEADLESS=true` in .env
   - Or use `"headless": true` in API requests

3. **Browser crashes?**
   - Try `TIKTOK_BROWSER=chromium` (most stable with Xvfb)
   - Reduce `TIKTOK_MAX_SESSIONS_PER_USER` if low on memory

4. **How to verify it's working?**
   - Check logs for: `✅ Virtual display started on DISPLAY=:99`
   - API responses should include data (not bot detection errors)
   - Session stats endpoint shows active sessions