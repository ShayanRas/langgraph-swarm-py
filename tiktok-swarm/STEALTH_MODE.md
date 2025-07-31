# TikTok Stealth Mode Configuration

## Overview

This guide explains the anti-bot detection features implemented to avoid TikTok's bot detection systems.

## Stealth Features

### 1. **Playwright Stealth Integration**
- Uses `playwright-stealth` to override browser fingerprints
- Removes telltale signs of automation (navigator.webdriver, HeadlessChrome UA)
- Implements realistic browser behavior patterns

### 2. **Browser Rotation**
- Randomly selects between Chromium, Firefox, and WebKit
- Each browser has different fingerprints, making detection harder
- Can be configured per-request or use random selection

### 3. **Human-like Behavior**
- Random delays between actions (2-5 seconds)
- Realistic viewport sizes (1920x1080, 1366x768, etc.)
- Randomized user agents and locales
- Time zone randomization

### 4. **Proxy Support**
- Built-in proxy configuration
- Supports authenticated proxies
- Can be enabled globally or per-request

### 5. **Retry Logic with Escalation**
- Automatic retry on bot detection
- Escalates strategies on each retry:
  - Attempt 1: Default settings
  - Attempt 2: Switch to WebKit browser
  - Attempt 3: Non-headless Firefox

## Configuration

### Environment Variables

```bash
# Stealth Level (none, basic, aggressive)
TIKTOK_STEALTH_LEVEL=aggressive

# Browser Settings
TIKTOK_HEADLESS=false  # Non-headless for better stealth
TIKTOK_BROWSER=chromium  # Default browser
TIKTOK_RANDOM_BROWSER=true  # Enable browser rotation

# Session Management
TIKTOK_MAX_SESSIONS_PER_USER=2
TIKTOK_SESSION_TIMEOUT=300

# Proxy Configuration
TIKTOK_PROXY_ENABLED=false
TIKTOK_PROXY_URL=http://user:pass@proxy.example.com:8080
```

### Per-Request Configuration

All TikTok API endpoints now accept stealth parameters:

```json
{
  "count": 10,
  "stealth_mode": true,
  "browser_type": "webkit",
  "headless": false,
  "proxy_url": "http://proxy.example.com:8080"
}
```

## Stealth Levels

### 1. **None** (`stealth_level=none`)
- No stealth measures applied
- Fastest performance
- High risk of detection

### 2. **Basic** (`stealth_level=basic`)
- Basic playwright-stealth applied
- Random user agents and viewports
- Headless mode allowed

### 3. **Aggressive** (`stealth_level=aggressive`)
- Full stealth measures
- Non-headless mode enforced
- Advanced fingerprint spoofing
- WebRTC leak prevention
- Slower but most effective

## Troubleshooting Bot Detection

### If You Get "EmptyResponseException"

1. **Check MS Token**
   - Ensure your MS token is fresh (get a new one)
   - Use incognito mode when getting the token

2. **Try Different Browser**
   ```json
   {
     "browser_type": "webkit",
     "headless": false
   }
   ```

3. **Enable Proxy**
   - Set `TIKTOK_PROXY_ENABLED=true`
   - Configure `TIKTOK_PROXY_URL` with a residential proxy

4. **Reduce Request Rate**
   - Add delays between requests
   - Don't make too many requests quickly

5. **Switch Stealth Level**
   - Try `TIKTOK_STEALTH_LEVEL=basic` if aggressive fails
   - Sometimes less is more

## Best Practices

1. **Use Fresh MS Tokens**
   - Get new tokens regularly
   - Don't reuse tokens across multiple sessions

2. **Rotate Browsers**
   - Keep `TIKTOK_RANDOM_BROWSER=true`
   - Let the system choose browsers automatically

3. **Add Delays**
   - Don't rapid-fire requests
   - Human-like timing is crucial

4. **Monitor Health**
   - Check `/tiktok/session/stats` regularly
   - Look for high failure rates

5. **Use Proxies for Scale**
   - Essential for production use
   - Residential proxies work best

## Example: Maximum Stealth Request

```bash
curl -X POST http://localhost:8000/tiktok/analyze/trending \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 5,
    "stealth_mode": true,
    "browser_type": "firefox",
    "headless": false,
    "proxy_url": "http://user:pass@residential-proxy.com:8080"
  }'
```

## Running Headed Browsers in Docker

### Automatic Xvfb Support

The Docker container now includes Xvfb (X Virtual Framebuffer) for running headed browsers:

1. **Automatic Detection**: The container detects when `TIKTOK_HEADLESS=false` and starts Xvfb automatically
2. **Virtual Display**: Creates a virtual display at `:99` with 1920x1080 resolution
3. **Seamless Operation**: Browsers run on the virtual display (you won't see windows)

### Configuration for Headed Mode

```bash
# .env settings for headed mode in Docker
TIKTOK_STEALTH_LEVEL=aggressive
TIKTOK_HEADLESS=false  # Triggers Xvfb startup
TIKTOK_BROWSER=chromium  # Recommended for Xvfb
```

### Smart Headless Detection

The system now includes smart detection:
- Detects container environments automatically
- Falls back to headless if no display is available
- Warns when forcing headless due to environment constraints

## Performance Considerations

- **Headless mode**: ~300MB per session, faster
- **Non-headless mode**: ~400MB per session, better stealth
- **Xvfb overhead**: Minimal CPU usage for virtual display
- **Browser rotation**: Slight overhead for browser switching
- **Stealth measures**: Add 2-5 seconds per request
- **Proxy usage**: May add latency depending on proxy quality

## Future Improvements

- [ ] Captcha solving integration
- [ ] Session persistence across requests
- [ ] Advanced proxy rotation
- [ ] Machine learning for behavior patterns
- [ ] Custom browser profiles