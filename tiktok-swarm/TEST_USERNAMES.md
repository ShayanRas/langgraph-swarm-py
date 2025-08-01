# Test TikTok Usernames

## Valid Usernames to Test

These are well-known public TikTok accounts you can use for testing:

1. **@khaby.lame** - Popular creator
2. **@charlidamelio** - Dance content
3. **@mrbeast** - Challenge videos
4. **@zachking** - Magic/illusion videos
5. **@bellapoarch** - Music content
6. **@gordonramsayofficial** - Cooking content
7. **@nike** - Brand account
8. **@nba** - Sports content

## Invalid Username Examples

These will return "User Not Found":
- `tybd8p5e2ut3` - Random string
- `test123456789` - Likely not registered
- `@#$%invalid` - Contains invalid characters
- `a` - Too short

## Testing the Endpoint

### Valid User Request:
```json
{
  "username": "gordonramsayofficial",
  "video_count": 10,
  "stealth_mode": true
}
```

### Expected Response:
- User info with follower counts
- Recent videos with performance metrics
- Content analysis and insights

### Invalid User Request:
```json
{
  "username": "thisisnotarealuser12345",
  "video_count": 10
}
```

### Expected Response:
```json
{
  "success": false,
  "username": "thisisnotarealuser12345",
  "error": "User Not Found",
  "message": "The user '@thisisnotarealuser12345' does not exist or is not accessible",
  "suggestions": [
    "Check the username spelling",
    "Ensure the account is public",
    "Try a different username"
  ]
}
```