import React, { useState, createContext } from 'react';
import Switch from "react-switch";
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Questionnaire from './Questionnaire';
import ContentList from './components/ContentList';
import JointContentList from './components/JoinedContent';
import TournamentBracket from './components/Bracket';
import LandingPage from './Landing';
import SignUp from './SignUp';
import LogIn from './LogIn';
import Home from './Home';
import Profile from './Profile';

export const DarkModeContext = createContext();

export default function App() {
  // storing the dark mode so even if page is refreshed it will remain
  const [darkMode, setDarkMode] = useState(() => {
    const localDarkMode = localStorage.getItem('darkMode');
    return localDarkMode !== null ? JSON.parse(localDarkMode) : false;
  });

  const handleChange = (checked) => {
    setDarkMode(checked);
    localStorage.setItem('darkMode', checked);
  }

  return (
    <DarkModeContext.Provider value={{ darkMode, setDarkMode: handleChange }}>
      <div className={darkMode ? 'dark' : ''}>
        <div className="fixed top-4 right-4 flex items-center space-x-2">
          <span className={darkMode ? 'text-white' : 'text-black'}>
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </span>
          <Switch
            onChange={handleChange}
            checked={darkMode}
            offColor="#222"
            onColor="#333"
            height={20}
            width={40}
            className="react-switch"
            uncheckedIcon={false}  
            checkedIcon={false}    
          />
        </div>
        <BrowserRouter>
          <Routes>
            <Route path='/' element={<LandingPage />} />
            <Route path='/signup' element={<SignUp />} />
            <Route path='/login' element={<LogIn />} />
            <Route path='/home' element={<Home />} />
            <Route path='/profile' element={<Profile />} />
            <Route path='/questionnaire' element={<Questionnaire />} />
            <Route path='/content-list' element={<ContentList />} />
            <Route path='/bracket' element={<TournamentBracket />} />
            <Route path='/joint-content-list' element={<JointContentList />} />
          </Routes>
        </BrowserRouter>
      </div>
    </DarkModeContext.Provider>
  );
}



