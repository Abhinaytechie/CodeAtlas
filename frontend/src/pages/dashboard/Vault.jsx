import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Link as LinkIcon, Github, FileText, Trash2, ExternalLink, X } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import api from '../../lib/api';

const Vault = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isAddOpen, setIsAddOpen] = useState(false);

    // Form State
    const [newItem, setNewItem] = useState({
        title: '',
        url: '',
        description: '',
        type: 'link', // link, github
        tags: ''
    });

    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = async () => {
        try {
            const res = await api.get('/vault/items');
            setItems(res.data);
        } catch (error) {
            console.error("Failed to fetch vault items", error);
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async () => {
        if (!newItem.title || !newItem.url) return;

        // Auto-detect type
        let type = 'link';
        if (newItem.url.includes('github.com')) type = 'github';
        if (newItem.url.endsWith('.pdf')) type = 'file';

        try {
            const payload = {
                ...newItem,
                type,
                tags: newItem.tags.split(',').map(t => t.trim()).filter(Boolean)
            };
            await api.post('/vault/items', payload);
            setIsAddOpen(false);
            setNewItem({ title: '', url: '', description: '', type: 'link', tags: '' });
            fetchItems();
        } catch (error) {
            console.error("Failed to add item", error);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Delete this proof item?")) return;
        try {
            await api.delete(`/vault/items/${id}`);
            setItems(items.filter(i => i._id !== id));
        } catch (error) {
            console.error("Failed to delete", error);
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-display font-bold">Proof-of-Work Vault</h1>
                    <p className="text-text-secondary mt-1">
                        Securely store your projects, certificates, and achievements.
                    </p>
                </div>
                <Button onClick={() => setIsAddOpen(true)}>
                    <Plus className="h-5 w-5 mr-2" /> Add Proof
                </Button>
            </div>

            {loading ? (
                <div className="text-center py-12 text-text-secondary">Loading Vault...</div>
            ) : items.length === 0 ? (
                <div className="text-center py-20 bg-surface/30 rounded-xl border border-dashed border-border">
                    <div className="inline-flex p-4 rounded-full bg-surface mb-4">
                        <LinkIcon className="h-8 w-8 text-text-secondary" />
                    </div>
                    <h3 className="text-lg font-bold mb-2">Your Vault is Empty</h3>
                    <p className="text-text-secondary mb-6 max-w-md mx-auto">
                        Start building your portfolio. Add GitHub links, deployed demos, or certificates to track your journey.
                    </p>
                    <Button onClick={() => setIsAddOpen(true)} variant="outline">
                        Add First Item
                    </Button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <AnimatePresence>
                        {items.map((item) => (
                            <motion.div
                                key={item._id}
                                layout
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                            >
                                <Card className="h-full flex flex-col group relative overflow-hidden">
                                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={() => handleDelete(item._id)}
                                            className="p-2 bg-background/80 hover:bg-red-500/10 hover:text-red-500 rounded-full text-text-secondary backdrop-blur-sm transition-colors"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>

                                    <div className="p-6 flex-1">
                                        <div className="flex items-center gap-3 mb-4">
                                            <div className={`p-3 rounded-lg ${item.type === 'github' ? 'bg-white/10 text-white' :
                                                item.type === 'file' ? 'bg-blue-500/10 text-blue-500' :
                                                    'bg-success/10 text-success'
                                                }`}>
                                                {item.type === 'github' ? <Github className="h-6 w-6" /> :
                                                    item.type === 'file' ? <FileText className="h-6 w-6" /> :
                                                        <LinkIcon className="h-6 w-6" />}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h3 className="font-bold truncate">{item.title}</h3>
                                                <p className="text-xs text-text-secondary capitalize">{item.type} • {new Date(item.created_at).toLocaleDateString()}</p>
                                            </div>
                                        </div>

                                        <p className="text-sm text-text-secondary line-clamp-3 mb-4">
                                            {item.description || "No description provided."}
                                        </p>

                                        <div className="flex flex-wrap gap-2">
                                            {item.tags.map(tag => (
                                                <span key={tag} className="px-2 py-1 text-[10px] uppercase font-bold tracking-wider rounded bg-surface border border-border text-text-secondary">
                                                    {tag}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="p-4 bg-surface/50 border-t border-border mt-auto">
                                        <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-xs font-bold text-primary flex items-center justify-center gap-2 hover:underline"
                                        >
                                            View Proof <ExternalLink className="h-3 w-3" />
                                        </a>
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}

            {/* Add Modal Overlay */}
            <AnimatePresence>
                {isAddOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 20 }}
                            className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden"
                        >
                            <div className="p-6 border-b border-border flex justify-between items-center">
                                <h2 className="text-xl font-bold">Add to Vault</h2>
                                <button onClick={() => setIsAddOpen(false)} className="text-text-secondary hover:text-white">
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="p-6 space-y-4">
                                <div>
                                    <label className="text-sm font-medium mb-1 block">Title</label>
                                    <Input
                                        placeholder="e.g. Portfolio Website"
                                        value={newItem.title}
                                        onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label className="text-sm font-medium mb-1 block">URL</label>
                                    <Input
                                        placeholder="https://github.com/username/project"
                                        value={newItem.url}
                                        onChange={(e) => setNewItem({ ...newItem, url: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label className="text-sm font-medium mb-1 block">Description</label>
                                    <textarea
                                        className="w-full bg-background border border-border rounded-lg p-3 text-sm focus:border-primary focus:outline-none resize-none h-24"
                                        placeholder="Brief details about what used..."
                                        value={newItem.description}
                                        onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label className="text-sm font-medium mb-1 block">Tags (comma separated)</label>
                                    <Input
                                        placeholder="React, API, Hackathon"
                                        value={newItem.tags}
                                        onChange={(e) => setNewItem({ ...newItem, tags: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="p-6 bg-surface/30 border-t border-border flex justify-end gap-3">
                                <Button variant="ghost" onClick={() => setIsAddOpen(false)}>Cancel</Button>
                                <Button onClick={handleAdd}>Add Item</Button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Vault;
