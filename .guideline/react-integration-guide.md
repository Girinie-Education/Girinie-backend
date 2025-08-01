# React 프론트엔드 연동 가이드

## API 서비스 클래스

```javascript
// services/chatService.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

class ChatService {
  // 채팅 세션 시작
  async startChatSession(childId, category) {
    const response = await fetch(`${API_BASE_URL}/chat/start/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        child_id: childId,
        category: category
      })
    });
    return response.json();
  }

  // 메시지 전송
  async sendMessage(sessionId, content) {
    const response = await fetch(`${API_BASE_URL}/chat/message/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        content: content
      })
    });
    return response.json();
  }

  // 채팅 기록 조회
  async getChatHistory(childId) {
    const response = await fetch(`${API_BASE_URL}/chat/history/${childId}/`);
    return response.json();
  }
}

export default new ChatService();
```

## React 컴포넌트 예시

```jsx
// components/ChatComponent.jsx
import React, { useState, useEffect } from 'react';
import chatService from '../services/chatService';

const ChatComponent = ({ childId }) => {
  const [messages, setMessages] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('order');
  const [loading, setLoading] = useState(false);
  const [sessionEnded, setSessionEnded] = useState(false);

  const categories = [
    { value: 'order', label: '질서' },
    { value: 'manners', label: '예절' },
    { value: 'selfcare', label: '자조' },
    { value: 'clean', label: '청결' },
    { value: 'calm', label: '감정조절' },
    { value: 'kindness', label: '존중' },
    { value: 'saving', label: '절약' },
    { value: 'eating', label: '식습관' }
  ];

  // 채팅 세션 시작
  const startChat = async () => {
    setLoading(true);
    try {
      const session = await chatService.startChatSession(childId, selectedCategory);
      setCurrentSession(session);
      setMessages(session.messages || []);
    } catch (error) {
      console.error('채팅 시작 오류:', error);
    }
    setLoading(false);
  };

  // 새 채팅 시작
  const startNewChat = () => {
    setCurrentSession(null);
    setMessages([]);
    setSessionEnded(false);
    setUserInput('');
  };

  // 메시지 전송
  const sendMessage = async () => {
    if (!userInput.trim() || !currentSession || sessionEnded) return;

    const userMessage = {
      sender: 'child',
      content: userInput,
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatService.sendMessage(currentSession.id, userInput);
      
      // LLM 피드백 메시지 추가
      const llmMessage = {
        sender: 'llm',
        content: response.feedback,
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, llmMessage]);

      // 레벨업 메시지가 있으면 추가
      if (response.level_up) {
        const levelUpMessage = {
          sender: 'llm',
          content: response.level_up,
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, levelUpMessage]);
      }

      // 다음 질문이 있으면 추가 (레벨업이 아닌 경우)
      if (response.next_question) {
        const nextQuestionMessage = {
          sender: 'llm',
          content: response.next_question,
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, nextQuestionMessage]);
      }

      // 레벨업으로 인한 세션 종료 체크
      if (response.session_ended) {
        setSessionEnded(true);
        const endMessage = {
          sender: 'llm',
          content: '레벨업을 축하합니다! 학습이 완료되었어요. 수고하셨습니다! 🎉',
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, endMessage]);
      }

    } catch (error) {
      console.error('메시지 전송 오류:', error);
    }
    
    setUserInput('');
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <select 
          value={selectedCategory} 
          onChange={(e) => setSelectedCategory(e.target.value)}
          disabled={currentSession}
        >
          {categories.map(cat => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
        
        {!currentSession && (
          <button onClick={startChat} disabled={loading}>
            채팅 시작
          </button>
        )}
        
        {sessionEnded && (
          <button onClick={startNewChat}>
            새 채팅 시작
          </button>
        )}
      </div>

      <div className="messages">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.sender === 'child' ? 'user' : 'bot'}`}
          >
            <div className="message-content">
              {message.content}
            </div>
            <div className="message-time">
              {new Date(message.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>

      {currentSession && !sessionEnded && (
        <div className="input-area">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="답변을 입력하세요..."
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading || !userInput.trim()}>
            전송
          </button>
        </div>
      )}
      
      {sessionEnded && (
        <div className="session-ended">
          <p>채팅이 종료되었습니다.</p>
        </div>
      )}
    </div>
  );
};

export default ChatComponent;
```

## CSS 스타일 예시

```css
/* styles/ChatComponent.css */
.chat-container {
  max-width: 600px;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  padding: 16px;
  background-color: #f5f5f5;
  display: flex;
  gap: 12px;
  align-items: center;
}

.messages {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
}

.message {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.bot {
  align-items: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px;
  border-radius: 12px;
  word-wrap: break-word;
}

.message.user .message-content {
  background-color: #007bff;
  color: white;
}

.message.bot .message-content {
  background-color: #e9ecef;
  color: #333;
}

.message-time {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 8px;
}

.input-area input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.input-area button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-area button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.session-ended {
  padding: 16px;
  text-align: center;
  background-color: #f8f9fa;
  border-top: 1px solid #ddd;
  color: #666;
}

.chat-header button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.chat-header button:first-of-type {
  background-color: #28a745;
  color: white;
}

.chat-header button:last-of-type {
  background-color: #dc3545;
  color: white;
}

.chat-header button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
```

## 사용 방법

```jsx
// App.js
import ChatComponent from './components/ChatComponent';

function App() {
  const childId = 1; // 실제 아이 ID

  return (
    <div className="App">
      <h1>교육용 채팅</h1>
      <ChatComponent childId={childId} />
    </div>
  );
}

export default App;
```

## 주요 기능

1. **카테고리 선택**: 8개 교육 카테고리 중 선택
2. **실시간 채팅**: 아이와 AI 간의 대화
3. **자동 평가**: 답변에 대한 즉시 피드백
4. **레벨업 알림**: 성취 시 축하 메시지
5. **채팅 기록**: 이전 대화 내용 조회

## 추가 개선사항

- 로딩 스피너 추가
- 에러 처리 개선
- 음성 입력/출력 기능
- 아바타 이미지 표시
- 진행도 표시 바