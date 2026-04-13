import React from 'react';
import WordAssociation from './games/WordAssociation';

function GameScreen(props) {
  var onClose = props.onClose;
  
  function handleComplete() {
    if (onClose) {
      onClose();
    }
  }
  
  var containerStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#f5f5f5',
    zIndex: 150
  };
  
  return React.createElement('div', { style: containerStyle },
    React.createElement(WordAssociation, {
      onComplete: handleComplete,
      onClose: onClose
    })
  );
}

export default GameScreen;