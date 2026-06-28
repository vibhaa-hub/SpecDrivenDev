import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import CategoryPage from './pages/CategoryPage';
import TagPage from './pages/TagPage';
import TransactionPage from './pages/TransactionPage';
import SavingsGoalPage from './pages/SavingsGoalPage';
import BudgetPage from './pages/BudgetPage';
import DashboardPage from './pages/DashboardPage';
import Layout from './components/Layout';

const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    if (!user) return <Navigate to="/login" />;
    return <Layout>{children}</Layout>;
};

const App = () => {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignupPage />} />
                    <Route path="/dashboard" element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    } />
                    <Route path="/transactions" element={<ProtectedRoute><TransactionPage /></ProtectedRoute>} />
                    <Route path="/categories" element={<ProtectedRoute><CategoryPage /></ProtectedRoute>} />
                    <Route path="/tags" element={<ProtectedRoute><TagPage /></ProtectedRoute>} />
                    <Route path="/goals" element={<ProtectedRoute><SavingsGoalPage /></ProtectedRoute>} />
                    <Route path="/budgets" element={<ProtectedRoute><BudgetPage /></ProtectedRoute>} />
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
};

export default App;

