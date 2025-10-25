# 🔐 Environment Configuration Guide

## Quick Setup

1. **Copy the example file to create your `.env`:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` and add your API keys:**
   ```bash
   nano .env  # or use any text editor
   ```

3. **Fill in your actual API keys:**
   ```env
   ZAI_API_KEY=your_actual_zai_api_key_here
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ZAI_API_KEY` | z.ai API key for GLM-4.5-air (Agent A) | `bfc0ba4de...` |
| `GEMINI_API_KEY` | Google Gemini API key (Agent B) | `AIzaSyD_S...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZAI_BASE_URL` | z.ai API base URL | `https://api.z.ai/api/coding/paas/v4` |
| `GLM_MODEL` | GLM model name | `glm-4.5-air` |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `MAX_TURN_LENGTH` | Maximum response length | `10000` |

## Getting API Keys

### 1. z.ai API Key (for GLM-4.5-air)

1. Visit [https://z.ai](https://z.ai)
2. Sign up or log in
3. Navigate to API section
4. Generate a new API key
5. Copy the key to your `.env` file as `ZAI_API_KEY`

### 2. Google Gemini API Key

1. Visit [https://ai.google.dev/](https://ai.google.dev/)
2. Click "Get API Key" or "Get started"
3. Sign in with your Google account
4. Create a new project (if needed)
5. Generate an API key
6. Copy the key to your `.env` file as `GEMINI_API_KEY`

## Security Best Practices

### ✅ DO:
- ✅ Keep `.env` in `.gitignore` (already configured)
- ✅ Use different API keys for development and production
- ✅ Rotate API keys regularly
- ✅ Use environment-specific `.env` files (`.env.development`, `.env.production`)
- ✅ Share `env.example` (without actual keys) with your team

### ❌ DON'T:
- ❌ Commit `.env` to Git
- ❌ Share API keys in chat/email
- ❌ Use production keys in development
- ❌ Hardcode API keys in source code
- ❌ Push `.env` to GitHub/GitLab

## Troubleshooting

### Error: "ZAI_API_KEY not found in environment variables"

**Solution:**
1. Make sure `.env` file exists in project root
2. Check that `ZAI_API_KEY=...` is in `.env` (no spaces around `=`)
3. Restart the application to reload environment variables

### Error: "GEMINI_API_KEY not found in environment variables"

**Solution:**
1. Make sure `.env` file exists in project root
2. Check that `GEMINI_API_KEY=...` is in `.env`
3. Restart the application

### Environment Variables Not Loading

**Check:**
1. `.env` file is in the **project root** (same directory as `conversation_processor.py`)
2. No spaces around `=` in `.env` file
3. No quotes around values (unless the value contains spaces)
4. File is named `.env` exactly (not `env` or `.env.txt`)

**Example of correct `.env` format:**
```env
ZAI_API_KEY=abc123def456
GEMINI_API_KEY=xyz789uvw012
GLM_MODEL=glm-4.5-air
```

**Example of incorrect format:**
```env
ZAI_API_KEY = "abc123def456"  # ❌ Spaces and unnecessary quotes
GEMINI_API_KEY: xyz789uvw012   # ❌ Using colon instead of equals
GLM_MODEL='glm-4.5-air'        # ❌ Unnecessary quotes
```

## Verifying Configuration

Run this command to test if your environment is configured correctly:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Test configuration
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('ZAI_API_KEY:', 'SET' if os.getenv('ZAI_API_KEY') else 'NOT SET'); print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

Expected output:
```
ZAI_API_KEY: SET
GEMINI_API_KEY: SET
```

## Multiple Environments

If you need different configurations for development and production:

1. **Create environment-specific files:**
   ```
   .env.development
   .env.production
   ```

2. **Load the appropriate file:**
   ```python
   from dotenv import load_dotenv
   import os
   
   environment = os.getenv('ENVIRONMENT', 'development')
   load_dotenv(f'.env.{environment}')
   ```

3. **Set the environment before running:**
   ```bash
   export ENVIRONMENT=production
   ./start.sh
   ```

## CI/CD Integration

For GitHub Actions, GitLab CI, or other CI/CD pipelines:

1. **Store secrets in your CI/CD platform:**
   - GitHub: Settings → Secrets and variables → Actions
   - GitLab: Settings → CI/CD → Variables

2. **Reference them in your workflow:**
   ```yaml
   # GitHub Actions example
   env:
     ZAI_API_KEY: ${{ secrets.ZAI_API_KEY }}
     GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
   ```

## Contact

If you encounter issues with API keys or environment configuration:
- Check [DOCUMENTATION.md](DOCUMENTATION.md)
- Open an issue on GitHub
- Review the [Troubleshooting](#troubleshooting) section above

---

**Last Updated**: October 25, 2025  
**Related Docs**: [DOCUMENTATION.md](DOCUMENTATION.md), [README.md](README.md)

