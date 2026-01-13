from django.shortcuts import render
from rest_framework.reverse import reverse

OPENAPI_URL = "schema"
TITLE = "Scalar API Reference"
JS_URL = "https://cdn.jsdelivr.net/npm/@scalar/api-reference"
PROXY_URL = ""
FAVICON_URL = "/favicon.ico"


def scalar_viewer(
    request,
    url_name=None,
    title=None,
    scalar_js_url=None,
    scalar_proxy_url=None,
    scalar_favicon_url=None,
):
    final_openapi_url = reverse(url_name if url_name is not None else OPENAPI_URL, request=request)
    final_title = title if title is not None else TITLE
    final_js_url = scalar_js_url if scalar_js_url is not None else JS_URL
    final_proxy_url = scalar_proxy_url if scalar_proxy_url is not None else PROXY_URL
    final_favicon_url = scalar_favicon_url if scalar_favicon_url is not None else FAVICON_URL

    context = {
        "openapi_url": final_openapi_url,
        "title": final_title,
        "scalar_js_url": final_js_url,
        "scalar_proxy_url": final_proxy_url,
        "scalar_favicon_url": final_favicon_url,
    }
    return render(request, "drf_apischema/scalar.html", context)
