import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { DollarSign, TrendingUp, Users, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';

const LoanManagement = () => {
    const [searchParams] = useSearchParams();
    const highlightId = searchParams.get('id');
    
    const [loans, setLoans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedRowId, setExpandedRowId] = useState(null);
    const [loanDetails, setLoanDetails] = useState(null);
    const [loadingDetails, setLoadingDetails] = useState(false);
    const [decisionReason, setDecisionReason] = useState('');

    useEffect(() => {
        fetchLoans();
    }, []);

    const fetchLoans = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('/api/admin/loans', { headers: { Authorization: `Bearer ${token}` } });
            setLoans(res.data);
            setLoading(false);
            
            // Auto-expand if highlightId is present
            if (highlightId) {
                const loan = res.data.find(l => l.id == highlightId);
                if (loan) handleRowClick(loan);
            }
        } catch (err) {
            console.error("Failed to fetch loans", err);
            setLoading(false);
        }
    };

    const handleRowClick = async (loan) => {
        if (expandedRowId === loan.id) {
            setExpandedRowId(null);
            setLoanDetails(null);
            return;
        }

        setExpandedRowId(loan.id);
        setLoadingDetails(true);
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`/api/admin/loans/${loan.id}/details`, { 
                headers: { Authorization: `Bearer ${token}` } 
            });
            setLoanDetails(res.data);
        } catch (err) {
            console.error("Failed to fetch details", err);
        } finally {
            setLoadingDetails(false);
        }
    };

    const handleDecision = async (decision) => {
        if (!decisionReason && decision === 'Rejected') {
            alert("Please provide a reason for rejection.");
            return;
        }
        
        try {
            const token = localStorage.getItem('token');
            const res = await axios.post('/api/admin/loan-decision', {
                loan_id: expandedRowId,
                decision,
                reason: decisionReason || "Approved by Admin"
            }, { headers: { Authorization: `Bearer ${token}` } });
            
            alert(res.data.message);
            
            // Download PDF
            if (res.data.pdf_url) {
                window.open(res.data.pdf_url, '_blank');
            }
            
            setExpandedRowId(null);
            setLoanDetails(null);
            setDecisionReason('');
            fetchLoans(); // Refresh list
        } catch (err) {
            console.error("Failed to submit decision", err);
            alert("Failed to submit decision");
        }
    };

    // Calculate Stats
    const totalDisbursed = loans.reduce((acc, loan) => acc + (loan.eligibility_status === 'Approved' ? loan.max_limit : 0), 0);
    const activeLoans = loans.length;
    const pendingApproval = loans.filter(l => l.eligibility_status === 'Review' || l.eligibility_status === 'Manual Review').length;

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-8">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Loan Management</h1>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg shadow-blue-500/20">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-blue-100 text-sm font-medium">Potential Disbursement</p>
                                <h3 className="text-3xl font-bold mt-1">PKR {totalDisbursed.toLocaleString()}</h3>
                            </div>
                            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                                <DollarSign size={24} />
                            </div>
                        </div>
                    </div>
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Total Applications</p>
                                <h3 className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{activeLoans}</h3>
                            </div>
                            <div className="p-3 bg-green-50 text-green-600 rounded-xl dark:bg-green-900/20 dark:text-green-400">
                                <TrendingUp size={24} />
                            </div>
                        </div>
                    </div>
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Pending Review</p>
                                <h3 className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{pendingApproval}</h3>
                            </div>
                            <div className="p-3 bg-amber-50 text-amber-600 rounded-xl dark:bg-amber-900/20 dark:text-amber-400">
                                <Users size={24} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Loan Table */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                    <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Recent Eligibility Checks</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-semibold">Applicant</th>
                                    <th className="px-6 py-4 font-semibold">Max Limit</th>
                                    <th className="px-6 py-4 font-semibold">Income Group</th>
                                    <th className="px-6 py-4 font-semibold">Risk Score</th>
                                    <th className="px-6 py-4 font-semibold">Status</th>
                                    <th className="px-6 py-4 font-semibold text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                                {loans.length === 0 ? (
                                    <tr>
                                        <td colSpan="6" className="px-6 py-8 text-center text-slate-500">No loan applications yet.</td>
                                    </tr>
                                ) : (
                                    loans.map((loan) => (
                                        <React.Fragment key={loan.id}>
                                            <tr 
                                                onClick={() => handleRowClick(loan)}
                                                className={`hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer
                                                    ${highlightId == loan.id ? 'bg-blue-50 dark:bg-blue-900/20 animate-pulse ring-2 ring-blue-500' : ''}
                                                    ${expandedRowId === loan.id ? 'bg-slate-50 dark:bg-slate-700/50' : ''}
                                                `}
                                            >
                                                <td className="px-6 py-4">
                                                    <div className="font-medium text-slate-900 dark:text-white">{loan.full_name}</div>
                                                    <div className="text-xs text-slate-500 font-mono">{loan.cnic}</div>
                                                </td>
                                                <td className="px-6 py-4 font-medium text-slate-900 dark:text-white">
                                                    PKR {loan.max_limit?.toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 text-slate-500 dark:text-slate-400 text-sm">
                                                    {loan.income_range}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`text-sm font-bold ${loan.risk_score > 70 ? 'text-red-500' : loan.risk_score > 30 ? 'text-yellow-500' : 'text-green-500'}`}>
                                                        {loan.risk_score}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border
                                                        ${loan.eligibility_status === 'Auto-Approved' || loan.eligibility_status === 'Approved' ? 'bg-green-50 text-green-700 border-green-100 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30' :
                                                            loan.eligibility_status === 'Rejected' ? 'bg-red-50 text-red-700 border-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30' :
                                                                'bg-yellow-50 text-yellow-700 border-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-900/30'}`}>
                                                        {loan.eligibility_status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
                                                        {expandedRowId === loan.id ? 'Close' : 'View Details'}
                                                    </button>
                                                </td>
                                            </tr>
                                            {expandedRowId === loan.id && (
                                                <tr>
                                                    <td colSpan="6" className="px-6 py-6 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700">
                                                        {loadingDetails ? (
                                                            <div className="flex justify-center py-4">
                                                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                                            </div>
                                                        ) : loanDetails ? (
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                                                {/* Left: Customer Profile & Docs */}
                                                                <div className="space-y-6">
                                                                    <div>
                                                                        <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">Customer Profile</h3>
                                                                        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700 space-y-2 text-sm">
                                                                            <div className="flex justify-between"><span className="text-slate-500">Full Name:</span> <span className="font-medium dark:text-white">{loanDetails.customer.full_name}</span></div>
                                                                            <div className="flex justify-between"><span className="text-slate-500">CNIC:</span> <span className="font-medium dark:text-white">{loanDetails.customer.cnic}</span></div>
                                                                            <div className="flex justify-between"><span className="text-slate-500">Email:</span> <span className="font-medium dark:text-white">{loanDetails.customer.email}</span></div>
                                                                            <div className="flex justify-between"><span className="text-slate-500">Phone:</span> <span className="font-medium dark:text-white">{loanDetails.customer.phone}</span></div>
                                                                            <div className="flex justify-between"><span className="text-slate-500">Address:</span> <span className="font-medium dark:text-white">{loanDetails.customer.address}</span></div>
                                                                        </div>
                                                                    </div>
                                                                    
                                                                    <div>
                                                                        <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">Documents</h3>
                                                                        <div className="grid grid-cols-2 gap-4">
                                                                            {loanDetails.documents.map((doc, idx) => (
                                                                                <div key={idx} className="relative group">
                                                                                    <img 
                                                                                        src={`http://localhost:8000/${doc.file_path}`} 
                                                                                        alt={doc.doc_type} 
                                                                                        className="w-full h-32 object-cover rounded-lg border border-slate-200 dark:border-slate-700"
                                                                                    />
                                                                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                                                                                        <span className="text-white text-xs font-medium">{doc.doc_type}</span>
                                                                                    </div>
                                                                                </div>
                                                                            ))}
                                                                            {loanDetails.documents.length === 0 && (
                                                                                <p className="text-slate-500 text-sm italic">No documents uploaded.</p>
                                                                            )}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                
                                                                {/* Right: Risk Analysis & Action */}
                                                                <div className="space-y-6">
                                                                    <div>
                                                                        <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">Risk Analysis</h3>
                                                                        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700 space-y-4">
                                                                            <div className="flex items-center justify-between">
                                                                                <span className="text-sm text-slate-500">Risk Score</span>
                                                                                <div className="flex items-center gap-2">
                                                                                    <div className="w-24 bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                                                                                        <div className={`h-2 rounded-full ${loanDetails.verification.risk_score > 70 ? 'bg-red-500' : 'bg-green-500'}`} style={{width: `${loanDetails.verification.risk_score}%`}}></div>
                                                                                    </div>
                                                                                    <span className="font-bold text-slate-900 dark:text-white">{loanDetails.verification.risk_score}</span>
                                                                                </div>
                                                                            </div>
                                                                            <div className="text-sm">
                                                                                <span className="text-slate-500 block mb-1">AI Remarks:</span>
                                                                                <p className="text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-900 p-2 rounded border border-slate-100 dark:border-slate-700">
                                                                                    {loanDetails.verification.remarks || "No remarks."}
                                                                                </p>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                    
                                                                    {(loan.eligibility_status === 'Pending' || loan.eligibility_status === 'Manual Review' || loan.eligibility_status === 'Review') && (
                                                                        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-900/30">
                                                                            <h3 className="text-sm font-bold text-blue-900 dark:text-blue-100 mb-3">Admin Decision</h3>
                                                                            <textarea
                                                                                className="w-full p-2 text-sm border border-blue-200 dark:border-blue-800 rounded-md mb-3 bg-white dark:bg-slate-800 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                                                                placeholder="Enter remarks or reason for rejection..."
                                                                                rows="3"
                                                                                value={decisionReason}
                                                                                onChange={(e) => setDecisionReason(e.target.value)}
                                                                            ></textarea>
                                                                            <div className="flex gap-3">
                                                                                <button
                                                                                    onClick={() => handleDecision('Approved')}
                                                                                    className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-md text-sm font-medium transition-colors"
                                                                                >
                                                                                    Approve Loan
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => handleDecision('Rejected')}
                                                                                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 rounded-md text-sm font-medium transition-colors"
                                                                                >
                                                                                    Reject Loan
                                                                                </button>
                                                                            </div>
                                                                        </div>
                                                                    )}
                                                                    
                                                                    {(loan.eligibility_status === 'Approved' || loan.eligibility_status === 'Rejected') && (
                                                                        <div className="text-center p-4 bg-slate-100 dark:bg-slate-700 rounded-lg">
                                                                            <p className="text-sm text-slate-600 dark:text-slate-300 font-medium">
                                                                                This loan has been <span className={loan.eligibility_status === 'Approved' ? 'text-green-600' : 'text-red-600'}>{loan.eligibility_status.toUpperCase()}</span>.
                                                                            </p>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        ) : (
                                                            <p className="text-center text-slate-500">No details available.</p>
                                                        )}
                                                    </td>
                                                </tr>
                                            )}
                                        </React.Fragment>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default LoanManagement;
