import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Bell, Lock, Globe, Shield, Clock } from 'lucide-react';
import axios from 'axios';

const Settings = () => {
    const [language, setLanguage] = useState('English (US)');
    const [notifications, setNotifications] = useState({
        email: true,
        push: true,
        fraud: true,
        loan: true,
        loginAlerts: true
    });
    const [sessionTimeout, setSessionTimeout] = useState('30');
    const [twoFactor, setTwoFactor] = useState(true);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('/api/admin/settings', { headers: { Authorization: `Bearer ${token}` } });
            if (res.data && Object.keys(res.data).length > 0) {
                if (res.data.language) setLanguage(res.data.language);
                if (res.data.notifications) setNotifications(res.data.notifications);
                if (res.data.sessionTimeout) setSessionTimeout(res.data.sessionTimeout);
                if (res.data.twoFactor !== undefined) setTwoFactor(res.data.twoFactor);
            }
        } catch (error) {
            console.error("Error fetching settings", error);
        }
    };

    const saveSettings = async (newSettings) => {
        try {
            const token = localStorage.getItem('token');
            // Merge with current state to ensure we send full object or just partial?
            // Let's send the specific update merged with current state
            const payload = {
                language,
                notifications,
                sessionTimeout,
                twoFactor,
                ...newSettings
            };

            await axios.post('/api/admin/settings', payload, { headers: { Authorization: `Bearer ${token}` } });
        } catch (error) {
            console.error("Error saving settings", error);
        }
    };

    const handleToggle = (key) => {
        const newNotifs = { ...notifications, [key]: !notifications[key] };
        setNotifications(newNotifs);
        saveSettings({ notifications: newNotifs });
    };

    const handleLanguageChange = (e) => {
        const lang = e.target.value;
        setLanguage(lang);
        saveSettings({ language: lang });
    };

    const handleTimeoutChange = (e) => {
        const timeout = e.target.value;
        setSessionTimeout(timeout);
        saveSettings({ sessionTimeout: timeout });
    };

    const handle2FAToggle = () => {
        const newVal = !twoFactor;
        setTwoFactor(newVal);
        saveSettings({ twoFactor: newVal });
    };

    return (
        <DashboardLayout>
            <div className="max-w-3xl mx-auto space-y-8">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>

                {/* General Settings */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                    <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Globe size={20} className="text-blue-500" /> General
                        </h2>
                    </div>
                    <div className="p-6 space-y-6">
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="font-medium text-slate-900 dark:text-white">Language</p>
                                <p className="text-sm text-slate-500">Select your preferred language</p>
                            </div>
                            <select
                                value={language}
                                onChange={handleLanguageChange}
                                className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm outline-none text-slate-700 dark:text-slate-300"
                            >
                                <option>English (US)</option>
                                <option>Urdu</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Notifications */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                    <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Bell size={20} className="text-yellow-500" /> Notifications
                        </h2>
                    </div>
                    <div className="p-6 space-y-4">
                        {[
                            { key: 'email', label: 'Email Notifications' },
                            { key: 'push', label: 'Push Notifications' },
                            { key: 'fraud', label: 'Fraud Alerts' },
                            { key: 'loan', label: 'Loan Updates' },
                            { key: 'loginAlerts', label: 'Login Alerts' }
                        ].map((item) => (
                            <div key={item.key} className="flex justify-between items-center">
                                <span className="text-slate-700 dark:text-slate-300 font-medium">{item.label}</span>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={notifications[item.key]}
                                        onChange={() => handleToggle(item.key)}
                                    />
                                    <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Security */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                    <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Lock size={20} className="text-green-500" /> Security
                        </h2>
                    </div>
                    <div className="p-6 space-y-4">
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="font-medium text-slate-900 dark:text-white">Two-Factor Authentication</p>
                                <p className="text-sm text-slate-500">Secure your account with 2FA</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    className="sr-only peer"
                                    checked={twoFactor}
                                    onChange={handle2FAToggle}
                                />
                                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-green-500"></div>
                            </label>
                        </div>

                        <div className="flex justify-between items-center pt-4 border-t border-slate-100 dark:border-slate-700">
                            <div>
                                <p className="font-medium text-slate-900 dark:text-white flex items-center gap-2">
                                    <Clock size={16} className="text-slate-400" /> Session Timeout
                                </p>
                                <p className="text-sm text-slate-500">Auto-logout after inactivity</p>
                            </div>
                            <select
                                value={sessionTimeout}
                                onChange={handleTimeoutChange}
                                className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm outline-none text-slate-700 dark:text-slate-300"
                            >
                                <option value="15">15 minutes</option>
                                <option value="30">30 minutes</option>
                                <option value="60">1 hour</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default Settings;
