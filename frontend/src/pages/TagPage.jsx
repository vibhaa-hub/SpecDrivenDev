import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const TagPage = () => {
    const [tags, setTags] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingTag, setEditingTag] = useState(null);
    const [formData, setFormData] = useState({ name: '' });

    useEffect(() => {
        fetchTags();
    }, []);

    const fetchTags = async () => {
        try {
            const response = await api.get('/tags');
            setTags(response.data);
        } catch (err) {
            alert('Failed to fetch tags');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingTag) {
                await api.patch(`/tags/${editingTag.id}`, formData);
            } else {
                await api.post('/tags', formData);
            }
            setShowForm(false);
            setEditingTag(null);
            setFormData({ name: '' });
            fetchTags();
        } catch (err) {
            alert('Error saving tag: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (tag) => {
        setEditingTag(tag);
        setFormData({ name: tag.name });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this tag?')) return;
        try {
            await api.delete(`/tags/${id}`);
            fetchTags();
        } catch (err) {
            alert('Error deleting tag: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Personal Tags</h1>
                <button 
                    onClick={() => { setShowForm(true); setEditingTag(null); setFormData({ name: '' }); }}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                >
                    + Add Tag
                </button>
            </div>

            {showForm && (
                <div className="mb-8 p-6 bg-white shadow rounded-lg border border-gray-200">
                    <h2 className="text-xl font-bold mb-4">{editingTag ? 'Edit Tag' : 'New Tag'}</h2>
                    <form onSubmit={handleSubmit} className="flex gap-4 items-end">
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-1">Tag Name</label>
                            <input 
                                type="text" 
                                className="w-full p-2 border rounded" 
                                value={formData.name} 
                                onChange={(e) => setFormData({...formData, name: e.target.value})} 
                                required 
                            />
                        </div>
                        <div className="flex space-x-3">
                            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                {editingTag ? 'Update' : 'Create'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="flex flex-wrap gap-3">
                {tags.map(tag => (
                    <div key={tag.id} className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full flex items-center space-x-3 border border-blue-200 group">
                        <span className="font-medium">{tag.name}</span>
                        <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition">
                            <button onClick={() => handleEdit(tag)} className="text-xs text-blue-500 hover:text-blue-700 font-bold">Edit</button>
                            <button onClick={() => handleDelete(tag.id)} className="text-xs text-red-500 hover:text-red-700 font-bold">Delete</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TagPage;
