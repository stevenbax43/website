from .models import ToolUsageEvent
from .usage_tracking import SERVER_CALCULATION_ROUTES, TOOL_ROUTE_CODES


class ToolUsageTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        match = getattr(request, "resolver_match", None)
        if (
            response.status_code < 400
            and getattr(request.user, "is_authenticated", False)
            and match is not None
            and match.namespace == "tools"
        ):
            tool = TOOL_ROUTE_CODES.get(match.url_name)
            if tool:
                action = None
                if request.method == "GET":
                    action = "page_view"
                elif (
                    request.method == "POST"
                    and match.url_name in SERVER_CALCULATION_ROUTES
                ):
                    action = "calculation"
                if action:
                    ToolUsageEvent.objects.create(
                        user=request.user,
                        tool=tool,
                        action=action,
                    )
        return response
