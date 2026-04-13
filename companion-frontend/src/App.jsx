import React from 'react';
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import HomeScreen from './components/HomeScreen';
import GreetingBanner from './components/GreetingBanner';
import PhotoViewer from './components/PhotoViewer';
import MusicPlayer from './components/MusicPlayer';
import { speak, listen, isSupported } from './services/speech';
import { startPolling, stopPolling } from './services/polling';
import './styles/john.css';

function App() {
  var greetingMessage = useState(null);
  var greetingType = useState('greeting');
  var currentView = useState('home');
  var isListening = useState(false);
  var isSpeaking = useState(false);
  var conversationId = useState(null);
  var showPhotos = useState(false);
  var photoAlbum = useState('merchant navy');
  var showMusic = useState(false);
  var musicTrack = useState(null);

  var setGreetingMessage = greetingMessage[1];
  var setGreetingType = greetingType[1];
  var setCurrentView = currentView[1];
  var setIsListening = isListening[1];
  var setIsSpeaking = isSpeaking[1];
  var setConversationId = conversationId[1];
  var setShowPhotos = showPhotos[1];
  var setPhotoAlbum = photoAlbum[1];
  var setShowMusic = showMusic[1];
  var setMusicTrack = musicTrack[1];

  greetingMessage = greetingMessage[0];
  greetingType = greetingType[0];
  currentView = currentView[0];
  isListening = isListening[0];
  isSpeaking = isSpeaking[0];
  conversationId = conversationId[0];
  showPhotos = showPhotos[0];
  photoAlbum = photoAlbum[0];
  showMusic = showMusic[0];
  musicTrack = musicTrack[0];

  function handleIncomingMessage(message) {
    if (message && message.content) {
      var content = message.content;
      
      if (content.indexOf('[SHOW_PHOTOS:') !== -1) {
        var startTag = '[SHOW_PHOTOS:';
        var endTag = ']';
        var startIdx = content.indexOf(startTag);
        var endIdx = content.indexOf(endTag, startIdx);
        if (startIdx !== -1 && endIdx !== -1) {
          var albumName = content.substring(startIdx + startTag.length, endIdx);
          setPhotoAlbum(albumName);
          setShowPhotos(true);
          content = content.substring(0, startIdx) + content.substring(endIdx + 1);
        }
      }
      
      if (content.indexOf('[PLAY_MUSIC:') !== -1) {
        var mStartTag = '[PLAY_MUSIC:';
        var mEndTag = ']';
        var mStartIdx = content.indexOf(mStartTag);
        var mEndIdx = content.indexOf(mEndTag, mStartIdx);
        if (mStartIdx !== -1 && mEndIdx !== -1) {
          var trackTitle = content.substring(mStartIdx + mStartTag.length, mEndIdx);
          setMusicTrack(trackTitle);
          setShowMusic(true);
          content = content.substring(0, mStartIdx) + content.substring(mEndIdx + 1);
        }
      }
      
      content = content.trim();
      
      setGreetingMessage(content);
      setGreetingType(message.message_type);
      if (content) {
        speak(content);
      }
      setTimeout(function() {
        if (greetingMessage === message.content) {
          setGreetingMessage(null);
        }
      }, 30000);
    }
  }

  useEffect(function() {
    startPolling(handleIncomingMessage, 1);
    return function() {
      stopPolling();
    };
  }, []);

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
    setPhotoAlbum('merchant navy');
    setShowPhotos(true);
    console.log('Photos pressed');
  }

  function handleMusic() {
    setShowMusic(true);
    console.log('Music pressed');
  }

  function handleClosePhotos() {
    setShowPhotos(false);
  }

  function handleCloseMusic() {
    setShowMusic(false);
  }

  function handleGames() {
    setCurrentView('games');
    console.log('Games pressed');
  }

  function handleDismissGreeting() {
    setGreetingMessage(null);
  }

  var content = null;
  
  if (showPhotos) {
    content = React.createElement(PhotoViewer, {
      albumName: photoAlbum,
      onClose: handleClosePhotos
    });
  } else if (showMusic) {
    content = React.createElement(MusicPlayer, {
      onClose: handleCloseMusic,
      initialTrack: musicTrack
    });
  } else {
    content = React.createElement('div', null,
      React.createElement(GreetingBanner, {
        message: greetingMessage,
        messageType: greetingType,
        onDismiss: handleDismissGreeting
      }),
      React.createElement(HomeScreen, {
        onHelpPress: handleHelpPress,
        onPhotos: handlePhotos,
        onMusic: handleMusic,
        onGames: handleGames,
        greetingMessage: greetingMessage,
        isListening: isListening,
        isSpeaking: isSpeaking,
        onListenStart: handleListenStart,
        onListenEnd: handleListenEnd
      })
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={content}
        />
        <Route path="/carer" element={<div>Carer dashboard coming in Phase 9</div>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;