import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getBook, purchaseBook } from '../api/books';
import { Book } from '../types';
import { useAuth } from '../context/AuthContext';
import { me } from '../api/auth';

const BookDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [purchaseStatus, setPurchaseStatus] = useState('');
  const { currentUser, setCurrentUser } = useAuth();


  useEffect(() => {
    if (!id) return;
    const fetchBook = async () => {
      try {
        const data = await getBook(id);
        setBook(data);
      } catch (err) {
        setError('Failed to fetch book details.');
      } finally {
        setLoading(false);
      }
    };
    fetchBook();
  }, [id]);
  
  const handlePurchase = async () => {
    if (!book) return;
    setPurchaseStatus('Processing...');
    try {
      const result = await purchaseBook(book.id, quantity);
      const quantityText = result.quantity > 1 ? `${result.quantity} copies of ` : '';
      setPurchaseStatus(`Success! Your purchase of ${quantityText}'${result.book_title}' for $${result.amount.toFixed(2)} is complete.`);
      const user = await me();
      setCurrentUser(user);
    } catch (err: any) {
      setPurchaseStatus(`Error: ${err.response?.data?.detail || 'Purchase failed.'}`);
    }
  };

  if (loading) return <div>Loading book details...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!book) return <div>Book not found.</div>;

  return (
    <div className="container mx-auto">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 className="text-4xl font-bold mb-2">{book.title}</h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-4">by {book.author}</p>
        <p className="bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 inline-block px-3 py-1 rounded-full text-sm font-semibold mb-6">{book.category}</p>
        <p className="mb-6">{book.description}</p>
        <div className="flex items-baseline mb-6">
          <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">${book.price.toFixed(2)}</p>
          {book.stock_count > 0 ? (
            <p className="ml-4 text-gray-500">({book.stock_count} in stock)</p>
          ) : (
            <p className="ml-4 text-sm font-bold text-red-500 dark:text-red-400 bg-red-100 dark:bg-red-900/50 inline-block px-2 py-1 rounded-full">Out of Stock</p>
          )}
        </div>
        
        {currentUser && (
          <div className="mt-6 p-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-3">Purchase this book</h3>
            {book.stock_count > 0 ? (
              <>
                {purchaseStatus ? (
                  <p className={purchaseStatus.startsWith('Error') ? 'text-red-500' : 'text-green-500'}>{purchaseStatus}</p>
                ) : (
                  <div className="flex items-center gap-4">
                    <div>
                      <label htmlFor="quantity" className="mr-2">Quantity:</label>
                      <input
                        type="number"
                        id="quantity"
                        value={quantity}
                        onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value, 10)))}
                        min="1"
                        max={book.stock_count}
                        className="w-20 p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                      />
                    </div>
                    <button onClick={handlePurchase} className="bg-indigo-600 text-white py-2 px-6 rounded hover:bg-indigo-700">
                      Buy Now
                    </button>
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-500">This book is currently out of stock and cannot be purchased.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BookDetail;