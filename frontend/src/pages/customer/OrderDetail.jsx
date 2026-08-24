import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useParams } from 'react-router-dom';
import { orderService } from '../../services/api';
import TrackingTimeline from '../../components/TrackingTimeline';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import './OrderDetail.css';

const OrderDetail = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rescheduleDate, setRescheduleDate] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const { data } = await orderService.getById(id);
        setOrder(data);
      } catch (error) {
        console.error('Error fetching order', error);
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!order) return <div className="page-container">Order not found</div>;

  const handleReschedule = async () => {
    if (!rescheduleDate) return;
    try {
      await orderService.reschedule(id, new Date(rescheduleDate).toISOString());
      const { data } = await orderService.getById(id);
      setOrder(data);
      setRescheduleDate('');
    } catch (error) {
      console.error('Reschedule failed', error);
    }
  };

  return (
    <div className="page-container">
      <div className="order-detail-header">
        <h1 className="page-title mb-0">Order #{order._id.slice(-6).toUpperCase()}</h1>
        <StatusBadge status={order.status} />
      </div>

      {user?.role === 'CUSTOMER' && order.status === 'FAILED' && (
        <div className="glass-panel detail-section">
          <h3>Reschedule Delivery</h3>
          <input type="datetime-local" className="form-input" value={rescheduleDate} onChange={(e) => setRescheduleDate(e.target.value)} />
          <button className="btn-primary" onClick={handleReschedule} disabled={!rescheduleDate}>Reschedule</button>
        </div>
      )}

      <div className="detail-grid">
        <div className="detail-left">
          <div className="glass-panel detail-section">
            <h3>Locations</h3>
            <div className="location-timeline">
              <div className="loc-item pickup">
                <span className="dot pickup-dot"></span>
                <div className="loc-content">
                  <h4>Pickup</h4>
                  <p>{order.pickup.address}</p>
                  <span className="loc-meta">PIN: {order.pickup.pincode} | Contact: {order.pickup.contactName} ({order.pickup.contactPhone})</span>
                </div>
              </div>
              <div className="loc-item drop">
                <span className="dot drop-dot"></span>
                <div className="loc-content">
                  <h4>Drop</h4>
                  <p>{order.drop.address}</p>
                  <span className="loc-meta">PIN: {order.drop.pincode} | Contact: {order.drop.contactName} ({order.drop.contactPhone})</span>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel detail-section">
            <h3>Package & Payment</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Type</span>
                <span className="info-value">{order.orderType}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Payment</span>
                <span className="info-value">{order.paymentType}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Chargeable Wt.</span>
                <span className="info-value">{order.chargeableWeight} kg</span>
              </div>
              <div className="info-item">
                <span className="info-label">Total Charge</span>
                <span className="info-value highlight">₹{order.charge.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="detail-right">
          <div className="glass-panel detail-section tracking-section">
            <h3>Tracking Journey</h3>
            <TrackingTimeline trackingHistory={order.trackingHistory} currentStatus={order.status} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;
