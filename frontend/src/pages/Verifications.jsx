import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import axios from 'axios';
import { CheckCircle, XCircle, Clock, Search, AlertTriangle, ShieldAlert, Trash2 } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const Verifications = () => {
    const [verifications, setVerifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState('active');
    const [searchTerm, setSearchTerm] = useState('');
    const [searchParams] = useSearchParams();
    const highlightId = searchParams.get('highlight');
    const navigate = useNavigate();
    const [selectedVerification, setSelectedVerification] = useState(null);
    const [showReviewModal, setShowReviewModal] = useState(false);
    const [decision, setDecision] = useState('');
    const [remarks, setRemarks] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchVerifications();
    }, []);

    const fetchVerifications = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('/api/admin/all-verifications', { 
                headers: { Authorization: `Bearer ${token}` } 
            });

            setVerifications(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const filteredData = verifications.filter(v => {
        if (viewMode === 'active') {
            if (v.status === 'Rejected') return false;
        } else {
            if (v.status !== 'Rejected') return false;
        }

        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            return (
                v.full_name.toLowerCase().includes(term) ||
                v.cnic.toLowerCase().includes(term) ||
                v.serial_no.toLowerCase().includes(term)
            );
        }
        return true;
    });

    const pendingVerifications = filteredData.filter(v => v.status === 'Pending');
    const verifiedVerifications = filteredData.filter(v => v.status === 'Verified');

    const handleRowClick = (item) => {
        navigate(`/admin/loan-management?highlight=${item.id}`);
    };

    const handleReviewClick = (e, item) => {
        e.stopPropagation(); // Prevent row click
        setSelectedVerification(item);
        setShowReviewModal(true);
        setRemarks('');
        setDecision('');
    };

    const handleSubmitDecision = async () => {
        if (!decision) {
            alert('Please select Approve or Reject');
            return;
        }
        
        setSubmitting(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`/api/admin/verify/${selectedVerification.customer_id}`, {
                status: decision === 'approve' ? 'Verified' : 'Rejected',
                remarks: remarks || (decision === 'approve' ? 'Approved by admin' : 'Rejected by admin'),
                risk_score: selectedVerification.risk_score,
                trust_score: selectedVerification.trust_score
            }, { 
                headers: { Authorization: `Bearer ${token}` } 
            });
            
            setShowReviewModal(false);
            setSelectedVerification(null);
            fetchVerifications(); // Refresh list
        } catch (err) {
            console.error(err);
            alert('Failed to submit decision');
        } finally {
            setSubmitting(false);
        }
    };

    const TableRow = ({ item, isHighlighted }) => {
        const riskColor = item.risk_score > 70 ? 'text-red-500' : item.risk_score > 30 ? 'text-yellow-500' : 'text-green-500';
        
        return (
            <tr
                onClick={() => handleRowClick(item)}
                className={`hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer
                    ${item.fraud_flagged ? 'bg-red-50/50 dark:bg-red-900/10 border-l-4 border-red-500' : ''}
                    ${isHighlighted ? 'ring-2 ring-blue-500 animate-pulse' : ''}
                `}
            >
                <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 font-mono">{item.serial_no}</td>
                <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                        <span className="font-medium text-slate-900 dark:text-white text-sm">{item.full_name}</span>
                        {item.fraud_flagged && (
                            <ShieldAlert size={14} className="text-red-600 dark:text-red-400" title="Fraud Alert" />
                        )}
                    </div>
                </td>
                <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 font-mono">{item.cnic}</td>
                <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400">{new Date(item.date).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border
                        ${item.status === 'Verified' ? 'bg-green-50 text-green-700 border-green-100 dark:bg-green-900/20 dark:text-green-400' :
                            'bg-yellow-50 text-yellow-700 border-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400'}`}>
                        {item.status}
                    </span>
                </td>
                <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                            <div
                                className={`h-1.5 rounded-full ${item.risk_score > 70 ? 'bg-red-500' : item.risk_score > 30 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                style={{ width: `${item.risk_score}%` }}
                            ></div>
                        </div>
                        <span className={`text-xs font-bold ${riskColor}`}>{item.risk_score}</span>
                    </div>
                    {item.fraud_alerts && item.fraud_alerts.length > 0 && (
                        <div className="text-[10px] text-red-600 dark:text-red-400 mt-1 flex items-center gap-1">
                            <AlertTriangle size={10} />
                            {item.fraud_alerts[0]}
                        </div>
                    )}
                </td>
            </tr>
        );
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center min-h-screen">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Verification Queue</h1>

                    <div className="bg-slate-100 dark:bg-slate-800 p-1 rounded-lg flex">
                        <button
                            onClick={() => setViewMode('active')}
                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${viewMode === 'active'
                                    ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                                }`}
                        >
                            Active Queue
                        </button>
                        <button
                            onClick={() => setViewMode('history')}
                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${viewMode === 'history'
                                    ? 'bg-white dark:bg-slate-700 text-red-600 dark:text-red-400 shadow-sm'
                                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                                }`}
                        >
                            Past Rejections
                        </button>
                    </div>
                </div>

                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                    <input
                        type="text"
                        placeholder="Search by Name, CNIC, or Serial No..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {viewMode === 'active' ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Pending Table */}
                        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                            <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-2">
                                <Clock className="text-yellow-600 dark:text-yellow-400" size={18} />
                                <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                                    Pending Verifications
                                </h2>
                                <span className="text-sm text-slate-500 dark:text-slate-400">
                                    ({pendingVerifications.length})
                                </span>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 text-xs uppercase">
                                        <tr>
                                            <th className="px-4 py-2 font-semibold">SN</th>
                                            <th className="px-4 py-2 font-semibold">Name</th>
                                            <th className="px-4 py-2 font-semibold">CNIC</th>
                                            <th className="px-4 py-2 font-semibold">Risk</th>
                                            <th className="px-4 py-2 font-semibold">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                                        {pendingVerifications.length > 0 ? (
                                            pendingVerifications.map((item) => (
                                                <tr
                                                    key={item.id}
                                                    onClick={() => handleRowClick(item)}
                                                    className={`hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer
                                                        ${item.fraud_flagged ? 'bg-red-50/50 dark:bg-red-900/10 border-l-4 border-red-500' : ''}
                                                        ${highlightId == item.id ? 'ring-2 ring-blue-500 animate-pulse' : ''}
                                                    `}
                                                >
                                                    <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 font-mono">{item.serial_no}</td>
                                                    <td className="px-4 py-3">
                                                        <div className="flex items-center gap-2">
                                                            <span className="font-medium text-slate-900 dark:text-white text-sm">{item.full_name}</span>
                                                            {item.fraud_flagged && (
                                                                <ShieldAlert size={14} className="text-red-600 dark:text-red-400" title="Fraud Alert" />
                                                            )}
                                                        </div>
                                                    </td>
                                                    <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 font-mono">{item.cnic}</td>
                                                    <td className="px-4 py-3">
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-16 bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                                                                <div
                                                                    className={`h-1.5 rounded-full ${item.risk_score > 70 ? 'bg-red-500' : item.risk_score > 30 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                                                    style={{ width: `${item.risk_score}%` }}
                                                                ></div>
                                                            </div>
                                                            <span className={`text-xs font-bold ${item.risk_score > 70 ? 'text-red-500' : item.risk_score > 30 ? 'text-yellow-500' : 'text-green-500'}`}>{item.risk_score}</span>
                                                        </div>
                                                        {item.fraud_alerts && item.fraud_alerts.length > 0 && (
                                                            <div className="text-[10px] text-red-600 dark:text-red-400 mt-1 flex items-center gap-1">
                                                                <AlertTriangle size={10} />
                                                                {item.fraud_alerts[0]}
                                                            </div>
                                                        )}
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <button 
                                                            onClick={(e) => handleReviewClick(e, item)}
                                                            className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md transition-colors"
                                                        >
                                                            Review Now
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="5" className="px-4 py-8 text-center text-slate-500 dark:text-slate-400 text-sm">
                                                    No pending verifications
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Verified Table */}
                        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                            <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-2">
                                <CheckCircle className="text-green-600 dark:text-green-400" size={18} />
                                <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                                    Verified
                                </h2>
                                <span className="text-sm text-slate-500 dark:text-slate-400">
                                    ({verifiedVerifications.length})
                                </span>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 text-xs uppercase">
                                        <tr>
                                            <th className="px-4 py-2 font-semibold">SN</th>
                                            <th className="px-4 py-2 font-semibold">Name</th>
                                            <th className="px-4 py-2 font-semibold">CNIC</th>
                                            <th className="px-4 py-2 font-semibold">Date</th>
                                            <th className="px-4 py-2 font-semibold">Risk</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                                        {verifiedVerifications.length > 0 ? (
                                            verifiedVerifications.map((item) => (
                                                <TableRow 
                                                    key={item.id} 
                                                    item={item}
                                                    isHighlighted={highlightId == item.id}
                                                />
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="5" className="px-4 py-8 text-center text-slate-500 dark:text-slate-400 text-sm">
                                                    No verified customers yet
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-2">
                            <XCircle className="text-red-600 dark:text-red-400" size={18} />
                            <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                                Rejected Customers
                            </h2>
                            <span className="text-sm text-slate-500 dark:text-slate-400">
                                ({filteredData.length})
                            </span>
                        </div>
                        <table className="w-full text-left">
                            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 text-xs uppercase">
                                <tr>
                                    <th className="px-4 py-2 font-semibold">SN</th>
                                    <th className="px-4 py-2 font-semibold">Name</th>
                                    <th className="px-4 py-2 font-semibold">CNIC</th>
                                    <th className="px-4 py-2 font-semibold">Date</th>
                                    <th className="px-4 py-2 font-semibold">Rejection Reason</th>
                                    <th className="px-4 py-2 font-semibold">Risk</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                                {filteredData.length > 0 ? (
                                    filteredData.map((item) => (
                                        <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                                            <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 font-mono">{item.serial_no}</td>
                                            <td className="px-4 py-3 text-sm font-medium text-slate-900 dark:text-white">{item.full_name}</td>
                                            <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 font-mono">{item.cnic}</td>
                                            <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400">{new Date(item.date).toLocaleDateString()}</td>
                                            <td className="px-4 py-3 text-sm text-red-600 dark:text-red-400 max-w-xs truncate" title={item.remarks}>
                                                {item.remarks || 'No reason provided'}
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs font-bold text-red-500">{item.risk_score}</span>
                                                    <button 
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            if(window.confirm('Are you sure you want to delete this record? This action cannot be undone.')) {
                                                                // Call delete API
                                                                axios.delete(`/api/admin/verifications/${item.customer_id || item.id}`, {
                                                                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                                                                }).then(() => {
                                                                    fetchVerifications();
                                                                }).catch(err => console.error(err));
                                                            }
                                                        }}
                                                        className="p-1 text-slate-400 hover:text-red-600 transition-colors"
                                                        title="Delete Record"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="6" className="px-4 py-8 text-center text-slate-500 dark:text-slate-400 text-sm">
                                            No rejected verifications
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
            {/* Review Modal */}
            {showReviewModal && selectedVerification && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white dark:bg-slate-800 rounded-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
                        <h3 className="text-xl font-bold mb-4 dark:text-white">Review Verification</h3>
                        
                        <div className="space-y-4 mb-6">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div><span className="text-slate-500">Name:</span> <span className="font-medium dark:text-white">{selectedVerification.full_name}</span></div>
                                <div><span className="text-slate-500">CNIC:</span> <span className="font-medium dark:text-white">{selectedVerification.cnic}</span></div>
                                <div><span className="text-slate-500">Email:</span> <span className="font-medium dark:text-white">{selectedVerification.email}</span></div>
                                <div><span className="text-slate-500">Phone:</span> <span className="font-medium dark:text-white">{selectedVerification.phone}</span></div>
                                <div className="col-span-2"><span className="text-slate-500">Risk Score:</span> <span className={`font-bold ${selectedVerification.risk_score > 70 ? 'text-red-600' : selectedVerification.risk_score > 30 ? 'text-yellow-600' : 'text-green-600'}`}>{selectedVerification.risk_score}</span></div>
                                {selectedVerification.remarks && (
                                    <div className="col-span-2">
                                        <span className="text-slate-500">AI Remarks:</span>
                                        <p className="text-sm mt-1 p-2 bg-slate-50 dark:bg-slate-700 rounded dark:text-white">{selectedVerification.remarks}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                        
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2 dark:text-white">Decision</label>
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setDecision('approve')}
                                        className={`flex-1 py-2 px-4 rounded-lg border-2 transition-colors ${decision === 'approve' ? 'bg-green-600 border-green-600 text-white' : 'border-slate-300 dark:border-slate-600 hover:border-green-600 dark:text-white'}`}
                                    >
                                        ✓ Approve
                                    </button>
                                    <button
                                        onClick={() => setDecision('reject')}
                                        className={`flex-1 py-2 px-4 rounded-lg border-2 transition-colors ${decision === 'reject' ? 'bg-red-600 border-red-600 text-white' : 'border-slate-300 dark:border-slate-600 hover:border-red-600 dark:text-white'}`}
                                    >
                                        ✗ Reject
                                    </button>
                                </div>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium mb-2 dark:text-white">Remarks (Optional)</label>
                                <textarea
                                    value={remarks}
                                    onChange={(e) => setRemarks(e.target.value)}
                                    className="w-full p-2 border dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
                                    rows="3"
                                    placeholder="Enter additional remarks..."
                                ></textarea>
                            </div>
                            
                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setShowReviewModal(false)}
                                    className="flex-1 px-4 py-2 border dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-white"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSubmitDecision}
                                    disabled={submitting || !decision}
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                >
                                    {submitting ? 'Submitting...' : 'Submit Decision'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
};

export default Verifications;
