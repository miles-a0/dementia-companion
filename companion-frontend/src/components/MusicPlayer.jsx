import React from 'react';

function MusicPlayer(props) {
  var tracks = React.useState([]);
  tracks = tracks[0];
  var setTracks = tracks[1];
  
  var currentIndex = React.useState(0);
  currentIndex = currentIndex[0];
  var setCurrentIndex = currentIndex[1];
  
  var isPlaying = React.useState(false);
  isPlaying = isPlaying[0];
  var setIsPlaying = isPlaying[1];
  
  var loading = React.useState(true);
  loading = loading[0];
  var setLoading = loading[1];
  
  var needsUserGesture = React.useState(false);
  needsUserGesture = needsUserGesture[0];
  var setNeedsUserGesture = needsUserGesture[1];
  
  var audioRef = React.useRef(null);
  
  var onClose = props.onClose;
  var autoPlay = props.autoPlay !== undefined ? props.autoPlay : true;
  var initialTrack = props.initialTrack;
  
  React.useEffect(function() {
    fetch('http://173.249.40.161:8001/api/media/music')
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        setLoading(false);
        if (data.tracks && data.tracks.length > 0) {
          setTracks(data.tracks);
          
          if (initialTrack) {
            for (var i = 0; i < data.tracks.length; i++) {
              if (data.tracks[i].title === initialTrack) {
                setCurrentIndex(i);
                break;
              }
            }
          }
        }
      })
      .catch(function(err) {
        setLoading(false);
        console.error('Error loading music:', err);
      });
  }, []);
  
  React.useEffect(function() {
    if (tracks.length === 0 || loading) {
      return;
    }
    
    var audio = new Audio();
    audioRef.current = audio;
    
    var trackUrl = 'http://173.249.40.161:8001' + tracks[currentIndex].url;
    audio.src = trackUrl;
    audio.volume = 1.0;
    
    audio.onended = function() {
      if (currentIndex < tracks.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        setIsPlaying(false);
      }
    };
    
    audio.onplay = function() {
      setIsPlaying(true);
      setNeedsUserGesture(false);
    };
    
    audio.onpause = function() {
      setIsPlaying(false);
    };
    
    audio.onerror = function() {
      console.error('Audio error');
    };
    
    if (autoPlay) {
      audio.play()
        .then(function() {
          setIsPlaying(true);
        })
        .catch(function(err) {
          console.log('Auto-play blocked, needs user gesture');
          setNeedsUserGesture(true);
        });
    }
    
    return function() {
      audio.pause();
      audio.src = '';
    };
  }, [currentIndex, tracks, loading]);
  
  function handlePlayPause() {
    var audio = audioRef.current;
    if (!audio) {
      return;
    }
    
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play()
        .catch(function(err) {
          console.error('Play error:', err);
        });
    }
  }
  
  function handlePrevious() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  }
  
  function handleNext() {
    if (currentIndex < tracks.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }
  
  function handleTapToPlay() {
    var audio = audioRef.current;
    if (audio) {
      audio.play()
        .then(function() {
          setIsPlaying(true);
          setNeedsUserGesture(false);
        })
        .catch(function(err) {
          console.error('Play error:', err);
        });
    }
  }
  
  var containerStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#1a1a2e',
    zIndex: 200,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px'
  };
  
  var closeButtonStyle = {
    position: 'absolute',
    top: '20px',
    right: '20px',
    width: '80px',
    height: '50px',
    fontSize: '20px',
    color: 'white',
    backgroundColor: 'transparent',
    border: '2px solid white',
    borderRadius: '8px',
    cursor: 'pointer'
  };
  
  var loadingStyle = {
    color: 'white',
    fontSize: '24px'
  };
  
  var iconStyle = {
    fontSize: '80px',
    color: 'white',
    marginBottom: '30px'
  };
  
  var titleStyle = {
    fontSize: '30px',
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: '10px',
    padding: '0 20px'
  };
  
  var artistStyle = {
    fontSize: '22px',
    color: '#999',
    textAlign: 'center',
    marginBottom: '10px'
  };
  
  var positionStyle = {
    fontSize: '18px',
    color: '#666',
    marginBottom: '40px'
  };
  
  var controlsContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%',
    maxWidth: '400px'
  };
  
  var playButtonStyle = {
    width: '200px',
    height: '90px',
    fontSize: '28px',
    color: 'white',
    backgroundColor: '#185FA5',
    border: 'none',
    borderRadius: '15px',
    cursor: 'pointer',
    marginBottom: '30px'
  };
  
  var navRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    width: '100%'
  };
  
  var navButtonStyle = {
    width: '120px',
    height: '70px',
    fontSize: '20px',
    color: 'white',
    backgroundColor: '#185FA5',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer'
  };
  
  var tapOverlayStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 201
  };
  
  var tapButtonStyle = {
    padding: '30px 60px',
    fontSize: '28px',
    color: 'white',
    backgroundColor: '#185FA5',
    border: 'none',
    borderRadius: '15px',
    cursor: 'pointer'
  };
  
  if (loading) {
    return React.createElement('div', { style: containerStyle },
      React.createElement('button', { style: closeButtonStyle, onClick: onClose }, 'Close'),
      React.createElement('div', { style: loadingStyle }, 'Loading music...')
    );
  }
  
  if (!tracks || tracks.length === 0) {
    return React.createElement('div', { style: containerStyle },
      React.createElement('button', { style: closeButtonStyle, onClick: onClose }, 'Close'),
      React.createElement('div', { style: loadingStyle }, 'No music found')
    );
  }
  
  var currentTrack = tracks[currentIndex];
  
  return React.createElement('div', { style: containerStyle },
    React.createElement('button', { style: closeButtonStyle, onClick: onClose }, 'Close'),
    React.createElement('div', { style: iconStyle }, '♪'),
    React.createElement('div', { style: titleStyle }, currentTrack.title),
    React.createElement('div', { style: artistStyle }, currentTrack.artist || 'Unknown Artist'),
    React.createElement('div', { style: positionStyle }, 'Track ' + (currentIndex + 1) + ' of ' + tracks.length),
    React.createElement('div', { style: controlsContainerStyle },
      React.createElement('button', { 
        style: playButtonStyle, 
        onClick: handlePlayPause
      }, isPlaying ? '⏸ Pause' : '▶ Play'),
      React.createElement('div', { style: navRowStyle },
        React.createElement('button', { 
          style: Object.assign({}, navButtonStyle, currentIndex === 0 ? {opacity: 0.5} : {}),
          onClick: currentIndex > 0 ? handlePrevious : function() {},
          disabled: currentIndex === 0
        }, '⏮ Prev'),
        React.createElement('button', { 
          style: Object.assign({}, navButtonStyle, currentIndex >= tracks.length - 1 ? {opacity: 0.5} : {}),
          onClick: currentIndex < tracks.length - 1 ? handleNext : function() {},
          disabled: currentIndex >= tracks.length - 1
        }, 'Next ⏭')
      )
    ),
    needsUserGesture ? React.createElement('div', { style: tapOverlayStyle },
      React.createElement('button', { style: tapButtonStyle, onClick: handleTapToPlay }, 'Tap to play')
    ) : null
  );
}

export default MusicPlayer;