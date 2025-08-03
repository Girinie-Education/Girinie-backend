from django.core.serializers import serialize
from django.shortcuts import render
from django.template.context_processors import request
from rest_framework.exceptions import AuthenticationFailed, ParseError, NotFound
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ParentUserSerializer
from .models import ParentUser
from django.shortcuts import get_object_or_404


class LoginView(APIView):

    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="username과 password를 받아 로그인합니다. 세션 기반 인증입니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 이름'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호'),
            }
        ),
        responses={
            200: openapi.Response(description='로그인 성공'),
            400: openapi.Response(description='입력 오류'),
            401: openapi.Response(description='인증 실패'),
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise ParseError({'error': 'Username and password are required'})

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({'message': 'Logged in'}, status=HTTP_200_OK)
        else:
            raise AuthenticationFailed({'error': 'Invalid username or password'})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃",
        operation_description="세션에서 사용자 로그아웃",
        responses={
            200: openapi.Response(description='로그아웃 성공'),
            403: openapi.Response(description='로그인 필요'),
        }
    )
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"}, status=HTTP_200_OK)


class ParentUserView(APIView):

    def get_permissions(self):
        if self.request.method == "PUT":
            return [IsAuthenticated()]
        return []  # POST는 인증 없이 허용

    @swagger_auto_schema(
        operation_summary="전체 회원 조회 (개발/관리자용)",
        operation_description="모든 사용자의 정보를 리스트로 반환합니다.",
        responses={200: ParentUserSerializer(many=True)}
    )
    def get(self, request):
        users = ParentUser.objects.all()
        serializer = ParentUserSerializer(users, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="새로운 사용자 등록. username, password, email 필요.",
        request_body=ParentUserSerializer,
        responses={
            201: ParentUserSerializer,
            400: openapi.Response(description='입력 오류'),
        }
    )
    def post(self, request):
        password = request.data.get('password')
        if not password:
            raise ParseError({'error': 'Password is required'})

        serializer = ParentUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Invalid input',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': serializer.data
        }, status=HTTP_201_CREATED)




class ParentUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 회원 정보 조회",
        responses={
            200: openapi.Response(description="성공", schema=ParentUserSerializer())
        }
    )
    def get(self, request):
        user = request.user
        serializer = ParentUserSerializer(user)
        return Response(serializer.data, status=HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="회원 정보 수정",
        operation_description="현재 로그인한 사용자의 username과 email을 수정합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='새 사용자 이름'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='새 이메일'),
            },
            required=[]
        ),
        responses={
            200: openapi.Response(description='수정 성공'),
            400: openapi.Response(description='입력 오류'),
            403: openapi.Response(description='로그인 필요'),
        }
    )
    def put(self, request):
        user = request.user
        serializer = ParentUserSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                'message': 'Invalid input',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            'message': 'User info updated successfully',
            'user': serializer.data
        }, status=HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="특정 회원 삭제",
        responses={200: openapi.Response(description="삭제 성공")}
    )
    def delete(self, request):
        user = request.user
        username = user.username
        user.delete()
        return Response({"message": f"User {username} deleted successfully."}, status=HTTP_200_OK)


