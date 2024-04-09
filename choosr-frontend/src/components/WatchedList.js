import { React, useState, useContext } from 'react';
import { DarkModeContext } from '../App';
import List from './List.js';
import ListItem from './ListItem.js';
import axios from 'axios'; 
import Select from 'react-select';


function WatchedList({ items, title, removeItem }) {
  const { darkMode } = useContext(DarkModeContext);
  const [selectedItem, setSelectedItem] = useState(null);
  const [watchProviders, setWatchProviders] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(6);

// styles same as questionnaire 
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

  const selectOptions = [
    { value: 3, label: '3 items per page' },
    { value: 6, label: '6 items per page' },
    { value: 9, label: '9 items per page' },
    { value: 12, label: '12 items per page' },
  ];

  // Calculating total pages and slicing items for current page
  const totalItems = items.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  // Reversing the items so that the most recently added appear first
  const reversedItems = [...items].reverse();

  // Slicing the reversed items for current page
  const currentItems = reversedItems.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleWatchClick = (item) => {

    // depending on the item properties determine the content type
    let content_type = '';
   
    if('title' in item) {
      content_type = 'movie';

    } else {
      content_type = 'tv';
    }
    setSelectedItem(item);
    axios.get(`https://api.themoviedb.org/3/${content_type}/${item.id}/watch/providers`, { headers: {
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNjA3MWEzNmZlMzc3MmEzYzQxZjdhMzU1OGY1NmMzNSIsInN1YiI6IjY0YWJlZmQzM2UyZWM4MDBhZjdlNjYxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.FRdlckEGD9yATBdXQ18yvQqT656qBzwqUappgjscI98',
      'Accept': 'application/json'
    } })
    .then(response => response.data)
    .then(data => {
      if (data.results && data.results.GB) {
        let providers = [];
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

  return (
    <div className={`divide-y divide-slate-100 ${darkMode ? 'dark:bg-gray-900 dark:text-gray-200' : ''} w-full mx-2`}>
    <h2 className="text-2xl font-bold text-center mb-12">{title}</h2>
    <div className="flex justify-end mb-4">
      {/* will look for value set by user, currently defualts on rerender */}
      <Select
      value={selectOptions.find(option => option.value === itemsPerPage)} 
      options={selectOptions}
      styles={customStyles}
      onChange={(option) => setItemsPerPage(option?.value)}
    />
    </div>
    {currentItems && (
      <List>
        <div className="grid grid-cols-3 gap-2 shadow-xl shadow-cyan-600/40 ring ring-2 ring-cyan-600"> 
          {currentItems.map((item) => (
            <div className="relative flex flex-col items-center justify-center" key={item.id}> 
              <ListItem movie={item} showDetails={false} />
                <div className="flex space-x-12">
                  <button onClick={() => removeItem(item)}>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                      <path fill-rule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <button 
                    onClick={() => handleWatchClick(item)}
                    onBlur={() => setSelectedItem(null)}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                      <path d="M19.5 6h-15v9h15V6z" />
                      <path fill-rule="evenodd" d="M3.375 3C2.339 3 1.5 3.84 1.5 4.875v11.25C1.5 17.16 2.34 18 3.375 18H9.75v1.5H6A.75.75 0 006 21h12a.75.75 0 000-1.5h-3.75V18h6.375c1.035 0 1.875-.84 1.875-1.875V4.875C22.5 3.839 21.66 3 20.625 3H3.375zm0 13.5h17.25a.375.375 0 00.375-.375V4.875a.375.375 0 00-.375-.375H3.375A.375.375 0 003 4.875v11.25c0 .207.168.375.375.375z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
                {selectedItem === item && (
                  // z index used to put watch providers infront of other items to maintain formatting
                <div className="absolute z-10 top-full mt-2 bg-white shadow-lg rounded border border-gray-200 p-2 dark:bg-gray-800 dark:text-gray-200">
                  {watchProviders?.map((provider, index) => (
                    <p key={index}>{provider.provider_name}</p>
                  ))}
                </div>
              )}         
            </div>
          ))}
        </div>
      </List>
      )}
      <div className="flex items-center justify-center mt-4"> 
  <button onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))} disabled={currentPage === 1} className="hover:bg-gray-800 p-2 rounded">Previous</button>
  {totalPages > 0 ? ( // check if there are pages
    <span className="mx-4">{currentPage} of {totalPages}</span>
  ) : (
    <span className="mx-4">No items in the list</span> // if no pages display message
  )}
  <button onClick={() => setCurrentPage(Math.min(currentPage + 1, totalPages))} disabled={currentPage === totalPages || totalPages === 0} className="hover:bg-gray-800 p-2 rounded">Next</button>
  </div>
  </div>
  );
}

export default WatchedList;

