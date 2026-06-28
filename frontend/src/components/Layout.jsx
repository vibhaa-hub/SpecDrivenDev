import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <div className="flex min-h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="w-64 bg-slate-800 text-white flex flex-col">
                <div className="p-6 text-2xl font-bold border-b border-slate-700">
                    ExpenseTracker
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    <Link to="/dashboard" className="block p-2 hover:bg-slate-700 rounded transition">Dashboard</Link>
                    <Link to="/transactions" className="block p-2 hover:bg-slate-700 rounded transition">Transactions</Link>
                    <Link to="/categories" className="block p-2 hover:bg-slate-700 rounded transition">Categories</Link>
                    <Link to="/tags" className="block p-2 hover:bg-slate-700 rounded transition">Tags</Link>
                    <Link to="/goals" className="block p-2 hover:bg-slate-700 rounded transition">Savings Goals</Link>
                    <Link to="/budgets" className="block p-2 hover:bg-slate-700 rounded transition">Budgets</Link>
                </nav>
                <div className="p-4 border-t border-slate-700">
                    <button 
                        onClick={handleLogout}
                        className="w-full text-left p-2 hover:bg-red-600 rounded transition"
                    >
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8">
                {children}
            </main>
        </div>
    );
};

export default Layout;
