import React from 'react';
import './Agent.css';

const Agent = ({ name, status, output }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'thinking':
        return 'yellow';
      case 'responded':
        return 'green';
      default:
        return 'grey';
    }
  };

  return (
    <div className="agent-card">
      <div className="agent-header">
        <span className={`status-light ${getStatusColor()}`}></span>
        <h3>{name}</h3>
      </div>
      <div className="agent-output">
        {output ? <p>{output}</p> : <p className="no-output">Awaiting analysis...</p>}
      </div>
    </div>
  );
};

export default Agent;