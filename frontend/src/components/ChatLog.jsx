import { useRef, useState, useEffect, useContext} from "react";
import { UserContext } from "./UserContext.jsx";
import axios from "axios";

const ChatbotLog = () => {
    const { user } = useContext(UserContext);
    const [logData, setLogData] = useState([]);
    const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;
    console.log({
        user_id: user?.id || "비로그인"
    });
    // API로부터 데이터 불러오기
    useEffect(() => {
        const fetchChatLogs = async () => {
            try {
                // 서버에서 로그 데이터를 요청
                const response = await axios.post(`http://${API_URL}/chat/log`, {
                    user_id: user.id
                });
                
                // 데이터 상태 업데이트
                console.log("Fetched chat logs:", response.data);
                setLogData(response.data.data || []);  // 서버의 데이터 구조에 맞게 처리
            } catch (error) {
                console.error("Error fetching chat logs:", error);
            }
        };

        if (user?.id) {
            fetchChatLogs();
        }
    }, [user]);

    return (
        <div className="chatbot-log">
            <h2>Chatbot Log</h2>
            {/* 로그 데이터가 있을 경우 */}
            {logData.length > 0 ? (
                <ul>
                    {logData.map((log, index) => (
                        <li key={index} className="chat-log-item">
                            <p><strong>User:</strong> {log["유저"]}</p>
                            <p><strong>Bot:</strong> {log["봇"]}</p>
                            <p><strong>Timestamp:</strong> {new Date(log.timestamp).toLocaleString()}</p>
                            <hr />
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No chat logs available.</p>
            )}
        </div>
    );
};

export default ChatbotLog;