import { useState, useEffect } from 'react';
import { orderService } from '../../services/api';
import DataTable from '../../components/DataTable';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

const MyOrders = () => {
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
    { header: 'Order ID', accessor: '_id', render: (row) => `#${row._id.slice(-6).toUpperCase()}` },
    { header: 'Date', accessor: 'createdAt', render: (row) => new Date(row.createdAt).toLocaleDateString() },
    { header: 'Pickup', accessor: 'pickup', render: (row) => row.pickup.pincode },
    { header: 'Drop', accessor: 'drop', render: (row) => row.drop.pincode },
    { header: 'Amount', accessor: 'charge', render: (row) => `₹${row.charge.toFixed(2)}` },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
  ];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">My Orders</h1>
      <DataTable 
        columns={columns} 
        data={orders} 
        onRowClick={(row) => navigate(`/order/${row._id}`)}
      />
    </div>
  );
};

export default MyOrders;
