# 이메일 설정 가이드

## 네이버 메일 SMTP 설정

### 1. 네이버 메일 설정
1. 네이버 메일 로그인
2. 환경설정 → POP3/IMAP 설정
3. **IMAP/SMTP 사용** 체크
4. 저장

### 2. .env 파일 설정
```env
EMAIL_MODE=smtp
EMAIL_HOST_USER=your-email@naver.com
EMAIL_HOST_PASSWORD=your-naver-password
```

### 3. 이메일 모드 옵션
- `console`: 터미널에 출력 (개발용)
- `file`: 파일로 저장 (개발용)
- `smtp`: 실제 이메일 발송

### 4. 비밀번호 재설정 API
```
POST /api/v1/parent_users/reset-password/
{
  "email": "user@example.com",
  "username": "testuser"
}
```

### 5. 주의사항
- 네이버 계정에 2단계 인증이 있으면 앱 비밀번호 사용
- SMTP 포트: 587 (TLS)
- 발신자 주소: noreply@girinie.com (설정된 주소)