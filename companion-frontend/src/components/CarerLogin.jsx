import React from 'react';

function CarerLogin(props) {
  var username = React.useState('');
  username = username[0];
  var setUsername = username[1];
  
  var password = React.useState('');
  password = password[0];
  var setPassword = password[1];
  
  var error = React.useState('');
  error = error[0];
  var setError = error[1];
  
  var loading = React.useState(false);
  loading = loading[0];
  var setLoading = loading[1];
  
  var onLoginSuccess = props.onLoginSuccess;
  
  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    fetch('http://173.249.40.161:8001/api/auth/login', {
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
      return response.json();
    })
    .then(function(data) {
      setLoading(false);
      if (data.token) {
        localStorage.setItem('companion_carer_token', data.token);
        if (onLoginSuccess) {
          onLoginSuccess();
        }
      } else {
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