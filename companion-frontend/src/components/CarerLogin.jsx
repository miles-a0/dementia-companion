import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function CarerLogin(props) {
  var navigate = useNavigate();
  var [username, setUsername] = useState('');
  var [password, setPassword] = useState('');
  var [error, setError] = useState('');
  var [loading, setLoading] = useState(false);
  
  var onLoginSuccess = props.onLoginSuccess;
  
  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        password: password
      })
    })
    .then(function(response) {
      console.log('Login response status:', response.status);
      return response.json();
    })
    .then(function(data) {
      console.log('Login response data:', data);
      setLoading(false);
      if (data.token) {
        console.log('Setting token in localStorage');
        localStorage.setItem('companion_carer_token', data.token);
        console.log('Calling onLoginSuccess');
        if (onLoginSuccess) {
          onLoginSuccess();
        }
        console.log('Navigating to /carer');
        alert('Login successful! Redirecting...');
        navigate('/carer', { replace: true });
      } else {
        console.log('No token in response');
        alert('Login failed - no token');
        setError('Incorrect username or password');
      }
    })
    .catch(function(err) {
      setLoading(false);
      setError('Incorrect username or password');
    });
  }
  
  var containerStyle = {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    backgroundColor: '#f5f5f5'
  };
  
  var formStyle = {
    width: '100%',
    maxWidth: '400px',
    display: 'flex',
    flexDirection: 'column'
  };
  
  var titleStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: '40px'
  };
  
  var inputStyle = {
    width: '100%',
    height: '60px',
    fontSize: '22px',
    padding: '0 15px',
    marginBottom: '20px',
    border: '2px solid #ccc',
    borderRadius: '8px',
    boxSizing: 'border-box'
  };
  
  var buttonStyle = {
    width: '100%',
    height: '64px',
    fontSize: '22px',
    color: 'white',
    backgroundColor: '#185FA5',
    border: 'none',
    borderRadius: '8px',
    cursor: loading ? 'default' : 'pointer',
    marginTop: '10px'
  };
  
  var errorStyle = {
    color: 'red',
    fontSize: '18px',
    textAlign: 'center',
    marginTop: '15px'
  };
  
  return React.createElement('div', { style: containerStyle },
    React.createElement('form', { style: formStyle, onSubmit: handleSubmit },
      React.createElement('div', { style: titleStyle }, 'Carer Login'),
      React.createElement('input', {
        type: 'text',
        placeholder: 'Username',
        style: inputStyle,
        value: username,
        onChange: function(e) { setUsername(e.target.value); }
      }),
      React.createElement('input', {
        type: 'password',
        placeholder: 'Password',
        style: inputStyle,
        value: password,
        onChange: function(e) { setPassword(e.target.value); }
      }),
      React.createElement('button', {
        type: 'submit',
        style: buttonStyle,
        disabled: loading
      }, loading ? 'Logging in...' : 'Login'),
      error ? React.createElement('div', { style: errorStyle }, error) : null
    )
  );
}

export default CarerLogin;