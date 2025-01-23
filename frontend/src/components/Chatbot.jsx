import { useRef, useState, useEffect, useContext} from "react";
import ChatbotIcon from "./ChatbotIcon";
import ChatForm from "./ChatForm"
import ChatMessage from "./ChatMessage"
import QuickMenu from "./QuickMenu";
import { UserContext } from "./UserContext.jsx";

import whatIsImage from '../assets/whatIsImage.png';
import bankImage from '../assets/bankImage.png';
import possibleImage from '../assets/possibleImage.png';
import practiceImage from '../assets/practiceImage.png';

import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
// 


const Chatbot = () => {
  const { user } = useContext(UserContext);
  const [chatHistory, setChatHistory] = useState([]);
  const [showChatbot, setShowChatbot] = useState(false);
  const [lastActivityTime, setLastActivityTime] = useState(Date.now());
  const [lastBotResponseTime, setLastBotResponseTime] = useState(Date.now());
  const [noResponseCount, setNoResponseCount] = useState(0); // 무응답 횟수 카운트
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;
  const resetActivityTimer = () => {
    setLastActivityTime(Date.now());
    setNoResponseCount(0);
  };
  const chatBodyRef = useRef();

  // 웰컴 메시지를 위한 useEffect 추가
  useEffect(() => {
    
    if (showChatbot) { // 챗봇이 열릴 때
      setTimeout(() => {
        setChatHistory(prev => [...prev,
          {
            role: "model",
            text: "안녕하세요, 청약 도우미 청약이입니다. 현재 청약 관련 FAQ와 최근 1년간의 청약 정보를 제공해드리고 있습니다. 특히 신혼부부 및 생애최초 특별공급 관련 상세 정보를 확인하실 수 있습니다."
          },
          {
            role: "model",
            type: "card_button",
            text: "안녕하세요, 청약 도우미 청약이입니다. 무엇을 도와드릴까요?",
            buttons: [
              { 
                text: "청약이란?",
                image: whatIsImage
               },
              { 
                text: "청약 통장이란?",
                image: bankImage
               },
              { 
                text: "나에게 가능한 청약은?",
                image: possibleImage
               },
              { 
                text: "청약체험 및 연습",
                image: practiceImage
              }
            ],
            timestamp: Date.now()
          }
        ]);
      }, 500); // 0.5초 후에 메시지 표시
    }
  }, [showChatbot]);

  // 챗봇이 닫혔을 때 5분 후 chatHistory 초기화
  useEffect(() => {
    let timer;
    if (!showChatbot) {
      timer = setTimeout(() => {
        setChatHistory([]); // 5분 후 history 초기화
      }, 5 * 60 * 1000); 
    }
    return () => clearTimeout(timer); // 컴포넌트가 언마운트되거나 챗봇이 다시 열리면 타이머 취소
  }, [showChatbot]);

  // 무응답 타이머 상태 관리
  useEffect(() => {
    const inactivityTimer = setInterval(() => {
      const currentTime = Date.now();
      
      // 3분(180000ms) 경과 체크
      if (currentTime - lastBotResponseTime > 180000 && noResponseCount === 0) { // 3분 = 180000ms
        setChatHistory(prev => [...prev, {
          role: "model",
          text: "청약이가 답변을 기다리고 있어요. 더 이어나가길 원하는 경우 질문을 입력해주세요.",
          timestamp: Date.now()
        }]);
        setNoResponseCount(1);
        setLastActivityTime(currentTime);
      }
      // 무응답 메시지 후 1분 경과 체크
      else if (noResponseCount ===1 && currentTime - lastActivityTime > 60000) {
        // 종료 메시지 출력
        setChatHistory(prev => [...prev, {
          role: "model",
          type: "card_button",
          text: "청약이와의 대화가 도움이 되었나요? 추가 질문이 있다면 언제든지 저에게 질문해주세요.",
          timestamp: Date.now(),
          buttons: [
            { text: "청약이란?", image: whatIsImage },
            { text: "청약 통장이란?", image: bankImage },
            { text: "나에게 가능한 청약은?", image: possibleImage },
            { text: "청약체험 및 연습", image: practiceImage }
          ] 
        }]);
        clearInterval(inactivityTimer); // 타이머 완전 종료
        setNoResponseCount(2); // 종료 상태로 변경
      }
    }, 10000); // 10초마다 체크

    // 컴포넌트 언마운트 시 타이머 정리
    return () => clearInterval(inactivityTimer);
}, [lastBotResponseTime, noResponseCount]);

  const generateBotResponse = async (history) => {
    // Helper function to update chat history
    const updateHistory = (text, isError = false) => {
      setChatHistory(prev => [...prev.filter(msg => msg.text !== "생각중..."),
        { role: "model", 
          text: typeof text === 'object' ? text.text : text,
          buttons: text.buttons,
          type: text.buttons ? "scenario_button" : undefined, 
          currentStep: text.currentStep,
          totalSteps: text.totalSteps,
          isError, 
          timestamp: Date.now()
        }
      ]);
      setLastBotResponseTime(Date.now()); // 봇 응답시간 업데이트
      setNoResponseCount(0); // 카운트 초기화
    };

    try {
      const response = await fetch(`http://${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: history[history.length - 1].text,
          user_id: user?.id || "비로그인"
        })  
      });
      if (!response.ok) throw new Error('서버 응답 오류');
      const data = await response.json();

      if (typeof data.response === 'object') {
        updateHistory(data.response);
      } else {
        updateHistory({
          text: data.response,
          buttons: data.buttons
        });
      }
    
      
    } catch (error) {
      updateHistory("죄송합니다. 오류가 발생했습니다.", true);
    }
  };

  useEffect(() => {
    // Auto-scroll whenever chat history updates
    chatBodyRef.current.scrollTo({ top: chatBodyRef.current.scrollHeight, behavior: "smooth" });
  }, [chatHistory]);

  return (
    <div className={`container ${showChatbot ? "show-chatbot" : ""}`} style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: showChatbot ? 999 : 0 }}>
      <button onClick={() => setShowChatbot(prev => !prev)} id="chatbot-toggler">
        <span className="material-symbols-rounded">mode_comment</span>
        <span className="material-symbols-rounded">close</span>
      </button>
  
      <div className="chatbot-popup">
        {/* Chatbot Header */}
        <div className="chat-header">
          <div className="header-info">
            <ChatbotIcon />
            <h2 className="logo-text">Chatbot</h2>
          </div>
          <div className="service-notice">
            청약이도 실수할 수 있어요!
          </div>
          <button onClick={() => setShowChatbot(prev => !prev)} className="material-symbols-rounded">
            keyboard_arrow_down</button>
        </div>
  
        <div className="chat-date">
          {new Date().getFullYear()}.
          {(new Date().getMonth() + 1).toString().padStart(2, '0')}.
          {new Date().getDate().toString().padStart(2, '0')}
        </div>
  
        {/* Chatbot Body */}
        <div ref={chatBodyRef} className="chat-body">
          {/* Render the chat history dynamically */}
          {chatHistory.map((chat, index) => (
            <ChatMessage key={index} chat={chat} setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} />
          ))}
        </div>
  
        <QuickMenu setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} />
  
        {/* Chatbot Footer */}
        <div className="chat-footer">
          <ChatForm chatHistory={chatHistory} setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} resetActivityTimer={resetActivityTimer} />
        </div>
      </div>
    </div>
  );
};

export default Chatbot