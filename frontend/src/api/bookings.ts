import axiosInstance from './axiosInstance';
import { Booking } from '../types';

export const listUserBookings = async (includePast: boolean = false): Promise<Booking[]> => {
  const response = await axiosInstance.get<Booking[]>('/api/bookings', {
    params: { past: includePast }
  });
  return response.data;
};

export const cancelBooking = async (bookingId: number) => {
  const response = await axiosInstance.delete(`/api/bookings/${bookingId}`);
  return response.data;
};