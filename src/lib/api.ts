// src/lib/api.ts
import axios, { type AxiosInstance } from 'axios';
import { get } from 'svelte/store';
import { page } from "$app/stores";

const apiClient: AxiosInstance = axios.create({
  baseURL: "https://yokyvsy7jw7o4e5t4prgpd5yt40cqubc.lambda-url.us-east-1.on.aws/",
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchPagedData = async <T>(
    endpoint: string,
    pagedRequest: { page: number; size: number; sort_by?: string[]; sort_direction?: string }
): Promise<T> => {
  try {
    const { data } = get(page);
    const token = (data?.session as any)?.accessToken;

    // Construct the query parameters for pagination
    const params = new URLSearchParams({
      page: pagedRequest.page.toString(),
      size: pagedRequest.size.toString(),
    });

    if (pagedRequest.sort_by) {
      params.append('sort_by', pagedRequest.sort_by.join(','));
    }
    if (pagedRequest.sort_direction) {
      params.append('sort_direction', pagedRequest.sort_direction);
    }

    // Set the Authorization header with the token
    const response = await apiClient.get<T>(`${endpoint}?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};

export const fetchData = async <T>(endpoint: string, options: object = {}): Promise<any> => {
  try {
    // const { data } = get(page);
    // const token = (data?.session as any)?.accessToken;

    // Set the Authorization header with the token
    const response = await apiClient.get<T>(endpoint, {
      // headers: {
      //   Authorization: `Bearer ${token}`
      // },
      ...options
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};

export const fetchDataWithRedirect = async (endpoint: string, options: object = {}): Promise<any> => {
  try {
    const { data } = get(page);
    const token = (data?.session as any)?.accessToken;

    // Set the Authorization header with the token
    const response = await axios.get(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`
      },
      ...options,
      maxRedirects: 0, // Ensure axios doesn't automatically follow redirects
      validateStatus: (status) => {
        return (status >= 200 && status < 300) || status === 302;
      }
    });

    console.log('Response Status:', response.status);
    console.log('Response Headers:', response.headers);
    console.log('Response Headers:', response.headers.location);

    if (response.status === 302 && response.headers.location) {
      console.log('Redirecting to:', response.headers.location);
      window.location.href = response.headers.location;
    } else {
      return response.data; // Return the response data if no redirect is needed
    }
  } catch (error) {
    console.error('Error handling request with redirect:', error);
    throw error;
  }
};

export const postData = async <T>(endpoint: string, data: object, options: object = {}): Promise<T> => {
  try {
    // const { data: pageData } = get(page);
    // const token = (pageData?.session as any)?.accessToken;

    // Set the Authorization header with the token
    const response = await apiClient.post<T>(endpoint, data, {
      // headers: {
      //   Authorization: `Bearer ${token}`
      // },
      ...options
    });

    return response.data;
  } catch (error) {
    console.error('Error making POST request:', error);
    throw error;
  }
};

export const deleteData = async <T>(endpoint: string, options: object = {}): Promise<T> => {
  try {
    const { data: pageData } = get(page);
    const token = (pageData?.session as any)?.accessToken;

    // Set the Authorization header with the token
    const response = await apiClient.delete<T>(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`
      },
      ...options
    });

    return response.data;
  } catch (error) {
    console.error('Error making DELETE request:', error);
    throw error;
  }
};