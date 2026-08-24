import { useState, useEffect } from 'react';
import { agentService, orderService } from '../../services/api';
import OrderCard from '../../components/OrderCard';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toastManager } from '../../components/Toast';
import './AgentDashboard.css';

const AgentDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAvailable, setIsAvailable] = useState(false);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const { data } = await agentService.getAssignedOrders();
        // Assuming the backend returns the agent's assigned orders
        // Filter out completed ones for the dashboard
        const active = data.orders.filter(o => !['DELIVERED', 'FAILED', 'RTO'].includes(o.status));
        setOrders(active);
        
        // Mocking agent profile fetch for availability toggle
        // In a real app, you'd fetch the agent profile here
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const handleToggle = async () => {
    try {
      await agentService.toggleAvailability({ isAvailable: !isAvailable });
      setIsAvailable(!isAvailable);
      toastManager.add(`You are now ${!isAvailable ? 'available' : 'offline'}`, 'success');
    } catch (error) {
      toastManager.add('Failed to update status', 'error');
    }
  };

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      await orderService.updateStatus(orderId, { status: newStatus, notes: 'Updated by agent' });
      toastManager.add('Status updated', 'success');
      // Refetch orders to update view
      const { data } = await agentService.getAssignedOrders();
      setOrders(data.orders.filter(o => !['DELIVERED', 'FAILED', 'RTO'].includes(o.status)));
    } catch (error) {
      toastManager.add('Failed to update status', 'error');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div className="agent-header">
        <h1 className="page-title mb-0">Agent Dashboard</h1>
        <div className="availability-toggle">
          <span>Status: {isAvailable ? 'Online' : 'Offline'}</span>
          <label className="switch">
            <input type="checkbox" checked={isAvailable} onChange={handleToggle} />
            <span className="slider round"></span>
          </label>
        </div>
      </div>

      <div className="assigned-orders">
        <h2 style={{marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '1.25rem'}}>Current Tasks</h2>
        {orders.length === 0 ? (
          <div className="glass-panel text-center p-4">
            <p className="text-secondary">No active tasks assigned to you right now.</p>
          </div>
        ) : (
          <div className="agent-orders-grid">
            {orders.map(order => (
              <div key={order._id} className="agent-order-wrapper">
                <OrderCard order={order} />
                <div className="action-buttons glass-panel">
                  {order.status === 'ASSIGNED' && (
                    <button className="btn-primary" onClick={() => handleUpdateStatus(order._id, 'PICKED_UP')}>Mark Picked Up</button>
                  )}
                  {order.status === 'PICKED_UP' && (
                    <button className="btn-primary" onClick={() => handleUpdateStatus(order._id, 'IN_TRANSIT')}>Start Transit</button>
                  )}
                  {order.status === 'IN_TRANSIT' && (
                    <button className="btn-primary" onClick={() => handleUpdateStatus(order._id, 'OUT_FOR_DELIVERY')}>Out for Delivery</button>
                  )}
                  {order.status === 'OUT_FOR_DELIVERY' && (
                    <div style={{display: 'flex', gap: '0.5rem', width: '100%'}}>
                      <button className="btn-primary" style={{flex: 1, background: 'var(--status-success)'}} onClick={() => handleUpdateStatus(order._id, 'DELIVERED')}>Delivered</button>
                      <button className="btn-primary" style={{flex: 1, background: 'var(--status-error)'}} onClick={() => handleUpdateStatus(order._id, 'FAILED')}>Failed</button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentDashboard;
