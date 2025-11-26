import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { FileText, Download, Clock, ChevronDown, BarChart2, PieChart as PieIcon } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const Reports = () => {
    const [selectedRange, setSelectedRange] = useState('24 Hours');
    const [loading, setLoading] = useState(true);
    const [barData, setBarData] = useState([]);
    const [pieData, setPieData] = useState([]);

    const timeRanges = [
        '1 Minute', '15 Minutes', '2 Hours', '6 Hours', '12 Hours',
        '24 Hours', '1 Week', '1 Month', '6 Months', '1 Year'
    ];

    useEffect(() => {
        fetchReportData();
    }, [selectedRange]);

    const fetchReportData = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`/api/admin/reports/stats?time_range=${selectedRange}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // Set bar chart data from API
            setBarData(res.data.daily_activity);

            // Set pie chart data from API
            setPieData([
                { name: 'Verified', value: res.data.overall.verified, color: '#10B981' },
                { name: 'Rejected', value: res.data.overall.rejected, color: '#EF4444' },
                { name: 'Pending', value: res.data.overall.pending, color: '#F59E0B' },
            ]);

            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch report data:', err);
            setLoading(false);
        }
    };

    const handleExport = async (type) => {
        const token = localStorage.getItem('token');
        const link = document.createElement('a');
        link.href = `/api/admin/reports/export/${type}?token=${token}`;
        link.setAttribute('download', `${type}_customers.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-8">
                <div className="flex justify-between items-end">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">System Reports</h1>
                        <p className="text-slate-500 dark:text-slate-400 mt-1">Analyze system performance and user statistics.</p>
                    </div>
                    <div className="relative w-48">
                        <select
                            value={selectedRange}
                            onChange={(e) => setSelectedRange(e.target.value)}
                            className="w-full appearance-none px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                        >
                            {timeRanges.map((range) => (
                                <option key={range} value={range}>{range}</option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
                    </div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Activity Chart */}
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                            <BarChart2 size={20} className="text-blue-500" /> Verification Activity
                        </h3>
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={barData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                        cursor={{ fill: '#f1f5f9' }}
                                    />
                                    <Bar dataKey="verified" fill="#10B981" radius={[4, 4, 0, 0]} stackId="a" />
                                    <Bar dataKey="rejected" fill="#EF4444" radius={[4, 4, 0, 0]} stackId="a" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Status Distribution */}
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                            <PieIcon size={20} className="text-purple-500" /> Overall Status
                        </h3>
                        <div className="h-[300px] w-full flex items-center justify-center">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={80}
                                        outerRadius={100}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex justify-center gap-6 mt-4">
                            {pieData.map((item) => (
                                <div key={item.name} className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                                    <span className="text-sm text-slate-600 dark:text-slate-400">{item.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Export Section */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                        <Download size={20} className="text-slate-500" /> Export Data
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button
                            onClick={() => handleExport('verified')}
                            className="p-4 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left group"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div className="p-2 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
                                    <FileText size={20} />
                                </div>
                                <Download size={16} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
                            </div>
                            <h4 className="font-medium text-slate-900 dark:text-white">Verified Users</h4>
                            <p className="text-xs text-slate-500 mt-1">Export list of all verified customers</p>
                        </button>

                        <button
                            onClick={() => handleExport('rejected')}
                            className="p-4 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left group"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div className="p-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg">
                                    <FileText size={20} />
                                </div>
                                <Download size={16} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
                            </div>
                            <h4 className="font-medium text-slate-900 dark:text-white">Rejected Applications</h4>
                            <p className="text-xs text-slate-500 mt-1">Export list of rejected applications</p>
                        </button>

                        <button
                            onClick={() => handleExport('pending')}
                            className="p-4 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left group"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div className="p-2 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded-lg">
                                    <FileText size={20} />
                                </div>
                                <Download size={16} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
                            </div>
                            <h4 className="font-medium text-slate-900 dark:text-white">Pending Queue</h4>
                            <p className="text-xs text-slate-500 mt-1">Export list of pending verifications</p>
                        </button>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default Reports;
