// FILE: frontend/src/components/Agent.js
// This is a new, reusable component for displaying each agent.
import React from 'react';

const StatusIndicator = ({ status }) => {
  const baseClasses = "w-3 h-3 rounded-full transition-all duration-300";
  const statusClasses = {
    inactive: "bg-gray-300",
    thinking: "bg-orange-400 animate-pulse",
    complete: "bg-green-500",
    error: "bg-red-500",
  };
  return <div className={`${baseClasses} ${statusClasses[status] || statusClasses.inactive}`} />;
};

const Agent = ({ name, status, output }) => {
  const statusText = {
    inactive: "Waiting for task...",
    thinking: "Analyzing...",
    complete: "Analysis complete.",
    error: "An error occurred.",
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200 flex flex-col h-full">
      <div className="flex items-center mb-2">
        <StatusIndicator status={status} />
        <h3 className="ml-3 text-lg font-semibold text-gray-800">{name}</h3>
      </div>
      <div className="text-sm text-gray-500 flex-grow">
        <p className="italic mb-2">{statusText[status]}</p>
        {output && <p className="text-gray-700 not-italic whitespace-pre-wrap">{output}</p>}
      </div>
    </div>
  );
};

export default Agent;
