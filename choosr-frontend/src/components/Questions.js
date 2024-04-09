// File to hold the questions depending on what the user selects as their initial answer 
// import { languageDictionary } from './Languages';

export const initialQuestion = {
    label: 'What sort of content are you interested in?',
    name: 'content_type',
    options: ['Film', 'TV'],
};

export const TVquestions = [
    {   
        label: "What genre best describes the TV show you are looking for?",
        name: 'genre',
        options: ['Action & Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Kids', 'Mystery', 'News', 'Reality',
                    'Sci-Fi & Fantasy', 'Soap', 'Talk', 'War & Politics', 'Western'],
    },
    {  
        label: 'Do you normally like mainstream TV shows?',
        name: 'mainstream',
        options: ['Yes', 'No'],
    },
    /*{   // language
        label: 'What language do you want to watch in?',
        name: 'language',
        options: [...Object.values(languageDictionary)],
     },*/
    {   
        label: 'What period of TV would you prefer?',
        name: 'period',
        options: ['Current', '2010s', '2000s', '1990s', '1980s', '1970s or earlier'],
    },
  ];
  
  export const Moviequestions = [
    {   
        label: "What genre best describes the film you are looking for?",
        name: 'genre',
        options: ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music',
                    'Mystery', 'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western'],
    },
    {   
        label: 'Do you normally like mainstream films?',
        name: 'mainstream',
        options: ['Yes', 'No'],
    },
    /*{  
        label: 'What language do you want to watch in?',
        name: 'language',
        options: [...Object.values(languageDictionary)],
    },*/
    {   
        label: 'What period of films would you prefer?',
        name: 'period',
        options: ['Current', '2010s', '2000s', '1990s', '1980s', '1970s or earlier'],
    },
  ];
  
  export const AdvancedTVquestions = [
    {
        label: 'On average how long do you want an episode to be?',
        name: 'length',
        options: ['15mins', '30mins', '45mins', '60mins', '>60mins'] 
    },
    {
        label: 'Where do the TV shows you prefer originate?',
        name: 'origin',
        options: ['United Kingdom', 'North America', 'Oceania', 'Anywhere']
    },
    {
        label: 'Roughly how many seasons would an ideal TV show have?',
        name: 'seasons',
        options: ['1-2', '3-4', '5-6', '7+'] 
    },
    
    {
        label: 'Do you want to watch something still being released?', 
        name: 'status',
        options: ['Yes', 'No', 'Indifferent'] 
    },
  ];
  
  export const AdvancedMoviequestions = [
    {
        label: 'On average how long do you want a film to be?',
        name: 'length',
        options: ['60mins', '90mins', '120mins', '>120mins'] 
    },
    {
        label: 'Do you enjoy films that are part of collections?',
        name: 'collection',
        options: ['Yes', 'No', 'Indifferent'] 
    },
    {
        label: 'Do films with a large budget appeal to you?',  
        name: 'budget',
        options: ['Yes', 'No', 'Indifferent'] 
    },
    {
        label: 'Do you prefer if a film generated a lot of revenue?', 
        name: 'revenue',
        options: ['Yes', 'No', 'Indifferent'] 
    }
  ];