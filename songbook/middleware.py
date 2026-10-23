from django.http import HttpResponse

CRAWLER_MARKERS = ("meta-externalagent", "gptbot", "bingbot")

class BlockCrawlersOnFiltersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET:  # only pages with filter parameters
            ua = request.META.get("HTTP_USER_AGENT", "").lower()
            if any(marker in ua for marker in CRAWLER_MARKERS):
                return HttpResponse("Not available to crawlers.", status=403)
        return self.get_response(request)