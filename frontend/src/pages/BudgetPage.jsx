import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const BudgetPage = () => {
    const [budgets, setBudgets] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingBudget, setEditingBudget] = useState(null);
    const [loading, setLoading] = useState(true);
    
    const [formData, setFormData] = useState({
        amount: '',
        period: 'Monthly',
        is_active: true,
        enable_rollover: false,
        category_id: ''
    });

    useEffect(() => {
        fetchBudgets();
    }, []);

    const fetchBudgets = async () => {
        setLoading(true);
        try {
            const response = await api.get('/budgets');
            setBudgets(response.data);
        } catch (err) {
            alert('Failed to fetch budgets');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                amount: parseFloat(formData.amount),
                category_id: formData.category_id ? parseInt(formData.category_id) : null
            };
            if (editingBudget) {
                await api.patch(`/budgets/${editingBudget.id}`, payload);
            } else {
                await api.post('/budgets', payload);
            }
            setShowForm(false);
            setEditingBudget(null);
            setFormData({ amount: '', period: 'Monthly', is_active: true, enable_rollover: false, category_id: '' });
            fetchBudgets();
        } catch (err) {
            alert('Error saving budget: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (budget) => {
        setEditingBudget(budget);
        setFormData({
            amount: budget.amount,
            period: budget.period,
            is_active: budget.is_active,
            enable_rollover: budget.enable_rollover,
            category_id: budget.category_id || ''
        });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this budget?')) return;
        try {
            await api.delete(`/budgets/${id}`);
            fetchBudgets();
        } catch (err) {
            alert('Error deleting budget: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Budgets</h1>
                <button 
                    onClick={() => { setShowForm(true); setEditingBudget(null); setFormData({ amount: '', period: 'Monthly', is_active: true, enable_rollover: false, category_id: '' }); }}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                >
                    + Set Budget
                </button>
            </div>

            {showForm && (
                <div className="mb-8 p-6 bg-white shadow rounded-lg border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">{editingBudget ? 'Edit Budget' : 'New Budget'}</h2>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Amount</label>
                            <input 
                                type="number" step="0.01" 
                                className="w-full p-2 border rounded" 
                                value={formData.amount} 
                                onChange={(e) => setFormData({...formData, amount: e.target.value})} 
                                required 
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Period</label>
                            <select 
                                className="w-full p-2 border rounded" 
                                value={formData.period} 
                                onChange={(e) => setFormData({...formData, period: e.target.value})} 
                            >
                                <option value="Weekly">Weekly</option>
                                <option value="Monthly">Monthly</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Category (Optional)</label>
                            <input 
                                type="number" 
                                className="w-full p-2 border rounded" 
                                value={formData.category_id} 
                                onChange={(e) => setFormData({...formData, category_id: e.target.value})} 
                                placeholder="Leave blank for overall"
                            />
                        </div>
                        <div className="flex items-center space-x-2 py-2">
                            <input 
                                type="checkbox" 
                                id="is_active" 
                                checked={formData.is_active} 
                                onChange={(e) => setFormData({...formData, is_active: e.target.checked})} 
                            />
                            <label htmlFor="is_active" className="text-sm font-medium">Active</label>
                        </div>
                        <div className="flex items-center space-x-2 py-2">
                            <input 
                                type="checkbox" 
                                id="enable_rollover" 
                                checked={formData.enable_rollover} 
                                onChange={(e) => setFormData({...formData, enable_rollover: e.target.checked})} 
                            />
                            <label htmlFor="enable_rollover" className="text-sm font-medium">Enable Rollover</label>
                        </div>
                        <div className="flex justify-end space-x-3 items-end">
                            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                {editingBudget ? 'Update' : 'Create'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {loading ? (
                    <p className="col-span-2 text-center text-gray-500">Loading budgets...</p>
                ) : budgets.length === 0 ? (
                    <p className="col-span-2 text-center text-gray-500">No budgets set yet.</p>
                ) : (
                    budgets.map(budget => (
                        <div key={budget.id} className={`p-6 bg-white shadow rounded-lg border-t-4 ${budget.is_active ? 'border-blue-500' : 'border-gray-300'}`}>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-lg font-bold">
                                        {budget.category_id ? `Category ${budget.category_id} Budget` : 'Overall Budget'}
                                    </h3>
                                    <p className="text-sm text-gray-500">{budget.period} Period</p>
                                </div>
                                <div className="flex space-x-2">
                                    <button onClick={() => handleEdit(budget)} className="text-sm text-blue-500 hover:underline">Edit</button>
                                    <button onClick={() => handleDelete(budget.id)} className="text-sm text-red-500 hover:underline">Delete</button>
                                </div>
                            </div>

                            <div className="mb-4">
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-gray-600">Spending: ${budget.current_spending.toFixed(2)}</span>
                                    <span className="font-semibold">Limit: ${budget.effective_limit.toFixed(2)}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-3">
                                    <div 
                                        className={`h-3 rounded-full transition-all duration-500 ${budget.progress_percentage >= 100 ? 'bg-red-500' : budget.progress_percentage >= 80 ? 'bg-yellow-500' : 'bg-blue-500'}`}
                                        style={{ width: `${Math.min(100, budget.progress_percentage)}%` }}
                                    ></div>
                                </div>
                                <p className="text-right text-xs mt-1 font-medium text-gray-500">
                                    {budget.progress_percentage.toFixed(1)}% used
                                </p>
                            </div>

                            <div className="flex justify-between items-center text-xs text-gray-400">
                                <span>Rollover: {budget.enable_rollover ? 'Enabled' : 'Disabled'}</span>
                                <span>Current Rollover: ${budget.rollover_amount.toFixed(2)}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default BudgetPage;
