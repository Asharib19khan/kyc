import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Users, Clock, CheckCircle, XCircle, MapPin, Search, FileText, TrendingUp, ShieldAlert, Activity, MessageSquare, ArrowUpRight, ArrowDownRight, MoreHorizontal } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import 'leaflet/dist/leaflet.css';
import DashboardLayout from '../components/DashboardLayout';

// Fix Leaflet Marker Icon
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const AdminDashboard = () => {
    const [stats, setStats] = useState({ total_customers: 0, pending_verifications: 0, approved_loans: 0 });
    const [chartData, setChartData] = useState([]);
    const [riskData, setRiskData] = useState([]);
    const [pendingUsers, setPendingUsers] = useState([]);
    const [auditLogs, setAuditLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Bearer ${token}` } };

            const statsRes = await axios.get('/api/admin/stats', config);
            setStats(statsRes.data);

            // Fetch Chart Data
            const reportsRes = await axios.get('/api/admin/reports/stats?time_range=1 Week', config);
            setChartData(reportsRes.data.daily_activity);
            setRiskData([
                { name: 'Verified', value: reportsRes.data.overall.verified, color: '#10B981' },
                { name: 'Rejected', value: reportsRes.data.overall.rejected, color: '#EF4444' },
                { name: 'Pending', value: reportsRes.data.overall.pending, color: '#F59E0B' },
            ]);

            setLoading(false);
        } catch (error) {
            console.error("Error fetching admin data", error);
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, icon: Icon, color, trend, trendValue }) => (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-md transition-all">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl ${color}`}>
                    <Icon size={24} />
                </div>
                {trend && (
                    <div className={`flex items-center text-xs font-medium px-2 py-1 rounded-full ${trend === 'up' ? 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400'}`}>
                        {trend === 'up' ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
                        {trendValue}
                    </div>
                )}
            </div>
            <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
                <h3 className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{value}</h3>
            </div>
        </div>
    );

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
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header & Stats */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard Overview</h1>
                        <p className="text-slate-500 dark:text-slate-400 text-sm">Welcome back, Admin</p>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <StatCard
                        title="Total Customers"
                        value={stats.total_customers}
                        icon={Users}
                        color="bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400"
                    />
                    <StatCard
                        title="Pending Verifications"
                        value={stats.pending_verifications}
                        icon={Clock}
                        color="bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400"
                    />
                    <StatCard
                        title="Approved Loans"
                        value={stats.approved_loans}
                        icon={CheckCircle}
                        color="bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400"
                    />
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Bar Chart */}
                    <div className="lg:col-span-2 bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6">Verification Activity</h3>
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData}>
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

                    {/* Risk Distribution (Now showing Overall Status) */}
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6">Overall Status</h3>
                        <div className="h-[300px] w-full flex items-center justify-center">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={riskData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={80}
                                        outerRadius={100}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {riskData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex justify-center gap-4 mt-4">
                            {riskData.map((item) => (
                                <div key={item.name} className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                                    <span className="text-xs text-slate-600 dark:text-slate-400">{item.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default AdminDashboard;
