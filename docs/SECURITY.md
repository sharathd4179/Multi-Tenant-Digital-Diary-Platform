# 🔐 Security Guide

## API Key Management

### GitHub Secrets (CI/CD)

1. Go to: Settings → Secrets → Actions
2. Add `OPENAI_API_KEY`
3. Value is encrypted and never exposed

### Local Development

Create `.env` file (already in `.gitignore`):

```env
OPENAI_API_KEY=sk-your-key-here
```

**Verify it's ignored:**
```bash
git check-ignore .env  # Should return: .env
git ls-files | grep .env  # Should return nothing
```

## Best Practices

1. **Never commit secrets** - `.env` is in `.gitignore`
2. **Use different keys** - Dev/staging/production
3. **Rotate keys regularly** - Every 3-6 months
4. **Monitor usage** - Check OpenAI dashboard
5. **Least privilege** - Minimal permissions needed

## Production Security

- Use strong `JWT_SECRET_KEY` (32+ characters)
- Enable HTTPS/TLS
- Restrict CORS origins
- Use environment-specific configs
- Enable rate limiting
- Monitor logs for suspicious activity

## See Also

- [API Key Setup](API_KEY_SETUP.md)
- [Deployment Security](../DEPLOYMENT.md#security-best-practices)

