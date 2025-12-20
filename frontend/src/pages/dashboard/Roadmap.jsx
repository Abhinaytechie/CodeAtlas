import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Layers, Calendar, AlertCircle, CheckCircle2, ChevronRight, Lock, PlayCircle, Map } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import api from '../../lib/api';

const Roadmap = () => {
    const [searchParams] = useSearchParams();
    const roadmapId = searchParams.get('id');
    const isNew = searchParams.get('new');

    const [step, setStep] = useState(0); // 0: Initial Load, 1: Form, 2: Result
    const [loading, setLoading] = useState(false);

    // Data Stats
    const [roadmap, setRoadmap] = useState(null);
    const [solvedIds, setSolvedIds] = useState([]);
    const [streak, setStreak] = useState(0);

    // Form Stats
    const [role, setRole] = useState('Backend');
    const [days, setDays] = useState(45);
    const [weaknesses, setWeaknesses] = useState('');

    // Derived State
    const allSkills = roadmap?.levels?.flatMap(l => l.tracks.flatMap(t => t.skills)) || [];
    const allSkillsCount = allSkills.length;
    const allSkillIds = allSkills.map(s => s.id);

    useEffect(() => {
        const fetchRoadmapAndStats = async () => {
            setLoading(true);
            try {
                if (isNew) {
                    setStep(1); // Force new creation
                } else if (roadmapId) {
                    // Fetch Specific Roadmap
                    try {
                        const res = await api.get(`/roadmap/${roadmapId}`);
                        if (res.data) {
                            setRoadmap(res.data);
                            setStep(2);
                        }
                    } catch (e) {
                        console.error("Roadmap ID not found");
                        setStep(1);
                    }
                } else {
                    // 1. Try to fetch the latest saved roadmap (default behavior)
                    try {
                        const res = await api.get('/roadmap/latest');
                        if (res.data) {
                            setRoadmap(res.data);
                            setStep(2); // Show result directly
                        }
                    } catch (e) {
                        setStep(1);
                    }
                }

                // 2. Fetch User Stats (Solved Problems)
                const statsRes = await api.get('/dashboard/stats');
                const solved = statsRes.data.solved_problems || [];
                setSolvedIds(solved);
                setInitialSolvedIds(solved); // Snapshot for comparison
                setStreak(statsRes.data.streak_days || 0);
            } catch (err) {
                console.error("Failed to fetch data", err);
                setStep(1);
            } finally {
                setLoading(false);
            }
        };
        fetchRoadmapAndStats();
    }, [roadmapId, isNew]);

    // State management for manual save
    const [initialSolvedIds, setInitialSolvedIds] = useState([]);
    const [isSaving, setIsSaving] = useState(false);

    // Derived state for unsaved changes (more robust than flag)
    const hasUnsavedChanges = JSON.stringify(solvedIds.sort()) !== JSON.stringify(initialSolvedIds.sort());

    const generateRoadmap = async () => {
        setLoading(true);
        try {
            const apiKey = localStorage.getItem('groq_api_key');
            console.log(apiKey)
            const res = await api.post('/roadmap/generate', {
                target_role: role,
                days_remaining: parseInt(days),
                weak_patterns: weaknesses.split(',').map(s => s.trim()).filter(Boolean),
                force_regenerate: true
            }, {
                headers: apiKey ? { 'x-groq-api-key': apiKey } : {}
            });
            setRoadmap(res.data);
            setStep(2);
        } catch (error) {
            console.error("Failed to generate roadmap", error);
        } finally {
            setLoading(false);
        }
    };

    const toggleProblem = (problemId) => {
        // Only update local state
        const isSolved = solvedIds.includes(problemId);
        setSolvedIds(prev => isSolved ? prev.filter(id => id !== problemId) : [...prev, problemId]);
    };

    const saveProgress = async () => {
        setIsSaving(true);
        try {
            await api.post('/dashboard/progress', { solved_ids: solvedIds });
            setInitialSolvedIds([...solvedIds]); // Update snapshot

            // Refresh stats to get updated streak
            const statsRes = await api.get('/dashboard/stats');
            setStreak(statsRes.data.streak_days || 0);
        } catch (err) {
            console.error("Failed to save progress", err);
            alert("Failed to save progress. Please try again.");
        } finally {
            setIsSaving(false);
        }
    };

    if (step === 0) {
        return (
            <div className="max-w-2xl mx-auto py-10 text-center">
                <p className="text-lg text-text-secondary">Loading your roadmap...</p>
            </div>
        );
    }

    if (step === 1) {
        return (
            <div className="max-w-3xl mx-auto py-12">
                <div className="mb-10 text-center space-y-4">
                    <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-full mb-4">
                        <Map className="h-8 w-8 text-primary" />
                    </div>
                    <h1 className="text-4xl font-display font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                        Design Your Career Path
                    </h1>
                    <p className="text-text-secondary text-lg max-w-xl mx-auto">
                        Our AI analyzes thousands of job descriptions to build the perfect curriculum for you.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {/* Left Col: Target Role */}
                    <Card className="p-1 hover:border-primary/50 transition-colors">
                        <div className="p-6 h-full flex flex-col">
                            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span>
                                Choose Your Target
                            </h3>
                            <div className="space-y-3 flex-1">
                                {['Backend Developer', 'Frontend Engineer', 'Full Stack', 'AI/ML Engineer', 'Data Scientist'].map((r) => (
                                    <button
                                        key={r}
                                        onClick={() => setRole(r)}
                                        className={`w-full text-left px-4 py-3 rounded-xl border transition-all flex items-center justify-between group ${role === r
                                            ? 'bg-primary/10 border-primary text-primary font-medium'
                                            : 'bg-surface/50 border-border hover:border-primary/30 hover:bg-surface'
                                            }`}
                                    >
                                        {r}
                                        {role === r && <CheckCircle2 className="h-4 w-4" />}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </Card>

                    {/* Right Col: Timeline & Weaknesses */}
                    <div className="space-y-6">
                        <Card className="p-6">
                            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span>
                                Set Your Timeline
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-text-secondary block mb-2">Days available for preparation</label>
                                    <div className="flex items-center gap-4">
                                        <div className="relative flex-1">
                                            <Calendar className="absolute left-3 top-3 h-5 w-5 text-text-secondary" />
                                            <Input
                                                type="number"
                                                className="pl-10 text-lg font-medium"
                                                value={days}
                                                onChange={(e) => setDays(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                    <input
                                        type="range"
                                        min="15"
                                        max="180"
                                        value={days}
                                        onChange={(e) => setDays(e.target.value)}
                                        className="w-full mt-4 accent-primary"
                                    />
                                    <div className="flex justify-between text-xs text-text-secondary mt-1">
                                        <span>Sprint (15d)</span>
                                        <span>Marathon (6mo)</span>
                                    </div>
                                </div>
                            </div>
                        </Card>

                        <Card className="p-6">
                            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">3</span>
                                Focus Areas
                            </h3>
                            <div>
                                <label className="text-sm text-text-secondary block mb-2">Topics you struggle with (Optional)</label>
                                <textarea
                                    className="w-full bg-surface border border-border rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-text-secondary/50"
                                    placeholder="e.g. Dynamic Programming, System Design, graph algorithms..."
                                    rows={3}
                                    value={weaknesses}
                                    onChange={(e) => setWeaknesses(e.target.value)}
                                />
                            </div>
                        </Card>
                    </div>
                </div>

                <div className="mt-10 flex justify-center">
                    <Button
                        size="lg"
                        className="w-full md:w-auto md:min-w-[300px] text-lg h-14 shadow-xl shadow-primary/20 hover:shadow-primary/30 transition-all font-display"
                        onClick={generateRoadmap}
                        disabled={loading}
                    >
                        {loading ? (
                            <span className="flex items-center gap-2">
                                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Analyzing Career Path...
                            </span>
                        ) : (
                            <span className="flex items-center gap-2">
                                Generate Personalized Roadmap <ChevronRight className="h-5 w-5" />
                            </span>
                        )}
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <div className="flex items-center justify-between sticky top-0 bg-background/95 backdrop-blur z-10 py-4 border-b border-border/50">
                <div>
                    <h1 className="text-2xl font-display font-bold flex items-center gap-3">
                        {roadmap?.title}
                        <button
                            onClick={async () => {
                                try {
                                    const newStatus = !roadmap.is_bookmarked;
                                    setRoadmap(prev => ({ ...prev, is_bookmarked: newStatus })); // Optimistic update
                                    await api.put(`/roadmap/${roadmap._id}/bookmark`);
                                } catch (e) {
                                    console.error("Bookmark failed");
                                    setRoadmap(prev => ({ ...prev, is_bookmarked: !prev.is_bookmarked })); // Revert
                                }
                            }}
                            className={`p-1.5 rounded-full transition-colors ${roadmap?.is_bookmarked ? 'text-yellow-400 bg-yellow-400/10' : 'text-text-secondary hover:text-text-primary'}`}
                            title={roadmap?.is_bookmarked ? "Bookmarked" : "Bookmark this roadmap"}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill={roadmap?.is_bookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-star"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
                        </button>
                    </h1>
                    <div className="flex gap-4 items-center">
                        <p className="text-text-secondary text-sm flex items-center gap-2">
                            {roadmap?.duration_days} Day Plan
                        </p>
                        {hasUnsavedChanges && (
                            <span className="text-xs text-warning animate-pulse">
                                ● Unsaved Changes
                            </span>
                        )}
                        {roadmap?.is_bookmarked && (
                            <span className="text-xs text-yellow-500 font-medium">
                                ★ Saved
                            </span>
                        )}
                    </div>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={() => setStep(1)}
                        className="hidden sm:flex"
                    >
                        New Roadmap
                    </Button>
                    <Button
                        onClick={saveProgress}
                        disabled={!hasUnsavedChanges || isSaving}
                        className={hasUnsavedChanges ? 'bg-primary text-background' : ''}
                    >
                        {isSaving ? 'Saving...' : 'Save Progress'}
                    </Button>
                </div>
            </div>

            {/* Progress Overview Card */}
            < Card className="p-6 bg-surface/50 border-primary/20" >
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <PlayCircle className="h-5 w-5 text-primary" /> Current Progress
                        </h2>
                        <p className="text-text-secondary text-sm">You are tracking this roadmap.</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-bold text-primary">
                            {solvedIds.filter(id => allSkillIds.includes(id)).length} / {allSkillsCount}
                        </div>
                        <div className="text-xs text-text-secondary">Skills Mastered</div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="h-3 bg-surface rounded-full overflow-hidden border border-border">
                    <motion.div
                        className="h-full bg-primary"
                        initial={{ width: 0 }}
                        animate={{ width: `${(solvedIds.filter(id => allSkillIds.includes(id)).length / Math.max(allSkillsCount, 1)) * 100}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>

                <div className="mt-4 flex gap-4 text-sm">
                    <div className="flex items-center gap-2 text-text-secondary">
                        <div className="h-2 w-2 rounded-full bg-success" />
                        <span>{(solvedIds.filter(id => allSkillIds.includes(id)).length / Math.max(allSkillsCount, 1) * 100).toFixed(0)}% Complete</span>
                    </div>
                    <div className="flex items-center gap-2 text-warning font-medium">
                        <span className="flex items-center gap-1"><div className="h-2 w-2 rounded-full bg-warning animate-pulse" /> {streak} Day Streak</span>
                    </div>
                </div>
            </Card >

            <div className="space-y-6">
                <div className="space-y-6">
                    {roadmap?.levels?.map((level, i) => (
                        <div key={i} className="space-y-4">
                            {/* Level Header directly in the list flow */}
                            <div className="flex items-center gap-3 mt-8 mb-4">
                                <div className="h-8 w-8 rounded-full bg-primary text-background font-bold flex items-center justify-center">
                                    {i + 1}
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold font-display">{level.name}</h3>
                                    <p className="text-sm text-text-secondary">{level.description}</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 gap-4">
                                {level.tracks.map((track, trackIdx) => (
                                    <Card key={trackIdx} className="overflow-hidden border-border/60">
                                        <div className="bg-surface/50 px-4 py-3 border-b border-border font-medium text-primary flex items-center justify-between">
                                            <span>{track.category}</span>
                                            <span className="text-xs text-text-secondary bg-background px-2 py-1 rounded border border-border">
                                                {track.skills.filter(s => solvedIds.includes(s.id)).length} / {track.skills.length}
                                            </span>
                                        </div>
                                        <div className="divide-y divide-border">
                                            {track.skills.map((skill, skillIdx) => (
                                                <div key={skillIdx} className="p-4 flex items-start gap-4 hover:bg-surface/30 transition-colors group">
                                                    <button
                                                        onClick={() => toggleProblem(skill.id)}
                                                        className="mt-1 text-text-secondary hover:text-primary transition-colors focus:outline-none flex-shrink-0"
                                                    >
                                                        {solvedIds.includes(skill.id) ? (
                                                            <CheckCircle2 className="h-5 w-5 text-success" />
                                                        ) : (
                                                            <div className="h-5 w-5 rounded-full border-2 border-border hover:border-primary transition-colors" />
                                                        )}
                                                    </button>
                                                    <div className="flex-1">
                                                        <div className={`font-medium transition-colors ${solvedIds.includes(skill.id) ? 'text-text-secondary line-through' : 'group-hover:text-primary'}`}>
                                                            {skill.name}
                                                        </div>
                                                        <p className="text-sm text-text-secondary mt-1 max-w-2xl leading-relaxed">
                                                            {skill.description}
                                                        </p>

                                                        {/* Resources Section */}
                                                        {skill.resources && skill.resources.length > 0 && (
                                                            <div className="mt-3 flex flex-wrap gap-2">
                                                                {skill.resources.map((res, rIdx) => (
                                                                    <a
                                                                        key={rIdx}
                                                                        href={res.url}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-xs px-2 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors flex items-center gap-1"
                                                                        onClick={(e) => e.stopPropagation()} // Prevent toggling when clicking link
                                                                    >
                                                                        📚 {res.title}
                                                                    </a>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                    {skill.status && (
                                                        <div className="hidden sm:block text-xs px-2 py-1 rounded bg-surface border border-border text-text-secondary">
                                                            {solvedIds.includes(skill.id) ? "Mastered" : "Pending"}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div >
    );
};

export default Roadmap;
