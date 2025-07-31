# Stealth Mode Limitations

## The Core Limitation

**TikTokApi manages its own Playwright browser instance**, which means we cannot directly control browser launch arguments that are crucial for stealth.

### What We Can't Control

1. **Browser Launch Args**:
   - `--disable-blink-features=AutomationControlled`
   - `--enable-automation` flag removal
   - Other Chrome flags for stealth

2. **Browser-Level Settings**:
   - `ignoreDefaultArgs`
   - Custom executable paths
   - Browser-specific stealth patches

### What We Can Control

1. **Context Options**:
   - User agent
   - Viewport size
   - Locale and timezone
   - Device scale factor
   - Color scheme
   - Permissions

2. **Session Behavior**:
   - Browser type selection (chromium/firefox/webkit)
   - Headless vs headed mode
   - Human-like delays
   - Proxy configuration

## Current Stealth Implementation

### Working Features
✅ Random user agents
✅ Viewport randomization  
✅ Timezone/locale variation
✅ Browser type rotation
✅ Headed mode with Xvfb
✅ Human-like delays
✅ Proxy support

### Limited Features
⚠️ Cannot disable automation flags
⚠️ Cannot apply browser-level stealth patches
⚠️ Limited control over browser fingerprinting
⚠️ playwright-stealth integration is partial

## Workarounds and Recommendations

### 1. Use Multiple Strategies Together
```python
{
  "stealth_mode": true,
  "browser_type": "firefox",  # Firefox has different fingerprints
  "headless": false,          # Headed mode is harder to detect
  "proxy_url": "http://..."   # Residential proxy recommended
}
```

### 2. Rotate Browsers
Firefox and WebKit have different detection signatures than Chromium:
- **Chromium**: Most common, well-optimized
- **Firefox**: Different fingerprint, good for rotation
- **WebKit**: Safari-like, unique characteristics

### 3. Fresh MS Tokens
- Get new MS tokens regularly
- Use different tokens for different sessions
- Don't reuse tokens that triggered detection

### 4. Rate Limiting
- Add delays between requests
- Don't scrape aggressively
- Mimic human browsing patterns

## Future Improvements

To achieve full stealth capabilities, we would need to:

1. **Fork TikTokApi** to expose browser launch options
2. **Create custom wrapper** that manages Playwright directly
3. **Use alternative libraries** that provide more control

## The Bottom Line

While we can't achieve perfect stealth due to TikTokApi's architecture, the combination of:
- Headed mode (via Xvfb)
- Browser rotation
- Proxy usage
- Smart session management

...provides reasonable bot detection evasion for most use cases.

For mission-critical applications requiring maximum stealth, consider using a custom Playwright implementation instead of TikTokApi.