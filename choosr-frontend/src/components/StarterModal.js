import React from 'react';
import { useNavigate } from 'react-router-dom';

function StarterModal() {
  const navigate = useNavigate();

  const handleGetStartedClick = () => {
    navigate('/questionnaire');
  };

  return (
    <div className="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div className="inline-block align-bottom bg-gray-200 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-gray-900 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h2 className="text-lg leading-6 font-bold text-white" id="modal-title">To find something to watch, you must first complete a questionnaire.</h2>
            <div className="mt-2">
            </div>
          </div>
          <div className="bg-gray-900 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button onClick={handleGetStartedClick} type="button" className="bg-cyan-600 text-white font-semibold py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 glow ">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </div>
  );  
}

export default StarterModal;

