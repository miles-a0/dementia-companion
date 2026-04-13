import React from 'react';

function CarerDashboard(props) {
  var onLogout = props.onLogout;
  
  var containerStyle = {
    minHeight: '100vh',
    padding: '20px',
    backgroundColor: '#f5f5f5'
  };
  
  var headerStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px'
  };
  
  var logoutButtonStyle = {
    padding: '15px 30px',
    fontSize: '18px',
    backgroundColor: '#666',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer'
  };
  
  return React.createElement('div', { style: containerStyle },
    React.createElement('div', { style: headerStyle }, 'Carer Dashboard'),
    React.createElement('p', null, 'Welcome to the Carer Dashboard. This is where you can manage Johns care.'),
    React.createElement('button', { style: logoutButtonStyle, onClick: onLogout }, 'Logout')
  );
}

export default CarerDashboard;