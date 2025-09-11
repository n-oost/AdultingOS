import React, { useState, useEffect } from 'react';

/**
 * A simple chatbot component.
 * This component will handle the chat interface, including displaying messages and handling user input.
 */
function Chatbot() {
  // State to store the messages in the chat
  const [messages, setMessages] = useState([]);

  // State to store the user's input
  const [inputValue, setInputValue] = useState('');

  /**
   * Sends an initial message to the backend to start the conversation.
   */
  useEffect(() => {
    const startConversation = async () => {
      try {
        const response = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: '' }), // Send an empty message to start
        });
        const data = await response.json();
        setMessages([data]);
      } catch (error) {
        console.error('Error starting conversation:', error);
      }
    };
    startConversation();
  }, []);

  /**
   * Handles changes to the input field.
   * @param {object} e - The event object.
   */
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  /**
   * Handles sending a message.
   * This function sends the user's message to the backend and displays the bot's response.
   */
  const handleSendMessage = async () => {
    // Don't send empty messages
    if (inputValue.trim() === '') return;

    // Add the user's message to the chat
    const newMessages = [...messages, { text: inputValue, sender: 'user' }];
    setMessages(newMessages);

    // Clear the input field
    setInputValue('');

    try {
      // Send the user's message to the backend
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputValue }),
      });
      const data = await response.json();

      // Add the bot's response to the chat
      setMessages([...newMessages, data]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chatbot">
      {/* The area where messages will be displayed */}
      <div className="chatbot-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message message-${message.sender}`}>
            {message.text}
          </div>
        ))}
      </div>

      {/* The input area for the user */}
      <div className="chatbot-input">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;