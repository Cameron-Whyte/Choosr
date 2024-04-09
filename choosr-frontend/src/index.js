import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const rootElement = document.getElementById('root');
const root = createRoot(rootElement);

root.render(
  /* 
  strict mode can double-invoke functions during development
  so note logs/requests may appear twice
  */
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();

