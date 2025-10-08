import React, { useState, useEffect, useCallback, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { listBooks, createBook, updateBook, deleteBook } from '../api/books';
import { Book, BookCreate, BookUpdate } from '../types';
import Modal from '../components/Modal';
import { useAuth } from '../context/AuthContext';

// Helper component for form fields
const InputField: React.FC<{name: string, label: string, value: string | number, onChange: any, type?: string, required?: boolean, min?: number, step?: number}> = ({ name, label, ...props }) => (
    <div>
        <label htmlFor={name} className="block text-sm font-medium mb-1">{label}</label>
        <input id={name} name={name} {...props} className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600" />
    </div>
);

const Books: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { currentUser } = useAuth();

  // State for admin modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentBook, setCurrentBook] = useState<BookCreate | BookUpdate | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [modalError, setModalError] = useState('');

  const defaultBook: BookCreate = {
    title: '',
    author: '',
    category: '',
    description: '',
    price: 0,
    stock_count: 0,
  };

  const fetchBooks = useCallback(async () => {
    try {
      const data = await listBooks();
      setBooks(data);
    } catch (err) {
      setError('Failed to fetch books.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchBooks();
  }, [fetchBooks]);

  // Admin handlers
  const openCreateModal = () => {
    setCurrentBook(defaultBook);
    setEditingId(null);
    setModalError('');
    setIsModalOpen(true);
  };

  const openEditModal = (book: Book) => {
    const { id, ...editableData } = book;
    setCurrentBook(editableData);
    setEditingId(book.id);
    setModalError('');
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentBook(null);
    setEditingId(null);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    if (currentBook) {
      setCurrentBook({
        ...currentBook,
        [name]: ['price', 'stock_count'].includes(name) ? Number(value) : value,
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentBook) return;

    try {
      if (editingId) {
        await updateBook(editingId, currentBook as BookUpdate);
      } else {
        await createBook(currentBook as BookCreate);
      }
      closeModal();
      fetchBooks();
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail;
      let errorMessage = 'An error occurred.';
      if (typeof errorDetail === 'string') {
          errorMessage = errorDetail;
      } else if (Array.isArray(errorDetail)) {
          errorMessage = errorDetail.map((e: any) => e.msg).join(', ');
      }
      setModalError(errorMessage);
    }
  };
  
  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this book? This action cannot be undone.')) {
        try {
            await deleteBook(id);
            fetchBooks();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete book.');
        }
    }
  };

  if (loading) return <div>Loading books...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="container mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Books Catalog</h1>
        {currentUser?.role === 'admin' && (
          <button onClick={openCreateModal} className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700">
            Create New Book
          </button>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {books.map((book) => (
          <div key={book.id} className={`bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md flex flex-col justify-between ${book.stock_count === 0 ? 'opacity-60' : ''}`}>
            <div>
              <h2 className="text-xl font-semibold">{book.title}</h2>
              <p className="text-gray-600 dark:text-gray-400">by {book.author}</p>
              <p className="bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 inline-block px-2 py-0.5 rounded-full text-sm font-semibold my-2">{book.category}</p>
              <p className="text-lg font-bold text-indigo-600 dark:text-indigo-400 mt-2">${book.price.toFixed(2)}</p>
              {book.stock_count > 0 ? (
                <p className="text-sm text-gray-500">Stock: {book.stock_count}</p>
              ) : (
                <p className="mt-1 text-sm font-bold text-red-500 dark:text-red-400 bg-red-100 dark:bg-red-900/50 inline-block px-2 py-0.5 rounded-full">Out of Stock</p>
              )}
            </div>
            <div className="mt-4 flex flex-col gap-2">
                <Link to={`/books/${book.id}`} className="block w-full text-center bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700">
                  View Details
                </Link>
                {currentUser?.role === 'admin' && (
                    <div className="flex justify-end space-x-2 border-t dark:border-gray-700 pt-2 mt-2">
                        <button onClick={() => openEditModal(book)} className="text-sm text-indigo-600 hover:underline">Edit</button>
                        <button onClick={() => handleDelete(book.id)} className="text-sm text-red-600 hover:underline">Delete</button>
                    </div>
                )}
            </div>
          </div>
        ))}
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingId ? 'Edit Book' : 'Create Book'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {modalError && <p className="text-red-500">{modalError}</p>}
          <InputField name="title" label="Title" value={currentBook?.title || ''} onChange={handleChange} required />
          <InputField name="author" label="Author" value={currentBook?.author || ''} onChange={handleChange} required />
          <InputField name="category" label="Category" value={currentBook?.category || ''} onChange={handleChange} required />
          <InputField name="price" label="Price ($)" type="number" value={currentBook?.price ?? 0} onChange={handleChange} required min={0} step={0.01} />
          <InputField name="stock_count" label="Stock" type="number" value={currentBook?.stock_count ?? 0} onChange={handleChange} required min={0} />
          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-1">Description</label>
            <textarea name="description" id="description" value={currentBook?.description || ''} onChange={handleChange} rows={4} className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600" />
          </div>
          <div className="flex justify-end space-x-2 pt-2">
            <button type="button" onClick={closeModal} className="bg-gray-200 dark:bg-gray-600 py-2 px-4 rounded hover:bg-gray-300 dark:hover:bg-gray-500">Cancel</button>
            <button type="submit" className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700">Save Book</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Books;