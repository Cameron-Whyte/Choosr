// style copied from login
import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { DarkModeContext } from './App';  

export default function SignUp() {
    
    const { darkMode } = useContext(DarkModeContext);
    const [formInput, setFormInput] = useState({
        first_name: '',
        last_name: '',
        date_of_birth: '',
        email: '',
        password1: '',
        password2: ''
    });
    const [errorMessage, setErrorMessage] = useState('');
    const [formErrors, setFormErrors] = useState({});
    const navigate = useNavigate();

    const handleChange = (e) => {
        const name = e.target.name;
        setFormInput({
            ...formInput,
            [name]: e.target.value
        });
    }

    const handleSubmit = (event) => {
        event.preventDefault();
    
        if (formInput.password1 !== formInput.password2) {
            setErrorMessage('Passwords do not match');
            return;
        }

        axios.post('http://localhost:8000/register/', formInput)
        .then(response => {
            console.log('Success:', response.data);
            navigate('/login'); 
        }).catch((error) => {
            console.error('Error: ', error.response.data);
            setFormErrors(error.response.data);
        });
    }

    const labels = ['First Name', 'Last Name', 'Date of Birth', 'Email', 'Password (Minimum of 8 Characters)', 'Confirm Password'];
    const fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'password1', 'password2'];

    return (
        <div className="relative flex flex-col justify-center min-h-screen overflow-hidden bg-gray-200 dark:bg-gray-800">
        <button onClick={() => navigate('/')} className="absolute top-4 left-4 w-10 h-10 p-2 rounded-full text-cyan-600 font-bold dark:text-cyan-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.70a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
                <path d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
            </svg>
        </button>
        <div className="w-full p-6 m-auto bg-white dark:bg-gray-900 rounded-md shadow-xl shadow-cyan-600/40 ring ring-2 ring-cyan-600 lg:max-w-xl">
            <h1 className="text-3xl font-semibold text-center text-cyan-700 uppercase dark:text-cyan-200">Sign Up</h1>
            <form className="mt-6" onSubmit={handleSubmit}>
                {errorMessage && <div className="error-message text-red-500">{errorMessage}</div>}
                {Object.keys(formErrors).map((field, index) =>
                    formErrors[field].map((error, i) => (
                        <div key={`${index}-${i}`} className="error-message text-red-500">{error}</div>
                    ))
                )}
                {labels.map((label, index) => (
                    <div className="mb-2" key={index}>
                        <label htmlFor={fields[index]} className="block text-sm font-semibold text-gray-800 dark:text-gray-200">{label}</label>
                        <input
                            type={fields[index] === 'password1' || fields[index] === 'password2' ? 'password' : fields[index] === 'date_of_birth' ? 'date' : 'text'}
                            required
                            name={fields[index]}
                            value={formInput[fields[index]]}
                            onChange={handleChange}
                            className="block w-full px-4 py-2 mt-2 text-cyan-700 bg-white dark:bg-gray-800 border rounded-md focus:border-cyan-400 focus:ring-cyan-300 focus:outline-none focus:ring focus:ring-opacity-40 dark:text-cyan-200"
                        />
                    </div>
                ))}
                <div className="mt-6">
                    <button className="w-full px-4 py-2 tracking-wide text-white transition-colors duration-200 transform bg-cyan-700 rounded-md hover:bg-cyan-600 focus:outline-none focus:bg-cyan-600 dark:bg-cyan-500 dark:hover:bg-cyan-400 dark:focus:bg-cyan-400">Sign Up</button>
                </div>
                <p className="mt-8 text-xs font-light text-center text-gray-700 dark:text-gray-300">
                    Already have an account? <Link to="/login" className="font-medium text-cyan-600 hover:underline dark:text-cyan-400">Login</Link>
                </p>
            </form>
        </div>
    </div>
    );
}


