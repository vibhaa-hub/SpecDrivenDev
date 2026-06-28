import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const SavingsGoalPage = () => {
    const [goals, setGoals] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingGoal, setEditingGoal] = useState(null);
    const [selectedGoal, setSelectedGoal] = useState(null);
    const [loading, setLoading] = useState(true);

    const [formData, setFormData] = useState({
        name: '',
        target_amount: '',
        target_date: '',
        description: '',
        icon: '💰',
        color: '#3b82f6'
    });

    useEffect(() => {
        fetchGoals();
    }, []);

    const fetchGoals = async () => {
        setLoading(true);
        try {
            const response = await api.get('/goals');
            setGoals(response.data);
        } catch (err) {
            alert('Failed to fetch goals');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                target_amount: parseFloat(formData.target_amount),
            };
            if (editingGoal) {
                await api.patch(`/goals/${editingGoal.id}`, payload);
            } else {
                await api.post('/goals', payload);
            }
            setShowForm(false);
            setEditingGoal(null);
            setFormData({ name: '', target_amount: '', target_date: '', description: '', icon: '💰', color: '#3b82f6' });
            fetchGoals();
        } catch (err) {
            alert('Error saving goal: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (goal) => {
        setEditingGoal(goal);
        setFormData({
            name: goal.name,
            target_amount: goal.target_amount,
            target_date: goal.target_date ? goal.target_date.split('T')[0] : '',
            description: goal.description,
            icon: goal.icon,
            color: goal.color
        });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this goal?')) return;
        try {
            await api.delete(`/goals/${id}`);
            fetchGoals();
            if (selectedGoal?.id === id) setSelectedGoal(null);
        } catch (err) {
            alert('Error deleting goal: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleContribute = async (amount) => {
        try {
            await api.post(`/goals/${selectedGoal.id}/contribute`, {
                amount: parseFloat(amount),
            });
            fetchGoals();
        } catch (err) {
            alert('Error contributing to goal: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Savings Goals</h1>
                <button
                    onClick={() => { setShowForm(true); setEditingGoal(null); setFormData({ name: '', target_amount: '', target_date: '', description: '', icon: '💰', color: '#3b82f6' }); }}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                >
                    + New Goal
                </button>
            </div>

            {showForm && (
                <div className="mb-8 p-6 bg-white shadow rounded-lg border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">{editingGoal ? 'Edit Goal' : 'New Goal'}</h2>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Goal Name</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.name}
                                onChange={(e) => setFormData({...formData, name: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Target Amount</label>
                            <input
                                type="number" step="0.01"
                                className="w-full p-2 border rounded"
                                value={formData.target_amount}
                                onChange={(e) => setFormData({...formData, target_amount: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Target Date</label>
                            <input
                                type="date"
                                className="w-full p-2 border rounded"
                                value={formData.target_date}
                                onChange={(e) => setFormData({...formData, target_date: e.target.value})}
                                required
                            />
                        </div>
                        <div className="md:col-span-3">
                            <label className="block text-sm font-medium mb-1">Description</label>
                            <textarea
                                className="w-full p-2 border rounded"
                                value={formData.description}
                                onChange={(e) => setFormData({...formData, description: e.target.value})}
                                rows="2"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Icon</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.icon}
                                onChange={(e) => setFormData({...formData, icon: e.target.value})}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Color</label>
                            <input
                                type="color"
                                className="w-full h-10 p-1 border rounded"
                                value={formData.color}
                                onChange={(e) => setFormData({...formData, color: e.target.value})}
                            />
                        </div>
                        <div className="md:col-span-3 flex justify-end space-x-3">
                            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                {editingGoal ? 'Update' : 'Create'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1 space-y-4">
                    <h2 className="text-xl font-semibold mb-4">My Goals</h2>
                    {loading ? (
                        <p className="text-gray-500">Loading goals...</p>
                    ) : goals.length === 0 ? (
                        <p className="text-gray-500">No goals created yet.</p>
                    ) : (
                        goals.map(goal => (
                            <div
                                key={goal.id}
                                onClick={() => setSelectedGoal(goal)}
                                className={`p-4 bg-white shadow rounded-lg cursor-pointer transition-all border-l-4 ${selectedGoal?.id === goal.id ? 'border-blue-600 ring-2 ring-blue-100' : 'border-gray-200 hover:border-blue-300'}`}
                                style={{ borderLeftColor: goal.color }}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xl">{goal.icon}</span>
                                        <span className="font-bold">{goal.name}</span>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${goal.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                                        {goal.status}
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                                    <div
                                        className="bg-blue-500 h-2 rounded-full transition-all"
                                        style={{ width: `${goal.progress_percentage}%` }}
                                    ></div>
                                </div>
                                <div className="flex justify-between text-xs text-gray-500">
                                    <span>${goal.current_amount.toFixed(2)} / ${goal.target_amount.toFixed(2)}</span>
                                    <span>{goal.progress_percentage.toFixed(1)}%</span>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                <div className="lg:col-span-2">
                    {selectedGoal ? (
                        <div className="bg-white p-6 shadow rounded-lg border border-gray-200">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <div className="flex items-center space-x-3 mb-2">
                                        <span className="text-4xl">{selectedGoal.icon}</span>
                                        <h2 className="text-2xl font-bold">{selectedGoal.name}</h2>
                                    </div>
                                    <p className="text-gray-600">{selectedGoal.description}</p>
                                    <p className="text-sm text-gray-400 mt-1">Target Date: {selectedGoal.target_date}</p>
                                </div>
                                <div className="flex space-x-2">
                                    <button onClick={() => handleEdit(selectedGoal)} className="p-2 text-blue-500 hover:bg-blue-50 rounded">Edit</button>
                                    <button onClick={() => handleDelete(selectedGoal.id)} className="p-2 text-red-500 hover:bg-red-50 rounded">Delete</button>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                                <div className="p-4 bg-gray-50 rounded-lg text-center">
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Current</p>
                                    <p className="text-xl font-bold">${selectedGoal.current_amount.toFixed(2)}</p>
                                </div>
                                <div className="p-4 bg-gray-50 rounded-lg text-center">
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Remaining</p>
                                    <p className="text-xl font-bold text-red-500">${selectedGoal.remaining_amount.toFixed(2)}</p>
                                </div>
                                <div className="p-4 bg-gray-50 rounded-lg text-center">
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Progress</p>
                                    <p className="text-xl font-bold text-blue-600">{selectedGoal.progress_percentage.toFixed(1)}%</p>
                                </div>
                            </div>

                            {selectedGoal.status !== 'COMPLETED' && (
                                <div className="mb-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
                                    <h3 className="text-sm font-bold text-blue-800 mb-3">Quick Contribute</h3>
                                    <form onSubmit={(e) => {
                                        e.preventDefault();
                                        handleContribute(e.target.amount.value);
                                    }} className="flex space-x-2">
                                        <input
                                            type="number" step="0.01"
                                            name="amount"
                                            className="flex-1 p-2 border rounded"
                                            placeholder="Enter amount"
                                            required
                                        />
                                        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                            Contribute
                                        </button>
                                    </form>
                                </div>
                            )}

                            <div>
                                <h3 className="text-lg font-bold mb-4">Contribution Timeline</h3>
                                <div className="space-y-3">
                                    <p className="text-sm text-gray-500 italic">Contributions are listed as transactions in the 'Savings' category linked to this goal.</p>
                                    <div className="text-center py-8 text-gray-400 border-2 border-dashed rounded-lg">
                                        Timeline view: List of linked transactions.
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg border-2 border-dashed p-12 text-center">
                            Select a goal from the list to see detailed progress and contribute.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SavingsGoalPage;
