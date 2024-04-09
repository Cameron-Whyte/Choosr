import React from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const navigate = useNavigate();

  const deleteAllWatchedData = () => {
    if (window.confirm('Are you sure you want to permanently delete all your watched TV and movie data?')) {
      const token = localStorage.getItem('token');
      axios.post(`http://localhost:8000/remove-all-watched/`, {}, { headers: { Authorization: `Token ${token}` } });
    }
  };

  return (
    <div className="relative flex flex-col min-h-screen overflow-auto bg-gray-200 dark:bg-gray-800 justify-center items-center">
      <div className="p-8 bg-white dark:bg-gray-700 shadow-md rounded-lg w-96 text-center">
        <h1 className="text-2xl font-bold text-cyan-700 dark:text-cyan-400 mb-4">
          User Profile
        </h1>
        <button
          onClick={deleteAllWatchedData}
          className="w-full bg-cyan-600 text-white py-2 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4"
        >
          Delete All Watched Data
        </button>
        <button
          onClick={() => navigate('/home')}
          className="w-full bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-50 transition duration-150 ease-in-out"
        >
          Back to Home
        </button>
      </div>
    </div>
  );  
}

