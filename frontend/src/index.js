import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';      // Optional: style imports. Create or remove it.
import App from './App';   // Your main App component

const root = ReactDOM.createRoot(
  document.getElementById('root')
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
