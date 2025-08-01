import os
import openai
from .models import ChatSession, ChatMessage
from child_users.models import ChildUser

class ChatService:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # 카테고리별 주제 매핑 (엑셀 파일 기반 - 20레벨)
        self.category_topics = {
            'order': [
                '차례차례 줄을 서요', '실내에서 걸어 다녀요', '전기를 아껴 써요', '주변을 깨끗이 정리해요',
                '바른 자세로 주사를 맞을 수 있어요', '전등을 끄고 나와요', '내 방을 정리해요', '교통규칙을 지켜요',
                '약속을 정해 지켜요', '친구들과 규칙을 정해 놀이해요', '사용한 물건을 제자리에 두어요', '줄을 서서 놀이기구를 타요',
                '실내에서는 조용히 걸어요', '자리를 정해 앉아요', '쓰레기를 분리수거해요', '컴퓨터 시간을 지켜요',
                '텔레비전을 오래 보지 않아요', '정해진 시간에 자요', '정해진 시간에 일어나요', '소지품을 사물함에 넣어요'
            ],
            'manners': [
                '식당 예절을 지켜요', '웃어른께 존댓말을 해요', '"미안해요"라고 말할 수 있어요', '도서관 예절을 알아요',
                '공공장소에서 약속을 지켜요', '선생님께 바르게 인사해요', '친구에게 양보해요', '어른께 두 손으로 드리고 받아요',
                '줄을 설 때 차례를 지켜요', '공공장소에서 떠들지 않아요', '기침할 때 입을 가려요', '다른 사람 말을 경청해요',
                '친구 물건을 허락 없이 사용하지 않아요', '바른 말, 고운 말을 써요', '함께 정한 약속을 지켜요', '교통신호를 지켜요',
                '도와줄 일이 있을 땐 먼저 도와요', '쓰레기를 버릴 땐 휴지를 사용해요', '규칙을 정하고 지켜요', '소방훈련 시 지시에 따라 대피해요'
            ],
            'selfcare': [
                '혼자서 화장실에 갈 수 있어요', '신발을 바르게 신어요', '약을 먹을 수 있어요', '혼자 잘 수 있어요',
                '손을 씻을 수 있어요', '옷을 입고 벗어요', '밥을 먹고 정리해요', '양치 후 칫솔을 닦아요',
                '손톱, 발톱을 깨끗이 해요', '집주소와 전화번호를 말할 수 있어요', '기분 나쁜 신체접촉에 "싫어요"라고 말해요', '예방접종을 받아요',
                '차에 탈 땐 안전벨트를 매요', '물건을 스스로 챙겨요', '머리를 감고 헹궈요', '손수건을 사용해요',
                '모자를 벗고 인사해요', '양말을 정리해요', '입은 옷을 제자리에 둬요', '친구의 물건을 소중히 다뤄요'
            ],
            'clean': [
                '내 몸을 깨끗이 해요', '손을 씻고 음식을 먹어요', '세수를 할 수 있어요', '깨끗하게 양치해요',
                '땀 나면 씻어요', '머리를 자주 감아요', '손톱을 깎아요', '발톱을 깎아요',
                '코를 푼 뒤 손을 씻어요', '음식물을 남기지 않아요', '물건을 함부로 만지지 않아요', '산책 후 손을 씻어요',
                '화장실을 깨끗이 써요', '양치컵을 정리해요', '친구 사용 중인 화장실 방해하지 않아요', '놀이 후 옷에 묻은 흙을 털어요',
                '날씨에 맞는 옷을 입어요', '옷을 제자리에 걸어요', '청소 도구를 제자리에 둬요', '친구와 함께 청소해요'
            ],
            'calm': [
                '울지 않고 말해요', '"미안해요"라고 말할 수 있어요', '참을 수 있어요', '기분 나쁜 신체접촉에 "싫어요"라고 말해요',
                '"고마워요"라고 말할 수 있어요', '화가 나면 말을 해요', '친구와 다툰 뒤 화해해요', '마음을 표현할 수 있어요',
                '속상할 때 선생님께 말해요', '친구의 마음을 이해해요', '감정을 얼굴 표정으로 표현해요', '친구가 속상할 때 위로해요',
                '나의 감정을 말로 표현해요', '친구가 기분 나빠하면 행동을 멈춰요', '상대방 입장에서 생각해요', '다른 사람과의 다름을 인정해요',
                '나와 생각이 달라도 존중해요', '친구와 의견을 나눠요', '실수해도 다시 해보아요', '짜증 나도 소리를 지르지 않아요'
            ],
            'kindness': [
                '웃어른께 인사해요', '친구를 때리지 않아요', '친구 물건을 빼앗지 않아요', '친구 이야기를 경청해요',
                '친구의 놀이를 방해하지 않아요', '친구의 의견을 존중해요', '"고마워요"라고 말해요', '친구에게 양보해요',
                '함께 정한 약속을 지켜요', '친구에게 바른 말을 써요', '친구의 차례를 지켜요', '친구와 협동해 놀이해요',
                '친구가 싫어하는 행동은 하지 않아요', '친구와 함께 정리해요', '다툰 친구에게 먼저 사과해요', '친구가 쓰는 물건을 함부로 만지지 않아요',
                '친구의 이야기에 반응해요', '친구가 기분 나빠하면 멈춰요', '친구의 장점을 이야기해요', '친구가 실수해도 놀리지 않아요'
            ],
            'saving': [
                '전기를 아껴 써요', '물을 아껴 써요', '휴지를 필요한 만큼만 써요', '일회용품 사용을 줄여요',
                '적절한 온도를 유지해요', '아이스크림을 적당히 먹어요', '음식은 남기지 않아요', '필요한 물건만 사요',
                '쓰레기를 줄여요', '자원을 재활용해요', '헌 옷을 깨끗이 정리해요', '장난감을 소중히 써요',
                '과자를 한꺼번에 다 먹지 않아요', '불필요한 불을 끄고 나와요', '양치할 때 물을 잠가요', '컴퓨터를 오래 켜놓지 않아요',
                '적당한 양만 덜어서 써요', '오래 쓰는 물건은 소중히 다뤄요', '계절에 맞는 옷을 입어요', '장난감 건전지를 오래 쓰기 위해 껐다 켜요'
            ],
            'eating': [
                '음식을 골고루 먹어요', '음식을 남기지 않아요', '김치를 먹을 수 있어요', '작은 목소리로 식사 중 말해요',
                '식사 전 손을 씻어요', '간식은 정해진 시간에 먹어요', '과자를 많이 먹지 않아요', '편식을 하지 않아요',
                '밥 먹을 땐 바르게 앉아요', '식사 시간에는 장난하지 않아요', '음식에 침 튀기지 않아요', '다른 친구 식판에 손 대지 않아요',
                '국을 불지 않고 식혀 먹어요', '숟가락과 젓가락을 바르게 써요', '식사 후 정리해요', '급식 선생님께 감사 인사해요',
                '좋아하지 않아도 한입은 먹어봐요', '식사 후 양치해요', '젓가락으로 장난치지 않아요', '간식을 혼자 다 먹지 않아요'
            ]
        }
    
    def create_scenario(self, child: ChildUser, category: str, level: int):
        topics = self.category_topics.get(category, [])
        topic = topics[min(level, len(topics)-1)] if topics else "기본상황"
        
        prompt = f"""
        {child.name}이(가) {child.age}살 아이입니다. 
        {category} 카테고리의 레벨 {level}에 맞는 자연스러운 일상 상황을 만들어주세요.
        주제: {topic}
        
        규칙:
        1. 아이가 실제로 경험할 수 있는 자연스러운 상황을 만드세요
        2. 상황 설명이 논리적이고 현실적이어야 합니다
        3. 어색한 표현이나 부자연스러운 설정을 피하세요
        4. 아이에게 "{child.name}이라면 어떻게 할까?"로 질문하세요 (이름 뒤 조사는 자연스럽게)
        5. 친근하고 따뜻한 말투로 작성하세요
        6. 상황의 배경과 맥락을 명확히 제시하세요
        
        예시:
        "{child.name}야, 안녕! 오늘 유치원에서 블록 놀이를 하고 난 후에 블록들이 바닥에 여기저기 흩어져 있어. 다음 친구들이 놀이하려고 기다리고 있는데, {child.name}이라면 어떻게 할까?"
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def evaluate_response(self, child_response: str, category: str, level: int):
        prompt = f"""
        아이의 답변을 평가해주세요: "{child_response}"
        카테고리: {category}, 레벨: {level}
        
        규칙:
        1. 1-5점으로 평가하세요 (5점이 최고)
        2. 아이의 답변을 먼저 칭찬하고 인정해주세요
        3. 자연스럽고 따뜻한 말투로 피드백하세요
        4. 추가적인 좋은 방법이 있다면 부드럽게 제안하세요
        5. 아이가 성취감을 느낄 수 있도록 격려해주세요
        6. 교육적이면서도 재미있게 설명하세요
        
        형식:
        점수: [1-5]
        피드백: [칭찬과 인정] + [자연스러운 추가 제안] + [따뜻한 격려]
        
        예시:
        점수: 4
        피드백: 와! 정말 좋은 생각이야! 장난감을 상자에 넣는 것도 훌륭하지만, 비슷한 장난감끼리 모아서 정리하면 더욱 좋을 것 같아. 그러면 다음에 놀 때 찾기도 쉽고 방도 더 깔끔해질 거야. 정말 잘 생각했어!
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.8
        )
        
        evaluation = response.choices[0].message.content.strip()
        
        # 점수 추출
        lines = evaluation.split('\n')
        score = 3  # 기본값
        feedback = "잘했어요!"
        
        for line in lines:
            if '점수:' in line:
                try:
                    score = int(line.split(':')[1].strip())
                except:
                    pass
            elif '피드백:' in line:
                feedback = line.split(':', 1)[1].strip()
        
        return score, feedback
    
    def check_level_up(self, session: ChatSession):
        # 최근 10개 메시지의 평균 점수가 4.5점 이상이면 레벨업
        recent_messages = session.messages.filter(
            sender='child',
            evaluation_score__isnull=False
        ).order_by('-created_at')[:10]
        
        if len(recent_messages) >= 5:
            avg_score = sum(msg.evaluation_score for msg in recent_messages) / len(recent_messages)
            if avg_score >= 4.5:
                return True
        return False
    
    def level_up_child(self, child: ChildUser, category: str):
        category_field = f"{category}_level"
        current_level = getattr(child, category_field)
        setattr(child, category_field, current_level + 1)
        child.save()
        return current_level + 1
    
    def create_next_question(self, child: ChildUser, category: str, level: int):
        topics = self.category_topics.get(category, [])
        topic = topics[min(level, len(topics)-1)] if topics else "기본상황"
        
        prompt = f"""
        {child.name}이(가) {child.age}살 아이입니다.
        {category} 카테고리의 레벨 {level}에 맞는 새로운 일상 상황을 만들어주세요.
        주제: {topic}
        
        규칙:
        1. 아이가 실제로 경험할 수 있는 자연스러운 상황을 만드세요
        2. 상황의 배경과 맥락이 논리적이고 현실적이어야 합니다
        3. 어색한 표현이나 부자연스러운 설정을 피하세요
        4. 구체적인 장소와 상황을 명확히 제시하세요
        5. "{child.name}이라면 어떻게 할까?"로 질문하세요 (이름 뒤 조사는 자연스럽게)
        6. 친근하고 자연스러운 말투로 작성하세요
        7. 이전과 다른 새로운 상황을 만들어주세요
        
        예시:
        "{child.name}야, 이번에는 다른 상황이야. 놀이터에서 친구들과 모래놀이를 하고 있는데, 모래가 옷에 많이 묻었어. 집에 들어가기 전에 엄마가 기다리고 계시는데, {child.name}이라면 어떻게 할까?"
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=1.0
        )
        
        return response.choices[0].message.content.strip()