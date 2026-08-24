import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header glass-panel">
      <div className="header-search">
        {/* Search could go here */}
      </div>
      <div className="header-user">
        <div className="user-info">
          <span className="user-name">{user?.name}</span>
          <span className="user-role">{user?.role}</span>
        </div>
        <button onClick={handleLogout} className="btn-secondary logout-btn">
          Logout 🚪
        </button>
      </div>
    </header>
  );
};

export default Header;
