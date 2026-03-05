import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

export const authAPI = {
    login: (data: any) => {
        const formData = new URLSearchParams();
        formData.append('username', data.email);
        formData.append('password', data.password);
        return api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
    },
    register: (data: any) => api.post('/auth/register', data),
    getMe: () => api.get('/auth/me')
};

export const productAPI = {
    search: (query: string) => api.get(`/products/search?query=${encodeURIComponent(query)}`),
    getDashboard: () => api.get('/products/dashboard'),
    generateSheet: (name: string, models: string[] = [], brand_search: boolean = false, query?: string) =>
        api.post('/products/sheets/generate', { name, models, brand_search, query }),
    getSheet: (id: number) => api.get(`/products/sheets/${id}`),
    getSheets: () => api.get('/products/sheets'),
    exportSheet: (id: number, retailer?: string) => {
        let url = `/products/sheets/${id}/export`;
        if (retailer && retailer !== 'All') {
            url += `?retailer=${encodeURIComponent(retailer)}`;
        }
        return api.get(url, { responseType: 'blob' });
    },
};
