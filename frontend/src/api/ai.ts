import axiosInstance from './axiosInstance';

interface SendMessagePayload {
  text: string;
}

export const sendMessage = async (payload: SendMessagePayload) => {
  const response = await axiosInstance.post('/api/agent/chat', { message: payload.text });
  return response.data;
};