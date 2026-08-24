import { useState, useEffect } from 'react';
import { agentService } from '../../services/api';
import DataTable from '../../components/DataTable';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

const AgentDeliveries = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const { data } = await agentService.getAssignedOrders();
        const history = data.orders.filter(o => ['DELIVERED', 'FAILED', 'RTO'].includes(o.status));
        setOrders(history);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const columns = [
    { header: 'Order ID', accessor: '_id', render: (row) => `#${row._id.slice(-6).toUpperCase()}` },
    { header: 'Date', accessor: 'updatedAt', render: (row) => new Date(row.updatedAt).toLocaleDateString() },
    { header: 'Pickup', accessor: 'pickup', render: (row) => row.pickup.pincode },
    { header: 'Drop', accessor: 'drop', render: (row) => row.drop.pincode },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
  ];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">Delivery History</h1>
      <DataTable 
        columns={columns} 
        data={orders} 
        onRowClick={(row) => navigate(`/order/${row._id}`)}
      />
    </div>
  );
};

export default AgentDeliveries;
