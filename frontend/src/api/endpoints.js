import api from './axios';

export const authAPI = {
  login: async (username, password) => {
    // Content-Type: application/x-www-form-urlencoded for OAuth2 Request Form compatibility
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const response = await api.post('/api/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },
  register: async (username, email, password, organizationName) => {
    const response = await api.post('/api/auth/register', {
      username,
      email,
      password,
      organization_name: organizationName
    });
    return response.data;
  },
  me: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  }
};

export const uploadsAPI = {
  uploadSap: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/uploads/sap', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  uploadUtility: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/uploads/utility', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  syncTravel: async () => {
    const response = await api.post('/api/uploads/travel/sync');
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/api/uploads/history');
    return response.data;
  },
  getDataSources: async () => {
    const response = await api.get('/api/uploads/datasources');
    return response.data;
  }
};

export const recordsAPI = {
  list: async (filters = {}) => {
    const response = await api.get('/api/records', { params: filters });
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/api/records/${id}`);
    return response.data;
  }
};

export const reviewsAPI = {
  approve: async (id, commentText = '') => {
    const response = await api.post(`/api/reviews/${id}/approve`, { comment_text: commentText });
    return response.data;
  },
  reject: async (id, commentText) => {
    const response = await api.post(`/api/reviews/${id}/reject`, { comment_text: commentText });
    return response.data;
  },
  addComment: async (id, commentText) => {
    const response = await api.post(`/api/reviews/${id}/comment`, { comment_text: commentText });
    return response.data;
  }
};

export const dashboardAPI = {
  summary: async () => {
    const response = await api.get('/api/dashboard/summary');
    return response.data;
  }
};

export const auditsAPI = {
  getSystemTimeline: async () => {
    const response = await api.get('/api/audit');
    return response.data;
  },
  getTargetTimeline: async (targetId) => {
    const response = await api.get(`/api/audit/${targetId}`);
    return response.data;
  }
};
