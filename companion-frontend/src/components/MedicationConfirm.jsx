import React from 'react';
import { speak } from '../services/speech';

function MedicationConfirm(props) {
  var loading = React.useState(false);
  var setLoading = loading[1];
  loading = loading[0];

  var medicationName = props.medicationName;
  var dose = props.dose;
  var instructions = props.instructions;
  var medicationId = props.medicationId;
  var userId = props.userId || 1;
  var onConfirmed = props.onConfirmed;
  var onDismiss = props.onDismiss;

  function handleConfirm() {
    setLoading(true);
    fetch('/api/medication/confirm', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        medication_id: medicationId
      })
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      setLoading(false);
      if (data.confirmed) {
        speak("Well done John, I've made a note that you've taken your tablets.")
          .then(function() {
            if (onConfirmed) {
              onConfirmed();
            }
          })
          .catch(function() {
            if (onConfirmed) {
              onConfirmed();
            }
          });
      }
    })
    .catch(function(err) {
      setLoading(false);
      console.error('Confirmation error:', err);
    });
  }

  function handleDismiss() {
    if (onDismiss) {
      onDismiss();
    }
  }

  var containerStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(250, 238, 218, 0.97)',
    zIndex: 100,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '30px',
    boxSizing: 'border-box'
  };

  var titleStyle = {
    fontSize: '30px',
    color: '#633806',
    textAlign: 'center',
    marginBottom: '40px',
    fontWeight: 'bold'
  };

  var medNameStyle = {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#412402',
    textAlign: 'center',
    marginBottom: '20px'
  };

  var doseStyle = {
    fontSize: '26px',
    color: '#412402',
    textAlign: 'center',
    marginBottom: '20px'
  };

  var instructionsStyle = {
    fontSize: '22px',
    color: '#412402',
    textAlign: 'center',
    marginBottom: '30px'
  };

  var noteStyle = {
    fontSize: '20px',
    fontStyle: 'italic',
    color: '#854F0B',
    textAlign: 'center',
    marginBottom: '50px'
  };

  var confirmButtonStyle = {
    width: '100%',
    height: '80px',
    backgroundColor: '#3B6D11',
    color: 'white',
    fontSize: '26px',
    fontWeight: 'bold',
    border: 'none',
    borderRadius: '12px',
    cursor: loading ? 'default' : 'pointer',
    opacity: loading ? 0.7 : 1,
    marginBottom: '20px'
  };

  var dismissButtonStyle = {
    width: '100%',
    height: '64px',
    backgroundColor: '#185FA5',
    color: 'white',
    fontSize: '22px',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer'
  };

  return (
    React.createElement('div', { style: containerStyle },
      React.createElement('div', { style: titleStyle }, 'Time for your tablets'),
      React.createElement('div', { style: medNameStyle }, medicationName),
      dose ? React.createElement('div', { style: doseStyle }, dose) : null,
      instructions ? React.createElement('div', { style: instructionsStyle }, instructions) : null,
      React.createElement('div', { style: noteStyle }, 
        "Your tablets are ready. Take them now so you don't forget."
      ),
      React.createElement('button', { 
        style: confirmButtonStyle, 
        onClick: handleConfirm,
        disabled: loading
      }, loading ? 'Please wait...' : "Yes, I've taken them"),
      React.createElement('button', { 
        style: dismissButtonStyle, 
        onClick: handleDismiss
      }, "Remind me in 10 minutes")
    )
  );
}

export default MedicationConfirm;