# TikTok API Error Handling Guide

## Overview

This guide explains the error handling system for TikTok API endpoints and how to interpret different error responses.

## Error Response Format

All error responses follow this structure:

```json
{
  "success": false,
  "error": "Error Type",
  "message": "Detailed error message",
  "raw_error": "Full error string from the API",
  "status_code": -1,
  "possible_causes": [
    "List of potential reasons for the error"
  ],
  "suggestions": [
    "Steps to resolve the issue"
  ]
}
```

## Error Classifications

### 1. **TikTok API Error** (statusCode: -1)

The most common error, indicating a general API failure.

#### Example Response:
```json
{
  "error": "TikTok API Error",
  "message": "TikTok API request failed with statusCode: -1",
  "status_code": -1,
  "possible_causes": [
    "MS token may be invalid or expired",
    "Bot detection triggered",
    "Network connectivity issues",
    "TikTok API temporary failure"
  ],
  "suggestions": [
    "Get a fresh MS token from TikTok",
    "Enable stealth mode and retry",
    "Try a different browser type",
    "Wait a few minutes before retrying"
  ]
}
```

#### Common Scenarios:
- **Invalid MS Token**: Most frequent cause
- **User Not Found**: When userInfo is empty
- **Rate Limiting**: Too many requests
- **Bot Detection**: Automated access detected

### 2. **Authentication Error**

MS token issues or missing authentication.

```json
{
  "error": "Authentication Error",
  "message": "MS token is invalid or missing",
  "possible_causes": ["MS token is missing or invalid"],
  "suggestions": ["Configure a valid TikTok MS token"]
}
```

### 3. **Rate Limit Error**

Too many requests to TikTok API.

```json
{
  "error": "Rate Limit Error",
  "message": "Too many requests to TikTok API",
  "status_code": 429,
  "possible_causes": ["API rate limit exceeded"],
  "suggestions": [
    "Wait 5-10 minutes before retrying",
    "Reduce request frequency"
  ]
}
```

### 4. **Bot Detection Error**

TikTok detected automated access.

```json
{
  "error": "Bot Detection Error",
  "message": "TikTok detected automated access",
  "possible_causes": ["Bot detection triggered", "Captcha required"],
  "suggestions": [
    "Enable stealth mode",
    "Use a different browser type",
    "Add proxy configuration",
    "Get a fresh MS token"
  ]
}
```

### 5. **Session Error**

Issues with browser session management.

```json
{
  "error": "Session Error",
  "message": "Session limit reached or expired",
  "possible_causes": ["Session limit reached", "Session expired"],
  "suggestions": [
    "Wait a moment and retry",
    "Restart the container if issue persists"
  ]
}
```

### 6. **Data Error**

Content not available or invalid parameters.

```json
{
  "error": "Data Error",
  "message": "Requested data not available",
  "possible_causes": [
    "Content not available",
    "Invalid request parameters"
  ],
  "suggestions": [
    "Verify the requested data exists",
    "Check request parameters"
  ]
}
```

## Debugging Tips

### 1. Check Logs

The system logs detailed error information:
```bash
docker-compose logs -f | grep ERROR
```

### 2. Common statusCode Values

- **-1**: Generic failure (auth, rate limit, not found)
- **0**: Success
- **429**: Rate limit exceeded
- **404**: Content not found
- **403**: Access forbidden

### 3. MS Token Issues

Most errors are related to MS tokens. Signs of token issues:
- statusCode: -1 on all requests
- Empty responses
- "userInfo: {}" in errors

**Solution**: Get a fresh MS token from TikTok (in incognito mode)

### 4. Error Patterns

- **Consistent failures**: Usually MS token or rate limit
- **Random failures**: Often bot detection
- **Specific user failures**: User doesn't exist or is private

## Best Practices

### 1. Error Recovery

```python
# Pseudo-code for handling errors
if error["status_code"] == -1:
    if "userInfo: {}" in error["raw_error"]:
        # User doesn't exist
        try_different_user()
    else:
        # Auth or bot detection
        refresh_ms_token()
        enable_stealth_mode()
        retry_with_delays()
```

### 2. Preventive Measures

- **Use fresh MS tokens** regularly
- **Enable stealth mode** for production
- **Add delays** between requests
- **Rotate browsers** to avoid detection
- **Use proxies** for heavy usage

### 3. Testing Errors

Test different error scenarios:
- Invalid username: `@thisisnotarealuser12345`
- Expired MS token: Use an old token
- Rate limiting: Make rapid requests
- Private user: Try a known private account

## Error Monitoring

Monitor these metrics:
- Error rate by type
- statusCode distribution
- Failed usernames
- Session health

Use `/tiktok/session/stats` endpoint to check session status.

## FAQ

**Q: Why do I keep getting statusCode: -1?**
A: Usually means your MS token is invalid. Get a fresh one.

**Q: How often should I refresh MS tokens?**
A: Every 2-4 hours for heavy usage, daily for light usage.

**Q: Can I retry failed requests automatically?**
A: Yes, but add delays and change parameters (browser type, stealth mode).

**Q: What's the difference between user not found and auth error?**
A: Check the raw_error - "userInfo: {}" means user not found, other -1 errors are usually auth.