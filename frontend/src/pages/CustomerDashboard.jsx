import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import useLanguage from '../hooks/useLanguage';
import DashboardLayout from '../components/DashboardLayout';
import { Sun, Moon, Bell, X, CreditCard, Clock, CheckCircle, Download, ChevronRight, LogOut } from 'lucide-react';

const CustomerDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loanAmount, setLoanAmount] = useState('');
  const [loanPurpose, setLoanPurpose] = useState('');
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [isSubmittingLoan, setIsSubmittingLoan] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showLoanForm, setShowLoanForm] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const view = params.get('view');
    if (view === 'loans') {
        setCurrentPage('loans');
    } else {
        setCurrentPage('dashboard');
    }
  }, [location.search]);

  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) document.documentElement.classList.add('dark');
    fetchDashboardData();
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode);
    document.documentElement.classList.toggle('dark');
  };

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      const [statsRes, notifRes] = await Promise.all([
        axios.get('/api/dashboard/stats', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('/api/dashboard/notifications', { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setData(statsRes.data);
      setNotifications(notifRes.data);
    } catch (err) {
      console.error('Dashboard Error:', err);
      if (err.response?.status === 401) navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const submitLoanApplication = async (e) => {
    e.preventDefault();
    setIsSubmittingLoan(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/dashboard/loan/apply', {
        amount: parseInt(loanAmount),
        purpose: loanPurpose,
        monthly_income: parseInt(monthlyIncome)
      }, { headers: { Authorization: `Bearer ${token}` } });
      alert('Loan Application Submitted Successfully!');
      setLoanAmount('');
      setLoanPurpose('');
      setMonthlyIncome('');
      setShowLoanForm(false);
      fetchDashboardData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit application');
    } finally {
      setIsSubmittingLoan(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );

  if (!data) return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-500 mb-4">Failed to load dashboard data.</p>
        <button onClick={fetchDashboardData} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Retry</button>
      </div>
    </div>
  );

  const { customer, verification, loan_application, loan_applications, documents, unread_notifications } = data;
  const isPending = !verification || verification?.status === 'Pending';

  return (
    <DashboardLayout>
      {/* Top Navigation Bar */}
      <main className="p-8">
        {currentPage === 'dashboard' && (
          <div className="space-y-6">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                    Welcome back, {customer?.full_name || 'User'}!
                </h1>
                <p className="text-slate-500 dark:text-slate-400">Here's what's happening with your account.</p>
            </div>

            {isPending ? (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-2xl p-6 flex items-center gap-6">
                <div className="p-4 bg-yellow-100 dark:bg-yellow-900/40 rounded-full"><Clock size={32} className="text-yellow-600" /></div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold mb-2 text-slate-900 dark:text-white">Verification In Progress</h2>
                  <p className="mb-4 text-slate-600 dark:text-slate-300">Your account is currently under review. This usually takes 24-48 hours.</p>
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
                    <span className="flex items-center gap-1"><CheckCircle size={16} /> Account Created</span>
                    <span className="w-8 h-px bg-yellow-300"></span>
                    <span className="flex items-center gap-1"><CheckCircle size={16} /> Docs Submitted</span>
                  </div>
                </div>
              </div>
            ) : (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-2xl p-6 flex items-center gap-6">
                    <div className="p-4 bg-green-100 dark:bg-green-900/40 rounded-full"><CheckCircle size={32} className="text-green-600" /></div>
                    <div className="flex-1">
                        <h2 className="text-xl font-bold mb-2 text-slate-900 dark:text-white">Account Verified</h2>
                        <p className="mb-4 text-slate-600 dark:text-slate-300">Your KYC verification is complete. You can now apply for loans and access all features.</p>
                        <button onClick={() => setCurrentPage('loans')} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                            Apply for Loan
                        </button>
                    </div>
                </div>
            )}
            
            {/* Quick Stats / Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
                    <h3 className="text-slate-500 text-sm font-medium mb-2">Active Loans</h3>
                    <p className="text-3xl font-bold text-slate-900 dark:text-white">{loan_applications?.filter(l => l.status === 'Approved').length || 0}</p>
                </div>
                <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
                    <h3 className="text-slate-500 text-sm font-medium mb-2">Pending Applications</h3>
                    <p className="text-3xl font-bold text-slate-900 dark:text-white">{loan_applications?.filter(l => l.status === 'Pending').length || 0}</p>
                </div>
                <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
                    <h3 className="text-slate-500 text-sm font-medium mb-2">Total Borrowed</h3>
                    <p className="text-3xl font-bold text-slate-900 dark:text-white">PKR {loan_applications?.filter(l => l.status === 'Approved').reduce((acc, curr) => acc + curr.amount, 0).toLocaleString() || 0}</p>
                </div>
            </div>
          </div>
        )}

        {currentPage === 'loans' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Loan Management</h2>
                <button onClick={() => setShowLoanForm(true)} disabled={loan_applications?.some(l => l.status === 'Pending')} className="px-4 py-2 bg-indigo-600 text-white rounded-lg disabled:opacity-50">
                  {loan_applications?.some(l => l.status === 'Pending') ? 'Pending Application Exists' : 'Apply for New Loan'}
                </button>
              </div>
              {loan_applications && loan_applications.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="border-b">
                      <tr>
                        <th className="pb-3">Amount</th>
                        <th className="pb-3">Purpose</th>
                        <th className="pb-3">Status</th>
                        <th className="pb-3">Applied On</th>
                        <th className="pb-3">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {loan_applications.map((loan) => (
                        <tr key={loan.id}>
                          <td className="py-2">PKR {loan.amount?.toLocaleString()}</td>
                          <td className="py-2">{loan.purpose}</td>
                          <td className="py-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${loan.status === 'Approved' ? 'bg-green-100 text-green-800' : loan.status === 'Rejected' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>{loan.status}</span>
                          </td>
                          <td className="py-2">{new Date(loan.created_at).toLocaleDateString()}</td>
                          <td className="py-2">
                            {(loan.status === 'Approved' || loan.status === 'Rejected') && (
                              <button onClick={() => window.open(`/api/dashboard/loan/download-pdf/${loan.id}`, '_blank')} className="text-sm text-indigo-600 flex items-center gap-1">
                                <Download size={14} /> PDF
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="mb-4">No loan applications yet</p>
                  <button onClick={() => setCurrentPage('dashboard')} className="text-indigo-600 hover:underline">Go to Dashboard</button>
                </div>
              )}
            </div>
          </div>
        )}

        {showLoanForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-md p-6 relative">
              <button onClick={() => setShowLoanForm(false)} className="absolute top-4 right-4 text-gray-400"><X size={20} /></button>
              <h3 className="text-xl font-bold mb-4">Apply for Loan</h3>
              <form onSubmit={submitLoanApplication} className="space-y-4">
                <div>
                  <label className="block mb-2">Loan Amount (PKR)</label>
                  <input type="number" value={loanAmount} onChange={(e) => setLoanAmount(e.target.value)} required min="10000" className="w-full p-2 border rounded" placeholder="Enter amount" />
                </div>
                <div>
                  <label className="block mb-2">Purpose</label>
                  <select value={loanPurpose} onChange={(e) => setLoanPurpose(e.target.value)} required className="w-full p-2 border rounded">
                    <option value="">Select purpose</option>
                    <option>Business</option>
                    <option>Education</option>
                    <option>Home Renovation</option>
                    <option>Medical</option>
                    <option>Personal</option>
                    <option>Other</option>
                  </select>
                </div>
                <div>
                  <label className="block mb-2">Monthly Income (PKR)</label>
                  <input type="number" value={monthlyIncome} onChange={(e) => setMonthlyIncome(e.target.value)} required min="10000" className="w-full p-2 border rounded" placeholder="Enter monthly income" />
                </div>
                <div className="flex gap-3 pt-4">
                  <button type="button" onClick={() => setShowLoanForm(false)} className="flex-1 p-2 border rounded">Cancel</button>
                  <button type="submit" disabled={isSubmittingLoan} className="flex-1 p-2 bg-indigo-600 text-white rounded disabled:opacity-50">
                    {isSubmittingLoan ? 'Submitting...' : 'Submit Application'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </DashboardLayout>
  );
};

export default CustomerDashboard;
