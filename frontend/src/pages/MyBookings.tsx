import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { listUserBookings, cancelBooking } from '../api/bookings';
import { listResources } from '../api/resources';
import { Booking, Resource } from '../types';
import { formatToLocalDateTime, formatToLocalTime, parseUTCDate } from '../utils/dateUtils';

const MyBookings: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelStatus, setCancelStatus] = useState<{ [key: number]: string }>({});
  const [showPast, setShowPast] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [bookingsData, resourcesData] = await Promise.all([
        listUserBookings(showPast),
        listResources()
      ]);
      const sortedData = bookingsData.sort((a, b) => parseUTCDate(a.start_datetime).getTime() - parseUTCDate(b.start_datetime).getTime());
      setBookings(sortedData);
      setResources(resourcesData);
    } catch (err) {
      setError('Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  }, [showPast]);


  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const resourceMap = useMemo(() => {
    return new Map(resources.map(r => [r.id, r]));
  }, [resources]);


  const handleCancel = async (bookingId: number) => {
    setCancelStatus(prev => ({ ...prev, [bookingId]: 'Cancelling...' }));
    try {
      const cancelledBooking = await cancelBooking(bookingId);
      setCancelStatus(prev => ({ ...prev, [bookingId]: 'Cancelled successfully!' }));
      // Update the state locally for instant feedback, instead of a full refetch
      setBookings(currentBookings =>
        currentBookings.map(b => b.id === bookingId ? { ...b, ...cancelledBooking } : b)
      );
    } catch (err: any) {
      setCancelStatus(prev => ({ ...prev, [bookingId]: `Error: ${err.response?.data?.detail || 'Failed to cancel.'}` }));
    }
  };

  const isPast = (endTime: string) => parseUTCDate(endTime) < new Date();

  if (loading) return <div>Loading your bookings...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold mb-6">My Bookings</h1>

      <div className="flex items-center mb-4">
          <input
              type="checkbox"
              id="show-past"
              checked={showPast}
              onChange={(e) => setShowPast(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600"
          />
          <label htmlFor="show-past" className="ml-2 block text-sm">
              Show past bookings
          </label>
      </div>

      {bookings.length === 0 ? (
        <p>You have no bookings.</p>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => {
            const resource = resourceMap.get(booking.resource_id);
            let displayCost = 'N/A';

            if (resource) {
              const startDate = parseUTCDate(booking.start_datetime);
              const endDate = parseUTCDate(booking.end_datetime);
              if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime())) {
                const durationMs = endDate.getTime() - startDate.getTime();
                const durationHours = durationMs / (1000 * 60 * 60);
                if (durationHours > 0) {
                  const calculatedCost = durationHours * resource.hourly_rate;
                  displayCost = `$${calculatedCost.toFixed(2)}`;
                }
              }
            }

            return (
              <div key={booking.id} className={`p-4 rounded-lg shadow-md ${isPast(booking.end_datetime) || booking.status === 'cancelled' ? 'bg-gray-200 dark:bg-gray-700 opacity-60' : 'bg-white dark:bg-gray-800'}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold">{resource?.name || `Resource ID: ${booking.resource_id}`}</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                      {formatToLocalDateTime(booking.start_datetime)} - {formatToLocalTime(booking.end_datetime)}
                    </p>
                    <p>Cost: {displayCost}</p>
                    {booking.notes && <p className="mt-2 text-sm italic text-gray-500 dark:text-gray-400">Notes: "{booking.notes}"</p>}

                    <div className="mt-2">
                      {isPast(booking.end_datetime) && booking.status !== 'cancelled' && <span className="text-xs font-bold text-gray-500 dark:text-gray-400 bg-gray-300 dark:bg-gray-600 px-2 py-0.5 rounded-full">Completed</span>}
                      {booking.status === 'cancelled' && <span className="text-xs font-bold text-yellow-800 dark:text-yellow-200 bg-yellow-200 dark:bg-yellow-700 px-2 py-0.5 rounded-full">Cancelled</span>}
                    </div>
                  </div>
                  {!isPast(booking.end_datetime) && booking.status !== 'cancelled' && (
                      <div>
                          <button
                              onClick={() => handleCancel(booking.id)}
                              className="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-600 disabled:bg-red-300"
                              disabled={!!cancelStatus[booking.id] && cancelStatus[booking.id] === 'Cancelling...'}
                              >
                              Cancel
                          </button>
                          {cancelStatus[booking.id] && <p className={`text-xs mt-1 ${cancelStatus[booking.id].startsWith('Error') ? 'text-red-500' : 'text-green-500'}`}>{cancelStatus[booking.id]}</p>}
                      </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyBookings;