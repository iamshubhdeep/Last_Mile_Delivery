import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';

// Customer Pages
import CustomerDashboard from './pages/customer/CustomerDashboard';
import CreateOrder from './pages/customer/CreateOrder';
import MyOrders from './pages/customer/MyOrders';
import OrderDetail from './pages/customer/OrderDetail';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminOrders from './pages/admin/AdminOrders';
import ZoneManagement from './pages/admin/ZoneManagement';
import RateCards from './pages/admin/RateCards';
import AgentManagement from './pages/admin/AgentManagement';

// Agent Pages
import AgentDashboard from './pages/agent/AgentDashboard';
import AgentDeliveries from './pages/agent/AgentDeliveries';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) return <div style={{color: 'white', padding: '2rem'}}>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />;

  return children;
};

function App() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={
          user?.role === 'ADMIN' ? <Navigate to="/admin/dashboard" replace /> :
          user?.role === 'AGENT' ? <Navigate to="/agent/dashboard" replace /> :
          <Navigate to="/customer/dashboard" replace />
        } />

        {/* Customer Routes */}
        <Route path="customer/dashboard" element={<ProtectedRoute allowedRoles={['CUSTOMER']}><CustomerDashboard /></ProtectedRoute>} />
        <Route path="customer/create-order" element={<ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN']}><CreateOrder /></ProtectedRoute>} />
        <Route path="customer/orders" element={<ProtectedRoute allowedRoles={['CUSTOMER']}><MyOrders /></ProtectedRoute>} />
        <Route path="order/:id" element={<ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN', 'AGENT']}><OrderDetail /></ProtectedRoute>} />

        {/* Admin Routes */}
        <Route path="admin/dashboard" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>} />
        <Route path="admin/orders" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminOrders /></ProtectedRoute>} />
        <Route path="admin/zones" element={<ProtectedRoute allowedRoles={['ADMIN']}><ZoneManagement /></ProtectedRoute>} />
        <Route path="admin/rates" element={<ProtectedRoute allowedRoles={['ADMIN']}><RateCards /></ProtectedRoute>} />
        <Route path="admin/agents" element={<ProtectedRoute allowedRoles={['ADMIN']}><AgentManagement /></ProtectedRoute>} />

        {/* Agent Routes */}
        <Route path="agent/dashboard" element={<ProtectedRoute allowedRoles={['AGENT']}><AgentDashboard /></ProtectedRoute>} />
        <Route path="agent/deliveries" element={<ProtectedRoute allowedRoles={['AGENT']}><AgentDeliveries /></ProtectedRoute>} />
      </Route>
    </Routes>
  );
}

export default App;

