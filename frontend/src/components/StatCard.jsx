import './StatCard.css';

const StatCard = ({ title, value, icon, color = 'blue' }) => {
  return (
    <div className={`stat-card glass-panel stat-${color}`}>
      <div className="stat-icon-wrapper">
        <span className="stat-icon">{icon}</span>
      </div>
      <div className="stat-info">
        <h3 className="stat-title">{title}</h3>
        <p className="stat-value">{value}</p>
      </div>
    </div>
  );
};

export default StatCard;
