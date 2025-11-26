import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { ShieldAlert, AlertTriangle, MapPin, Clock } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import axios from 'axios';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const FraudDetection = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchFraudAlerts();
    }, []);

    const fetchFraudAlerts = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('/api/admin/pending', { headers: { Authorization: `Bearer ${token}` } });

            // Filter for high risk (> 70)
            const highRiskUsers = res.data.filter(user => user.risk_score > 70).map(user => ({
                id: user.id,
                type: 'High Risk Application',
                user: user.full_name,
                location: user.city || 'Unknown',
                time: 'Just now',
                severity: 'High',
                risk_score: user.risk_score
            }));

            setAlerts(highRiskUsers);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching fraud alerts", error);
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-8">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                    <ShieldAlert className="text-red-600" /> Fraud Detection Center
                </h1>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Live Alerts Feed */}
                    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Live Alerts</h2>
                            <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded-full animate-pulse">LIVE</span>
                        </div>
                        <div className="divide-y divide-slate-100 dark:divide-slate-700">
                            {loading ? (
                                <div className="p-8 text-center text-slate-500">Loading alerts...</div>
                            ) : alerts.length === 0 ? (
                                <div className="p-8 text-center text-slate-500 dark:text-slate-400">
                                    <ShieldAlert size={48} className="mx-auto text-slate-300 mb-2" />
                                    <p>No active fraud alerts detected.</p>
                                </div>
                            ) : (
                                alerts.map((alert) => (
                                    <div key={alert.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                                        <div className="flex justify-between items-start mb-1">
                                            <h3 className="text-sm font-bold text-slate-900 dark:text-white">{alert.type}</h3>
                                            <span className="bg-red-50 text-red-600 border-red-100 text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase">
                                                Score: {alert.risk_score}
                                            </span>
                                        </div>
                                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">{alert.user} • {alert.location}</p>
                                        <div className="flex items-center gap-1 text-[10px] text-slate-400">
                                            <Clock size={12} /> {alert.time}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Map */}
                    <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col h-[500px]">
                        <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <MapPin size={18} className="text-blue-500" /> Threat Heatmap
                            </h2>
                        </div>
                        <div className="flex-1 relative z-0">
                            <MapContainer center={[30.3753, 69.3451]} zoom={5} style={{ height: '100%', width: '100%' }}>
                                <TileLayer
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    attribution='&copy; OpenStreetMap contributors'
                                />
                                {/* Real markers would be added here based on geocoded location data */}
                            </MapContainer>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default FraudDetection;
