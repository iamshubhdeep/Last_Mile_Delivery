import { useState, useEffect } from 'react';
import { agentService } from '../../services/api';
import DataTable from '../../components/DataTable';
import LoadingSpinner from '../../components/LoadingSpinner';

const AgentManagement = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const { data } = await agentService.list();
        setAgents(data.agents);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, []);

  const columns = [
    { header: 'Name', accessor: 'user', render: (row) => row.user.name },
    { header: 'Email', accessor: 'user', render: (row) => row.user.email },
    { header: 'Status', accessor: 'isAvailable', render: (row) => (
      <span style={{ color: row.isAvailable ? 'var(--status-success)' : 'var(--text-secondary)'}}>
        {row.isAvailable ? '● Available' : '○ Offline'}
      </span>
    )},
    { header: 'Current Location', accessor: 'currentLocation', render: (row) => 
      row.currentLocation?.coordinates?.length ? `${row.currentLocation.coordinates[1].toFixed(4)}, ${row.currentLocation.coordinates[0].toFixed(4)}` : 'Unknown'
    },
  ];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">Agent Management</h1>
      <DataTable columns={columns} data={agents} />
    </div>
  );
};

export default AgentManagement;
