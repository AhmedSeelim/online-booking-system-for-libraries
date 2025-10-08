import React, { useState, useRef, useEffect } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AgentChat from './AgentChat';
import Modal from './Modal';
import { addBalance } from '../api/auth';

const UserIcon = () => (
    <svg className="w-8 h-8 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z"></path>
    </svg>
);


const Layout: React.FC = () => {
  const { currentUser, logout, setCurrentUser } = useAuth();
  const navigate = useNavigate();
  const [isBalanceModalOpen, setIsBalanceModalOpen] = useState(false);
  const [amountToAdd, setAmountToAdd] = useState('');
  const [balanceStatus, setBalanceStatus] = useState('');
  
  // State for the new profile dropdown
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);


  const handleLogout = () => {
    setIsProfileOpen(false);
    logout();
    navigate('/login');
  };
  
  const openBalanceModal = () => {
    setAmountToAdd('');
    setBalanceStatus('');
    setIsBalanceModalOpen(true);
  };

  const handleAddBalance = async () => {
    const amount = parseFloat(amountToAdd);
    if (isNaN(amount) || amount <= 0) {
      setBalanceStatus('Error: Please enter a valid positive amount.');
      return;
    }

    setBalanceStatus('Processing...');
    try {
      const updatedUser = await addBalance(amount);
      setCurrentUser(updatedUser);
      setBalanceStatus(`Success! $${amount.toFixed(2)} added. New balance: $${updatedUser.balance.toFixed(2)}.`);
      setAmountToAdd('');
      setTimeout(() => {
        setIsBalanceModalOpen(false);
      }, 2500);
    } catch (err: any) {
      setBalanceStatus(`Error: ${err.response?.data?.detail || 'Failed to add balance.'}`);
    }
  };

  // Effect to close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
        if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
            setIsProfileOpen(false);
        }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
        document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [profileMenuRef]);


  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-800">
      <div className="flex flex-col flex-1">
        <header className="bg-white dark:bg-gray-900 shadow-md p-4">
          <nav className="container mx-auto flex justify-between items-center">
            <Link to="/" className="text-xl font-bold text-indigo-600 dark:text-indigo-400">Library System</Link>
            <div className="flex items-center">
              <Link to="/books" className="px-3 py-2 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">Books</Link>
              <Link to="/resources" className="px-3 py-2 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">Resources</Link>
              {currentUser ? (
                <>
                  <Link to="/my-bookings" className="px-3 py-2 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">My Bookings</Link>
                  
                  {/* Balance Block */}
                  <div className="flex items-center space-x-2 pl-3 ml-3 border-l border-gray-200 dark:border-gray-700">
                    <span className="text-sm font-semibold text-gray-500 dark:text-gray-400">Balance: ${currentUser.balance.toFixed(2)}</span>
                    <button 
                      onClick={openBalanceModal} 
                      title="Add Balance" 
                      className="w-5 h-5 flex items-center justify-center bg-green-500 text-white rounded-full hover:bg-green-600 text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-green-500"
                    >
                      +
                    </button>
                  </div>
                  
                  {/* Profile Menu Block */}
                  <div className="relative ml-4" ref={profileMenuRef}>
                      <button 
                        onClick={() => setIsProfileOpen(!isProfileOpen)}
                        className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500"
                      >
                         <UserIcon />
                      </button>

                      {isProfileOpen && (
                         <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 z-10">
                            <div className="px-4 py-3">
                                <p className="text-sm">Signed in as</p>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{currentUser.name}</p>
                            </div>
                            <div className="border-t border-gray-200 dark:border-gray-700"></div>
                            <button onClick={handleLogout} className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600">
                                Logout
                            </button>
                        </div>
                      )}
                  </div>

                </>
              ) : (
                <Link to="/login" className="px-3 py-2 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">Login</Link>
              )}
            </div>
          </nav>
        </header>
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <aside className="w-96 bg-white dark:bg-gray-900 shadow-lg border-l border-gray-200 dark:border-gray-700">
        <AgentChat />
      </aside>

      <Modal isOpen={isBalanceModalOpen} onClose={() => setIsBalanceModalOpen(false)} title="Add Balance">
        {balanceStatus ? (
          <p className={balanceStatus.startsWith('Error') ? 'text-red-500' : 'text-green-500'}>{balanceStatus}</p>
        ) : (
          <div>
            <p className="mb-4">Enter the amount you would like to add to your balance.</p>
            <div className="mb-4">
              <label htmlFor="amount" className="block text-sm font-medium mb-2">Amount ($)</label>
              <input
                type="number"
                id="amount"
                value={amountToAdd}
                onChange={(e) => setAmountToAdd(e.target.value)}
                min="0.01"
                step="0.01"
                className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                placeholder="50.00"
                required
              />
            </div>
            <button onClick={handleAddBalance} className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700">
              Add Funds
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Layout;