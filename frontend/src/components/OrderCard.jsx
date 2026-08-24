import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import './OrderCard.css';

const OrderCard = ({ order }) => {
  return (
    <Link to={`/order/${order._id}`} className="order-card glass-panel">
      <div className="order-header">
        <span className="order-id">#{order._id.slice(-6).toUpperCase()}</span>
        <StatusBadge status={order.status} />
      </div>
      
      <div className="order-body">
        <div className="location">
          <span className="dot pickup"></span>
          <p className="address">{order.pickup.address} ({order.pickup.pincode})</p>
        </div>
        <div className="location">
          <span className="dot drop"></span>
          <p className="address">{order.drop.address} ({order.drop.pincode})</p>
        </div>
      </div>

      <div className="order-footer">
        <div className="detail">
          <span className="label">Type</span>
          <span className="value">{order.orderType}</span>
        </div>
        <div className="detail">
          <span className="label">Payment</span>
          <span className="value">{order.paymentType}</span>
        </div>
        <div className="detail">
          <span className="label">Amount</span>
          <span className="value price">₹{order.charge.toFixed(2)}</span>
        </div>
      </div>
    </Link>
  );
};

export default OrderCard;
