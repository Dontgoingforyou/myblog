def https_settings(debug):
    """При DEBUG=False куки и редирект требуют HTTPS за прокси с X-Forwarded-Proto."""
    enabled = not debug
    return {
        'SECURE_SSL_REDIRECT': enabled,
        'SESSION_COOKIE_SECURE': enabled,
        'CSRF_COOKIE_SECURE': enabled,
        'SECURE_HSTS_SECONDS': 3600 if enabled else 0,
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': False,
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https') if enabled else None,
    }
