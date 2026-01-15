import { defineStore } from 'pinia';
import axios from '../axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    isAdmin: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      try {
        const response = await axios.post('/token', formData);
        this.token = response.data.access_token;
        localStorage.setItem('token', this.token);
        await this.fetchUser();
      } catch (error) {
        console.error('Login failed', error);
        throw error;
      }
    },
    async register(username, password) {
      try {
        await axios.post('/users/', { username, password });
      } catch (error) {
        console.error('Registration failed', error);
        throw error;
      }
    },
    async fetchUser() {
      try {
        const response = await axios.get('/users/me/');
        this.user = response.data;
        this.isAdmin = response.data.is_admin;
      } catch (error) {
        console.error('Fetch user failed', error);
        this.logout();
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      this.isAdmin = false;
      localStorage.removeItem('token');
    },
  },
});
