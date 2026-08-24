import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Sidebar.css';

const Sidebar = () => {
  const { user } = useAuth();
  const location = useLocation();

  const getLinks = () => {
    switch (user?.role) {
      case 'admin':
        return [
          { path: '/admin/dashboard', icon: '📊', label: 'Dashboard' },
          { path: '/admin/orders', icon: '📦', label: 'All Orders' },
          { path: '/customer/create-order', icon: '➕', label: 'Create Order' },
          { path: '/admin/zones', icon: '🗺️', label: 'Zones' },
          { path: '/admin/rates', icon: '💰', label: 'Rate Cards' },
          { path: '/admin/agents', icon: '🛵', label: 'Agents' },
        ];
      case 'agent':
        return [
          { path: '/agent/dashboard', icon: '🛵', label: 'Dashboard' },
          { path: '/agent/deliveries', icon: '📜', label: 'My Deliveries' },
        ];
      default:
        return [
          { path: '/customer/dashboard', icon: '📊', label: 'Dashboard' },
          { path: '/customer/create-order', icon: '➕', label: 'Create Order' },
          { path: '/customer/orders', icon: '📦', label: 'My Orders' },
        ];
    }
  };

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-brand">
        🚀 <span className="brand-text">LastMile</span>
      </div>
      <nav className="sidebar-nav">
        {getLinks().map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className={`nav-item ${location.pathname.startsWith(link.path) ? 'active' : ''}`}
          >
            <span className="nav-icon">{link.icon}</span>
            <span className="nav-label">{link.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
