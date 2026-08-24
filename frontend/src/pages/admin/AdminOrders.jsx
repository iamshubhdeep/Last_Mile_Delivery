import { useState, useEffect } from 'react';
import { orderService } from '../../services/api';
import DataTable from '../../components/DataTable';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

const AdminOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const { data } = await orderService.list();
        setOrders(data.orders);
      } catch (error) {
        console.error('Failed to fetch orders', error);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  const columns = [
    { header: 'ID', accessor: '_id', render: (row) => `#${row._id.slice(-6).toUpperCase()}` },
    { header: 'Type', accessor: 'orderType' },
    { header: 'Pickup', accessor: 'pickup', render: (row) => row.pickup.pincode },
    { header: 'Drop', accessor: 'drop', render: (row) => row.drop.pincode },
    { header: 'Agent', accessor: 'agentId', render: (row) => row.agentId ? 'Assigned' : 'Unassigned' },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
  ];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title mb-0">All Orders</h1>
        <button className="btn-primary" onClick={() => navigate('/customer/create-order')}>+ Create Order</button>
      </div>
      
      <DataTable 
        columns={columns} 
        data={orders} 
        onRowClick={(row) => navigate(`/order/${row._id}`)}
      />
    </div>
  );
};

export default AdminOrders;
