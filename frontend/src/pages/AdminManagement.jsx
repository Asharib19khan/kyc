import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { UserPlus, Edit2, Trash2, Shield, X, Check } from 'lucide-react';
import axios from 'axios';

const AdminManagement = () => {
    const [admins, setAdmins] = useState([]);
    const [showAddModal, setShowAddModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [formData, setFormData] = useState({ name: '', email: '', role: 'Moderator', password: '' });
    const [editData, setEditData] = useState({ username: '', password: '', newPassword: '' });

    useEffect(() => {
        fetchAdmins();
    }, []);

    const fetchAdmins = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('/api/admin/admins', { headers: { Authorization: `Bearer ${token}` } });
            setAdmins(res.data);
        } catch (error) {
            console.error("Error fetching admins", error);
        }
    };

    const handleAddAdmin = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            await axios.post('/api/auth/admin/register', {
                username: formData.email, // Using email as username for now
                password: formData.password,
                full_name: formData.name
            }, { headers: { Authorization: `Bearer ${token}` } });

            alert("New admin added successfully!");
            setShowAddModal(false);
            setFormData({ name: '', email: '', role: 'Moderator', password: '' });
            fetchAdmins();
        } catch (error) {
            console.error("Error adding admin", error);
            alert("Failed to add admin");
        }
    };

    const handleEditProfile = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            // Assuming current user is updating their own profile
            // We need to know the current username. For now, we'll ask for it or use a stored one.
            // Let's use the input username.
            await axios.put('/api/admin/profile', {
                username: editData.username,
                password: editData.newPassword
            }, { headers: { Authorization: `Bearer ${token}` } });

            alert("Profile updated successfully!");
            setShowEditModal(false);
        } catch (error) {
            console.error("Error updating profile", error);
            alert("Failed to update profile");
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admin Management</h1>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowAddModal(true)}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                        >
                            <UserPlus size={18} /> Add New Admin
                        </button>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-4 font-semibold">Name</th>
                                <th className="px-6 py-4 font-semibold">Username</th>
                                <th className="px-6 py-4 font-semibold">Role</th>
                                <th className="px-6 py-4 font-semibold">Status</th>
                                <th className="px-6 py-4 font-semibold">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                            {admins.map((admin) => (
                                <tr key={admin.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xs">
                                                {admin.full_name ? admin.full_name.charAt(0) : 'A'}
                                            </div>
                                            <span className="font-medium text-slate-900 dark:text-white">{admin.full_name}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-600 dark:text-slate-300">{admin.username}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-slate-300">
                                            <Shield size={14} className="text-blue-500" /> {admin.role}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-100 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30">
                                            {admin.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <button
                                            onClick={() => {
                                                setEditData({ username: admin.username, password: '', newPassword: '' });
                                                setShowEditModal(true);
                                            }}
                                            className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 p-1 rounded hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
                                            title="Edit Admin"
                                        >
                                            <Edit2 size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add Admin Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl max-w-md w-full p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Add New Admin</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleAddAdmin} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Full Name</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Username / Email</label>
                                <input
                                    type="text"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Role</label>
                                <select
                                    value={formData.role}
                                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="Super Admin">Super Admin</option>
                                    <option value="Moderator">Moderator</option>
                                    <option value="Viewer">Viewer</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Password</label>
                                <input
                                    type="password"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition-colors">
                                Create Admin
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit Profile Modal */}
            {showEditModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl max-w-md w-full p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Edit Profile</h3>
                            <button onClick={() => setShowEditModal(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleEditProfile} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Username</label>
                                <input
                                    type="text"
                                    value={editData.username}
                                    onChange={(e) => setEditData({ ...editData, username: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">New Password</label>
                                <input
                                    type="password"
                                    value={editData.newPassword}
                                    onChange={(e) => setEditData({ ...editData, newPassword: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Leave blank to keep current"
                                />
                            </div>
                            <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition-colors">
                                Update Profile
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
};

export default AdminManagement;
