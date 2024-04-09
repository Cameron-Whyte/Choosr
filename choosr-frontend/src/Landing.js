import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import LandingHeader from './components/LandingHeader';
import Footer from './components/Footer';
import TopPicks from './components/TopPicks';
import axios from 'axios';


function LandingPage() {
  const navigate = useNavigate();
  const [topPickedMovies, setTopPickedMovies] = useState([]);
  const [topPickedTVShows, setTopPickedTVShows] = useState([]);
  const topPicksRef = useRef(null);
  const [showFooter, setShowFooter] = useState(false);

  const handleBeginClick = () => {
    navigate('/questionnaire');
  };

  // get the top picks from the view and set the states
  useEffect(() => {
    axios.get('http://localhost:8000/top-picks')
      .then((response) => {
        setTopPickedMovies(response.data.movies);
        setTopPickedTVShows(response.data.tv_shows);
      });
  }, []);

  const handleScroll = () => {
    // using a buffer to avoid glitchy behavior
    const buffer = 10;
  
    // gets the top position of the topPicks section relative to the viewport
    // https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect
    const topPicksTop = topPicksRef.current.getBoundingClientRect().top;
  
    // checks if the user has scrolled past the top picks section
    if (topPicksTop + buffer <= 0) {
      setShowFooter(true);
    } else {
      setShowFooter(false);
    }
  };

  useEffect(() => {
    // adds an event listener to the 'scroll' event on the window object
    // will call the 'handleScroll' function every time the user scrolls
    window.addEventListener('scroll', handleScroll);
  
    /*
    return a cleanup function that will be executed if the component is unmounted
    will remove the event listener, so 'handleScroll' is no longer called after the component has been removed from the DOM
    https://www.w3schools.com/js/js_htmldom.asp#:~:text=The%20DOM%20defines%20a%20standard,and%20style%20of%20a%20document.%22
    */
   return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []); // empty dependency array means it will run once after the initial render, and the cleanup function will run on unmount
  
  return (
    <div className="flex flex-col min-h-screen dark:bg-gray-900 dark:text-gray-200 overflow-y-auto">
      <div className="flex items-center justify-center shadow-xl shadow-cyan-600/40 ring ring-2 ring-cyan-600 w-full">
        <LandingHeader />
      </div>
      <div className="flex flex-row bg-gray-800 items-center justify-center p-14 text-xl md:text-2xl border-t border-cyan-600 shadow-cyan-600/40 ring-2 ring-cyan-600 w-full"> 
        <p className="font-bold leading-relaxed mr-32">Use our basic service without signing up:</p>
        <button onClick={handleBeginClick} className="bg-gray-300 dark:bg-gray-900 rounded-full px-16 py-8 text-xl md:text-2xl font-bold text-cyan-600 dark:text-cyan-400 glow">
          Try Now
        </button>
      </div>
      <div className="flex flex-row-reverse items-center justify-center p-14 text-xl md:text-2xl border-t border-cyan-600 shadow-cyan-600/40 ring-2 ring-cyan-600 w-full"> 
        <p className="font-bold leading-relaxed ml-32">...or for more accurate choices and additional features create an account or log in</p>
        <div className="flex flex-col"> 
          <Link to="/login" className="mb-4 bg-gray-300 dark:bg-gray-600 rounded-full px-16 py-8 text-xl text-center md:text-2xl font-bold text-cyan-600 dark:text-cyan-400 glow">Log in</Link>
          <Link to="/signup" className="bg-gray-300 dark:bg-gray-600 rounded-full px-16 py-8 text-xl md:text-2xl font-bold text-cyan-600 dark:text-cyan-400 glow">Sign up</Link>
        </div>
      </div>
      <div
        className="flex items-center justify-center"
        ref={topPicksRef}
      >
        <TopPicks movies={topPickedMovies} tvShows={topPickedTVShows} />
      </div>
      <Footer showFooter={showFooter} />
    </div>
  );  
  }
  
  export default LandingPage;
  
  









