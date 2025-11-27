import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Lock, User, Moon, Sun, ShieldCheck, CreditCard, ArrowRight, ArrowLeft } from 'lucide-react';

const Login = () => {
    const [role, setRole] = useState('customer'); // 'admin' or 'customer'
    const [step, setStep] = useState(1); // 1: Credentials, 2: 2FA
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [customerCode, setCustomerCode] = useState('');
    const [twoFaCode, setTwoFaCode] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [darkMode, setDarkMode] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [darkMode]);

    const handleNextStep = async (e) => {
        e.preventDefault();
        setError('');

        if (!username || !password) {
            setError('Please fill in all fields.');
            return;
        }

        if (role === 'customer' && !customerCode) {
            setError('Please enter your customer code.');
            return;
        }

        // DIRECT LOGIN FOR ADMIN (2FA DISABLED)
        handleLogin();
    };

    const handleLogin = async (e) => {
        if (e) e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            if (role === 'admin') {
                // No 2FA code needed
            } else {
                formData.append('client_secret', customerCode);
            }

            const response = await axios.post('/api/auth/token', formData);
            const { access_token, role: userRole, user_id, full_name } = response.data;

            if (userRole !== role) {
                setError(`Please login via the ${userRole} tab.`);
                setIsLoading(false);
                return;
            }

            localStorage.setItem('token', access_token);
            localStorage.setItem('role', userRole);
            localStorage.setItem('user_id', user_id);
            localStorage.setItem('full_name', full_name);

            if (userRole === 'customer') {
                localStorage.setItem('customer_id', user_id);
            }

            if (userRole === 'admin') {
                navigate('/admin');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            console.error(err);
            setError('Invalid credentials. Please check your details.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={`min-h-screen flex items-center justify-center transition-colors duration-300 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>

            <button
                onClick={() => setDarkMode(!darkMode)}
                className="absolute top-6 right-6 p-2 rounded-full bg-opacity-20 hover:bg-opacity-30 transition-all"
            >
                {darkMode ? <Sun className="text-yellow-400" /> : <Moon className="text-slate-600" />}
            </button>

            <div className={`w-full max-w-md p-8 rounded-2xl shadow-2xl transition-all duration-300 ${darkMode ? 'bg-slate-800 text-white shadow-slate-900/50' : 'bg-white text-slate-800 shadow-slate-200'}`}>

                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4 dark:bg-blue-900/30">
                        <ShieldCheck className="text-blue-600" size={32} />
                    </div>
                    <h1 className="text-3xl font-bold mb-2 tracking-tight">
                        NeoBank
                    </h1>
                    <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Secure KYC & Banking Portal</p>
                </div>

                {step === 1 && (
                    <div className="flex mb-8 bg-slate-100 rounded-xl p-1 dark:bg-slate-700/50">
                        <button
                            onClick={() => setRole('customer')}
                            className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2
                  ${role === 'customer'
                                    ? 'bg-white text-blue-600 shadow-sm dark:bg-slate-600 dark:text-white'
                                    : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'}`}
                        >
                            <User size={16} /> Customer
                        </button>
                        <button
                            onClick={() => setRole('admin')}
                            className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2
                  ${role === 'admin'
                                    ? 'bg-white text-blue-600 shadow-sm dark:bg-slate-600 dark:text-white'
                                    : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'}`}
                        >
                            <Lock size={16} /> Admin Portal
                        </button>
                    </div>
                )}

                {error && <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm text-center font-medium dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">{error}</div>}

                {step === 1 ? (
                    <form onSubmit={handleNextStep} className="space-y-5">
                        <div className="space-y-1">
                            <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                                {role === 'admin' ? 'Username' : 'CNIC Number'}
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                    {role === 'admin' ? <User size={18} className="text-slate-400" /> : <CreditCard size={18} className="text-slate-400" />}
                                </div>
                                <input
                                    type="text"
                                    placeholder={role === 'admin' ? "Enter username" : "XXXXX-XXXXXXX-X"}
                                    className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all
                      ${darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'bg-slate-50 border-slate-200 text-slate-900 hover:bg-white focus:bg-white'}`}
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                                Password
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                    <Lock size={18} className="text-slate-400" />
                                </div>
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all
                    ${darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'bg-slate-50 border-slate-200 text-slate-900 hover:bg-white focus:bg-white'}`}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        {role === 'customer' && (
                            <div className="space-y-1">
                                <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                                    Customer Code
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                        <ShieldCheck size={18} className="text-slate-400" />
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Enter your 8-digit code"
                                        className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all font-mono tracking-wider uppercase
                    ${darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'bg-slate-50 border-slate-200 text-slate-900 hover:bg-white focus:bg-white'}`}
                                        value={customerCode}
                                        onChange={(e) => setCustomerCode(e.target.value.toUpperCase())}
                                        maxLength={8}
                                        required
                                    />
                                </div>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 rounded-xl transition-all shadow-lg hover:shadow-blue-500/30 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Processing...' : 'Login Securely'}
                            {!isLoading && <ArrowRight size={18} />}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="text-center mb-2">
                            <h3 className="text-lg font-semibold">Two-Factor Authentication</h3>
                            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                                We sent a code to your WhatsApp.
                            </p>
                        </div>

                        <div className="space-y-1">
                            <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                                Verification Code
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                    <ShieldCheck size={18} className="text-slate-400" />
                                </div>
                                <input
                                    type="text"
                                    placeholder="Enter 6-digit code"
                                    className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-center tracking-widest font-mono text-lg
                    ${darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'bg-slate-50 border-slate-200 text-slate-900 hover:bg-white focus:bg-white'}`}
                                    value={twoFaCode}
                                    onChange={(e) => setTwoFaCode(e.target.value)}
                                    maxLength={6}
                                    autoFocus
                                />
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className={`flex-1 py-3.5 rounded-xl font-semibold transition-all border
                  ${darkMode ? 'border-slate-600 text-slate-300 hover:bg-slate-700' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}
                            >
                                Back
                            </button>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="flex-[2] bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 rounded-xl transition-all shadow-lg hover:shadow-blue-500/30 disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {isLoading ? 'Verifying...' : 'Verify & Login'}
                            </button>
                        </div>
                    </form>
                )}

                {role === 'customer' && step === 1 && (
                    <div className="mt-8 text-center border-t pt-6 dark:border-slate-700/50">
                        <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                            Don't have an account?{' '}
                            <a href="/register" className="text-blue-600 hover:text-blue-700 font-semibold hover:underline">
                                Register Now
                            </a>
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Login;
