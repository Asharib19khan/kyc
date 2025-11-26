import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import AdminDashboard from './pages/AdminDashboard'
import Register from './pages/Register'
import CustomerDashboard from './pages/CustomerDashboard';
import { LanguageProvider } from './contexts/LanguageContext';

import Verifications from './pages/Verifications';
import LoanManagement from './pages/LoanManagement';
import FraudDetection from './pages/FraudDetection';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import AdminManagement from './pages/AdminManagement';

function App() {
    return (
        <LanguageProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Navigate to="/login" />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/dashboard" element={<CustomerDashboard />} />

                    {/* Admin Routes */}
                    <Route path="/admin" element={<AdminDashboard />} />
                    <Route path="/admin/verifications" element={<Verifications />} />
                    <Route path="/admin/loans" element={<LoanManagement />} />
                    <Route path="/admin/fraud" element={<FraudDetection />} />
                    <Route path="/admin/reports" element={<Reports />} />
                    <Route path="/admin/settings" element={<Settings />} />
                    <Route path="/admin/users" element={<AdminManagement />} />
                </Routes>
            </Router>
        </LanguageProvider>
    );
}

export default App;
