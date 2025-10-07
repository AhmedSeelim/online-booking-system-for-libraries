// auth.ts
import axiosInstance from './axiosInstance';
import { User } from '../types';

export const signup = async (payload: { name: string; email: string; password: string }) => {
  // POST /api/auth/signup expects { name, email, password }
  const resp = await axiosInstance.post('/api/auth/signup', {
    name: payload.name,
    email: payload.email,
    password: payload.password
  });
  return resp.data; // created user (no password)
};

export const login = async (credentials: { email: string; password: string }) => {
  // POST /api/auth/login expects { email, password }
  const resp = await axiosInstance.post<{ access_token: string; token_type: string; expires_in_minutes: number }>(
    '/api/auth/login',
    {
      email: credentials.email,
      password: credentials.password,
    }
  );
  return resp.data; // { access_token, token_type, expires_in_minutes }
};

export const me = async (): Promise<User> => {
  const resp = await axiosInstance.get<User>('/api/auth/me');
  return resp.data;
};

export const addBalance = async (amount: number): Promise<User> => {
  const resp = await axiosInstance.post<User>('/api/auth/add-balance', { amount });
  return resp.data;
};