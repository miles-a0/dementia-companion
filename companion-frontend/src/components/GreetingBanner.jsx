import React from 'react';

function GreetingBanner(props) {
  var message = props.message;
  var messageType = props.messageType;
  var onDismiss = props.onDismiss;

  if (!message || message === '') {
    return null;
  }

  var colors = getColorsForType(messageType);

  React.useEffect(function() {
    var styleEl = document.createElement('style');
    styleEl.innerHTML = '\n      @keyframes fadeIn {\n        from { opacity: 0; }\n        to { opacity: 1; }\n      }\n    ';
    document.head.appendChild(styleEl);
    return function() {
      document.head.removeChild(styleEl);
    };
  }, []);

  var bannerStyle = {
    width: '100%',
    padding: '20px',
    paddingRight: '64px',
    borderRadius: '16px',
    fontSize: '26px',
    lineHeight: '1.5',
    position: 'relative',
    background: colors.background,
    color: colors.text,
    borderLeft: '6px solid ' + colors.border,
    animation: 'fadeIn 0.5s ease-in',
  };

  var dismissStyle = {
    position: 'absolute',
    top: '10px',
    right: '10px',
    width: '44px',
    height: '44px',
    borderRadius: '50%',
    border: 'none',
    background: 'rgba(0,0,0,0.1)',
    color: colors.text,
    fontSize: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  function getColorsForType(type) {
    switch (type) {
      case 'greeting':
        return {
          background: '#E1F5EE',
          text: '#085041',
          border: '#0F6E56',
        };
      case 'medication':
        return {
          background: '#FAEEDA',
          text: '#633806',
          border: '#854F0B',
        };
      case 'check_in':
        return {
          background: '#E6F1FB',
          text: '#0C447C',
          border: '#185FA5',
        };
      case 'intervention':
        return {
          background: '#FAECE7',
          text: '#712B13',
          border: '#993C1D',
        };
      default:
        return {
          background: '#F1EFE8',
          text: '#444441',
          border: '#5F5E5A',
        };
    }
  }

  function handleDismiss() {
    if (onDismiss) {
      onDismiss();
    }
  }

  return (
    <div style={bannerStyle}>
      <span>{message}</span>
      <button style={dismissStyle} onClick={handleDismiss} aria-label="Dismiss">
        x
      </button>
    </div>
  );
}

export default GreetingBanner;