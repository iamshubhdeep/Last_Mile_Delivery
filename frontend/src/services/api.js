import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const statusToUi = {
  Created: 'PENDING', Assigned: 'ASSIGNED', 'Picked Up': 'PICKED_UP',
  'In Transit': 'IN_TRANSIT', 'Out for Delivery': 'OUT_FOR_DELIVERY',
  Delivered: 'DELIVERED', Failed: 'FAILED', Rescheduled: 'ASSIGNED'
};

const normalizeOrder = (o, tracking = []) => ({
  ...o,
  _id: o.id,
  createdAt: o.created_at,
  updatedAt: o.updated_at,
  orderType: o.order_type,
  paymentType: o.payment_type,
  status: statusToUi[o.current_status] || o.current_status,
  agentId: o.agent_id,
  chargeableWeight: Number(o.billable_weight),
  charge: Number(o.total_charge),
  baseRate: Number(o.base_charge),
  codSurcharge: Number(o.cod_surcharge),
  zone: `${o.pickup_zone_id} → ${o.drop_zone_id}`,
  pickup: { address: o.pickup_address, pincode: o.pickup_pincode, contactName: '', contactPhone: '' },
  drop: { address: o.drop_address, pincode: o.drop_pincode, contactName: '', contactPhone: '' },
  trackingHistory: tracking.map(t => ({
    status: statusToUi[t.status] || t.status,
    timestamp: t.created_at,
    notes: t.notes,
    changedBy: t.changed_by_id
  }))
});

export const authService = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
  listCustomers: () => api.get('/auth/customers'),
};

export const orderService = {
  calculate: async (data) => {
    const payload = {
      pickup_pincode: data.pickupPincode,
      drop_pincode: data.dropPincode,
      length: data.length,
      breadth: data.breadth,
      height: data.height,
      actual_weight: data.actualWeight,
      order_type: data.orderType,
      payment_type: data.paymentType,
    };
    const res = await api.post('/orders/calculate', payload);
    return { ...res, data: {
      volumetricWeight: Number(res.data.volumetric_weight),
      chargeableWeight: Number(res.data.billable_weight),
      baseCharge: Number(res.data.base_charge),
      codSurcharge: Number(res.data.cod_surcharge),
      totalCharge: Number(res.data.total_charge),
      pickupZoneId: res.data.pickup_zone_id,
      dropZoneId: res.data.drop_zone_id,
    }};
  },
  create: async (formData) => {
    const payload = {
      customer_id: formData.customerId || undefined,
      pickup_address: formData.pickup.address,
      pickup_pincode: formData.pickup.pincode,
      drop_address: formData.drop.address,
      drop_pincode: formData.drop.pincode,
      length: formData.packageDetails.length,
      breadth: formData.packageDetails.breadth,
      height: formData.packageDetails.height,
      actual_weight: formData.packageDetails.actualWeight,
      order_type: formData.orderType,
      payment_type: formData.paymentType,
    };
    const res = await api.post('/orders/', payload);
    return { ...res, data: { order: normalizeOrder(res.data) }};
  },
  list: async (params) => {
    const res = await api.get('/orders/', { params });
    return { ...res, data: { orders: res.data.map(o => normalizeOrder(o)) }};
  },
  getById: async (id) => {
    const res = await api.get(`/orders/${id}`);
    return { ...res, data: normalizeOrder(res.data.order, res.data.tracking) };
  },
  updateStatus: (id, data) => {
    const statusMap = { PICKED_UP: 'Picked Up', IN_TRANSIT: 'In Transit', OUT_FOR_DELIVERY: 'Out for Delivery', DELIVERED: 'Delivered', FAILED: 'Failed' };
    return api.put(`/orders/${id}/status`, { ...data, status: statusMap[data.status] || data.status });
  },
  assign: (id, agentId) => api.put(`/orders/${id}/assign`, null, { params: { agent_id: agentId } }),
  autoAssign: (id) => api.post(`/orders/${id}/auto-assign`),
  reschedule: (id, scheduledDate) => api.post(`/orders/${id}/reschedule`, { scheduled_date: scheduledDate }),
};

export const zoneService = {
  list: async () => {
    const res = await api.get('/zones/');
    return { ...res, data: { zones: res.data.map(z => ({ ...z, _id: z.id, areas: [] })) }};
  },
  create: (data) => api.post('/zones/', { name: data.name, description: data.description }),
  addAreas: (zoneId, data) => api.post(`/zones/${zoneId}/areas`, { pincode: data.pincode, area_name: data.area_name || '' }),
  getAreas: async (zoneId) => {
    const res = await api.get(`/zones/${zoneId}/areas`);
    return { ...res, data: res.data.map(a => ({ ...a, _id: a.id })) };
  },
  detect: (pincode) => api.get(`/zones/detect?pincode=${encodeURIComponent(pincode)}`),
};

export const rateCardService = {
  list: async () => {
    const res = await api.get('/rate-cards/');
    return { ...res, data: { rateCards: res.data.map(r => ({ ...r, _id: r.id, pickupZoneId: r.source_zone_id, dropZoneId: r.dest_zone_id, orderType: r.order_type, baseRate: Number(r.rate_per_kg), minCharge: Number(r.min_charge) })) }};
  },
  create: (data) => api.post('/rate-cards/', {
    source_zone_id: Number(data.pickupZoneId), dest_zone_id: Number(data.dropZoneId),
    order_type: data.orderType, rate_per_kg: Number(data.ratePerKg), min_charge: Number(data.minCharge)
  }),
  listCodSurcharges: () => api.get('/cod-surcharges/'),
  setCodSurcharge: (data) => api.post('/cod-surcharges/', data),
};

export const agentService = {
  list: async () => {
    const res = await api.get('/agents/');
    return { ...res, data: { agents: res.data.map(a => ({
      ...a, _id: a.id, user: { name: a.name || a.user_id, email: a.email || '' },
      isAvailable: a.is_available, currentLocation: a.latitude != null && a.longitude != null ? { coordinates: [a.longitude, a.latitude] } : null
    })) }};
  },
  updateLocation: (data) => api.put('/agents/location', {
    latitude: data.latitude, longitude: data.longitude, current_zone_id: data.currentZoneId
  }),
  toggleAvailability: (data) => api.put('/agents/availability', { is_available: data.isAvailable }),
  getAssignedOrders: async () => {
    const res = await api.get('/agents/orders');
    return { ...res, data: { orders: res.data.map(o => normalizeOrder(o)) } };
  },
};

export default api;
