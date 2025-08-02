from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import LevelUpLog
from .serializers import LevelUpLogSerializer
from child_users.models import ChildUser

class LevelUpLogView(APIView):
    @swagger_auto_schema(
        operation_summary="전체 레벨업 로그 조회",
        operation_description="모든 아이들의 레벨업 기록을 최신순으로 조회합니다.",
        responses={200: LevelUpLogSerializer(many=True)}
    )
    def get(self, request):
        logs = LevelUpLog.objects.all()
        serializer = LevelUpLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChildLevelUpLogView(APIView):
    @swagger_auto_schema(
        operation_summary="아이별 레벨업 로그 조회",
        operation_description="특정 아이의 레벨업 기록을 최신순으로 조회합니다.",
        manual_parameters=[
            openapi.Parameter('child_id', openapi.IN_PATH, description="아이 ID", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: LevelUpLogSerializer(many=True),
            404: openapi.Response(description='아이를 찾을 수 없음'),
        }
    )
    def get(self, request, child_id):
        child = get_object_or_404(ChildUser, id=child_id)
        logs = LevelUpLog.objects.filter(child=child)
        serializer = LevelUpLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)