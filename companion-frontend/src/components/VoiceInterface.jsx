import React from 'react';
import { speak, listen, isSupported } from '../services/speech';

function VoiceInterface(props) {
  var transcriptState = React.useState('');
  var errorMessageState = React.useState(null);
  
  var transcript = transcriptState[0];
  var setTranscript = transcriptState[1];
  
  var errorMessage = errorMessageState[0];
  var setErrorMessage = errorMessageState[1];

  var isListening = props.isListening === true;
  var isSpeaking = props.isSpeaking === true;

  function getBackgroundColor() {
    if (isListening) {
      return '#E24B4A';
    }
    if (isSpeaking) {
      return '#0F6E56';
    }
    return '#185FA5';
  }

  function getStatusText() {
    if (isListening) {
      return 'Listening...';
    }
    if (isSpeaking) {
      return "John's companion is speaking...";
    }
    return 'Tap to speak';
  }

  function handleMicPress() {
    if (isSpeaking) {
      return;
    }
    
    if (props.onListenStart) {
      props.onListenStart();
    }
    
    listen()
      .then(function(text) {
        setTranscript(text);
        setErrorMessage(null);
        if (props.onMessage) {
          props.onMessage(text);
        }
        if (props.onListenEnd) {
          props.onListenEnd();
        }
      })
      .catch(function(err) {
        setErrorMessage(err);
        setTimeout(function() {
          setErrorMessage(null);
        }, 3000);
        if (props.onListenEnd) {
          props.onListenEnd();
        }
      });
  }

  var buttonStyle = {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: getBackgroundColor(),
    border: 'none',
    fontSize: '32px',
    cursor: isSpeaking ? 'not-allowed' : 'pointer',
    opacity: isSpeaking ? 0.5 : 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  var containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  };

  var statusStyle = {
    fontSize: '18px',
    color: '#888888',
    marginTop: '10px',
  };

  var transcriptStyle = {
    fontSize: '20px',
    color: '#888888',
    fontStyle: 'italic',
    marginTop: '20px',
    textAlign: 'center',
    minHeight: '30px',
  };

  return (
    <div style={containerStyle}>
      <button
        style={buttonStyle}
        onClick={handleMicPress}
        disabled={isSpeaking}
        aria-label="Speak"
      >
        🎤
      </button>
      <div style={statusStyle}>{getStatusText()}</div>
      <div style={transcriptStyle}>
        {errorMessage !== null ? errorMessage : transcript}
      </div>
    </div>
  );
}

export default VoiceInterface;