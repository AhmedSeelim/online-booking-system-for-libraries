import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="container mx-auto">
      <h1 className="text-4xl font-bold mb-6">Welcome to the Digital Library</h1>
      <p className="mb-8 text-lg text-gray-600 dark:text-gray-400">Your one-stop place to browse, purchase books, and book library resources.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-3">Browse Books</h2>
          <p className="mb-4">Explore our extensive catalog of books across all genres.</p>
          <Link to="/books" className="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">Go to Books &rarr;</Link>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-3">Book a Resource</h2>
          <p className="mb-4">Reserve study rooms, equipment, and more for your needs.</p>
          <Link to="/resources" className="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">Go to Resources &rarr;</Link>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-3">AI Assistant</h2>
          <p className="mb-4">Use our AI assistant on the side panel to quickly find what you need.</p>
        </div>
      </div>
    </div>
  );
};

export default Home;
