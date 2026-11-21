from core.https import https_settings


def test_debug_keeps_local_http():
    local = https_settings(debug=True)

    assert local['SECURE_SSL_REDIRECT'] is False
    assert local['SESSION_COOKIE_SECURE'] is False
    assert local['CSRF_COOKIE_SECURE'] is False
    assert local['SECURE_HSTS_SECONDS'] == 0
    assert local['SECURE_PROXY_SSL_HEADER'] is None


def test_host_requires_https():
    host = https_settings(debug=False)

    assert host['SECURE_SSL_REDIRECT'] is True
    assert host['SESSION_COOKIE_SECURE'] is True
    assert host['CSRF_COOKIE_SECURE'] is True
    assert host['SECURE_HSTS_SECONDS'] == 3600
    assert host['SECURE_CONTENT_TYPE_NOSNIFF'] is True
    assert host['SECURE_PROXY_SSL_HEADER'] == ('HTTP_X_FORWARDED_PROTO', 'https')
