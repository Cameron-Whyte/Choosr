import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function EmailModal({ onClose }) {

  const navigate = useNavigate();
  const [email, setEmail] = useState(''); // input fields are controlled so value not expected to be null thus initialize with empty string
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  
  
  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    setUser(storedUser);
    if (storedUser) {
    console.log('User email', storedUser.email);
}
  }, []);

  const validateInput = async (recommendationFunction) => {
    if (!email) {
      setError({ message: 'Please enter an email.' });
    } else {
      recommendationFunction(email);
    }
  };

  const tvCombinedRecommendation = async (email) => {
   
  let content_type = 'tv';
    try {
      const combinedResponse = await axios.get(`http://localhost:8000/dual-recommend-tv/${user.email}/${email}/`, {
        headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      if (combinedResponse.data.length === 0) {
        setError({ message: 'Sorry no recommendations were found, please try again.' });
      } else {
        navigate('/joint-content-list', { state: { contentData: combinedResponse.data, content_type, inputUserEmail: email } });
      }
    } catch (error) {
      // this may not always be the issue but for now it is the reason the requests fail
      setError({ message: 'Either you or the user entered have not watched any of this content type yet.'});
    }    
  };

  const movieCombinedRecommendation = async (email) => {
    let content_type = 'movie';
    try {
      const combinedResponse = await axios.get(`http://localhost:8000/dual-recommend-movie/${user.email}/${email}/`, {
        headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      if (combinedResponse.data.length === 0) {
        setError({ message: 'Sorry no recommendations were found, please try again.' });
      } else {
        navigate('/joint-content-list', { state: { contentData: combinedResponse.data, content_type, inputUserEmail: email } });
      }
    } catch (error) {
      // this may not always be the issue but for now it is the reason the requests fail
      setError({ message: 'Either you or the user entered have not watched any of this content type yet.'});
    }    
  };
    
  return (
    <div className="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div className="inline-block align-bottom bg-gray-200 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-gray-900 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h2 className="text-lg leading-6 font-bold text-white" id="modal-title">To watch with a friend, enter their choosr email and select a content type.</h2>
            <div className="mt-6">
              <input
                className="w-full sm:w-full text-black white p-2 rounded"
                type="text"
                placeholder="Enter email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError(null); // make the error disappear when the user changes their input
                }}
              />
              {error && (
                <div className="text-red-500 mt-2">
                  Error: {error.detail || error.message || JSON.stringify(error)}
                </div>
              )}
            </div>
          </div>
          <div className="bg-gray-900 px-4 py-3 sm:px-6 sm:flex sm:items-center sm:justify-between">
            <button 
              onClick={onClose}
              type="button" 
              className="inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
            <div className="sm:flex sm:space-x-2">
              <button 
                onClick={() => validateInput(tvCombinedRecommendation)}
                type="button" 
                className="bg-cyan-600 text-white font-semibold py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out glow"
              >
                TV
              </button>
              <button 
                onClick={() => validateInput(movieCombinedRecommendation)}
                type="button" 
                className="bg-cyan-600 text-white font-semibold py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out glow"
              >
                FILM
              </button>
            </div>
          </div>
        </div>
      </div>
      <button onClick={onClose}>Close</button>
    </div>
  );  
  }
  