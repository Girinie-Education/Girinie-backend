from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .services import ChatService
from child_users.models import ChildUser

chat_service = ChatService()

class ChatSessionView(APIView):
    @swagger_auto_schema(
        operation_summary="채팅 세션 시작",
        operation_description="아이와 AI의 새로운 채팅 세션을 시작합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['child_id', 'category'],
            properties={
                'child_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='아이 ID'),
                'category': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='학습 카테고리',
                    enum=['order', 'manners', 'selfcare', 'clean', 'calm', 'kindness', 'saving', 'eating']
                ),
            }
        ),
        responses={
            201: ChatSessionSerializer,
            404: openapi.Response(description='아이를 찾을 수 없음'),
        }
    )
    def post(self, request):
        child_id = request.data.get('child_id')
        category = request.data.get('category')
        
        child = get_object_or_404(ChildUser, id=child_id)
        current_level = getattr(child, f"{category}_level")
        
        # 기존 활성 세션 비활성화
        ChatSession.objects.filter(child=child, category=category, is_active=True).update(is_active=False)
        
        # 새 시나리오 생성
        scenario = chat_service.create_scenario(child, category, current_level)
        
        # 새 세션 생성
        session = ChatSession.objects.create(
            child=child,
            category=category,
            current_level=current_level,
            scenario=scenario
        )
        
        # LLM 첫 메시지 생성
        ChatMessage.objects.create(
            session=session,
            sender='llm',
            content=scenario
        )
        
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatMessageView(APIView):
    @swagger_auto_schema(
        operation_summary="채팅 메시지 전송",
        operation_description="아이의 답변을 전송하고 AI 피드백을 받습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['session_id', 'content'],
            properties={
                'session_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='채팅 세션 ID'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='아이의 답변 내용'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'feedback': openapi.Schema(type=openapi.TYPE_STRING, description='AI 피드백'),
                    'score': openapi.Schema(type=openapi.TYPE_INTEGER, description='답변 점수 (1-5)'),
                    'level_up': openapi.Schema(type=openapi.TYPE_STRING, description='레벨업 메시지'),
                    'next_question': openapi.Schema(type=openapi.TYPE_STRING, description='다음 질문'),
                    'session_ended': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='세션 종료 여부'),
                }
            ),
            404: openapi.Response(description='세션을 찾을 수 없음'),
        }
    )
    def post(self, request):
        session_id = request.data.get('session_id')
        content = request.data.get('content')
        
        session = get_object_or_404(ChatSession, id=session_id, is_active=True)
        
        # 아이 메시지 저장
        child_message = ChatMessage.objects.create(
            session=session,
            sender='child',
            content=content
        )
        
        # 답변 평가
        score, feedback = chat_service.evaluate_response(content, session.category, session.current_level)
        child_message.evaluation_score = score
        child_message.save()
        
        # 진행도 업데이트
        session.progress_score += score
        session.save()
        
        # LLM 피드백 메시지 생성
        llm_message = ChatMessage.objects.create(
            session=session,
            sender='llm',
            content=feedback
        )
        
        # 레벨업 체크
        level_up_message = ""
        session_ended = False
        next_question = ""
        
        if chat_service.check_level_up(session):
            new_level = chat_service.level_up_child(session.child, session.category)
            level_up_message = f"🎉 축하해요! {session.get_category_display()} 레벨이 {new_level}로 올랐어요!"
            
            ChatMessage.objects.create(
                session=session,
                sender='llm',
                content=level_up_message
            )
            
            # 레벨업 시 세션 자동 종료
            session.is_active = False
            session.save()
            session_ended = True
        else:
            # 레벨업이 아니면 다음 질문 생성
            next_question = chat_service.create_next_question(session.child, session.category, session.current_level)
            
            ChatMessage.objects.create(
                session=session,
                sender='llm',
                content=next_question
            )
        
        return Response({
            'feedback': feedback,
            'score': score,
            'level_up': level_up_message,
            'next_question': next_question,
            'session_ended': session_ended
        })

class ChatHistoryView(APIView):
    @swagger_auto_schema(
        operation_summary="채팅 기록 조회",
        operation_description="특정 아이의 최근 채팅 세션 기록을 조회합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['child_id'],
            properties={
                'child_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='아이 ID'),
            }
        ),
        responses={
            200: ChatSessionSerializer(many=True),
            404: openapi.Response(description='아이를 찾을 수 없음'),
        }
    )
    def post(self, request):
        child_id = request.data.get('child_id')
        child = get_object_or_404(ChildUser, id=child_id)
        sessions = ChatSession.objects.filter(child=child).order_by('-created_at')[:10]
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)