import { useState, useEffect } from 'react';
import { zoneService } from '../../services/api';
import Modal from '../../components/Modal';
import { toastManager } from '../../components/Toast';
import DataTable from '../../components/DataTable';
import LoadingSpinner from '../../components/LoadingSpinner';

const ZoneManagement = () => {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', areas: '' });

  const fetchZones = async () => {
    try {
      const { data } = await zoneService.list();
      const enriched = await Promise.all(data.zones.map(async (zone) => {
        try {
          const areasRes = await zoneService.getAreas(zone.id);
          return { ...zone, areas: areasRes.data.map(a => a.pincode) };
        } catch {
          return zone;
        }
      }));
      setZones(enriched);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchZones();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: formData.name,
        description: formData.description,
        areas: formData.areas.split(',').map(a => a.trim()).filter(a => a)
      };
      const { data: zone } = await zoneService.create(payload);
      for (const pincode of payload.areas) {
        await zoneService.addAreas(zone.id, { pincode });
      }
      toastManager.add('Zone created successfully', 'success');
      setIsModalOpen(false);
      setFormData({ name: '', description: '', areas: '' });
      fetchZones();
    } catch (error) {
      toastManager.add('Failed to create zone', 'error');
    }
  };

  const columns = [
    { header: 'Zone Name', accessor: 'name' },
    { header: 'Description', accessor: 'description' },
    { header: 'Areas (Pincodes)', accessor: 'areas', render: (row) => (row.areas || []).join(', ') },
    { header: 'Status', accessor: 'isActive', render: (row) => 'Active' }
  ];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title mb-0">Zone Management</h1>
        <button className="btn-primary" onClick={() => setIsModalOpen(true)}>+ Add Zone</button>
      </div>

      <DataTable columns={columns} data={zones} />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Zone">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Zone Name</label>
            <input type="text" className="form-input" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input type="text" className="form-input" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
          </div>
          <div className="form-group">
            <label className="form-label">Areas (comma separated pincodes)</label>
            <textarea className="form-input" value={formData.areas} onChange={(e) => setFormData({...formData, areas: e.target.value})} placeholder="e.g. 110001, 110002" required rows={3}></textarea>
          </div>
          <button type="submit" className="btn-primary" style={{width: '100%'}}>Save Zone</button>
        </form>
      </Modal>
    </div>
  );
};

export default ZoneManagement;
