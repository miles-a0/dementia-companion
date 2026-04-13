import React from 'react';

function Home() {
  return (
    <div className="page">
      <h1>Welcome, John</h1>
      <div className="card">
        <h2>What would you like to do?</h2>
      </div>
      <div className="card">
        <h2>Today's Date</h2>
        <p id="current-date"></p>
      </div>
    </div>
  );
}

export default Home;