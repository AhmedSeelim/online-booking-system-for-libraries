import axiosInstance from './axiosInstance';
import { Book, BookCreate, BookUpdate } from '../types';

interface PurchaseResult {
    transaction_id: number;
    book_id: number;
    book_title: string;
    quantity: number;
    amount: number;
    currency: string;
    status: string;
}

// Corresponds to GET /api/books
export const listBooks = async (): Promise<Book[]> => {
    const response = await axiosInstance.get<Book[]>('/api/books');
    return response.data;
};

// Corresponds to GET /api/books/{book_id}
export const getBook = async (bookId: string): Promise<Book> => {
    const response = await axiosInstance.get<Book>(`/api/books/${bookId}`);
    return response.data;
};

// Corresponds to POST /api/books/{book_id}/purchase
export const purchaseBook = async (bookId: number, quantity: number): Promise<PurchaseResult> => {
    const response = await axiosInstance.post<PurchaseResult>(`/api/books/${bookId}/purchase`, { quantity });
    return response.data;
};

// Admin Functions
export const createBook = async (data: BookCreate): Promise<Book> => {
  const response = await axiosInstance.post<Book>('/api/books', data);
  return response.data;
}

export const updateBook = async (id: number, data: BookUpdate): Promise<Book> => {
  const response = await axiosInstance.put<Book>(`/api/books/${id}`, data);
  return response.data;
}

export const deleteBook = async (id: number): Promise<void> => {
  await axiosInstance.delete(`/api/books/${id}`);
}