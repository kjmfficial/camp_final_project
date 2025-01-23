import { useRef } from "react";

const ChatForm = ({ chatHistory, setChatHistory, generateBotResponse }) => {
    const inputRef = useRef();
    
    const handleFormSubmit = (e) => {
        e.preventDefault();
        const userMessage = inputRef.current.value.trim();
        if(!userMessage) return;
        inputRef.current.value = "";

        // Update chat history with the user's message
        setChatHistory((history) => [...history, { role: "user", text: userMessage }]);

        // Delay 600 ms before showing "생각중..." and generating response
        setTimeout(() => {
            // Add a "생각중..." placeholder for the bot's response
            setChatHistory((history) => [...history, { 
                role: "model", 
                text: "생각중...", 
                timestamp: Date.now() 
            }]);

            // Call the function to generate the bot's response
            generateBotResponse([...chatHistory, { role: "user", text: userMessage }]);
        }, 600);
    };
    
    return (
        <form action="#" className="chat-form" onSubmit={handleFormSubmit}>
            <input ref={inputRef} type="text" placeholder="입력해주세요..." className="message-input" required />
            <button className="material-symbols-rounded">arrow_upward</button>
        </form>
    );
};

export default ChatForm;
