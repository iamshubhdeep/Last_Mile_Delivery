import { useState, useEffect } from 'react';
import './Toast.css';

// Simple pub-sub for toasts
export const toastManager = {
  listeners: [],
  add(message, type = 'info') {
    this.listeners.forEach(listener => listener({ id: Date.now(), message, type }));
  },
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
};

const Toast = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const unsubscribe = toastManager.subscribe((toast) => {
      setToasts(prev => [...prev, toast]);
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== toast.id));
      }, 3000);
    });
    return unsubscribe;
  }, []);

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <div key={toast.id} className={`toast toast-${toast.type} glass-panel`}>
          {toast.message}
        </div>
      ))}
    </div>
  );
};

export default Toast;
