from django.http import HttpResponse, JsonResponse

def pwa_manifest(request):
    return JsonResponse({
        "name": "LED Factory",
        "short_name": "LED Factory",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#16a34a",
        "description": "LED Factory Management",
        "icons": [
            {"src": "/static/images/app-icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/images/app-icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })

def pwa_service_worker(request):
    js = """
self.addEventListener('install', event => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
"""
    response = HttpResponse(js, content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response
