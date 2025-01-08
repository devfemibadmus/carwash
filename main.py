from app import application
import functions_framework

@functions_framework.http
def carwash(request):
    with application.test_request_context(request.path, method=request.method):
        return application.full_dispatch_request()
