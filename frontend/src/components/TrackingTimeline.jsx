import './TrackingTimeline.css';

const ALL_STATUSES = [
  'PENDING', 'ASSIGNED', 'PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED'
];

const TrackingTimeline = ({ trackingHistory, currentStatus }) => {
  // If failed or RTO, we append it to the normal flow where it failed
  const isFailed = currentStatus === 'FAILED' || currentStatus === 'RTO';
  
  const getStatusIndex = (status) => ALL_STATUSES.indexOf(status);
  const currentIndex = isFailed ? trackingHistory.length - 1 : getStatusIndex(currentStatus);

  return (
    <div className="tracking-timeline">
      {ALL_STATUSES.map((status, index) => {
        const historyItem = trackingHistory?.find(h => h.status === status);
        const isCompleted = index <= currentIndex && historyItem;
        const isActive = index === currentIndex && !isFailed;
        
        return (
          <div key={status} className={`timeline-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}>
            <div className="timeline-marker"></div>
            <div className="timeline-content">
              <h4 className="timeline-status">{status.replace(/_/g, ' ')}</h4>
              {historyItem && (
                <p className="timeline-time">
                  {new Date(historyItem.timestamp).toLocaleString()}
                </p>
              )}
              {historyItem?.notes && (
                <p className="timeline-notes">{historyItem.notes}</p>
              )}
            </div>
          </div>
        );
      })}
      
      {isFailed && (
        <div className="timeline-item failed active">
          <div className="timeline-marker"></div>
          <div className="timeline-content">
            <h4 className="timeline-status">{currentStatus}</h4>
            <p className="timeline-notes">Order could not be delivered.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrackingTimeline;
