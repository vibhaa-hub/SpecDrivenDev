import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';
import api from '../api/axios';

const DashboardPage = () => {
    const [summary, setSummary] = useState(null);
    const [breakdown, setBreakdown] = useState([]);
    const [trends, setTrends] = useState([]);
    const [topCats, setTopCats] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            const [sumRes, breakRes, trendRes, topRes] = await Promise.all([
                api.get('/analytics/summary'),
                api.get('/analytics/breakdown'),
                api.get('/analytics/trends'),
                api.get('/analytics/top-categories'),
            ]);
            setSummary(sumRes.data);
            setBreakdown(breakRes.data);
            setTrends(trendRes.data);
            setTopCats(topRes.data);
        } catch (err) {
            alert('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc659', '#ff7675'];

    if (loading) return <div className="flex items-center justify-center min-h-screen">Loading Analytics...</div>;

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Financial Overview</h1>
            
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="p-6 bg-white shadow rounded-lg border-l-4 border-blue-500">
                    <p className="text-gray-500 text-sm uppercase font-semibold">Total Income</p>
                    <p className="text-2xl font-bold">${summary?.total_income.toFixed(2)}</p>
                </div>
                <div className="p-6 bg-white shadow rounded-lg border-l-4 border-red-500">
                    <p className="text-gray-500 text-sm uppercase font-semibold">Total Expenses</p>
                    <p className="text-2xl font-bold">${summary?.total_expenses.toFixed(2)}</p>
                </div>
                <div className="p-6 bg-white shadow rounded-lg border-l-4 border-green-500">
                    <p className="text-gray-500 text-sm uppercase font-semibold">Net Savings</p>
                    <p className="text-2xl font-bold">${summary?.net_savings.toFixed(2)}</p>
                </div>
                <div className="p-6 bg-white shadow rounded-lg border-l-4 border-indigo-500">
                    <p className="text-gray-500 text-sm uppercase font-semibold">Savings Rate</p>
                    <p className="text-2xl font-bold">{summary?.savings_rate.toFixed(1)}%</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Spending Breakdown */}
                <div className="p-6 bg-white shadow rounded-lg">
                    <h3 className="text-lg font-bold mb-4">Category Breakdown</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie 
                                    data={breakdown} 
                                    dataKey="amount" 
                                    nameKey="category_id" 
                                    cx="50%" cy="50%" 
                                    outerRadius={80} 
                                    fill="#8884d8" 
                                    label
                                >
                                    {breakdown.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Spending Trends */}
                <div className="p-6 bg-white shadow rounded-lg">
                    <h3 className="text-lg font-bold mb-4">12-Month Spending Trend</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trends}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="amount" stroke="#ef4444" strokeWidth={2} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Top Categories */}
                <div className="p-6 bg-white shadow rounded-lg lg:col-span-2">
                    <h3 className="text-lg font-bold mb-4">Top 5 Spending Categories</h3>
                    <div className="space-y-4">
                        {topCats.map((cat, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <span className="font-medium">Category {cat.category_id}</span>
                                <span className="font-bold text-red-500">${cat.amount.toFixed(2)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
