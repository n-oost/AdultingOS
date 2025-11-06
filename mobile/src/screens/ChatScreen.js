/**
 * Chat Screen - AI Assistant conversation interface
 */
import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { apiService } from '../services/apiService';

const ChatScreen = () => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant',
      content: 'Hi! I\'m your AdultingOS assistant. I can help you manage tasks and answer questions about life admin. Try "/task list" or ask me anything!',
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef(null);

  const sendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      const response = await apiService.chat(userMessage.content, messages);
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = ({ item }) => (
    <View style={[
      styles.messageContainer,
      item.role === 'user' ? styles.userMessage : styles.assistantMessage
    ]}>
      <Text style={[
        styles.messageText,
        item.role === 'user' ? styles.userText : styles.assistantText
      ]}>
        {item.content}
      </Text>
      <Text style={styles.timestamp}>
        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />
      
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type a message or /task command..."
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!inputText.trim() || loading) && styles.disabledButton]}
          onPress={sendMessage}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.sendButtonText}>
            {loading ? '...' : 'Send'}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  messagesList: {
    flex: 1,
    padding: 16,
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#2563eb',
    borderRadius: 16,
    borderBottomRightRadius: 4,
    padding: 12,
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    padding: 12,
  },
  messageText: {
    fontSize: 16,
  },
  userText: {
    color: '#fff',
  },
  assistantText: {
    color: '#1e293b',
  },
  timestamp: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 8,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: '#2563eb',
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  disabledButton: {
    backgroundColor: '#9ca3af',
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});

export default ChatScreen;