import React from 'react';
import HelpButton from './HelpButton';
import VoiceInterface from './VoiceInterface';

function HomeScreen(props) {
  var currentTime = new Date();
  var [time, setTime] = React.useState(currentTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }));
  var [date, setDate] = React.useState(currentTime.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' }));

  React.useEffect(function() {
    var interval = setInterval(function() {
      var now = new Date();
      setTime(now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }));
      setDate(now.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' }));
    }, 1000);
    return function() {
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="homescreen">
      <div className="homescreen-topbar">
        <div className="homescreen-greeting">Hello John</div>
        <div className="homescreen-time">{time}</div>
        <div className="homescreen-date">{date}</div>
      </div>
      <div id="greeting-banner" className={"homescreen-banner" + (props.greetingMessage !== null ? " homescreen-banner-message" : "")}>
        {props.greetingMessage !== null ? props.greetingMessage : null}
      </div>
      <div className="homescreen-center">
        <div className="help-button-container">
          <HelpButton onPress={props.onHelpPress} />
        </div>
        <div className="voice-interface-container">
          <VoiceInterface
            isListening={props.isListening}
            isSpeaking={props.isSpeaking}
            onListenStart={props.onListenStart}
            onListenEnd={props.onListenEnd}
          />
        </div>
      </div>
      <div className="homescreen-bottom">
        <button className="homescreen-btn" onClick={props.onPhotos}>
          Photos
        </button>
        <button className="homescreen-btn" onClick={props.onMusic}>
          Music
        </button>
        <button className="homescreen-btn" onClick={props.onGames}>
          Games
        </button>
      </div>
    </div>
  );
}

export default HomeScreen;