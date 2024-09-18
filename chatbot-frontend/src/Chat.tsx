// src/components/Chat.tsx
import React, { useState } from "react";
import styled from "styled-components";
import axios from "axios";

interface Message {
  sender: "user" | "bot";
  text: string;
}

// Modify the container to fill the entire screen
const ChatContainer = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #ffffff; /* White background */
  font-family: Arial, sans-serif;
`;

const ChatHeader = styled.div`
  background-color: #1d3a45; /* Dark blue for the header */
  color: white;
  padding: 20px;
  font-size: 20px;
  text-align: center;
  font-weight: bold;
`;

const ChatBody = styled.div`
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #ffffff; /* White for the body background */
  display: flex;
  flex-direction: column;
`;

const MessageBubble = styled.div<{ sender: "user" | "bot" }>`
  background-color: ${(props) =>
    props.sender === "user"
      ? "#C9D1D3"
      : "#FFFFFF"}; /* Soft green for user, white for bot */
  color: ${(props) =>
    props.sender === "user" ? "#1D3A45" : "#1D3A45"}; /* Dark blue text */
  padding: 15px;
  border-radius: 20px;
  margin-bottom: 10px;
  max-width: 70%;
  align-self: ${(props) =>
    props.sender === "user" ? "flex-end" : "flex-start"};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const ChatFooter = styled.div`
  padding: 20px;
  background-color: #ffffff; /* White for the footer */
  display: flex;
  border-top: 1px solid #ddd;
`;

const Input = styled.input`
  flex-grow: 1;
  border: none;
  border-radius: 20px;
  padding: 15px;
  font-size: 16px;
  background-color: #c9d1d3; /* Soft green for input field */
  margin-right: 10px;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
  color: #1d3a45; /* Dark blue text */
`;

const SendButton = styled.button`
  border: none;
  background-color: #3c6661; /* Dark green send button */
  color: white;
  padding: 15px;
  border-radius: 50%;
  cursor: pointer;
`;

const QuickReplyButton = styled.button`
  background-color: #c9d1d3; /* Soft green for quick reply buttons */
  border: none;
  padding: 10px 15px;
  border-radius: 20px;
  color: #1d3a45; /* Dark blue text */
  margin-right: 10px;
  cursor: pointer;
  font-size: 14px;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
`;

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");

  const handleSendMessage = async (text: string) => {
    if (text.trim() === "") return;

    // Add user message
    setMessages([...messages, { sender: "user", text }]);

    try {
      // Send the question to the Flask backend
      const response = await axios.post("http://127.0.0.1:5000/api/ask", {
        question: text,
      });

      // Add bot response
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: response.data.response },
      ]);
    } catch (error) {
      console.error("Error fetching response from backend", error);
    }

    setInput(""); // Clear input field
  };

  return (
    <ChatContainer>
      <ChatHeader>Elective Bot</ChatHeader>
      <ChatBody>
        {messages.map((message, index) => (
          <MessageBubble key={index} sender={message.sender}>
            {message.text}
          </MessageBubble>
        ))}
      </ChatBody>
      <ChatFooter>
        <Input
          type="text"
          placeholder="How can I help you?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage(input)}
        />
        <SendButton onClick={() => handleSendMessage(input)}>
          &#9658;
        </SendButton>
      </ChatFooter>
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          padding: "10px",
        }}
      >
        <QuickReplyButton
          onClick={() => handleSendMessage("Just saying hello!")}
        >
          Just saying hello!
        </QuickReplyButton>
        <QuickReplyButton
          onClick={() =>
            handleSendMessage("What courses to learn about Machine learning?")
          }
        >
          What courses to learn about Machine learning?
        </QuickReplyButton>
      </div>
    </ChatContainer>
  );
};

export default Chat;
