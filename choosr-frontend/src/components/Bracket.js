import React, { useState, useEffect, useMemo, useContext } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { DarkModeContext } from '../App'; 

function TournamentBracket() {
  const { darkMode } = useContext(DarkModeContext);
  const location = useLocation();
  // useMemo will only recompute the memoized value when one of the dependencies has changed
  const bracketData = useMemo(() => location.state ? location.state.bracketData : [], [location.state]);
  const [queue, setQueue] = useState([]);
  const [currentMatch, setCurrentMatch] = useState([]);
  const [selectedChoice, setSelectedChoice] = useState(null); 
  const [watchProviders, setWatchProviders] = useState(null);
  const content_type = location.state.content_type;
  const navigate = useNavigate();
  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);

  useEffect(() => {
    setQueue([...bracketData]);
  }, [bracketData]);

  useEffect(() => {
    // Whenever the queue changes, update the current match
    setCurrentMatch(queue.slice(0, 2));
    setSelectedChoice(null); // Reset selected choice
  }, [queue]);

  useEffect(() => {
    // Check if a token exists in local storage to verify user is logged in
    setIsUserLoggedIn(!!localStorage.getItem('token'));
  }, []);

  useEffect(() => {
    if(queue.length === 1) {
      const winner = queue[0];
  
      axios.get(`https://api.themoviedb.org/3/${content_type}/${winner.id}/watch/providers`, {
        headers: {
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNjA3MWEzNmZlMzc3MmEzYzQxZjdhMzU1OGY1NmMzNSIsInN1YiI6IjY0YWJlZmQzM2UyZWM4MDBhZjdlNjYxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.FRdlckEGD9yATBdXQ18yvQqT656qBzwqUappgjscI98',
          'Accept': 'application/json'
        }
      })
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
        }
      });
    }
  }, [queue, content_type]);
  
  function selectChoice(choice) {
    setSelectedChoice(choice);
  }

  function confirmSelection() {
    if (selectedChoice) selectWinner(selectedChoice);
  }

  function selectWinner(winner) {
    const newQueue = [...queue];
    // Remove the current match from the queue
    newQueue.splice(0, 2);
    // Add the winner to the end of the queue
    newQueue.push(winner);
    setQueue(newQueue);
  }
  const handleAddToWatchList = (item) => {
    const token = localStorage.getItem('token');
    console.log(content_type);
    axios.post(
        `http://localhost:8000/add-watched-${content_type}/`, 
        { [`${content_type}_id`]: item.id },
        { headers: { Authorization: `Token ${token}` } }
    )
    .then(() => navigate('/home'))
    .catch(error => console.error('There was an error!', error));
  };
  // depending on the content type return the correct information for the winner
  if(queue.length === 1) {
    const winner = queue[0];
    
    const MovieDetails = () => (
      <div className="text-xl space-y-4">
        {winner.overview && <p>{winner.overview}</p>}
        {winner.runtime && <p><span className="font-semibold">Runtime:</span> {winner.runtime} minutes</p>}
        {winner.release_date && <p><span className="font-semibold">Release Date:</span> {winner.release_date}</p>}
        {watchProviders?.length > 0 && (
          <div className="mt-4">
            <p className="font-semibold">Watch in the UK on:</p>
            {watchProviders.map((provider, index) => (
              <p key={index}>{provider.provider_name}</p>
            ))}
          </div>
        )}
      </div>
    );
  
    const TVShowDetails = () => (
      <div className="text-xl space-y-4">
        {winner.overview && <p>{winner.overview}</p>}
        {winner.episode_run_time && <p><span className="font-semibold">Avg. Runtime:</span> {winner.episode_run_time} minutes</p>}
        {winner.number_of_seasons && <p><span className="font-semibold">Seasons:</span> {winner.number_of_seasons}</p>}
        {winner.first_air_date && <p><span className="font-semibold">First Air Date:</span> {winner.first_air_date}</p>}
        {winner.last_air_date && <p><span className="font-semibold">Last Air Date:</span> {winner.last_air_date}</p>}
        {watchProviders?.length > 0 && (
          <div className="mt-4">
            <p className="font-semibold">Watch in the UK on:</p>
            {watchProviders.map((provider, index) => (
              <p key={index}>{provider.provider_name}</p>
            ))}
          </div>
        )}
      </div>
    );
  
    return (
      <div className={`flex flex-col justify-center items-center h-screen p-10 space-y-10 ${darkMode ? 'dark:bg-gray-900 dark:text-gray-200' : ''}`}>
       <button
  onClick={() => {
    if (isUserLoggedIn) {
      navigate('/home');
    } else {
      navigate('/');
    }
  }}
  className="absolute top-4 left-4 w-10 h-10 p-2 rounded-full text-cyan-600 font-bold dark:text-cyan-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700"
>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
    <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.70a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
    <path d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
  </svg>
</button>
        <h1 className={`text-4xl mb-10 font-bold ${darkMode ? 'dark:text-white' : 'text-gray-900'}`}>The winner is {winner.name || winner.title}</h1>
        <div className="flex flex-row justify-between w-full max-w-6xl space-x-16">
          <img src={`http://image.tmdb.org/t/p/w500${winner.poster_path}`} alt={winner.name || winner.title} className="w-full max-w-md h-full object-cover rounded" />
          <div className="ml-4 flex flex-col justify-between space-y-8">
            {winner.title ? <MovieDetails /> : <TVShowDetails />}
          </div>
        </div>
        <div className="flex justify-end w-full space-x-4">
          {isUserLoggedIn && (
            <button
              onClick={() => handleAddToWatchList(winner)}
              className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 glow"
            >
              I'll Watch This
            </button>
          )}
           {/* might be too simple a way, maybe reloading window should mean staying on the winner?*/}
          <button className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 glow"onClick={() => window.location.reload()}>Restart Bracket</button>
        </div>
      </div>
    );
    
  }
  
  return (
    <div className={`flex flex-col justify-center items-center h-screen p-4 space-y-4 ${darkMode ? 'dark:bg-gray-900 dark:text-gray-200' : 'bg-gray-200'}`}>
       <button
  onClick={() => {
    if (isUserLoggedIn) {
      navigate('/home');
    } else {
      navigate('/');
    }
  }}
  className="absolute top-4 left-4 w-10 h-10 p-2 rounded-full text-cyan-600 font-bold dark:text-cyan-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700"
>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
    <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.70a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
    <path d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
  </svg>
</button>
      <div className="w-full max-w-2xl flex flex-col items-center">
      <h1 className="text-5xl text-cyan-500 font-bold mb-8 text-center">Choose the poster that appeals to you most</h1>
        <p className="text-2xl font-semibold mb-4 text-center">Two options are presented at a time. Click one to continue.</p>
      </div>
      <div className="flex flex-col items-center space-y-4">
        <div className="flex justify-center items-center w-full max-w-2xl space-x-4">
          {currentMatch.map((choice, index) => (
            <div
              key={index}
              className={`flex flex-col p-4 m-4 rounded shadow w-full sm:w-1/2 h-full justify-between ${darkMode ? 'dark:bg-gray-800 dark:text-gray-200' : 'bg-white'} ${selectedChoice === choice ? 'border-2 border-cyan-400 shadow-xl shadow-cyan-600/40 ring ring-2 ring-cyan-600' : ''}`}
              onClick={() => selectChoice(choice)}
            >
              <h2 className={`text-xl font-bold mb-2 overflow-hidden h-14 leading-5 text-center ${darkMode ? 'dark:text-gray-200' : ''}`}>{choice.name || choice.title}</h2>
              <img className="mx-auto" src={`http://image.tmdb.org/t/p/w500${choice.poster_path}`} alt={choice.name || choice.title} />
            </div>
          ))}
          {currentMatch.length === 2 && <div className={`absolute rounded-full h-12 w-12 flex items-center justify-center text-2xl font-bold ${darkMode ? 'dark:bg-gray-800 dark:text-gray-200' : 'bg-gray-200'}`}>VS</div>}
        </div>
        {selectedChoice && <button className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 glow" onClick={confirmSelection}>Choose</button>}
      </div>
    </div>
  );  
}

export default TournamentBracket;











