/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

export interface User {
  id: number;
  name: string;
  email: string;
  balance: number;
  role: 'user' | 'admin';
}

export interface Book {
  id: number;
  title: string;
  author: string;
  category: string;
  description: string;
  price: number;
  stock_count: number;
}

export type BookCreate = Omit<Book, 'id'>;
export type BookUpdate = Partial<BookCreate>;

export interface Resource {
  id: number;
  name: string;
  type: 'room' | 'seat' | 'equipment';
  capacity: number;
  hourly_rate: number;
  features: string; // JSON string
  open_hour: string; // "HH:MM"
  close_hour: string; // "HH:MM"
}

export type ResourceCreate = Omit<Resource, 'id'>;
export type ResourceUpdate = Partial<ResourceCreate>;

export interface Booking {
  id: number;
  user_id: number;
  resource_id: number;
  start_datetime: string; // ISO 8601
  end_datetime: string; // ISO 8601
  notes?: string;
  status: 'confirmed' | 'cancelled' | 'completed';
  total_cost: number;
}

export interface AIParsedDetails {
  intent?: string;
  book_title?: string;
  book_author?: string;
  resource_name?: string;
  resource_type?: 'room' | 'seat' | 'equipment';
  date?: string; // "YYYY-MM-DD"
  time?: string; // "HH:MM"
  start_datetime?: string; // ISO 8601
  end_datetime?: string; // ISO 8601
  resource_id?: number;
  [key: string]: any; // Allow other properties
}