import React from 'react';

function HelpButton(props) {
  var isDisabled = props.disabled === true;
  var isPulsing = props.isPulsing === true;

  React.useEffect(function() {
    var styleEl = document.createElement('style');
    styleEl.innerHTML = '\n      @keyframes pulse-animation {\n        0% { transform: scale(1); }\n        50% { transform: scale(1.05); }\n        100% { transform: scale(1); }\n      }\n    ';
    document.head.appendChild(styleEl);
    return function() {
      document.head.removeChild(styleEl);
    };
  }, []);

  var buttonStyle = {
    width: '180px',
    height: '180px',
    borderRadius: '50%',
    background: '#E24B4A',
    color: 'white',
    fontSize: '24px',
    fontWeight: 'bold',
    border: 'none',
    boxShadow: '0 4px 20px rgba(226, 75, 74, 0.4)',
    cursor: isDisabled ? 'not-allowed' : 'pointer',
    transition: 'transform 0.1s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
    lineHeight: '1.2',
    opacity: isDisabled ? 0.5 : 1,
  };

  var containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  };

  var labelStyle = {
    fontSize: '16px',
    color: '#888888',
    marginTop: '10px',
  };

  function handleClick(e) {
    if (!isDisabled && props.onPress) {
      props.onPress();
    }
  }

  function handleMouseDown(e) {
    if (!isDisabled) {
      e.currentTarget.style.transform = 'scale(0.95)';
    }
  }

  function handleMouseUp(e) {
    e.currentTarget.style.transform = 'scale(1)';
  }

  function handleMouseLeave(e) {
    e.currentTarget.style.transform = 'scale(1)';
  }

  var animationStyle = {};
  if (isPulsing) {
    animationStyle = {
      animation: 'pulse-animation 2s infinite ease-in-out',
    };
  }

  return (
    <div style={containerStyle}>
      <button
        style={Object.assign({}, buttonStyle, animationStyle)}
        onClick={handleClick}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        disabled={isDisabled}
        aria-label="I Need Help"
      >
        <span>I Need</span>
        <span>Help</span>
      </button>
      <div style={labelStyle}>Tap for help</div>
    </div>
  );
}

export default HelpButton;