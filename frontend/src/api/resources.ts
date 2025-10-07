import axiosInstance from './axiosInstance';
import { Resource, ResourceCreate, ResourceUpdate } from '../types';

interface ListResourcesParams {
  min_capacity?: number;
  page?: number;
  limit?: number;
}

export const listResources = async (params: ListResourcesParams = {}): Promise<Resource[]> => {
  const response = await axiosInstance.get<Resource[]>('/api/resources', { params });
  return response.data;
};

export const getResource = async (resourceId: string): Promise<Resource> => {
  const response = await axiosInstance.get<Resource>(`/api/resources/${resourceId}`);
  return response.data;
};

interface AvailabilitySlot {
  start: string;
  end: string;
  available: boolean;
}

interface AvailabilityResponse {
  date?: string;
  slots?: AvailabilitySlot[];
  available?: boolean;
  start?: string;
  end?: string;
}

export const checkResourceAvailability = async (resourceId: number, params: { start?: string; end?: string; date?: string }): Promise<AvailabilityResponse> => {
  const response = await axiosInstance.get<AvailabilityResponse>(`/api/resources/${resourceId}/availability`, {
    params,
  });
  return response.data;
};

interface CreateBookingParams {
  resource_id: number;
  start_datetime: string;
  end_datetime: string;
  notes?: string;
}

export const createBooking = async (params: CreateBookingParams) => {
    const response = await axiosInstance.post('/api/bookings', params);
    return response.data;
};

// Admin Functions
export const createResource = async (data: ResourceCreate): Promise<Resource> => {
  const response = await axiosInstance.post<Resource>('/api/resources', data);
  return response.data;
}

export const updateResource = async (id: number, data: ResourceUpdate): Promise<Resource> => {
  const response = await axiosInstance.put<Resource>(`/api/resources/${id}`, data);
  return response.data;
}

export const deleteResource = async (id: number): Promise<void> => {
  await axiosInstance.delete(`/api/resources/${id}`);
}