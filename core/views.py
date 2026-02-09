from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import time


class HealthCheckView(APIView):
    """
    System health check endpoint
    Used for load balancer (CLB) or container orchestration system probe detection
    """

    authentication_classes = []  # Allow anonymous access
    permission_classes = []  # Allow access without permissions

    def get(self, request):
        return Response(
            {"status": "ok", "service": "web-server", "timestamp": int(time.time())},
            status=status.HTTP_200_OK,
        )
