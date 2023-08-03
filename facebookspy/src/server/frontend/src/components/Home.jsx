import React from 'react';
import Navbar from './Navbar';
// import './Page.css'; 

const HomePage = () => {
  return (
    <div className="page">
      <Navbar />
      <div className="content">
        <h1>Home</h1>
      </div>
    </div>
  );
};

export default HomePage;
