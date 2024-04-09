// template taken from https://tailwindcss.com/ but removed uneccesary features
export default function ListItem({ movie, showDetails = true }) {
  const imageBaseUrl = "https://image.tmdb.org/t/p/w500";

  // movie here refers to both films and tv due to template
  
  return (
    <div className="mx-auto max-w-3xl">
      <article className="flex items-start space-x-6 py-3">
        <img src={`${imageBaseUrl}${movie.poster_path}`} alt="" width="200" height="280" className="flex-none rounded-md bg-slate-100" />
        {showDetails && (
          <div className="min-w-0 relative flex-auto space-y-2">
            <h2 className="font-semibold text-slate-900 truncate pr-20 dark:text-gray-100">{movie.title || movie.name}</h2>
            <div>
              <dl className="mt-2 flex flex-wrap text-sm leading-6 font-medium dark:text-gray-400">
                <dt className="sr-only">Overview</dt>
                <dd>{movie.overview}</dd>
              </dl>
              <dl className="mt-2 flex flex-wrap text-sm leading-6 font-medium dark:text-gray-400">
                <dt className="sr-only">Runtime</dt>
                <dd>{movie.runtime ? movie.runtime + " mins" : movie.episode_run_time ? movie.episode_run_time + " mins" : "Runtime unavailable"}</dd> 
              </dl>
            </div>
          </div>
        )}
      </article>
    </div>
  );
}











  
  
  