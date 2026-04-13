import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation() {
  var location = useLocation();
  var path = location.pathname;

  function isActive(itemPath) {
    if (itemPath === '/' && path !== '/') {
      return false;
    }
    if (itemPath !== '/' && path.startsWith(itemPath)) {
      return true;
    }
    if (itemPath === '/' && path === '/') {
      return true;
    }
    return false;
  }

  return (
    <nav className="nav">
      <Link to="/" className={'nav-item' + (isActive('/') ? ' active' : '')}>
        <span className="nav-icon">🏠</span>
        <span>Home</span>
      </Link>
      <Link to="/photos" className={'nav-item' + (isActive('/photos') ? ' active' : '')}>
        <span className="nav-icon">📷</span>
        <span>Photos</span>
      </Link>
      <Link to="/music" className={'nav-item' + (isActive('/music') ? ' active' : '')}>
        <span className="nav-icon">🎵</span>
        <span>Music</span>
      </Link>
      <Link to="/messages" className={'nav-item' + (isActive('/messages') ? ' active' : '')}>
        <span className="nav-icon">💬</span>
        <span>Messages</span>
      </Link>
      <Link to="/settings" className={'nav-item' + (isActive('/settings') ? ' active' : '')}>
        <span className="nav-icon">⚙️</span>
        <span>Settings</span>
      </Link>
    </nav>
  );
}

export default Navigation;