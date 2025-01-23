import chatbotIcon from '../assets/cheongyak-piggy.jpg';

const ChatbotIcon = () => {
    return (
        <img 
            src={chatbotIcon} 
            alt="Chatbot Icon"
            style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',  // 원형으로 표시
                objectFit: 'cover'    // 이미지 비율 유지
            }}
        />
    );
};

export default ChatbotIcon;