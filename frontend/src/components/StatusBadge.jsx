import './StatusBadge.css';

const statusConfig = {
  PENDING: { color: 'warning', label: 'Pending' },
  ASSIGNED: { color: 'info', label: 'Assigned' },
  PICKED_UP: { color: 'info', label: 'Picked Up' },
  IN_TRANSIT: { color: 'blue', label: 'In Transit' },
  OUT_FOR_DELIVERY: { color: 'cyan', label: 'Out for Delivery' },
  DELIVERED: { color: 'success', label: 'Delivered' },
  FAILED: { color: 'error', label: 'Failed' },
  RTO: { color: 'error', label: 'RTO' },
};

const StatusBadge = ({ status }) => {
  const config = statusConfig[status] || { color: 'info', label: status };
  
  return (
    <span className={`status-badge status-${config.color}`}>
      {config.label}
    </span>
  );
};

export default StatusBadge;
