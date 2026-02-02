from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication without CSRF enforcement.
    
    This is safe because:
    1. We use CORS properly (only allowing trusted origins)
    2. Session cookies have SameSite attribute
    3. This is an API designed for SPA consumption
    """

    def enforce_csrf(self, request):
        # Skip CSRF check
        return
