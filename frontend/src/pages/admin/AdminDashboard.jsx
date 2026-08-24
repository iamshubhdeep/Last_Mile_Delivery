import { useState, useEffect } from 'react';
import StatCard from '../../components/StatCard';
import { orderService, agentService } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ordersRes, agentsRes] = await Promise.all([
          orderService.list(),
          agentService.list()
        ]);
        
        const orders = ordersRes.data.orders;
        const agents = agentsRes.data.agents;

        setStats({
          totalOrders: orders.length,
          pendingOrders: orders.filter(o => o.status === 'PENDING').length,
          revenue: orders.reduce((sum, o) => sum + (o.charge || 0), 0),
          activeAgents: agents.filter(a => a.isAvailable).length,
          totalAgents: agents.length
        });
      } catch (error) {
        console.error('Failed to load admin stats', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">Admin Overview</h1>
      
      <div className="dashboard-stats">
        <StatCard title="Total Revenue" value={`₹${stats?.revenue.toFixed(0)}`} icon="💰" color="success" />
        <StatCard title="Total Orders" value={stats?.totalOrders} icon="📦" color="blue" />
        <StatCard title="Pending Assignment" value={stats?.pendingOrders} icon="⏳" color="warning" />
        <StatCard title="Active Agents" value={`${stats?.activeAgents}/${stats?.totalAgents}`} icon="🛵" color="cyan" />
      </div>

      <div className="admin-grid">
        <div className="glass-panel p-4">
          <h3>Recent System Activity</h3>
          <p className="text-secondary mt-2">Activity logs would go here in a full implementation.</p>
        </div>
        <div className="glass-panel p-4">
          <h3>Agent Availability</h3>
          <p className="text-secondary mt-2">Agent map or list would go here.</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
