/ FILE: frontend/src/components/Agent.js
// ACTION: Ensure this component exists in your project. No changes from last time.

import React from 'react';

const Agent = ({ name, status, output }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'thinking':
        return 'bg-yellow-400 animate-pulse';
      case 'responded':
        return 'bg-green-500';
      case 'inactive':
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="border border-gray-200 rounded-xl p-4 bg-white shadow-md transition-all duration-300">
      <div className="flex items-center mb-2">
        <div className={`w-3 h-3 rounded-full mr-3 ${getStatusColor()}`}></div>
        <h3 className="text-md font-semibold text-gray-800">{name}</h3>
      </div>
      <div className="text-sm text-gray-600 pl-6 h-16 overflow-y-auto">
        {status === 'thinking' && <p className="italic">Analyzing...</p>}
        {status === 'responded' && output && <p>{output}</p>}
        {status === 'inactive' && <p className="text-gray-400">Waiting for task...</p>}
      </div>
    </div>
  );
};

export default Agent;