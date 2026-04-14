import React, { useState, useEffect } from 'react';
import PhotoViewer from './PhotoViewer';

function CarerDashboard(props) {
  var onLogout = props.onLogout;
  var [activeTab, setActiveTab] = useState('photos');
  var [albums, setAlbums] = useState([]);
  var [selectedAlbum, setSelectedAlbum] = useState('');
  var [photos, setPhotos] = useState([]);
  var [loading, setLoading] = useState(false);
  var [message, setMessage] = useState('');

  useEffect(function() {
    loadAlbums();
    loadMusic();
  }, []);

  function loadAlbums() {
    setLoading(true);
    fetch('/api/media/albums')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        setAlbums(data.albums || []);
        setLoading(false);
      })
      .catch(function() {
        setLoading(false);
      });
  }

  function loadMusic() {
    fetch('/api/media/music')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        setMusicTracks(data.tracks || []);
      })
      .catch(function() {});
  }

  function loadPhotos() {
    if (!selectedAlbum) return;
    setLoading(true);
    fetch('/api/media/photos?album=' + encodeURIComponent(selectedAlbum))
      .then(function(res) { return res.json(); })
      .then(function(data) {
        setPhotos(data.photos || []);
        setLoading(false);
      })
      .catch(function() {
        setLoading(false);
      });
  }

  var [selectedPhoto, setSelectedPhoto] = useState(null);
  var [musicTracks, setMusicTracks] = useState([]);
  var [uploading, setUploading] = useState(false);

  function handleAlbumChange(e) {
    setSelectedAlbum(e.target.value);
    setPhotos([]);
  }

  function handlePhotoClick(photo) {
    var index = photos.findIndex(function(p) { return p.id === photo.id; });
    setSelectedPhoto(index);
  }

  function closePhotoViewer() {
    setSelectedPhoto(null);
  }

  function handleUploadPhoto() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
      var file = e.target.files[0];
      if (!file) return;
      if (!selectedAlbum) {
        setMessage('Please select an album first');
        return;
      }
      setLoading(true);
      var formData = new FormData();
      formData.append('file', file);
      formData.append('album_name', selectedAlbum);
      fetch('/api/media/upload/photo', {
        method: 'POST',
        body: formData
      })
        .then(function(res) { return res.json(); })
        .then(function(data) {
          setLoading(false);
          if (data.error) {
            setMessage(data.error);
          } else {
            setMessage('Photo uploaded successfully!');
            loadPhotos();
          }
        })
        .catch(function() {
          setLoading(false);
          setMessage('Upload failed');
        });
    };
    input.click();
  }

  function handleUploadMusic() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.onchange = function(e) {
      var file = e.target.files[0];
      if (!file) return;
      setLoading(true);
      var formData = new FormData();
      formData.append('file', file);
      fetch('/api/media/upload/music', {
        method: 'POST',
        body: formData
      })
        .then(function(res) { return res.json(); })
        .then(function(data) {
          setLoading(false);
          if (data.error) {
            setMessage(data.error);
          } else {
            setMessage('Music uploaded successfully!');
            loadMusic();
          }
        })
        .catch(function() {
          setLoading(false);
          setMessage('Upload failed');
        });
    };
    input.click();
  }

  useEffect(function() {
    if (selectedAlbum) {
      loadPhotos();
    }
  }, [selectedAlbum]);

  var containerStyle = {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px'
  };

  var headerStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  var tabStyle = {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px'
  };

  var tabButtonStyle = function(isActive) {
    return {
      padding: '12px 24px',
      fontSize: '16px',
      backgroundColor: isActive ? '#185FA5' : '#ddd',
      color: isActive ? 'white' : '#333',
      border: 'none',
      borderRadius: '8px',
      cursor: 'pointer'
    };
  };

  var contentStyle = {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  var selectStyle = {
    padding: '12px',
    fontSize: '16px',
    width: '100%',
    marginBottom: '20px',
    borderRadius: '8px',
    border: '2px solid #ddd'
  };

  var photoGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
    gap: '10px',
    marginTop: '20px'
  };

  var photoStyle = {
    width: '100%',
    height: '150px',
    objectFit: 'cover',
    borderRadius: '8px',
    cursor: 'pointer'
  };

  var logoutButtonStyle = {
    padding: '12px 24px',
    fontSize: '16px',
    backgroundColor: '#666',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer'
  };

  var sectionTitleStyle = {
    fontSize: '22px',
    fontWeight: 'bold',
    marginBottom: '15px'
  };

  var uploadButtonStyle = {
    padding: '15px 30px',
    fontSize: '18px',
    backgroundColor: '#185FA5',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: '10px',
    display: 'block'
  };

  var inputStyle = {
    padding: '12px',
    fontSize: '16px',
    width: '100%',
    marginBottom: '15px',
    borderRadius: '8px',
    border: '2px solid #ddd',
    boxSizing: 'border-box'
  };

  var formStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  };

  var renderPhotosTab = function() {
    return React.createElement('div', { style: contentStyle },
      React.createElement('div', { style: sectionTitleStyle }, 'Photo Albums (from Immich)'),
      React.createElement('select', {
        style: selectStyle,
        value: selectedAlbum,
        onChange: handleAlbumChange
      },
        React.createElement('option', { value: '' }, '-- Select Album --'),
        albums.map(function(album) {
          return React.createElement('option', { key: album.id, value: album.name }, album.name + ' (' + album.asset_count + ' photos)');
        })
      ),
      React.createElement('div', { style: { marginBottom: '15px' } },
        React.createElement('button', {
          style: uploadButtonStyle,
          onClick: handleUploadPhoto,
          disabled: !selectedAlbum
        }, 'Upload Photo'),
        React.createElement('span', { style: { marginLeft: '10px', color: '#666' } }, 
          selectedAlbum ? 'Select an album above to upload photos to' : 'Select an album first'
        )
      ),
      message ? React.createElement('div', { style: { padding: '10px', backgroundColor: message.indexOf('success') !== -1 ? '#d4edda' : '#f8d7da', marginBottom: '10px', borderRadius: '4px' } }, message) : null,
      loading ? React.createElement('div', null, 'Loading...') : null,
      selectedAlbum && photos.length === 0 && !loading ? React.createElement('div', null, 'No photos in this album') : null,
      selectedAlbum && photos.length > 0 ? React.createElement('div', { style: photoGridStyle },
        photos.map(function(photo) {
          return React.createElement('img', {
            key: photo.id,
            src: photo.thumbnail_url,
            alt: photo.description || 'Photo',
            style: photoStyle,
            onClick: function() { handlePhotoClick(photo); }
          });
        })
      ) : !loading && selectedAlbum ? React.createElement('div', null, 'No photos in this album') : null,
      selectedPhoto !== null ? React.createElement(PhotoViewer, {
        albumName: selectedAlbum,
        photos: photos,
        initialIndex: selectedPhoto,
        onClose: closePhotoViewer
      }) : null
    );
  };

  var renderMusicTab = function() {
    return React.createElement('div', { style: contentStyle },
      React.createElement('div', { style: sectionTitleStyle }, 'Music'),
      React.createElement('div', { style: { marginBottom: '15px' } },
        React.createElement('button', {
          style: uploadButtonStyle,
          onClick: handleUploadMusic
        }, 'Upload Music File'),
        React.createElement('span', { style: { marginLeft: '10px', color: '#666' } }, 
          'Supports MP3, WAV, OGG, M4A'
        )
      ),
      message ? React.createElement('div', { style: { padding: '10px', backgroundColor: message.indexOf('success') !== -1 ? '#d4edda' : '#f8d7da', marginBottom: '10px', borderRadius: '4px' } }, message) : null,
      musicTracks.length > 0 ? React.createElement('div', { style: { marginTop: '20px' } },
        React.createElement('h3', null, 'Available Tracks'),
        React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: '10px' } },
          musicTracks.map(function(track) {
            return React.createElement('div', { key: track.title, style: { padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px' } },
              track.title
            );
          })
        )
      ) : React.createElement('p', { style: { color: '#666', marginTop: '20px' } }, 'No music files found. Upload some music above.')
    );
  };

  var renderMemoriesTab = function() {
    return React.createElement('div', { style: contentStyle },
      React.createElement('div', { style: sectionTitleStyle }, 'Memories & Messages'),
      React.createElement('p', { style: { color: '#666', marginBottom: '20px' } }, 
        'Record memories and messages that John can access through the app.'
      ),
      React.createElement('form', { style: formStyle },
        React.createElement('div', null,
          React.createElement('label', { style: { display: 'block', marginBottom: '5px', fontWeight: 'bold' } }, 'Title'),
          React.createElement('input', { type: 'text', style: inputStyle, placeholder: 'Memory title' })
        ),
        React.createElement('div', null,
          React.createElement('label', { style: { display: 'block', marginBottom: '5px', fontWeight: 'bold' } }, 'Message'),
          React.createElement('textarea', { style: Object.assign({}, inputStyle, { height: '100px' }), placeholder: 'Write a memory or message...' })
        ),
        React.createElement('button', { type: 'button', style: uploadButtonStyle }, 'Save Memory')
      )
    );
  };

  var renderRoutinesTab = function() {
    return React.createElement('div', { style: contentStyle },
      React.createElement('div', { style: sectionTitleStyle }, 'Daily Routines'),
      React.createElement('p', { style: { color: '#666', marginBottom: '20px' } }, 
        'Manage daily routines and schedules for John.'
      ),
      React.createElement('div', { style: { marginBottom: '20px' } },
        React.createElement('h3', null, 'Morning Routine'),
        React.createElement('p', null, 'Configure the morning routine workflow in n8n')
      ),
      React.createElement('div', { style: { marginBottom: '20px' } },
        React.createElement('h3', null, 'Medication Reminders'),
        React.createElement('p', null, 'Configure medication reminders in n8n')
      ),
      React.createElement('p', { style: { color: '#666' } },
        'n8n workflows are available in the repo at: n8n_workflows/'
      )
    );
  };

  return React.createElement('div', { style: containerStyle },
    React.createElement('div', { style: headerStyle },
      React.createElement('span', null, 'Carer Dashboard'),
      React.createElement('button', { style: logoutButtonStyle, onClick: onLogout }, 'Logout')
    ),
    React.createElement('div', { style: tabStyle },
      React.createElement('button', { style: tabButtonStyle(activeTab === 'photos'), onClick: function() { setActiveTab('photos'); } }, 'Photos'),
      React.createElement('button', { style: tabButtonStyle(activeTab === 'music'), onClick: function() { setActiveTab('music'); } }, 'Music'),
      React.createElement('button', { style: tabButtonStyle(activeTab === 'memories'), onClick: function() { setActiveTab('memories'); } }, 'Memories'),
      React.createElement('button', { style: tabButtonStyle(activeTab === 'routines'), onClick: function() { setActiveTab('routines'); } }, 'Routines')
    ),
    activeTab === 'photos' ? renderPhotosTab() : 
    activeTab === 'music' ? renderMusicTab() :
    activeTab === 'memories' ? renderMemoriesTab() :
    renderRoutinesTab()
  );
}

export default CarerDashboard;