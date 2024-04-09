import React, { useState, useContext, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import List from './List.js';
import ListItem from './ListItem.js';
import { DarkModeContext } from '../App'; 

function JointContentList() {
  const { darkMode } = useContext(DarkModeContext);
  const location = useLocation();
  const navigate = useNavigate();
  const [contentData, setContentData] = useState(location.state ? location.state.contentData : []);
  const content_type = location.state ? location.state.content_type : '';
  const email2 = location.state ? location.state.inputUserEmail : '';
  const [selectedItem, setSelectedItem] = useState(null);
  const [watchProviders, setWatchProviders] = useState([]);
  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);
  const [excludedContent, setExcludedContent] = useState([]);
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    setUser(storedUser);
  }, []);

  // tracking the content a user has already seen and storing it
  useEffect(() => {
    const newExcludedContent = [...excludedContent, ...contentData.map(content_type => content_type.id)];
    setExcludedContent(newExcludedContent);
  }, [contentData]); // eslint warns about missing excludedContent dependency but including it causes a 'Maximum update depth exceeded' warning
  
  const handleWatchClick = (item) => {
    setSelectedItem(item);
    axios.get(`https://api.themoviedb.org/3/${content_type}/${item.id}/watch/providers`, { headers: {
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNjA3MWEzNmZlMzc3MmEzYzQxZjdhMzU1OGY1NmMzNSIsInN1YiI6IjY0YWJlZmQzM2UyZWM4MDBhZjdlNjYxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.FRdlckEGD9yATBdXQ18yvQqT656qBzwqUappgjscI98',
      'Accept': 'application/json'
    } })
    .then(response => response.data)
    .then(data => {
      if (data.results && data.results.GB) {
        let providers = [];
        /* 
          Loop through each key in GB, treating it as a category if it contains an array
          This is because I encountered 3 seperate categories so if there are more im unaware of this should capture them
          Need the key value for API request to work
        */
          // eslint-disable-next-line
        for (const [key, value] of Object.entries(data.results.GB)) {
          if (Array.isArray(value)) {
            providers = [...providers, ...value];
          }
        }

        const uniqueProviders = Array.from(new Set(providers.map(p => p.provider_name)))
                                    .map(name => providers.find(p => p.provider_name === name));

        setWatchProviders(uniqueProviders);
        console.log(uniqueProviders);
      }
    })
    .catch(error => {
        console.error('There was an error!', error);
    });
  };

  useEffect(() => {
    // Check if a token exists in local storage to verify user is logged in
    setIsUserLoggedIn(!!localStorage.getItem('token'));
  }, []);

  // should it add to both users watch list? Maybe a bad idea, could send a message to the user asking if they want to add it?
  const handleAddToWatchList = (item) => {
    const token = localStorage.getItem('token');
    axios.post(
        `http://localhost:8000/add-watched-${content_type}/`, 
        { [`${content_type}_id`]: item.id },
        { headers: { Authorization: `Token ${token}` } }
    )
    .then(() => navigate('/home'))
    .catch(error => console.error('There was an error!', error));
  };

  // refreshing numerous times can lead to very large requests as all excluded ids will be included
  // so may want to set a limit of some sort. It can handle a lot though because of refining in the backend
  const handleRefreshResults = () => {
    const email1 = user.email; 
    const excludeIds = excludedContent.join(',');
    axios.get(`http://localhost:8000/dual-recommend-${content_type}/${email1}/${email2}/?exclude=${excludeIds}`, {
        headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
        }
    })
    .then(response => {
      // directly update the contentData state with the new recommendations.
      setContentData(response.data);
    })
    .catch(error => {
      console.error(error);
    });
  }
  
  return (
    <div className={`flex flex-col min-h-screen divide-y divide-slate-100 ${darkMode ? 'dark:bg-gray-900 dark:text-gray-200' : ''}`}>
      <button
        onClick={() => {navigate('/home');}}
        className="absolute top-4 left-4 w-10 h-10 p-2 rounded-full text-cyan-600 font-bold dark:text-cyan-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700"
      >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
        <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.70a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
        <path d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
      </svg>
    </button>
      <div className="flex-grow">
        {contentData && (
          <List>
            {contentData.map((item) => (
              <div key={item.id} className="flex justify-between items-start space-x-10">
                <ListItem movie={item}/>
                <div>
                <div>
                {isUserLoggedIn && (
                    <button
                      onClick={() => handleAddToWatchList(item)}
                      className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mr-10 glow"
                    >
                      We'll Watch This
                    </button>
                  )}
                  </div>
                  <button className='mr-56'
                  onClick={() => handleWatchClick(item)}
                  onBlur={() => setSelectedItem(null)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8">
                    <path d="M19.5 6h-15v9h15V6z" />
                    <path fillRule="evenodd" d="M3.375 3C2.339 3 1.5 3.84 1.5 4.875v11.25C1.5 17.16 2.34 18 3.375 18H9.75v1.5H6A.75.75 0 006 21h12a.75.75 0 000-1.5h-3.75V18h6.375c1.035 0 1.875-.84 1.875-1.875V4.875C22.5 3.839 21.66 3 20.625 3H3.375zm0 13.5h17.25a.375.375 0 00.375-.375V4.875a.375.375 0 00-.375-.375H3.375A.375.375 0 003 4.875v11.25c0 .207.168.375.375.375z" clipRule="evenodd" />
                  </svg>
                </button>
                {selectedItem === item && (
                  // absolute z-index to maintain formatting integrity
                <div className="absolute z-10 mt-2 bg-white shadow-lg rounded border border-gray-200 p-2 dark:bg-gray-800 dark:text-gray-200">
                  {watchProviders?.map((provider, index) => (
                    <p key={index}>{provider.provider_name}</p>
                  ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </List>
        )}
      <div className="flex items-center justify-center">
      <button
        onClick={handleRefreshResults}
        className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 mr-4 glow"
      >
        Refresh Results
      </button>
      <h1 className='mb-4'>Please note, increased refreshing can diminish accuracy of recommendations.</h1>
    </div>
    </div>
  </div>
);
}

export default JointContentList;