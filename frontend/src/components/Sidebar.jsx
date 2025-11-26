import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, FileText, ShieldAlert, CreditCard, Settings, LogOut } from 'lucide-react';

const Sidebar = ({ darkMode, role }) => {
    const adminNavItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
        { icon: Users, label: 'Verifications', path: '/admin/verifications' },
        { icon: CreditCard, label: 'Loan Management', path: '/admin/loans' },
        { icon: ShieldAlert, label: 'Fraud Detection', path: '/admin/fraud' },
        { icon: Users, label: 'Admin Management', path: '/admin/users' },
        { icon: FileText, label: 'Reports', path: '/admin/reports' },
        { icon: Settings, label: 'Settings', path: '/admin/settings' },
    ];

    const customerNavItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: CreditCard, label: 'Apply for Loan', path: '/dashboard?view=loans' },
    ];

    const navItems = role === 'admin' ? adminNavItems : customerNavItems;

    const handleLogout = () => {
        localStorage.clear();
        window.location.href = '/login';
    };

    return (
        <aside className={`w-64 h-screen fixed left-0 top-0 flex flex-col transition-colors duration-300 border-r
            ${darkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`}>

            {/* Logo */}
            <div className="p-6 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                    <ShieldAlert className="text-white" size={20} />
                </div>
                <h1 className={`text-xl font-bold tracking-tight ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    NeoBank <span className="text-blue-500">{role === 'admin' ? 'Admin' : 'Customer'}</span>
                </h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.path === '/admin' || item.path === '/dashboard'} // Exact match for roots
                        className={({ isActive }) => `
                            flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all
                            ${isActive
                                ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                : `text-slate-500 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white`}
                        `}
                    >
                        <item.icon size={20} />
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            {/* User Profile & Logout */}
            <div className={`p-4 border-t ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
                <div className={`flex items-center gap-3 p-3 rounded-xl mb-2 ${darkMode ? 'bg-slate-800' : 'bg-slate-50'}`}>
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                        {role === 'admin' ? 'A' : 'C'}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className={`text-sm font-semibold truncate ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            {role === 'admin' ? 'Asharib Admin' : 'Customer User'}
                        </p>
                        <p className="text-xs text-slate-500 truncate">
                            {role === 'admin' ? 'admin@neobank.com' : 'user@neobank.com'}
                        </p>
                    </div>
                </div>
                <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                >
                    <LogOut size={18} /> Sign Out
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
