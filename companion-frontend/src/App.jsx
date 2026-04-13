import React from 'react';
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import HomeScreen from './components/HomeScreen';
import GreetingBanner from './components/GreetingBanner';
import { speak, listen, isSupported } from './services/speech';
import './styles/john.css';

function App() {
  var greetingMessage = useState(null);
  var greetingType = useState('greeting');
  var currentView = useState('home');
  var isListening = useState(false);
  var isSpeaking = useState(false);
  var conversationId = useState(null);

  var setGreetingMessage = greetingMessage[1];
  var setGreetingType = greetingType[1];
  var setCurrentView = currentView[1];
  var setIsListening = isListening[1];
  var setIsSpeaking = isSpeaking[1];
  var setConversationId = conversationId[1];

  greetingMessage = greetingMessage[0];
  greetingType = greetingType[0];
  currentView = currentView[0];
  isListening = isListening[0];
  isSpeaking = isSpeaking[0];
  conversationId = conversationId[0];

  function handleHelpPress() {
    setIsListening(true);
    
    listen()
      .then(function(transcript) {
        fetch('http://localhost:8001/api/messages/respond', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: transcript,
            user_id: 1,
            conversation_id: conversationId
          })
        })
        .then(function(response) {
          return response.json();
        })
        .then(function(data) {
          if (data.conversation_id) {
            setConversationId(data.conversation_id);
          }
          setIsListening(false);
          setIsSpeaking(true);
          
          speak(data.response)
            .then(function() {
              setIsSpeaking(false);
            })
            .catch(function(err) {
              console.error('TTS error:', err);
              setIsSpeaking(false);
            });
        })
        .catch(function(err) {
          console.error('API error:', err);
          setIsListening(false);
        });
      })
      .catch(function(err) {
        console.error('Listen error:', err);
        setIsListening(false);
      });
  }

  function handleListenStart() {
    setIsListening(true);
  }

  function handleListenEnd() {
    setIsListening(false);
  }

  function handlePhotos() {
    setCurrentView('photos');
    console.log('Photos pressed');
  }

  function handleMusic() {
    setCurrentView('music');
    console.log('Music pressed');
  }

  function handleGames() {
    setCurrentView('games');
    console.log('Games pressed');
  }

  function handleDismissGreeting() {
    setGreetingMessage(null);
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <div>
              <GreetingBanner
                message={greetingMessage}
                messageType={greetingType}
                onDismiss={handleDismissGreeting}
              />
              <HomeScreen
                onHelpPress={handleHelpPress}
                onPhotos={handlePhotos}
                onMusic={handleMusic}
                onGames={handleGames}
                greetingMessage={greetingMessage}
                isListening={isListening}
                isSpeaking={isSpeaking}
                onListenStart={handleListenStart}
                onListenEnd={handleListenEnd}
              />
            </div>
          }
        />
        <Route path="/carer" element={<div>Carer dashboard coming in Phase 9</div>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;