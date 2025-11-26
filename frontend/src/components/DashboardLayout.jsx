import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Moon, Sun, Bell } from 'lucide-react';
import axios from 'axios';

import Chatbot from './Chatbot';

const DashboardLayout = ({ children }) => {
    const navigate = useNavigate();
    const [darkMode, setDarkMode] = useState(() => {
        return localStorage.getItem('darkMode') === 'true';
    });
    const [notifications, setNotifications] = useState([]);

    const [role, setRole] = useState('customer');

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('darkMode', 'false');
        }
    }, [darkMode]);

    useEffect(() => {
        const userRole = localStorage.getItem('role') || 'customer';
        setRole(userRole);
        fetchNotifications();
    }, []);

    const fetchNotifications = async () => {
        try {
            const token = localStorage.getItem('token');
            // Fetch pending users as "notifications" for new registrations
            const res = await axios.get('/api/admin/pending', { headers: { Authorization: `Bearer ${token}` } });
            // Map pending users to notification format
            const newNotifs = res.data.map(user => ({
                id: user.id,
                title: 'New Registration',
                message: `${user.full_name} registered`,
                time: 'Just now' // In a real app, calculate relative time
            }));
            setNotifications(newNotifs);
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        }
    };

    const handleNotificationClick = () => {
        if (role === 'admin') {
            navigate('/admin/verifications');
        } else {
            navigate('/dashboard');
        }
    };

    return (
        <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'bg-slate-950' : 'bg-slate-50'}`}>
            <Sidebar darkMode={darkMode} role={role} />

            <main className="ml-64 min-h-screen flex flex-col">
                {/* Topbar */}
                <header className={`h-16 px-8 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md border-b transition-colors duration-300
                    ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white/80 border-slate-200'}`}>

                    {/* Spacer since Search is removed */}
                    <div className="flex-1"></div>

                    {/* Actions */}
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setDarkMode(!darkMode)}
                            className={`p-2 rounded-full transition-colors ${darkMode ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-600'}`}
                        >
                            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                        </button>

                        <div className="relative group">
                            <button className={`relative p-2 rounded-full transition-colors ${darkMode ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-600'}`}>
                                <Bell size={20} />
                                {notifications.length > 0 && (
                                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900"></span>
                                )}
                            </button>

                            {/* Notification Dropdown */}
                            <div className={`absolute right-0 top-full mt-2 w-80 rounded-xl shadow-lg border py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50
                                ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'}`}>
                                <div className={`px-4 py-2 border-b text-sm font-semibold ${darkMode ? 'border-slate-700 text-white' : 'border-slate-100 text-slate-900'}`}>
                                    Notifications ({notifications.length})
                                </div>
                                <div className="max-h-64 overflow-y-auto">
                                    {notifications.length === 0 ? (
                                        <div className="px-4 py-8 text-center text-sm text-slate-500">
                                            No new notifications
                                        </div>
                                    ) : (
                                        notifications.map((notif) => (
                                            <div
                                                key={notif.id}
                                                onClick={handleNotificationClick}
                                                className={`px-4 py-3 border-b hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}
                                            >
                                                <p className={`text-sm font-medium ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{notif.title}</p>
                                                <p className="text-xs text-slate-500 mt-0.5">{notif.message}</p>
                                                <p className="text-[10px] text-slate-400 mt-1">{notif.time}</p>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3 pl-4 border-l border-slate-200 dark:border-slate-700">
                            <div className="text-right hidden sm:block">
                                <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                                    {localStorage.getItem('full_name') || 'User'}
                                </p>
                                <p className="text-xs text-slate-500 capitalize">{role}</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 p-[2px]">
                                <div className={`w-full h-full rounded-full ${darkMode ? 'bg-slate-900' : 'bg-white'} flex items-center justify-center`}>
                                    <span className="font-bold text-blue-500">
                                        {(localStorage.getItem('full_name') || 'U').charAt(0).toUpperCase()}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Content Area */}
                <div className="flex-1 p-8 overflow-y-auto">
                    {children}
                </div>
            </main>

            <Chatbot />
        </div>
    );
};

export default DashboardLayout;
