import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Calendar, ChevronRight, Star } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const RoadmapList = () => {
    const [roadmaps, setRoadmaps] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRoadmaps = async () => {
            try {
                const res = await api.get('/roadmap/');
                setRoadmaps(res.data);
            } catch (error) {
                console.error("Failed to fetch roadmaps");
            } finally {
                setLoading(false);
            }
        };
        fetchRoadmaps();
    }, []);

    const toggleBookmark = async (id, currentStatus) => {
        try {
            await api.put(`/roadmap/${id}/bookmark`);
            setRoadmaps(prev => prev.map(r =>
                r.id === id ? { ...r, is_bookmarked: !currentStatus } : r
            ));
        } catch (e) {
            console.error("Failed to toggle bookmark");
        }
    };

    if (loading) return <div className="text-center py-20 text-text-secondary">Loading roadmaps...</div>;

    return (
        <div className="max-w-5xl mx-auto space-y-8 pb-12">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-display font-bold">Your Roadmaps</h1>
                    <p className="text-text-secondary mt-1">
                        History of all your generated learning paths.
                    </p>
                </div>
                <Link to="/dashboard/roadmap?new=true">
                    <Button>Create New +</Button>
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {roadmaps.length > 0 ? roadmaps.map((map) => (
                    <Card key={map.id} className="p-6 hover:border-primary/50 transition-colors group relative">
                        <div className="absolute top-4 right-4 z-10">
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    toggleBookmark(map.id, map.is_bookmarked);
                                }}
                                className={`p-1.5 rounded-full transition-colors ${map.is_bookmarked ? 'text-yellow-400 bg-yellow-400/10' : 'text-text-secondary hover:text-text-primary bg-surface border border-border'}`}
                                title={map.is_bookmarked ? "Bookmarked (Saved)" : "Not Bookmarked (Removed on Signout)"}
                            >
                                <Star className={`h-4 w-4 ${map.is_bookmarked ? 'fill-current' : ''}`} />
                            </button>
                        </div>

                        <Link to={`/dashboard/roadmap?id=${map.id}`} className="block h-full">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                    <Layers className="h-5 w-5" />
                                </div>
                                <div>
                                    <h3 className="font-bold line-clamp-1 group-hover:text-primary transition-colors">{map.title}</h3>
                                    <span className="text-xs text-text-secondary px-2 py-0.5 rounded-full border border-border bg-surface">
                                        {map.role}
                                    </span>
                                </div>
                            </div>

                            <div className="space-y-2 text-sm text-text-secondary">
                                <div className="flex items-center gap-2">
                                    <Calendar className="h-4 w-4" />
                                    <span>{map.days} Day Plan</span>
                                </div>
                                <div className="text-xs opacity-70">
                                    Created {new Date(map.created_at).toLocaleDateString()}
                                </div>
                            </div>

                            <div className="mt-6 pt-4 border-t border-border flex justify-between items-center text-primary text-sm font-medium">
                                <span>View Roadmap</span>
                                <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </Link>
                    </Card>
                )) : (
                    <div className="col-span-full text-center py-20 border border-dashed border-border rounded-xl">
                        <p className="text-text-secondary mb-4">You haven't generated any roadmaps yet.</p>
                        <Link to="/dashboard/roadmap?new=true">
                            <Button>Generate Your First Plan</Button>
                        </Link>
                    </div>
                )}
            </div>

            <div className="bg-surface/30 p-4 rounded-lg border border-border text-xs text-text-secondary flex items-start gap-3">
                <div className="mt-0.5"><div className="h-2 w-2 rounded-full bg-yellow-500" /></div>
                <p>
                    <strong>Note:</strong> Roadmaps that are NOT bookmarked (starred) will be automatically deleted when you sign out to keep your dashboard clean. Bookmark the ones you want to keep forever.
                </p>
            </div>
        </div>
    );
};

export default RoadmapList;

