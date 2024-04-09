import React from 'react';

const imageBaseUrl = "https://image.tmdb.org/t/p/w500";

function TopPicks({ movies, tvShows }) {

  // Similar structure to content list however has two rows of three for each top picks
  return (
    <div className="w-full flex justify-center bg-gray-100 dark:bg-gray-800 mx-auto border-t border-b border-cyan-600 shadow-cyan-600/40 ring-2 ring-cyan-600">
      <div className="w-3/4 p-10 flex flex-col items-start">
        <h2 className="text-4xl font-bold mb-4">Top Picked Films</h2>
        <div className="flex flex-wrap">
          {movies.map((movie, index) => (
            <div key={index} className="w-1/3 p-4">
            <div className="h-12 flex items-center justify-center overflow-hidden"> {/* Stops longer titles messing up formatting*/}
              <h3 className="mt-4 text-lg font-bold">{movie.title}</h3>
            </div>
            <img src={`${imageBaseUrl}${movie.poster_path}`} alt={movie.title} />
            {/*<p>{movie.overview}</p>*/}
            <p className="mt-4 text-lg font-semibold">Release Date: {movie.release_date}</p>
            <p className="mt-4 text-lg font-semibold">Runtime: {movie.runtime} minutes</p>
          </div>
          ))}
        </div>
        <h2 className="text-4xl font-bold mt-8 mb-4">Top Picked TV Shows</h2>
        <div className="flex flex-wrap">
          {tvShows.map((tvShow, index) => (
            <div key={index} className="w-1/3 p-4">
              <div className="h-12 flex items-center justify-center overflow-hidden"> {/* Stops longer titles messing up formatting*/}
              <h3 className="mt-4 text-lg font-bold">{tvShow.name}</h3>
              </div >
              <img src={`${imageBaseUrl}${tvShow.poster_path}`} alt={tvShow.name} />
              {/*<p>{tvShow.overview}</p>*/}
              <p className="mt-4 text-lg font-semibold">First Air Date: {tvShow.first_air_date}</p>
              <p className="mt-4 text-lg font-semibold">Episode Runtime: {tvShow.episode_run_time} minutes</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );  
}


export default TopPicks;

