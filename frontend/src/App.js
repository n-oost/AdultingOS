import React from 'react';
import './App.css';
import Chatbot from './components/Chatbot';

/**
 * The main component of the AdultingOS application.
 */
function App() {
  return (
    <div className="App">
      <h1>AdultingOS Chatbot</h1>
      <Chatbot />
    </div>
  );
}

export default App;