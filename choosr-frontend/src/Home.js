import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Footer from './components/Footer';
import StarterModal from './components/StarterModal';
import WatchedList from './components/WatchedList';
import EmailModal from './components/EmailModal';

export default function Home() {
  const navigate = useNavigate();
  const [storedUser, setUser] = useState(null);
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [watchedTVShows, setWatchedTVShows] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [showFooter, setShowFooter] = useState(false);



  useEffect(() => {
    // Fetch watched movies
    axios.get('http://localhost:8000/watched-movies/', {
      headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
      }
    })
    .then(response => setWatchedMovies(response.data))
    .catch(error => console.error('Watched movies fetch error:', error));
    console.log(watchedMovies)
    // Fetch watched TV shows
    axios.get('http://localhost:8000/watched-tvshows/', {
      headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
      }
    })
    .then(response => setWatchedTVShows(response.data))
    .catch(error => console.error('Watched TV shows fetch error:', error));
    console.log(watchedTVShows)
  }, []);

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    setUser(storedUser);

  }, []);

  // gets the height of the window so if users watched lists dont extend below scroll depth the footer will still
  useEffect(() => {
    const contentHeight = document.documentElement.scrollHeight;
    const viewportHeight = window.innerHeight;
    if (contentHeight <= viewportHeight) {
      setShowFooter(true);
    }
  
    const handleScroll = () => {
      const scrollHeight = document.documentElement.scrollHeight;
      const scrollTop = document.documentElement.scrollTop;
      const clientHeight = document.documentElement.clientHeight;
      
      if (scrollHeight - scrollTop === clientHeight) {
        setShowFooter(true);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
  
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);
  

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      // use null as data parameter as nothing required for logout
      axios.post('http://localhost:8000/logout/', null, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        console.log('Logout successful:', response.data);
        localStorage.removeItem('token'); 
        navigate('/login'); // Redirect the user to the login page after successful logout
      })
      .catch(error => {
        console.error('Logout error:', error);
        
      });
    }
  };  
  
  // logic for removing items handled here so state can be updated immediately 
  const removeTVShow = (tvShowToRemove) => {
    if (window.confirm('Are you sure you want to permanently remove this TV show?')) {
      const updatedTVShows = watchedTVShows.filter(tvShow => tvShow.id !== tvShowToRemove.id);
      setWatchedTVShows(updatedTVShows);
  
      const token = localStorage.getItem('token');
      axios.post(
          `http://localhost:8000/remove-watched-tv/`, 
          { id: tvShowToRemove.id },
          { headers: { Authorization: `Token ${token}` } }
      )
      .catch(error => console.error('There was an error!', error));
    }
  };
  
  const removeMovie = (movieToRemove) => {
    if (window.confirm('Are you sure you want to permanently remove this movie?')) {
      const updatedMovies = watchedMovies.filter(movie => movie.id !== movieToRemove.id);
      setWatchedMovies(updatedMovies);
  
      const token = localStorage.getItem('token');
      axios.post(
          `http://localhost:8000/remove-watched-movie/`, 
          { id: movieToRemove.id },
          { headers: { Authorization: `Token ${token}` } }
      )
      .catch(error => console.error('There was an error!', error));
    }
  };

  const goToQuestionnaire = () => {
    navigate('/questionnaire', {
      state: {
        watchedMovies: watchedMovies,
        watchedTVShows: watchedTVShows,
      },
    });
  };  

   return (
    <div className={`relative flex flex-col min-h-screen overflow-auto bg-gray-900`}>
      {/* Header Section */}
      <div className="w-full p-6 bg-white dark:bg-gray-900 shadow-xl">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-semibold text-cyan-700 uppercase dark:text-cyan-200">
            Choosr Home
          </h1>
          <div className="flex items-center">
            <div
              onClick={() => navigate('/profile')}
              className="cursor-pointer bg-gray-300 dark:bg-gray-600 w-10 h-10 rounded-full flex items-center justify-center glow"
              title="Profile"
            >
              <svg
                className="text-cyan-600 dark:text-cyan-400"
                fill="currentColor"
                viewBox="0 0 24 24"
                width="32"
                height="32"
              >
                {/* Got profile icon from here --> https://github.com/googlearchive/core-icons/blob/master/core-icons.html */}
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" />
              </svg>
            </div>
            <button
              onClick={handleLogout}
              className="ml-4 bg-gray-300 dark:bg-gray-600 rounded-full px-2 py-1 text-cyan-600 font-bold dark:text-cyan-400 glow"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
  
      {/* Features Section */}
     <div className="mt-16 flex justify-center space-x-16">
     {(watchedMovies.length !== 0 || watchedTVShows.length !== 0) && 
  <button
    onClick={goToQuestionnaire}
    className="flex items-center ml-4 bg-gray-300 dark:bg-gray-600 rounded-full px-8 py-8 text-cyan-600 font-bold dark:text-cyan-400 glow"
  >
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 mr-2">
      <path fill-rule="evenodd" d="M12 2.25a.75.75 0 01.75.75v.756a49.106 49.106 0 019.152 1 .75.75 0 01-.152 1.485h-1.918l2.474 10.124a.75.75 0 01-.375.84A6.723 6.723 0 0118.75 18a6.723 6.723 0 01-3.181-.795.75.75 0 01-.375-.84l2.474-10.124H12.75v13.28c1.293.076 2.534.343 3.697.776a.75.75 0 01-.262 1.453h-8.37a.75.75 0 01-.262-1.453c1.162-.433 2.404-.7 3.697-.775V6.24H6.332l2.474 10.124a.75.75 0 01-.375.84A6.723 6.723 0 015.25 18a6.723 6.723 0 01-3.181-.795.75.75 0 01-.375-.84L4.168 6.241H2.25a.75.75 0 01-.152-1.485 49.105 49.105 0 019.152-1V3a.75.75 0 01.75-.75zm4.878 13.543l1.872-7.662 1.872 7.662h-3.744zm-9.756 0L5.25 8.131l-1.872 7.662h3.744z" clip-rule="evenodd" />
    </svg>
    Choose Again
  </button>
}
  {(watchedMovies.length !== 0 || watchedTVShows.length !== 0) && 
    <button
      onClick={() => setIsOpen(true)}
      className="flex items-center ml-4 bg-gray-300 dark:bg-gray-600 rounded-full px-8 py-8 text-cyan-600 font-bold dark:text-cyan-400 glow"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 mr-2">
        <path d="M4.5 6.375a4.125 4.125 0 118.25 0 4.125 4.125 0 01-8.25 0zM14.25 8.625a3.375 3.375 0 116.75 0 3.375 3.375 0 01-6.75 0zM1.5 19.125a7.125 7.125 0 0114.25 0v.003l-.001.119a.75.75 0 01-.363.63 13.067 13.067 0 01-6.761 1.873c-2.472 0-4.786-.684-6.76-1.873a.75.75 0 01-.364-.63l-.001-.122zM17.25 19.128l-.001.144a2.25 2.25 0 01-.233.96 10.088 10.088 0 005.06-1.01.75.75 0 00.42-.643 4.875 4.875 0 00-6.957-4.611 8.586 8.586 0 011.71 5.157v.003z" />
      </svg>
      Watch with a friend
    </button>
  }
  {isOpen && <EmailModal onClose={() => setIsOpen(false)} />}
</div>
      {/* Watched Lists Section */}
    <div className="mt-14 mx-8">
      {watchedMovies.length === 0 && watchedTVShows.length === 0 ? (
        <StarterModal />
      ) : (
        <div className="flex flex-row space-x-8 justify-center"> 
          <div className="flex flex-col space-y-8 md:space-y-0 md:space-x-4 w-1/2">
            <WatchedList items={watchedMovies} title="Watched Movies" removeItem={removeMovie} />
          </div>
          <div className="flex flex-col space-y-8 md:space-y-0 md:space-x-4 w-1/2">
            <WatchedList items={watchedTVShows} title="Watched TV Shows" removeItem={removeTVShow} />
          </div>
        </div>
      )}
    </div>
      <Footer showFooter={showFooter} />
    </div>
  );
}




