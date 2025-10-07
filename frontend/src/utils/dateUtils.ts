/**
 * Parses a date string from the backend.
 * Assumes UTC if no timezone is specified. This is a common issue where a server
 * sends a datetime string like '2024-10-26T17:00:00' which is in UTC but lacks
 * the 'Z' suffix. Appending 'Z' ensures the browser parses it as UTC, not local time.
 * @param dateString The date string from the API.
 * @returns A Date object.
 */
export const parseUTCDate = (dateString: string): Date => {
  if (typeof dateString !== 'string') {
    return new Date(NaN); // Invalid date
  }
  // Check if timezone information is already present (e.g., 'Z', '+05:00', '-0800')
  if (!/Z|[+-]\d{2}(:?\d{2})?$/.test(dateString)) {
    return new Date(dateString + 'Z');
  }
  return new Date(dateString);
};

/**
 * Formats a date string from the API into a localized date and time string
 * readable by the user.
 * @param dateString The date string from the API.
 * @returns A formatted string, e.g., "October 26, 2024, 5:00 PM".
 */
export const formatToLocalDateTime = (dateString: string): string => {
  const date = parseUTCDate(dateString);
  if (isNaN(date.getTime())) {
    return "Invalid Date";
  }
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
};

/**
 * Formats a date string from the API into a localized time string.
 * @param dateString The date string from the API.
 * @returns A formatted string, e.g., "5:00 PM".
 */
export const formatToLocalTime = (dateString: string): string => {
  const date = parseUTCDate(dateString);
  if (isNaN(date.getTime())) {
    return "Invalid Time";
  }
  return date.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });
};

/**
 * Formats a UTC time string (HH:mm) into a localized time string.
 * This is useful for displaying daily operating hours that are stored in UTC.
 * @param timeString The time string from the API, e.g., "09:00".
 * @returns A formatted string, e.g., "4:00 AM" (for UTC-5).
 */
export const formatUTCTimeToLocal = (timeString: string): string => {
  if (typeof timeString !== 'string' || !/^\d{2}:\d{2}$/.test(timeString)) {
    return "Invalid Time";
  }
  const [hours, minutes] = timeString.split(':').map(Number);
  const date = new Date();
  date.setUTCHours(hours, minutes, 0, 0);

  if (isNaN(date.getTime())) {
    return "Invalid Time";
  }

  return date.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });
};
