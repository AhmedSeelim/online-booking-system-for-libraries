import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getResource, checkResourceAvailability, createBooking } from '../api/resources';
import { Resource } from '../types';
import { useAIAction } from '../context/AIActionContext';
import { formatToLocalTime, parseUTCDate, formatUTCTimeToLocal } from '../utils/dateUtils';
import { useAuth } from '../context/AuthContext';
import { me } from '../api/auth';

interface TimeSlot {
  start: string;
  end: string;
}

// Helper to get today's date in YYYY-MM-DD format for the user's local timezone
const getLocalTodayString = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

const FeatureDisplay: React.FC<{ features: string }> = ({ features }) => {
  try {
    const parsedFeatures = JSON.parse(features);
    const entries = Object.entries(parsedFeatures);

    if (entries.length === 0) {
      return <p className="text-gray-500 italic">No special features listed.</p>;
    }
    
    // Helper to format keys like "power_outlets" to "Power Outlets"
    const formatKey = (key: string) => {
      return key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
    };

    return (
      <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
        {entries.map(([key, value]) => (
          <li key={key}>
            <strong>{formatKey(key)}:</strong>
            {value === true ? ' Available' : ` ${value}`}
          </li>
        ))}
      </ul>
    );
  } catch (error) {
    // Fallback for plain string features
    if (features) {
      return <p className="text-gray-600 dark:text-gray-400">{features}</p>;
    }
    return <p className="text-gray-500 italic">No special features listed.</p>;
  }
};


const ResourceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const localToday = getLocalTodayString();
  const [selectedDate, setSelectedDate] = useState(localToday);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [notes, setNotes] = useState('');

  const [bookingStatus, setBookingStatus] = useState('');
  const { suggestion, setSuggestion } = useAIAction();
  const { setCurrentUser } = useAuth();

  useEffect(() => {
    if (id && suggestion?.resource_id?.toString() === id) {
        if (suggestion.start_datetime) {
          setSelectedDate(new Date(suggestion.start_datetime).toISOString().split('T')[0]);
        }
        setSuggestion(null); // Consume suggestion
    }
  }, [suggestion, id, setSuggestion]);


  useEffect(() => {
    if (!id) return;
    const fetchResource = async () => {
      setLoading(true);
      try {
        const data = await getResource(id);
        setResource(data);
      } catch (err) {
        setError('Failed to fetch resource details.');
      } finally {
        setLoading(false);
      }
    };
    fetchResource();
  }, [id]);

  useEffect(() => {
    if (!id || !selectedDate || !resource) return;
    
    const fetchSlots = async () => {
      setSlotsLoading(true);
      setAvailableSlots([]);
      setSelectedSlot(null);
      setBookingStatus('');
      try {
        const data = await checkResourceAvailability(parseInt(id, 10), { date: selectedDate });
        if (data.slots) {
          const now = new Date();
          const isToday = selectedDate === localToday;
          
          const [openH, openM] = resource.open_hour.split(':').map(Number);
          const [closeH, closeM] = resource.close_hour.split(':').map(Number);
          const effectiveCloseH = closeH === 0 ? 24 : closeH;


          // Filter for available slots within operating hours
          let availableHalfHourSlots = data.slots
            .filter(slot => {
                if (!slot.available) return false;

                const slotStart = parseUTCDate(slot.start);
                const slotEnd = parseUTCDate(slot.end);

                const slotStartHour = slotStart.getUTCHours();
                const slotStartMin = slotStart.getUTCMinutes();
                const slotEndHour = slotEnd.getUTCHours();
                const slotEndMin = slotEnd.getUTCMinutes();

                const startsOnOrAfterOpen = slotStartHour > openH || (slotStartHour === openH && slotStartMin >= openM);
                const endsOnOrBeforeClose = slotEndHour < effectiveCloseH || (slotEndHour === effectiveCloseH && slotEndMin <= closeM);
                
                return startsOnOrAfterOpen && endsOnOrBeforeClose;
            })
            .map(({ start, end }) => ({ start, end }));

          // If it's today, filter out past slots
          if (isToday) {
            availableHalfHourSlots = availableHalfHourSlots.filter(slot => parseUTCDate(slot.start) > now);
          }

          // Sort slots chronologically to ensure correct merging
          const sortedSlots = availableHalfHourSlots.sort((a, b) => 
            parseUTCDate(a.start).getTime() - parseUTCDate(b.start).getTime()
          );

          // Merge consecutive half-hour slots into one-hour slots
          const hourlySlots: TimeSlot[] = [];
          let i = 0;
          while (i < sortedSlots.length - 1) {
            const currentSlot = sortedSlots[i];
            const nextSlot = sortedSlots[i + 1];

            const currentStartDate = parseUTCDate(currentSlot.start);
            const currentEndDate = parseUTCDate(currentSlot.end);
            const nextStartDate = parseUTCDate(nextSlot.start);

            // Check if the current slot starts on the hour and is followed immediately by the next half-hour slot
            if (currentStartDate.getMinutes() === 0 && currentEndDate.getTime() === nextStartDate.getTime()) {
              hourlySlots.push({
                start: currentSlot.start,
                end: nextSlot.end,
              });
              i += 2; // Skip both merged slots
            } else {
              i++; // Move to the next slot
            }
          }
          setAvailableSlots(hourlySlots);
        }
      } catch (err) {
        console.error("Failed to fetch slots", err);
        setAvailableSlots([]);
      } finally {
        setSlotsLoading(false);
      }
    };
    fetchSlots();
  }, [id, selectedDate, resource, localToday]);

  const handleCreateBooking = async () => {
    if (!resource || !selectedSlot) return;
    setBookingStatus('Creating booking...');
    try {
      const result = await createBooking({
        resource_id: resource.id,
        start_datetime: selectedSlot.start,
        end_datetime: selectedSlot.end,
        notes: notes.trim() ? notes.trim() : undefined,
      });
      setBookingStatus(`Success! Booking created with ID: ${result.id}. You can see the details in "My Bookings".`);
      
      // Refetch user to update balance immediately
      try {
        const updatedUser = await me();
        setCurrentUser(updatedUser);
      } catch (userError) {
        console.error("Failed to refetch user after booking:", userError);
      }

      setSelectedSlot(null);
      setNotes(''); // Clear notes after booking
      // Refetch slots to show updated availability
      const data = await checkResourceAvailability(parseInt(id!, 10), { date: selectedDate });
        if (data.slots && resource) {
          const now = new Date();
          const isToday = selectedDate === localToday;

          const [openH, openM] = resource.open_hour.split(':').map(Number);
          const [closeH, closeM] = resource.close_hour.split(':').map(Number);
          const effectiveCloseH = closeH === 0 ? 24 : closeH;


          // Filter for available slots within operating hours
          let availableHalfHourSlots = data.slots
            .filter(slot => {
                if (!slot.available) return false;

                const slotStart = parseUTCDate(slot.start);
                const slotEnd = parseUTCDate(slot.end);

                const slotStartHour = slotStart.getUTCHours();
                const slotStartMin = slotStart.getUTCMinutes();
                const slotEndHour = slotEnd.getUTCHours();
                const slotEndMin = slotEnd.getUTCMinutes();

                const startsOnOrAfterOpen = slotStartHour > openH || (slotStartHour === openH && slotStartMin >= openM);
                const endsOnOrBeforeClose = slotEndHour < effectiveCloseH || (slotEndHour === effectiveCloseH && slotEndMin <= closeM);
                
                return startsOnOrAfterOpen && endsOnOrBeforeClose;
            })
            .map(({ start, end }) => ({ start, end }));

          if (isToday) {
            availableHalfHourSlots = availableHalfHourSlots.filter(slot => parseUTCDate(slot.start) > now);
          }

          // Sort slots chronologically to ensure correct merging
          const sortedSlots = availableHalfHourSlots.sort((a, b) => 
            parseUTCDate(a.start).getTime() - parseUTCDate(b.start).getTime()
          );

          // Merge consecutive half-hour slots into one-hour slots
          const hourlySlots: TimeSlot[] = [];
          let i = 0;
          while (i < sortedSlots.length - 1) {
            const currentSlot = sortedSlots[i];
            const nextSlot = sortedSlots[i + 1];

            const currentStartDate = parseUTCDate(currentSlot.start);
            const currentEndDate = parseUTCDate(currentSlot.end);
            const nextStartDate = parseUTCDate(nextSlot.start);

            // Check if the current slot starts on the hour and is followed immediately by the next half-hour slot
            if (currentStartDate.getMinutes() === 0 && currentEndDate.getTime() === nextStartDate.getTime()) {
              hourlySlots.push({
                start: currentSlot.start,
                end: nextSlot.end,
              });
              i += 2; // Skip both merged slots
            } else {
              i++; // Move to the next slot
            }
          }
          setAvailableSlots(hourlySlots);
        }
    } catch (err: any) {
      setBookingStatus(`Error: ${err.response?.data?.detail || 'Failed to create booking.'}`);
    }
  };


  if (loading) return <div>Loading resource details...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!resource) return <div>Resource not found.</div>;

  return (
    <div className="container mx-auto">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold">{resource.name}</h1>
        <p className="text-gray-600 dark:text-gray-400 capitalize mb-4">{resource.type}</p>
        <p>Capacity: {resource.capacity} people</p>
        <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-2 mb-6">${resource.hourly_rate.toFixed(2)} / hour</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <h3 className="text-lg font-semibold mb-3">Book this Resource</h3>
                <div className="mb-4">
                    <label htmlFor="booking-date" className="block text-sm font-medium mb-1">Select Date</label>
                    <input 
                      type="date" 
                      id="booking-date"
                      value={selectedDate}
                      min={localToday}
                      onChange={e => setSelectedDate(e.target.value)}
                      className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                    />
                </div>
                
                <h4 className="text-md font-semibold mb-2">Available Slots</h4>
                {slotsLoading ? (
                  <p>Loading slots...</p>
                ) : availableSlots.length > 0 ? (
                  <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-60 overflow-y-auto pr-2">
                    {availableSlots.map((slot, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedSlot(slot)}
                        className={`p-2 border rounded text-xs transition-colors ${
                          selectedSlot?.start === slot.start
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-600 hover:bg-indigo-100 dark:hover:bg-indigo-500'
                        }`}
                      >
                        {formatToLocalTime(slot.start)}
                         - 
                        {formatToLocalTime(slot.end)}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No available slots for this date.</p>
                )}
                
                <div className="mt-4">
                  <label htmlFor="booking-notes" className="block text-sm font-medium mb-1">Notes (Optional)</label>
                  <textarea
                    id="booking-notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={2}
                    className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                    placeholder="E.g., for a team meeting"
                  />
                </div>

                <button 
                  onClick={handleCreateBooking} 
                  disabled={!selectedSlot || slotsLoading}
                  className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700 mt-4 disabled:bg-indigo-300 dark:disabled:bg-indigo-800 disabled:cursor-not-allowed"
                >
                  Confirm Booking
                </button>
                {bookingStatus && (
                    <div className={`text-sm mt-2 ${bookingStatus.startsWith('Error') ? 'text-red-500' : 'text-green-500'}`}>
                        {bookingStatus}
                        {bookingStatus.startsWith('Success') && 
                            <Link to="/my-bookings" className="ml-2 text-indigo-600 hover:underline">Go to My Bookings</Link>
                        }
                    </div>
                )}
            </div>

            <div className="p-4">
                 <h3 className="text-lg font-semibold mb-3">Details</h3>
                 <h4 className="text-md font-semibold mb-2">Operating Hours</h4>
                 <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {formatUTCTimeToLocal(resource.open_hour)} - {formatUTCTimeToLocal(resource.close_hour)}
                 </p>
                 <h4 className="text-md font-semibold mb-2">Features</h4>
                 <FeatureDisplay features={resource.features} />
            </div>
        </div>
      </div>
    </div>
  );
};

export default ResourceDetail;