import { useState, useEffect } from 'react';
import { orderService } from '../../services/api';
import StatCard from '../../components/StatCard';
import OrderCard from '../../components/OrderCard';
import LoadingSpinner from '../../components/LoadingSpinner';
import { Link } from 'react-router-dom';
import './CustomerDashboard.css';

const CustomerDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const { data } = await orderService.list({ limit: 5 });
        setRecentOrders(data.orders);
        
        // Mock stats calculation for now - ideally comes from an aggregate API
        const allOrders = (await orderService.list()).data.orders;
        const calcStats = {
          total: allOrders.length,
          inTransit: allOrders.filter(o => ['PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY'].includes(o.status)).length,
          delivered: allOrders.filter(o => o.status === 'DELIVERED').length,
          failed: allOrders.filter(o => ['FAILED', 'RTO'].includes(o.status)).length
        };
        setStats(calcStats);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">Welcome Back</h1>
      
      <div className="dashboard-stats">
        <StatCard title="Total Orders" value={stats?.total || 0} icon="📦" color="blue" />
        <StatCard title="In Transit" value={stats?.inTransit || 0} icon="🚚" color="cyan" />
        <StatCard title="Delivered" value={stats?.delivered || 0} icon="✅" color="success" />
        <StatCard title="Failed/RTO" value={stats?.failed || 0} icon="❌" color="error" />
      </div>

      <div className="dashboard-section">
        <div className="section-header">
          <h2>Recent Orders</h2>
          <Link to="/customer/orders" className="btn-secondary view-all-btn">View All</Link>
        </div>
        <div className="recent-orders-grid">
          {recentOrders.length === 0 ? (
            <p className="empty-text">No recent orders found.</p>
          ) : (
            recentOrders.map(order => (
              <OrderCard key={order._id} order={order} />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;
