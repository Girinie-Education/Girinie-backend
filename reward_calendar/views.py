from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import RewardCalendar
from child_users.models import ChildUser
from .serializers import RewardCalendarSerializer

class RewardCalendarMonthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="자녀 월별 칭찬 조회",
        operation_description="지정한 자녀의 특정 연/월에 해당하는 칭찬 기록을 조회합니다.",
        responses={200: RewardCalendarSerializer(many=True)}
    )
    def get(self, request, child_id, year, month):
        child = get_object_or_404(ChildUser, id=child_id, parent=request.user)
        rewards = RewardCalendar.objects.filter(
            child=child, date__year=year, date__month=month
        ).order_by('date')

        serializer = RewardCalendarSerializer(rewards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RewardCalendarDayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="자녀 칭찬 전체 조회",
        operation_description="특정 자녀에게 연결된 모든 칭찬 데이터를 조회합니다.",
        responses={200: RewardCalendarSerializer(many=True)}
    )
    def get(self, request, child_id):
        child = get_object_or_404(ChildUser, id=child_id, parent=request.user)
        rewards = RewardCalendar.objects.filter(child=child).order_by('date')
        serializer = RewardCalendarSerializer(rewards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="자녀 칭찬 추가",
        operation_description="특정 자녀에게 날짜, 스티커 종류, 메시지를 입력하여 칭찬을 등록합니다.",
        request_body=RewardCalendarSerializer,
        responses={201: RewardCalendarSerializer}
    )
    def post(self, request, child_id):
        child = get_object_or_404(ChildUser, id=child_id, parent=request.user)
        serializer = RewardCalendarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(child=child)  # child를 명시적으로 지정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="자녀 칭찬 수정",
        operation_description="지정한 날짜에 해당하는 자녀의 칭찬 데이터를 수정합니다. date는 필수입니다.",
        request_body=RewardCalendarSerializer,
        responses={200: RewardCalendarSerializer, 400: "입력 오류", 404: "데이터 없음"}
    )
    def put(self, request, child_id):
        child = get_object_or_404(ChildUser, id=child_id, parent=request.user)
        target_date = request.data.get('date')
        if not target_date:
            return Response({"error": "날짜(date)는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        reward = get_object_or_404(RewardCalendar, child=child, date=target_date)
        serializer = RewardCalendarSerializer(reward, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(child=child)  # 수정 시에도 child를 명시적으로 지정
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="자녀 칭찬 삭제",
        operation_description="자녀의 특정 날짜(date)에 해당하는 칭찬 기록을 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['date'],
            properties={
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='삭제할 날짜 (예: 2025-07-18)'),
            }
        ),
        responses={
            204: openapi.Response(description="삭제 성공"),
            400: "날짜 누락",
            404: "해당 데이터 없음"
        }
    )
    def delete(self, request, child_id):
        child = get_object_or_404(ChildUser, id=child_id, parent=request.user)
        target_date = request.data.get('date')
        if not target_date:
            return Response({"error": "날짜(date)는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        reward = get_object_or_404(RewardCalendar, child=child, date=target_date)
        reward.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)