class FindUsernameView(APIView):
    @swagger_auto_schema(
        operation_summary="사용자명 찾기",
        operation_description="이메일을 입력하여 해당하는 사용자명을 찾습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='이메일 주소'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자명'),
                }
            ),
            404: openapi.Response(description='해당 이메일로 등록된 사용자가 없습니다'),
        }
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': '이메일을 입력해주세요.'}, status=HTTP_400_BAD_REQUEST)
        
        try:
            user = ParentUser.objects.get(email=email)
            return Response({'username': user.username}, status=HTTP_200_OK)
        except ParentUser.DoesNotExist:
            return Response({'error': '해당 이메일로 등록된 사용자가 없습니다.'}, status=HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="비밀번호 재설정 이메일 발송",
        operation_description="이메일과 사용자명을 입력하여 비밀번호 재설정 이메일을 발송합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'username'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='이메일 주소'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자명'),
            }
        ),
        responses={
            200: openapi.Response(description='비밀번호 재설정 이메일이 발송되었습니다'),
            404: openapi.Response(description='일치하는 사용자 정보가 없습니다'),
        }
    )
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        
        if not email or not username:
            return Response({'error': '이메일과 사용자명을 모두 입력해주세요.'}, status=HTTP_400_BAD_REQUEST)
        
        try:
            user = ParentUser.objects.get(email=email, username=username)
            
            # 토큰 생성
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # 이메일 발송
            reset_url = f"{settings.BACKEND_URL}/api/v1/parent_users/reset-password-confirm/{uid}/{token}/"
            subject = "[Girinie] 비밀번호 재설정"
            message = f"안녕하세요 {user.username}님,\n\n아래 링크를 클릭하여 비밀번호를 재설정하세요:\n{reset_url}\n\n감사합니다."
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({'message': '비밀번호 재설정 이메일이 발송되었습니다.'}, status=HTTP_200_OK)
            
        except ParentUser.DoesNotExist:
            return Response({'error': '일치하는 사용자 정보가 없습니다.'}, status=HTTP_404_NOT_FOUND)


class ResetPasswordConfirmView(APIView):
    @swagger_auto_schema(
        operation_summary="비밀번호 재설정 확인",
        operation_description="""
        이메일 링크를 통해 비밀번호를 재설정합니다.
        
        **동작 과정:**
        1. 사용자가 이메일의 재설정 링크 클릭
        2. GET 요청: 비밀번호 입력 폼 제공
        3. POST 요청: 실제 비밀번호 변경
        
        **링크 형태:** `http://127.0.0.1:8000/api/v1/parent_users/reset-password-confirm/{uid}/{token}/`
        
        **파라미터:**
        - uid: 사용자 ID (base64 인코딩)
        - token: 재설정 토큰 (시간 제한 있음)
        """,
        manual_parameters=[
            openapi.Parameter('uid', openapi.IN_PATH, description="사용자 ID (base64 인코딩)", type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, description="재설정 토큰 (시간 제한 있음)", type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_password'],
            properties={
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='새 비밀번호'),
            }
        ),
        responses={
            200: openapi.Response(description='비밀번호가 성공적으로 변경되었습니다'),
            400: openapi.Response(description='잘못된 요청 또는 만료된 토큰'),
        }
    )
    def post(self, request, uid, token):
        try:
            # uid 디코딩
            user_id = force_str(urlsafe_base64_decode(uid))
            user = ParentUser.objects.get(pk=user_id)
            
            # 토큰 검증
            if not default_token_generator.check_token(user, token):
                return Response({'error': '잘못된 또는 만료된 토큰입니다.'}, status=HTTP_400_BAD_REQUEST)
            
            # 새 비밀번호 설정
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({'error': '새 비밀번호를 입력해주세요.'}, status=HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=HTTP_200_OK)
            
        except (TypeError, ValueError, OverflowError, ParentUser.DoesNotExist):
            return Response({'error': '잘못된 요청입니다.'}, status=HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="비밀번호 재설정 폼 제공",
        operation_description="이메일 링크를 통해 접근할 때 HTML 폼을 제공합니다.",
        manual_parameters=[
            openapi.Parameter('uid', openapi.IN_PATH, description="사용자 ID (base64 인코딩)", type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, description="재설정 토큰 (시간 제한 있음)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(description='HTML 폼 반환'),
        }
    )
    def get(self, request, uid, token):
        # HTML 폼 제공 (선택사항)
        return HttpResponse("""
        <html>
        <body>
            <h2>비밀번호 재설정</h2>
            <form method="post">
                <input type="password" name="new_password" placeholder="새 비밀번호" required>
                <button type="submit">변경</button>
            </form>
        </body>
        </html>
        """)
