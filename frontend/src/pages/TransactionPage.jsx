import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const TransactionPage = () => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingTransaction, setEditingTransaction] = useState(null);

    const [filters, setFilters] = useState({
        start_date: '',
        end_date: '',
        category_id: '',
        skip: 0,
        limit: 20
    });

    const [formData, setFormData] = useState({
        amount: '',
        date: new Date().toISOString().split('T')[0],
        category_id: '',
        transaction_type: 'Expense',
        payment_method: 'Cash',
        description: '',
        merchant_name: '',
        notes: '',
        goal_id: '',
        tags: [],
        is_recurring: false,
        recurrence_pattern: 'Monthly'
    });

    const [receiptFile, setReceiptFile] = useState(null);

    useEffect(() => {
        fetchTransactions();
    }, [filters]);

    const fetchTransactions = async () => {
        setLoading(true);
        try {
            const params = {
                start_date: filters.start_date || undefined,
                end_date: filters.end_date || undefined,
                category_id: filters.category_id || undefined,
                skip: filters.skip,
                limit: filters.limit
            };
            const response = await api.get('/transactions', { params });
            setTransactions(response.data);
        } catch (err) {
            alert('Failed to fetch transactions');
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
                tags: formData.tags || []
            };

            let txId;
            if (editingTransaction) {
                const response = await api.patch(`/transactions/${editingTransaction.id}`, payload);
                txId = response.data.id;
            } else {
                const response = await api.post('/transactions', payload);
                txId = response.data.id;
            }

            if (receiptFile) {
                const fd = new FormData();
                fd.append('file', receiptFile);
                await api.post(`/transactions/${txId}/receipt`, fd, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            }

            if (formData.is_recurring) {
                const recurringPayload = {
                    amount: parseFloat(formData.amount),
                    description: formData.description,
                    transaction_type: formData.transaction_type,
                    payment_method: formData.payment_method,
                    merchant_name: formData.merchant_name,
                    notes: formData.notes,
                    recurrence_pattern: formData.recurrence_pattern,
                    start_date: formData.date,
                    category_id: parseInt(formData.category_id),
                    goal_id: formData.goal_id ? parseInt(formData.goal_id) : null
                };
                await api.post('/recurring', recurringPayload);
            }

            setShowForm(false);
            setEditingTransaction(null);
            setFormData({
                amount: '',
                date: new Date().toISOString().split('T')[0],
                category_id: '',
                transaction_type: 'Expense',
                payment_method: 'Cash',
                description: '',
                merchant_name: '',
                notes: '',
                goal_id: '',
                tags: [],
                is_recurring: false,
                recurrence_pattern: 'Monthly'
            });
            setReceiptFile(null);
            fetchTransactions();
        } catch (err) {
            alert('Error saving transaction: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (tx) => {
        setEditingTransaction(tx);
        setFormData({
            amount: tx.amount,
            date: tx.date.split('T')[0],
            category_id: tx.category_id,
            transaction_type: tx.transaction_type,
            payment_method: tx.payment_method,
            description: tx.description,
            merchant_name: tx.merchant_name,
            notes: tx.notes,
            goal_id: tx.goal_id,
            tags: tx.tags?.map(t => t.id) || [],
            is_recurring: false,
            recurrence_pattern: 'Monthly'
        });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this transaction?')) return;
        try {
            await api.delete(`/transactions/${id}`);
            fetchTransactions();
        } catch (err) {
            alert('Error deleting transaction: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Transactions</h1>
                <button
                    onClick={() => { setShowForm(true); setEditingTransaction(null); setFormData({
                        amount: '',
                        date: new Date().toISOString().split('T')[0],
                        category_id: '',
                        transaction_type: 'Expense',
                        payment_method: 'Cash',
                        description: '',
                        merchant_name: '',
                        notes: '',
                        goal_id: '',
                        tags: [],
                        is_recurring: false,
                        recurrence_pattern: 'Monthly'
                    }); }}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                >
                    + Add Transaction
                </button>
            </div>

            {showForm && (
                <div className="mb-8 p-6 bg-white shadow rounded-lg border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">{editingTransaction ? 'Edit Transaction' : 'New Transaction'}</h2>
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
                            <label className="block text-sm font-medium mb-1">Date</label>
                            <input
                                type="date"
                                className="w-full p-2 border rounded"
                                value={formData.date}
                                onChange={(e) => setFormData({...formData, date: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Category</label>
                            <input
                                type="number"
                                className="w-full p-2 border rounded"
                                value={formData.category_id}
                                onChange={(e) => setFormData({...formData, category_id: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Type</label>
                            <select
                                className="w-full p-2 border rounded"
                                value={formData.transaction_type}
                                onChange={(e) => setFormData({...formData, transaction_type: e.target.value})}
                            >
                                <option value="Expense">Expense</option>
                                <option value="Income">Income</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Payment Method</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.payment_method}
                                onChange={(e) => setFormData({...formData, payment_method: e.target.value})}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Merchant</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.merchant_name}
                                onChange={(e) => setFormData({...formData, merchant_name: e.target.value})}
                            />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium mb-1">Description</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.description}
                                onChange={(e) => setFormData({...formData, description: e.target.value})}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Notes</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.notes}
                                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Goal ID (Optional)</label>
                            <input
                                type="number"
                                className="w-full p-2 border rounded"
                                value={formData.goal_id}
                                onChange={(e) => setFormData({...formData, goal_id: e.target.value})}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Receipt</label>
                            <input
                                type="file"
                                className="w-full p-1 border rounded"
                                onChange={(e) => setReceiptFile(e.target.files[0])}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Tags (Comma separated)</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.tags.join(',')}
                                onChange={(e) => setFormData({...formData, tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)})}
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="is_recurring"
                                checked={formData.is_recurring}
                                onChange={(e) => setFormData({...formData, is_recurring: e.target.checked})}
                            />
                            <label htmlFor="is_recurring" className="text-sm font-medium">Recurring</label>
                        </div>
                        {formData.is_recurring && (
                            <div>
                                <label className="block text-sm font-medium mb-1">Pattern</label>
                                <select
                                    className="w-full p-2 border rounded"
                                    value={formData.recurrence_pattern}
                                    onChange={(e) => setFormData({...formData, recurrence_pattern: e.target.value})}
                                >
                                    <option value="Daily">Daily</option>
                                    <option value="Weekly">Weekly</option>
                                    <option value="Monthly">Monthly</option>
                                    <option value="Yearly">Yearly</option>
                                </select>
                            </div>
                        )}
                        <div className="md:col-span-3 flex justify-end space-x-3">
                            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                {editingTransaction ? 'Update' : 'Create'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="mb-6 p-4 bg-white shadow rounded-lg border border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label className="block text-sm font-medium mb-1">Start Date</label>
                        <input
                            type="date"
                            className="w-full p-2 border rounded"
                            value={filters.start_date}
                            onChange={(e) => setFilters({...filters, start_date: e.target.value, skip: 0})}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">End Date</label>
                        <input
                            type="date"
                            className="w-full p-2 border rounded"
                            value={filters.end_date}
                            onChange={(e) => setFilters({...filters, end_date: e.target.value, skip: 0})}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">Category</label>
                        <input
                            type="number"
                            className="w-full p-2 border rounded"
                            value={filters.category_id}
                            onChange={(e) => setFilters({...filters, category_id: e.target.value, skip: 0})}
                        />
                    </div>
                    <div className="flex items-end space-x-2">
                        <button
                            onClick={() => setFilters({start_date: '', end_date: '', category_id: '', skip: 0, limit: 20})}
                            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-gray-50 text-gray-600 text-sm uppercase font-semibold">
                        <tr>
                            <th className="px-6 py-3 border-b">Date</th>
                            <th className="px-6 py-3 border-b">Merchant/Desc</th>
                            <th className="px-6 py-3 border-b">Category</th>
                            <th className="px-6 py-3 border-b">Amount</th>
                            <th className="px-6 py-3 border-b">Method</th>
                            <th className="px-6 py-3 border-b text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-10 text-center text-gray-500">Loading transactions...</td>
                            </tr>
                        ) : transactions.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-10 text-center text-gray-500">No transactions found.</td>
                            </tr>
                        ) : (
                            transactions.map(tx => (
                                <tr key={tx.id} className="border-b hover:bg-gray-50 transition">
                                    <td className="px-6 py-4 text-sm">{tx.date.split('T')[0]}</td>
                                    <td className="px-6 py-4">
                                        <div className="font-medium">{tx.merchant_name || tx.description || 'N/A'}</div>
                                        <div className="text-xs text-gray-400">{tx.notes}</div>
                                    </td>
                                    <td className="px-6 py-4 text-sm">{tx.category_id}</td>
                                    <td className={`px-6 py-4 font-bold ${tx.transaction_type === 'Income' ? 'text-green-600' : 'text-red-600'}`}>
                                        {tx.transaction_type === 'Income' ? '+' : '-'}${tx.amount.toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{tx.payment_method}</td>
                                    <td className="px-6 py-4 text-right space-x-2">
                                        <button onClick={() => handleEdit(tx)} className="text-blue-500 hover:underline text-sm">Edit</button>
                                        <button onClick={() => handleDelete(tx.id)} className="text-red-500 hover:underline text-sm">Delete</button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
                <div className="px-6 py-4 bg-gray-50 border-t flex justify-between items-center">
                    <div className="text-sm text-gray-500">
                        Showing {filters.skip + 1} - {Math.min(filters.skip + filters.limit, transactions.length)} of {transactions.length}
                    </div>
                    <div className="flex space-x-2">
                        <button
                            disabled={filters.skip === 0}
                            onClick={() => setFilters({...filters, skip: Math.max(0, filters.skip - filters.limit)})}
                            className="px-4 py-2 bg-white border rounded disabled:opacity-50"
                        >
                            Previous
                        </button>
                        <button
                            disabled={transactions.length < filters.skip + filters.limit}
                            onClick={() => setFilters({...filters, skip: filters.skip + filters.limit})}
                            className="px-4 py-2 bg-white border rounded disabled:opacity-50"
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TransactionPage;
