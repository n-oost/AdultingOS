import React, { useState } from 'react';
import { assistant } from '../services/apiService';

/**
 * A simple chatbot component.
 * This component will handle the chat interface, including displaying messages and handling user input.
 * 
 * Note: This component requires the user to be authenticated. The assistant API
 * will automatically forward the auth token to Django for user context.
 */
function Chatbot() {
  // State to store the messages in the chat
  const [messages, setMessages] = useState([]);

  // State to store the user's input
  const [inputValue, setInputValue] = useState('');

  // State to track loading
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Handles changes to the input field.
   * @param {object} e - The event object.
   */
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  /**
   * Handles sending a message.
   * This function sends the user's message to the FastAPI assistant and displays the bot's response.
   */
  const handleSendMessage = async () => {
    // Don't send empty messages or send while loading
    if (inputValue.trim() === '' || isLoading) return;

    // Add the user's message to the chat
    const userMessage = { text: inputValue, sender: 'user' };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);

    // Clear the input field
    const messageToSend = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Send the user's message to the assistant API
      const data = await assistant.chat(messageToSend);

      // Add the bot's response to the chat
      // The assistant API returns user profile data, but we need to extract a response message
      const botMessage = {
        text: data.message || 'I received your message. How can I help you?',
        sender: 'bot',
        data: data, // Include full response data for debugging
      };
      setMessages([...newMessages, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to chat
      const errorMessage = {
        text: `Error: ${error.message}. Please make sure you're logged in and both servers are running.`,
        sender: 'bot',
        isError: true,
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot">
      {/* The area where messages will be displayed */}
      <div className="chatbot-messages">
        {messages.length === 0 && (
          <div className="message message-bot">
            Hi! I'm your AdultingOS assistant. How can I help you today?
          </div>
        )}
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message message-${message.sender} ${message.isError ? 'message-error' : ''}`}
          >
            {message.text}
          </div>
        ))}
        {isLoading && (
          <div className="message message-bot">
            <em>Thinking...</em>
          </div>
        )}
      </div>

      {/* The input area for the user */}
      <div className="chatbot-input">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button onClick={handleSendMessage} disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default Chatbot;