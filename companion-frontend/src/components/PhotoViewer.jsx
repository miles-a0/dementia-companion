import React from 'react';
import { speak } from '../services/speech';

function PhotoViewer(props) {
  var loading = React.useState(true);
  var setLoading = loading[1];
  loading = loading[0];
  
  var photos = React.useState([]);
  photos = photos[0];
  var setPhotos = photos[1];
  
  var currentIndex = React.useState(0);
  currentIndex = currentIndex[0];
  var setCurrentIndex = currentIndex[1];
  
  var albumName = props.albumName;
  var onClose = props.onClose;
  var autoNarrate = props.autoNarrate !== undefined ? props.autoNarrate : true;
  
  React.useEffect(function() {
    fetch('http://173.249.40.161:8001/api/media/photos?album=' + encodeURIComponent(albumName))
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        setLoading(false);
        if (data.photos) {
          setPhotos(data.photos);
          if (data.photos.length > 0 && autoNarrate) {
            narratePhoto(data.photos[0], 0);
          }
        }
      })
      .catch(function(err) {
        setLoading(false);
        console.error('Error loading photos:', err);
      });
  }, []);
  
  function narratePhoto(photo, index) {
    var albumType = 'photo';
    if (albumName && albumName.toLowerCase().indexOf('family') !== -1) {
      albumType = 'family photo';
    } else if (albumName && albumName.toLowerCase().indexOf('holiday') !== -1) {
      albumType = 'holiday photo';
    }
    
    var text = 'Here is a photo from your ' + albumName + ' album.';
    if (photo.description) {
      text = text + ' This one shows ' + photo.description + '.';
    }
    
    speak(text);
  }
  
  function handlePrevious() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      if (autoNarrate) {
        narratePhoto(photos[currentIndex - 1], currentIndex - 1);
      }
    }
  }
  
  function handleNext() {
    if (currentIndex < photos.length - 1) {
      setCurrentIndex(currentIndex + 1);
      if (autoNarrate) {
        narratePhoto(photos[currentIndex + 1], currentIndex + 1);
      }
    }
  }
  
  var touchStartX = React.useRef(0);
  var touchEndX = React.useRef(0);
  
  function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
  }
  
  function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].clientX;
    handleSwipe();
  }
  
  function handleSwipe() {
    var diff = touchStartX - touchEndX;
    if (Math.abs(diff) > 50) {
      if (diff > 0) {
        handleNext();
      } else {
        handlePrevious();
      }
    }
  }
  
  var containerStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'white',
    zIndex: 200,
    display: 'flex',
    flexDirection: 'column'
  };
  
  var closeButtonStyle = {
    position: 'absolute',
    top: '20px',
    right: '20px',
    width: '50px',
    height: '50px',
    fontSize: '18px',
    backgroundColor: 'transparent',
    border: '2px solid #666',
    borderRadius: '8px',
    cursor: 'pointer',
    zIndex: 201
  };
  
  var loadingStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    fontSize: '24px',
    color: '#666'
  };
  
  var imageContainerStyle = {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative'
  };
  
  var imageStyle = {
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain'
  };
  
  var captionStyle = {
    position: 'absolute',
    bottom: '20px',
    left: '20px',
    right: '20px',
    textAlign: 'center',
    fontSize: '24px',
    color: '#333',
    backgroundColor: 'rgba(255,255,255,0.9)',
    padding: '10px',
    borderRadius: '8px'
  };
  
  var counterStyle = {
    position: 'absolute',
    bottom: '80px',
    left: 0,
    right: 0,
    textAlign: 'center',
    fontSize: '18px',
    color: '#999'
  };
  
  var navButtonStyle = {
    height: '80px',
    fontSize: '22px',
    padding: '0 30px',
    backgroundColor: '#f0f0f0',
    border: 'none',
    cursor: 'pointer'
  };
  
  var navContainerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 20px',
    backgroundColor: '#f5f5f5'
  };
  
  var disabledStyle = {
    color: '#ccc',
    cursor: 'default'
  };
  
  if (loading) {
    return React.createElement('div', { style: containerStyle },
      React.createElement('button', { style: closeButtonStyle, onClick: onClose }, 'Close'),
      React.createElement('div', { style: loadingStyle }, 'Loading photos...')
    );
  }
  
  if (!photos || photos.length === 0) {
    return React.createElement('div', { style: containerStyle },
      React.createElement('button', { style: closeButtonStyle, onClick: onClose }, 'Close'),
      React.createElement('div', { style: loadingStyle },
        'No photos found in this album'
      ),
      React.createElement('div', { style: navContainerStyle },
        React.createElement('button', { 
          style: Object.assign({}, navButtonStyle, disabledStyle),
          onClick: function() {}
        }, 'Close')
      )
    );
  }
  
  var currentPhoto = photos[currentIndex];
  
  return React.createElement('div', { style: containerStyle },
    React.createElement('button', { style: closeButtonStyle, onClick: onClose }, 'Close'),
    React.createElement('div', 
      { 
        style: imageContainerStyle,
        onTouchStart: handleTouchStart,
        onTouchEnd: handleTouchEnd
      },
      React.createElement('img', { 
        src: currentPhoto.full_url, 
        alt: currentPhoto.description || 'Photo',
        style: imageStyle
      }),
      currentPhoto.description ? React.createElement('div', { style: captionStyle }, currentPhoto.description) : null,
      React.createElement('div', { style: counterStyle }, 'Photo ' + (currentIndex + 1) + ' of ' + photos.length)
    ),
    React.createElement('div', { style: navContainerStyle },
      React.createElement('button', { 
        style: Object.assign({}, navButtonStyle, currentIndex === 0 ? disabledStyle : {}),
        onClick: currentIndex > 0 ? handlePrevious : function() {},
        disabled: currentIndex === 0
      }, '< Prev'),
      React.createElement('button', { 
        style: Object.assign({}, navButtonStyle, currentIndex >= photos.length - 1 ? disabledStyle : {}),
        onClick: currentIndex < photos.length - 1 ? handleNext : function() {},
        disabled: currentIndex >= photos.length - 1
      }, 'Next >')
    )
  );
}

export default PhotoViewer;