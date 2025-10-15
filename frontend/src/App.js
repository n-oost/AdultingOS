import React from 'react';
import './App.css';
import Chatbot from './components/Chatbot';
import ApiTest from './components/ApiTest';

/**
 * The main component of the AdultingOS application.
 */
function App() {
  return (
    <div className="App">
      <h1>AdultingOS</h1>
      
      {/* API Connection Test - Remove this after testing */}
      <ApiTest />
      
      <hr style={{ margin: '40px 0' }} />
      
      {/* Your existing chatbot */}
      <h2>Chatbot</h2>
      <Chatbot />
    </div>
  );
}

export default App;