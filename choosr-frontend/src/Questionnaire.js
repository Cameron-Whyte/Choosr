import React, { useState, useEffect } from 'react';
import { initialQuestion, TVquestions, Moviequestions, AdvancedTVquestions, AdvancedMoviequestions } from './components/Questions';
//import { languageDictionary } from './Languages';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import Select from 'react-select';

/*const reversedLanguageDictionary = {};
for (const code in languageDictionary) {
  reversedLanguageDictionary[languageDictionary[code]] = code;
}
*/

function Questionnaire() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState([initialQuestion]);
  const navigate = useNavigate();
  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);
  const location = useLocation();
  const { watchedMovies, watchedTVShows } = location.state || { watchedMovies: null, watchedTVShows: null }; // allows non registered users to still access page
  const [excludedContent, setExcludedContent] = useState([]);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    setStartTime(performance.now());
  }, []); // empty dependency array ensures that the effect only runs once


  const checkForToken = () => {
    const token = localStorage.getItem('token');
    setIsUserLoggedIn(!!token);
  };

  const mapAnswers = (answers) => {
    return {
      content_type: { Film: 'movie', TV: 'tv' }[answers.content_type],
      genre: answers.genre,
      mainstream: { Yes: '>10', No: '<=10' }[answers.mainstream],
      //language: { Any: 'any', ...reversedLanguageDictionary }[answers.language],
      period: {
        Current: 'Current',
        '2010s': '2010',
        '2000s': '2000',
        '1990s': '1990',
        '1980s': '1980',
        '1970s or earlier': '<1970',
      }[answers.period],
      length: answers.length, 
      origin: answers.origin,
      // if a user selects indifferent, just ignore it in the request
      seasons: answers.seasons === 'Indifferent' ? undefined : answers.seasons,
      status: answers.status,
      collection: answers.collection === 'Indifferent' ? undefined : answers.collection,
      budget: answers.budget === 'Indifferent' ? undefined : answers.budget,
      revenue: answers.revenue === 'Indifferent' ? undefined : answers.revenue
    };
  };

  const [answers, setAnswers] = useState({
    content_type: '',
    genre: '',
    mainstream: '',
    //language: '',
    period: '',
    length: '',
    origin: '',
    seasons: '',
    status: '',
    collection: '',
    budget: '',
    revenue: '',
  });

  const setWatchedIds = () => {
    // exit if user is unregistered version
    if (!isUserLoggedIn) return; 
    if (!watchedMovies || !watchedTVShows) return;
  
    // Separate watched movies and TV shows based on the data passed through props
    const watchedIdsMovies = watchedMovies.map(item => item.id);
    const watchedIdsTVShows = watchedTVShows.map(item => item.id);
  
    // exclude content based on the content type selected by the user
    if (answers.content_type === 'Film') {
      setExcludedContent(watchedIdsMovies);
    } else if (answers.content_type === 'TV') {
      setExcludedContent(watchedIdsTVShows);
    }
  };

  useEffect(() => {
    setWatchedIds();
  }, [isUserLoggedIn, answers.content_type]); 

  useEffect(() => {
    checkForToken();
    // Event listener for storage changes
    window.addEventListener('storage', checkForToken);
    // Cleanup function to remove the event listener when the component unmounts
    return () => {
      window.removeEventListener('storage', checkForToken);
    };
  }, []); // Empty dependency array so it only runs on mount and unmount

  // if a user is logged in offer them more questions
  useEffect(() => {
    if (answers.content_type === 'TV') {
      if (isUserLoggedIn) {
        setQuestions([initialQuestion, ...TVquestions, ...AdvancedTVquestions]);
      } else {
        setQuestions([initialQuestion, ...TVquestions]);
      }
    } else if (answers.content_type === 'Film') {
      if (isUserLoggedIn) {
        setQuestions([initialQuestion, ...Moviequestions, ...AdvancedMoviequestions]);
      } else {
        setQuestions([initialQuestion, ...Moviequestions]);
      }
    } else {
      setQuestions([initialQuestion]);
    }
  }, [answers.content_type, isUserLoggedIn]); 

  const handleChange = (value, name) => {
    setAnswers({
      ...answers,
      [name]: value,
    });
  };  

  const handleSubmit = (e) => {
    e.preventDefault();
    if (answers[questions[currentQuestion].name] === '') return;
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      const mappedAnswers = mapAnswers(answers);
  
      if (isUserLoggedIn && excludedContent.length > 0) {
        mappedAnswers.exclude = excludedContent.join(','); // Converts the array to a comma-separated string
      }
  
      const backendURL = `http://localhost:8000/${mappedAnswers.content_type}/`;
      const endTime = performance.now();
      const timeTaken = (endTime - startTime) / 1000; // convert time from milliseconds to seconds
      console.log(timeTaken)
  
      axios.get(backendURL, { params: mappedAnswers })
        .then(response => {
          navigate('/content-list', { state: { contentData: response.data, mappedAnswers: mappedAnswers, excludedContent: excludedContent, } });
        })
        .catch(error => {
          console.error('There was an error!', error);
        });
  
      // set correct URL based on whether the user is logged in
      const timeTakenURL = isUserLoggedIn ?
        'http://localhost:8000/save-time-taken-registered/' :
        'http://localhost:8000/save-time-taken-unregistered/';
  
      axios.post(timeTakenURL, { timeTaken })
        .then(response => console.log(response.data))
        .catch(error => console.error('Error:', error));
    }
  };  

  const handleBack = () => {
    setCurrentQuestion(currentQuestion - 1);
  };

  const customStyles = {
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isFocused ? '#f5f5f5' : null,
      color: state.isFocused ? 'black' : '#blue-gray-700', // desired color for text here
    }),
    control: (provided) => ({
      ...provided,
      borderColor: '#blue-gray-200',
      borderWidth: '2px',
      backgroundColor: '#blue-gray-700',
    }),
    singleValue: (provided) => ({
      ...provided,
      color: '#blue-gray-700', // selected value text
    }),
    placeholder: (provided) => ({
      ...provided,
      color: '#blue-gray-400', // placeholder text
    }),
  };

  const selectOptions = questions[currentQuestion].options?.map((option) => ({
    value: option,
    label: option,
  }));

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-gray-300 via-gray-100 to-gray-300 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 text-gray-900 dark:text-gray-200">
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
      <form className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-lg shadow-md p-8" onSubmit={handleSubmit}>
        {currentQuestion < questions.length && (
          <div className="relative mb-6">
            <label className="block text-black dark:text-gray-100 text-xl font-semibold mb-2">
              {questions[currentQuestion].label}
            </label>
            <div className="w-full">
            <Select
              value={{ value: answers[questions[currentQuestion].name], label: answers[questions[currentQuestion].name] }}
              options={selectOptions}
              styles={customStyles}
              onChange={(option) => handleChange(option?.value, questions[currentQuestion].name)}
              placeholder="Select..."
            />
            </div>
          </div>
        )}
        <div className="flex space-x-4">
          {currentQuestion > 0 && (
            <button
              className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 glow"
              type="button"
              onClick={handleBack}
            >
              Previous
            </button>
          )}
          <button
            className="bg-cyan-600 text-white py-2 px-4 min-w-32 rounded-lg hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-opacity-50 transition duration-150 ease-in-out mb-4 glow"
            type="submit"
            disabled={answers[questions[currentQuestion].name] === ''}
          >
            {currentQuestion < questions.length - 1 ? 'Next Question' : 'Submit'}
          </button>
        </div>
      </form>
    </div>
  );  
};

export default Questionnaire;
