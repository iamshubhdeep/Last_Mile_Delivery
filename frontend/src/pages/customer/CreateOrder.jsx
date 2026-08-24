import { useState, useEffect } from 'react';
import { orderService, authService } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { toastManager } from '../../components/Toast';
import { useAuth } from '../../context/AuthContext';
import './CreateOrder.css';

const CreateOrder = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [calculation, setCalculation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState([]); // For admin creating order

  const [formData, setFormData] = useState({
    customerId: user?.role === 'ADMIN' ? '' : user?.id,
    pickup: { address: '', pincode: '', contactName: '', contactPhone: '' },
    drop: { address: '', pincode: '', contactName: '', contactPhone: '' },
    packageDetails: { length: '', breadth: '', height: '', actualWeight: '' },
    orderType: 'B2C',
    paymentType: 'Prepaid',
    declaredValue: ''
  });

  useEffect(() => {
    // If admin, they might need to select a customer (simulated here)
    // Normally you'd fetch users with role 'customer'
    if (user?.role === 'ADMIN') {
      authService.listCustomers().then(({ data }) => {
        setCustomers(data.map(c => ({ _id: c.id, name: c.name })));
      }).catch(() => setCustomers([]));
    }
  }, [user]);

  const handleChange = (e, section) => {
    const { name, value } = e.target;
    if (section) {
      setFormData({
        ...formData,
        [section]: { ...formData[section], [name]: value }
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleNext = async () => {
    if (step === 2) {
      setLoading(true);
      try {
        const payload = {
          pickupPincode: formData.pickup.pincode,
          dropPincode: formData.drop.pincode,
          ...formData.packageDetails,
          orderType: formData.orderType,
          paymentType: formData.paymentType,
          declaredValue: formData.declaredValue || 0
        };
        const { data } = await orderService.calculate(payload);
        setCalculation(data);
        setStep(3);
      } catch (error) {
        toastManager.add(error.response?.data?.message || 'Error calculating charge', 'error');
      } finally {
        setLoading(false);
      }
    } else {
      setStep(step + 1);
    }
  };

  const handleCreate = async () => {
    setLoading(true);
    try {
      const { data } = await orderService.create(formData);
      toastManager.add('Order created successfully!', 'success');
      navigate(`/order/${data.order._id}`);
    } catch (error) {
      toastManager.add(error.response?.data?.message || 'Error creating order', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Create New Order</h1>
      
      <div className="create-order-container glass-panel">
        <div className="step-indicator">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>1. Locations</div>
          <div className="step-line"></div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Package</div>
          <div className="step-line"></div>
          <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Confirm</div>
        </div>

        <div className="step-content">
          {step === 1 && (
            <div className="form-section fade-in">
              {user?.role === 'ADMIN' && (
                <div className="form-group">
                  <label className="form-label">Select Customer</label>
                  <select name="customerId" className="form-select" onChange={(e) => handleChange(e, null)} value={formData.customerId}>
                    <option value="">Select a customer...</option>
                    {customers.map(c => <option key={c._id} value={c._id}>{c.name}</option>)}
                    <option value="test-id">Test Customer</option>
                  </select>
                </div>
              )}
              
              <div className="locations-grid">
                <div className="location-box">
                  <h3>Pickup Details</h3>
                  <div className="form-group">
                    <label className="form-label">Address</label>
                    <textarea name="address" className="form-input" onChange={(e) => handleChange(e, 'pickup')} value={formData.pickup.address} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Pincode</label>
                    <input type="text" name="pincode" className="form-input" onChange={(e) => handleChange(e, 'pickup')} value={formData.pickup.pincode} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Contact Name</label>
                    <input type="text" name="contactName" className="form-input" onChange={(e) => handleChange(e, 'pickup')} value={formData.pickup.contactName} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Contact Phone</label>
                    <input type="tel" name="contactPhone" className="form-input" onChange={(e) => handleChange(e, 'pickup')} value={formData.pickup.contactPhone} />
                  </div>
                </div>

                <div className="location-box">
                  <h3>Drop Details</h3>
                  <div className="form-group">
                    <label className="form-label">Address</label>
                    <textarea name="address" className="form-input" onChange={(e) => handleChange(e, 'drop')} value={formData.drop.address} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Pincode</label>
                    <input type="text" name="pincode" className="form-input" onChange={(e) => handleChange(e, 'drop')} value={formData.drop.pincode} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Contact Name</label>
                    <input type="text" name="contactName" className="form-input" onChange={(e) => handleChange(e, 'drop')} value={formData.drop.contactName} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Contact Phone</label>
                    <input type="tel" name="contactPhone" className="form-input" onChange={(e) => handleChange(e, 'drop')} value={formData.drop.contactPhone} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="form-section fade-in">
              <h3>Package Details</h3>
              <div className="dimensions-grid">
                <div className="form-group">
                  <label className="form-label">Length (cm)</label>
                  <input type="number" name="length" className="form-input" onChange={(e) => handleChange(e, 'packageDetails')} value={formData.packageDetails.length} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Breadth (cm)</label>
                  <input type="number" name="breadth" className="form-input" onChange={(e) => handleChange(e, 'packageDetails')} value={formData.packageDetails.breadth} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Height (cm)</label>
                  <input type="number" name="height" className="form-input" onChange={(e) => handleChange(e, 'packageDetails')} value={formData.packageDetails.height} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Actual Weight (kg)</label>
                  <input type="number" step="0.1" name="actualWeight" className="form-input" onChange={(e) => handleChange(e, 'packageDetails')} value={formData.packageDetails.actualWeight} required />
                </div>
              </div>

              <div className="options-grid">
                <div className="form-group">
                  <label className="form-label">Order Type</label>
                  <select name="orderType" className="form-select" onChange={(e) => handleChange(e, null)} value={formData.orderType}>
                    <option value="B2B">B2B</option>
                    <option value="B2C">B2C</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Payment Type</label>
                  <select name="paymentType" className="form-select" onChange={(e) => handleChange(e, null)} value={formData.paymentType}>
                    <option value="Prepaid">Prepaid</option>
                    <option value="COD">COD</option>
                  </select>
                </div>
                {formData.paymentType === 'COD' && (
                  <div className="form-group">
                    <label className="form-label">Declared Value (₹)</label>
                    <input type="number" name="declaredValue" className="form-input" onChange={(e) => handleChange(e, null)} value={formData.declaredValue} />
                  </div>
                )}
              </div>
            </div>
          )}

          {step === 3 && calculation && (
            <div className="form-section fade-in text-center">
              <h3>Order Summary</h3>
              <div className="summary-card">
                <div className="summary-row">
                  <span>Chargeable Weight:</span>
                  <span>{calculation.chargeableWeight} kg</span>
                </div>
                <div className="summary-row">
                  <span>Zone:</span>
                  <span>{calculation.zone}</span>
                </div>
                <div className="summary-row">
                  <span>Base Rate:</span>
                  <span>₹{calculation.baseRate}</span>
                </div>
                <div className="summary-row">
                  <span>COD Surcharge:</span>
                  <span>₹{calculation.codSurcharge}</span>
                </div>
                <div className="summary-total">
                  <span>Total Charge:</span>
                  <span className="price">₹{calculation.totalCharge}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="step-actions">
          {step > 1 && (
            <button className="btn-secondary" onClick={() => setStep(step - 1)} disabled={loading}>
              Back
            </button>
          )}
          {step < 3 ? (
            <button className="btn-primary" onClick={handleNext} disabled={loading}>
              {loading ? 'Calculating...' : 'Next'}
            </button>
          ) : (
            <button className="btn-primary" onClick={handleCreate} disabled={loading}>
              {loading ? 'Creating...' : 'Create Order'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateOrder;
