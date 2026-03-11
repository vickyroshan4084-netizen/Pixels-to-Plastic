/**
 * API Configuration & Constants
 * Centralized API endpoint configuration for frontend
 * This file is imported by all frontend pages
 */

const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api',
  TIMEOUT: 10000, // 10 seconds
  
  // Endpoints
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    ADMIN_REGISTER: '/auth/admin-register/',
    PROFILE: '/auth/profile/',
    REFRESH: '/auth/refresh/',
    VERIFY: '/auth/verify/',
  },
  
  PRODUCTS: {
    LIST: '/products/products/',
    DETAIL: (id) => `/products/products/${id}/`,
    CREATE: '/products/products/',
    UPDATE: (id) => `/products/products/${id}/`,
    DELETE: (id) => `/products/products/${id}/`,
  },
  
  CATEGORIES: {
    LIST: '/products/categories/',
    DETAIL: (id) => `/products/categories/${id}/`,
    CREATE: '/products/categories/',
    UPDATE: (id) => `/products/categories/${id}/`,
    DELETE: (id) => `/products/categories/${id}/`,
  },
  
  MAIN_CATEGORIES: {
    LIST: '/products/main-categories/',
    DETAIL: (id) => `/products/main-categories/${id}/`,
  },
  
  DISCOUNTS: {
    LIST: '/products/discounts/',
    DETAIL: (id) => `/products/discounts/${id}/`,
    CREATE: '/products/discounts/',
    UPDATE: (id) => `/products/discounts/${id}/`,
    DELETE: (id) => `/products/discounts/${id}/`,
  },
  
  CART: {
    LIST: '/cart/',
    ADD_ITEM: '/cart/items/',
    UPDATE_ITEM: (id) => `/cart/items/${id}/`,
    REMOVE_ITEM: (id) => `/cart/items/${id}/`,
  },
  
  ORDERS: {
    LIST: '/orders/',
    CREATE: '/orders/checkout/',
    DETAIL: (id) => `/orders/${id}/`,
    VERIFY_PAYMENT: '/orders/payment/verify/',
  },
};

/**
 * Enhanced API Client
 * Handles authentication, error handling, and request formatting
 */
class APIClient {
  constructor(config = {}) {
    this.baseURL = config.baseURL || API_CONFIG.BASE_URL;
    this.timeout = config.timeout || API_CONFIG.TIMEOUT;
    this.listeners = {
      request: [],
      response: [],
      error: [],
      unauthorized: []
    };
  }
  
  /**
   * Get authorization header with access token
   */
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }
  
  /**
   * Make API request with built-in error handling
   */
  async request(endpoint, options = {}) {
    const url = this.baseURL + endpoint;
    const timeoutId = setTimeout(() => {
      throw new Error(`Request timeout after ${this.timeout}ms`);
    }, this.timeout);
    
    try {
      // Notify listeners of request
      this.emit('request', { url, options });
      
      const response = await fetch(url, {
        headers: this.getAuthHeaders(),
        ...options
      });
      
      clearTimeout(timeoutId);
      
      // Handle 401 Unauthorized - token expired
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        this.emit('unauthorized', { url, status: response.status });
        
        // Redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = 'admin-login.html';
        }
        throw new Error('Unauthorized. Please login again.');
      }
      
      // Parse response
      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
      
      // Notify listeners of response
      this.emit('response', { url, status: response.status, data });
      
      if (!response.ok) {
        const error = new APIError(
          data.detail || data.message || 'API Error',
          response.status,
          data,
          url
        );
        this.emit('error', error);
        throw error;
      }
      
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof APIError) {
        throw error;
      }
      
      const apiError = new APIError(
        error.message || 'Network error',
        0,
        { original_error: error },
        url
      );
      this.emit('error', apiError);
      throw apiError;
    }
  }
  
  /**
   * GET request
   */
  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }
  
  /**
   * POST request
   */
  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  /**
   * PATCH request
   */
  patch(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }
  
  /**
   * PUT request
   */
  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  /**
   * DELETE request
   */
  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
  
  /**
   * Listen to API events
   */
  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  }
  
  /**
   * Stop listening to events
   */
  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }
  
  /**
   * Emit event to listeners
   */
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (e) {
          console.error(`Error in ${event} listener:`, e);
        }
      });
    }
  }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, status, data = {}, url = '') {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
    this.url = url;
  }
}

/**
 * Global API client instance
 */
const api = new APIClient();

/**
 * Helper: Check if user is authenticated
 */
function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

/**
 * Helper: Get current user info
 */
function getCurrentUser() {
  const userJson = localStorage.getItem('user');
  return userJson ? JSON.parse(userJson) : null;
}

/**
 * Helper: Check if user is admin
 */
function isAdmin() {
  const user = getCurrentUser();
  return user && user.is_staff === true;
}

/**
 * Helper: Logout
 */
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  window.location.href = 'admin-login.html';
}

/**
 * Helper: Format error message for display
 */
function formatErrorMessage(error) {
  if (error instanceof APIError) {
    // Handle different error types
    if (error.data && typeof error.data === 'object') {
      // Extract field errors from Django REST Framework
      const errors = [];
      Object.entries(error.data).forEach(([field, messages]) => {
        if (Array.isArray(messages)) {
          errors.push(...messages);
        } else {
          errors.push(`${field}: ${messages}`);
        }
      });
      if (errors.length > 0) return errors[0];
    }
    
    // Check for HTML response (can happen on 404/500 if server misconfigured)
    if (typeof error.data === 'string' && error.data.includes('<!DOCTYPE html>')) {
      return `Server Error (${error.status}): The URL ${error.url} could not be reached.`;
    }
    
    return error.message;
  }
  return error.message || 'An unknown error occurred';
}

/**
 * Export for use in other files
 */
// Make globally available
window.API_CONFIG = API_CONFIG;
window.APIClient = APIClient;
window.APIError = APIError;
window.api = api;
window.isAuthenticated = isAuthenticated;
window.getCurrentUser = getCurrentUser;
window.isAdmin = isAdmin;
window.logout = logout;
window.formatErrorMessage = formatErrorMessage;
