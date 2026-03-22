/**
 * api-client.js — Pixels to Plastic
 * ─────────────────────────────────────────────────────────────────────────────
 * REPLACE your existing api-client.js with this.
 *
 * After deploying to Render, update RENDER_BACKEND_URL below with your
 * actual URL from: Render Dashboard → p2p-backend → Settings → URL
 * ─────────────────────────────────────────────────────────────────────────────
 */

// ── UPDATE THIS after Render deploy ──────────────────────────────────────────
const RENDER_BACKEND_URL = 'https://p2p-qm1i.onrender.com';
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE = (() => {
  const h = window.location.hostname;
  if (h === 'localhost' || h === '127.0.0.1') return 'http://127.0.0.1:8000/api';
  return RENDER_BACKEND_URL + '/api';
})();

const API_CONFIG = {
  BASE_URL: API_BASE,
  AUTH: {
    LOGIN:           `${API_BASE}/auth/login/`,
    REGISTER:        `${API_BASE}/auth/register/`,
    ADMIN_REGISTER:  `${API_BASE}/auth/admin-register/`,
    PROFILE:         `${API_BASE}/auth/profile/`,
    REFRESH:         `${API_BASE}/auth/refresh/`,
    USERS:           `${API_BASE}/auth/users/`,
  },
  PRODUCTS: {
    LIST:             `${API_BASE}/products/products/`,
    DETAIL:   (id) => `${API_BASE}/products/products/${id}/`,
    DELETE:   (id) => `${API_BASE}/products/products/${id}/`,
  },
  MAIN_CATEGORIES: {
    LIST:             `${API_BASE}/products/main-categories/`,
    DETAIL:   (id) => `${API_BASE}/products/main-categories/${id}/`,
    DELETE:   (id) => `${API_BASE}/products/main-categories/${id}/`,
  },
  CATEGORIES: {
    LIST:             `${API_BASE}/products/categories/`,
    DETAIL:   (id) => `${API_BASE}/products/categories/${id}/`,
    DELETE:   (id) => `${API_BASE}/products/categories/${id}/`,
  },
  DISCOUNTS: {
    LIST:             `${API_BASE}/products/discounts/`,
    DETAIL:   (id) => `${API_BASE}/products/discounts/${id}/`,
    DELETE:   (id) => `${API_BASE}/products/discounts/${id}/`,
  },
  CART: {
    LIST:              `${API_BASE}/cart/`,
    ADD_ITEM:          `${API_BASE}/cart/items/`,
    UPDATE_ITEM: (id) =>`${API_BASE}/cart/items/${id}/`,
    REMOVE_ITEM: (id) =>`${API_BASE}/cart/items/${id}/`,
  },
  ORDERS: {
    LIST:              `${API_BASE}/orders/`,
    CREATE:            `${API_BASE}/orders/checkout/`,
    DETAIL:    (id) => `${API_BASE}/orders/${id}/`,
    STATUS:    (id) => `${API_BASE}/orders/${id}/status/`,
    VERIFY:            `${API_BASE}/orders/payment/verify/`,
    EXPORT_EXCEL:      `${API_BASE}/orders/export/excel/`,
  },
  DASHBOARD: {
    STATS: `${API_BASE}/orders/dashboard/stats/`,
  },
};

// ── Auth helpers ──────────────────────────────────────────────────────────────
function getToken()        { return localStorage.getItem('access_token') || ''; }
function getCurrentUser()  {
  try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch { return null; }
}
function isAuthenticated() { return !!getToken() && !!getCurrentUser(); }
function isAdmin()         { const u = getCurrentUser(); return !!u && u.is_staff === true; }
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  window.location.href = 'admin-login.html';
}

// ── Error class ───────────────────────────────────────────────────────────────
class APIError extends Error {
  constructor(message, status, data) {
    super(message); this.name = 'APIError'; this.status = status; this.data = data;
  }
}

// ── Core fetch ────────────────────────────────────────────────────────────────
async function _request(method, url, data = null, options = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token   = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config = { method, headers, signal: AbortSignal.timeout(35000), ...options };
  if (data && method !== 'GET') config.body = JSON.stringify(data);

  let response;
  try {
    response = await fetch(url, config);
  } catch (err) {
    if (err.name === 'TimeoutError' || err.name === 'AbortError') {
      throw new APIError('⏳ Server is waking up (free hosting takes ~30 sec). Please try again.', 0, null);
    }
    throw new APIError('🔌 Cannot connect to server. Check your internet connection.', 0, null);
  }

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = 'admin-login.html';
    return;
  }

  let responseData;
  try {
    const ct = response.headers.get('content-type') || '';
    responseData = ct.includes('application/json') ? await response.json() : await response.text();
  } catch { responseData = null; }

  if (!response.ok) {
    let msg = `Error ${response.status}`;
    if (responseData && typeof responseData === 'object') {
      msg = responseData.detail || responseData.non_field_errors?.[0]
            || Object.values(responseData).flat()[0] || msg;
    }
    throw new APIError(String(msg), response.status, responseData);
  }
  return responseData;
}

// ── Public API ────────────────────────────────────────────────────────────────
const api = {
  get:    (url, opts)       => _request('GET',    url, null, opts),
  post:   (url, data, opts) => _request('POST',   url, data, opts),
  put:    (url, data, opts) => _request('PUT',    url, data, opts),
  patch:  (url, data, opts) => _request('PATCH',  url, data, opts),
  delete: (url, opts)       => _request('DELETE', url, null, opts),
  upload: async (url, formData) => {
    const headers = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const r = await fetch(url, { method: 'POST', headers, body: formData });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new APIError(d.detail || 'Upload failed', r.status, d);
    return d;
  },
};

function formatErrorMessage(error) {
  if (!error) return 'An unknown error occurred.';
  if (typeof error === 'string') return error;
  if (error.status === 0) return error.message;
  if (error.data && typeof error.data === 'object') {
    const first = Object.values(error.data).flat()[0];
    if (first) return String(first);
  }
  return error.message || 'Something went wrong.';
}

// ── Wake-up ping on page load (keeps Render free tier alive) ─────────────────
(async () => {
  try {
    await fetch(`${API_BASE}/products/products/?page_size=1`, { signal: AbortSignal.timeout(35000) });
  } catch { /* silent */ }
})();
