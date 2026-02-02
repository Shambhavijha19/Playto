import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE + '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Auth
export const register = (username, password) => 
  api.post('/auth/register/', { username, password });

export const login = (username, password) => 
  api.post('/auth/login/', { username, password });

export const logout = () => 
  api.post('/auth/logout/');

export const getCurrentUser = () => 
  api.get('/auth/me/');

// Posts
export const getPosts = () => 
  api.get('/posts/');

export const getPost = (id) => 
  api.get(`/posts/${id}/`);

export const createPost = (content) => 
  api.post('/posts/', { content });

export const likePost = (id) => 
  api.post(`/posts/${id}/like/`);

export const unlikePost = (id) => 
  api.post(`/posts/${id}/unlike/`);

// Comments
export const createComment = (postId, content, parentId = null) => 
  api.post('/comments/', { post: postId, content, parent: parentId });

export const likeComment = (id) => 
  api.post(`/comments/${id}/like/`);

export const unlikeComment = (id) => 
  api.post(`/comments/${id}/unlike/`);

// Leaderboard
export const getLeaderboard = () => 
  api.get('/leaderboard/');

export default api;
