import { useState, useEffect } from 'react';
import { rateCardService, zoneService } from '../../services/api';
import Modal from '../../components/Modal';
import { toastManager } from '../../components/Toast';
import DataTable from '../../components/DataTable';
import LoadingSpinner from '../../components/LoadingSpinner';

const RateCards = () => {
  const [rates, setRates] = useState([]);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    pickupZoneId: '', dropZoneId: '', orderType: 'B2C', ratePerKg: '', minCharge: ''
  });

  const fetchData = async () => {
    try {
      const [rateRes, zoneRes] = await Promise.all([rateCardService.list(), zoneService.list()]);
      setRates(rateRes.data.rateCards);
      setZones(zoneRes.data.zones);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await rateCardService.create({
        ...formData,
        ratePerKg: Number(formData.ratePerKg),
        minCharge: Number(formData.minCharge)
      });
      toastManager.add('Rate card created successfully', 'success');
      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      toastManager.add('Failed to create rate card', 'error');
    }
  };

  const columns = [
    { header: 'Pickup Zone', accessor: 'pickupZoneId', render: (row) => zones.find(z => z.id === row.pickupZoneId)?.name || row.pickupZoneId },
    { header: 'Drop Zone', accessor: 'dropZoneId', render: (row) => zones.find(z => z.id === row.dropZoneId)?.name || row.dropZoneId },
    { header: 'Type', accessor: 'orderType' },
    { header: 'Rate per Kg (₹)', accessor: 'baseRate' },
    { header: 'Minimum Charge (₹)', accessor: 'extraWeightRate' },
  ];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title mb-0">Rate Cards</h1>
        <button className="btn-primary" onClick={() => setIsModalOpen(true)}>+ Add Rate Card</button>
      </div>

      <DataTable columns={columns} data={rates} />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Rate Card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Pickup Zone</label>
            <select className="form-select" value={formData.pickupZoneId} onChange={(e) => setFormData({...formData, pickupZoneId: e.target.value})}>
              <option value="">Any</option>
              {zones.map(z => <option key={z.id} value={z.id}>{z.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Drop Zone</label>
            <select className="form-select" value={formData.dropZoneId} onChange={(e) => setFormData({...formData, dropZoneId: e.target.value})}>
              <option value="">Any</option>
              {zones.map(z => <option key={z.id} value={z.id}>{z.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Order Type</label>
            <select className="form-select" value={formData.orderType} onChange={(e) => setFormData({...formData, orderType: e.target.value})}>
              <option value="B2B">B2B</option>
              <option value="B2C">B2C</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Rate per Kg (₹)</label>
            <input type="number" className="form-input" value={formData.ratePerKg} onChange={(e) => setFormData({...formData, baseRate: e.target.value})} required />
          </div>
          <div className="form-group">
            <label className="form-label">Extra Weight Rate (₹/kg)</label>
            <input type="number" className="form-input" value={formData.minCharge} onChange={(e) => setFormData({...formData, extraWeightRate: e.target.value})} required />
          </div>
          <button type="submit" className="btn-primary" style={{width: '100%'}}>Save Rate Card</button>
        </form>
      </Modal>
    </div>
  );
};

export default RateCards;
