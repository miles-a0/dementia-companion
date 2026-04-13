import React from 'react';
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import HomeScreen from './components/HomeScreen';
import GreetingBanner from './components/GreetingBanner';
import PhotoViewer from './components/PhotoViewer';
import MusicPlayer from './components/MusicPlayer';
import GameScreen from './components/GameScreen';
import CarerLogin from './components/CarerLogin';
import CarerDashboard from './components/CarerDashboard';
import { speak, listen, isSupported } from './services/speech';
import { startPolling, stopPolling } from './services/polling';
import './styles/john.css';

function App() {
  var [greetingMessage, setGreetingMessage] = useState(null);
  var [greetingType, setGreetingType] = useState('greeting');
  var [currentView, setCurrentView] = useState('home');
  var [isListening, setIsListening] = useState(false);
  var [isSpeaking, setIsSpeaking] = useState(false);
  var [conversationId, setConversationId] = useState(null);
  var [showPhotos, setShowPhotos] = useState(false);
  var [photoAlbum, setPhotoAlbum] = useState('merchant navy');
  var [showMusic, setShowMusic] = useState(false);
  var [musicTrack, setMusicTrack] = useState(null);
  var [showGame, setShowGame] = useState(false);
  var [carrierAuthenticated, setCarerAuthenticated] = useState(false);

  React.useEffect(function() {
    var token = localStorage.getItem('companion_carer_token');
    if (token) {
      setCarerAuthenticated(true);
    }
  }, []);

  function handleCarerLogin() {
    setCarerAuthenticated(true);
  }

  function handleCarerLogout() {
    localStorage.removeItem('companion_carer_token');
    setCarerAuthenticated(false);
  }

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
      
      if (content.indexOf('[PLAY_GAME]') !== -1) {
        content = content.replace('[PLAY_GAME]', '');
        setShowGame(true);
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
  
  React.useEffect(function() {
    if (!isSpeaking && !isListening) {
      startPolling(handleIncomingMessage, 1);
      return function() {
        stopPolling();
      };
    }
  }, [isSpeaking, isListening]);
  
  function handleMicClick() {
    if (!isSupported()) {
      setGreetingMessage("Sorry, voice input is not supported on this device.");
      setGreetingType('error');
      speak("Sorry, voice input is not supported on this device.");
      return;
    }
    
    if (isListening) {
      return;
    }
    
    setIsListening(true);
    speak("I'm listening...");
    
    listen(function(transcript) {
      setIsListening(false);
      if (transcript) {
        setGreetingMessage(transcript);
        setGreetingType('user');
        fetch('/api/messages/respond', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: transcript,
            user_id: 1
          })
        })
        .then(function(response) {
          return response.json();
        })
        .then(function(data) {
          if (data.response) {
            setGreetingMessage(data.response);
            setGreetingType('greeting');
            speak(data.response);
          }
        })
        .catch(function(err) {
          setGreetingMessage("Sorry, I had trouble connecting. Please try again.");
          setGreetingType('error');
          speak("Sorry, I had trouble connecting. Please try again.");
        });
      }
    }, function(err) {
      setIsListening(false);
      setGreetingMessage("Sorry, I couldn't understand. Please try again.");
      setGreetingType('error');
      speak("Sorry, I couldn't understand. Please try again.");
    });
  }
  
  function handleMessageClick() {
    setCurrentView('chat');
  }
  
  function handleHomeClick() {
    setCurrentView('home');
    setShowPhotos(false);
    setShowMusic(false);
    setShowGame(false);
    setGreetingMessage(null);
  }
  
  function handleCarerClick() {
    window.location.href = '/carer/login';
  }
  
  function handleClosePhotos() {
    setShowPhotos(false);
    setCurrentView('home');
  }
  
  function handleCloseMusic() {
    setShowMusic(false);
    setCurrentView('home');
  }
  
  function handleCloseGame() {
    setShowGame(false);
    setCurrentView('home');
  }
  
  var content = null;
  
  if (showPhotos) {
    content = React.createElement(PhotoViewer, {
      albumName: photoAlbum,
      onClose: handleClosePhotos,
      autoNarrate: false
    });
  } else if (showMusic) {
    content = React.createElement(MusicPlayer, {
      initialTrack: musicTrack,
      autoPlay: true,
      onClose: handleCloseMusic
    });
  } else if (showGame) {
    content = React.createElement(GameScreen, {
      onComplete: handleCloseGame,
      onClose: handleCloseGame
    });
  } else if (currentView === 'home' || currentView === 'chat') {
    var backgroundImage = 'linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url(background.jpg)';
    var mainContainerStyle = {
      minHeight: '100vh',
      backgroundImage: backgroundImage,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      position: 'relative',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      paddingTop: '80px'
    };
    
    var headerStyle = {
      fontSize: '48px',
      fontWeight: 'bold',
      color: 'white',
      textAlign: 'center',
      textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
      marginTop: '40px',
      marginBottom: '20px'
    };
    
    var buttonStyle = {
      padding: '20px 40px',
      fontSize: '32px',
      fontWeight: 'bold',
      color: 'white',
      backgroundColor: '#185FA5',
      border: 'none',
      borderRadius: '15px',
      cursor: 'pointer',
      margin: '20px',
      boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
    };
    
    var micButtonStyle = {
      position: 'fixed',
      bottom: '100px',
      right: '30px',
      width: '80px',
      height: '80px',
      borderRadius: '50%',
      backgroundColor: isListening ? '#e74c3c' : '#185FA5',
      border: 'none',
      color: 'white',
      fontSize: '36px',
      cursor: 'pointer',
      boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    };
    
    var micIcon = isListening ? '⏹' : '🎤';
    
    var carrierLinkStyle = {
      position: 'fixed',
      bottom: '30px',
      right: '30px',
      color: 'white',
      fontSize: '18px',
      textDecoration: 'underline',
      cursor: 'pointer'
    };
    
    content = React.createElement('div', { style: mainContainerStyle },
      greetingMessage ? React.createElement(GreetingBanner, { message: greetingMessage, type: greetingType }) : null,
      React.createElement('div', { style: headerStyle }, 'John\'s Companion'),
      React.createElement('button', { style: buttonStyle, onClick: handleMessageClick }, 'I Need Help'),
      React.createElement('button', { 
        style: Object.assign({}, micButtonStyle, { animation: isListening ? 'pulse 1s infinite' : 'none' }), 
        onClick: handleMicClick 
      }, micIcon),
      React.createElement(Link, { to: '/carer', style: carrierLinkStyle }, 'Carer')
    );
  }
  
  return (
    React.createElement(BrowserRouter, null,
      React.createElement(Routes, null,
        React.createElement(Route, { path: '/', element: content }),
        React.createElement(Route, { path: '/carer/login', element: React.createElement(CarerLogin, { onLoginSuccess: handleCarerLogin }) }),
        React.createElement(Route, { 
          path: '/carer', 
          element: carrierAuthenticated 
            ? React.createElement(CarerDashboard, { onLogout: handleCarerLogout })
            : React.createElement(Navigate, { to: '/carer/login', replace: true })
        }),
        React.createElement(Route, { path: '*', element: React.createElement(Navigate, { to: '/', replace: true }) })
      )
    )
  );
}

export default App;