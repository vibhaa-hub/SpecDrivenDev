import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const CategoryPage = () => {
    const [categories, setCategories] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingCategory, setEditingCategory] = useState(null);
    const [formData, setFormData] = useState({ name: '', icon: '', color: '#000000', type: 'Expense' });

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await api.get('/categories');
            setCategories(response.data);
        } catch (err) {
            alert('Failed to fetch categories');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingCategory) {
                await api.patch(`/categories/${editingCategory.id}`, formData);
            } else {
                await api.post('/categories', formData);
            }
            setShowForm(false);
            setEditingCategory(null);
            setFormData({ name: '', icon: '', color: '#000000', type: 'Expense' });
            fetchCategories();
        } catch (err) {
            alert('Error saving category: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (category) => {
        setEditingCategory(category);
        setFormData({ name: category.name, icon: category.icon, color: category.color, type: category.type });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this category?')) return;
        try {
            await api.delete(`/categories/${id}`);
            fetchCategories();
        } catch (err) {
            alert('Error deleting category: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Categories</h1>
                <button
                    onClick={() => { setShowForm(true); setEditingCategory(null); setFormData({ name: '', icon: '', color: '#000000', type: 'Expense' }); }}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                >
                    + Add Category
                </button>
            </div>

            {showForm && (
                <div className="mb-8 p-6 bg-white shadow rounded-lg border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">{editingCategory ? 'Edit Category' : 'New Category'}</h2>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                        <div>
                            <label className="block text-sm font-medium mb-1">Name</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.name}
                                onChange={(e) => setFormData({...formData, name: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Icon (Emoji/Text)</label>
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
                        <div>
                            <label className="block text-sm font-medium mb-1">Type</label>
                            <select
                                className="w-full p-2 border rounded"
                                value={formData.type}
                                onChange={(e) => setFormData({...formData, type: e.target.value})}
                            >
                                <option value="Expense">Expense</option>
                                <option value="Income">Income</option>
                                <option value="Both">Both</option>
                            </select>
                        </div>
                        <div className="md:col-span-4 flex justify-end space-x-3">
                            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                {editingCategory ? 'Update' : 'Create'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {categories.map(cat => (
                    <div key={cat.id} className="p-4 bg-white shadow rounded-lg flex items-center justify-between border-l-4" style={{ borderColor: cat.color }}>
                        <div className="flex items-center space-x-3">
                            <span className="text-2xl">{cat.icon || '📁'}</span>
                            <div>
                                <p className="font-bold">{cat.name}</p>
                                <p className="text-xs text-gray-500">{cat.type}</p>
                            </div>
                        </div>
                        <div className="flex space-x-2">
                            <button onClick={() => handleEdit(cat)} className="p-1 text-blue-500 hover:bg-blue-50 rounded">Edit</button>
                            {cat.user_id !== null && (
                                <button onClick={() => handleDelete(cat.id)} className="p-1 text-red-500 hover:bg-red-50 rounded">Delete</button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CategoryPage;
