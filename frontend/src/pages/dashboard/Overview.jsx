import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ArrowRight, CheckCircle2, Clock, Code2, Brain, Layers } from 'lucide-react';
import api from '../../lib/api';

const DashboardHome = () => {
    const [stats, setStats] = useState({
        problems_solved: 0,
        total_problems: 100, // Estimated
        streak_days: 0,
        weak_pattern: "None detected yet"
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get('/dashboard/stats');
                setStats(res.data);
            } catch (err) {
                console.error("Failed to fetch stats", err);
            }
        };
        fetchStats();
    }, []);

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-display font-bold">Welcome back</h1>
                    <p className="text-text-secondary mt-1">Ready to master your next skill?</p>
                </div>
                <Link to="/dashboard/roadmap">
                    <Button>
                        Resume Roadmap
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </Link>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Solved Problems with Detailed Breakdown */}
                <Card className="p-6 space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="text-text-secondary text-sm font-medium">Skills Mastered</div>
                            <div className="text-4xl font-bold font-display text-primary">{stats.problems_solved || 0}</div>
                        </div>
                        <div className="h-12 w-12 rounded-full bg-surface border-4 border-primary/20 flex items-center justify-center text-xs font-bold text-text-secondary">
                            Stats
                        </div>
                    </div>
                    <div className="w-full h-2 bg-surface rounded-full overflow-hidden border border-border">
                        <div className="h-full bg-primary" style={{ width: `${Math.min(((stats.problems_solved || 0) / 50) * 100, 100)}%` }} />
                    </div>
                    <p className="text-xs text-text-secondary">
                        Keep checking off skills in your roadmap to increase your mastery score.
                    </p>
                </Card>

                {/* Streak & Weakness */}
                <div className="space-y-6">
                    <Card className="p-6 flex items-center justify-between bg-surface/50">
                        <div>
                            <div className="text-text-secondary text-sm font-medium">Current Streak</div>
                            <div className="text-3xl font-bold font-display">{stats.streak_days} <span className="text-lg font-normal">Days</span></div>
                            <div className="text-xs text-success flex items-center mt-1">
                                <CheckCircle2 className="h-3 w-3 mr-1" /> Consistency is key!
                            </div>
                        </div>
                        <div className="h-14 w-14 rounded-full bg-warning/10 text-warning flex items-center justify-center">
                            <Clock className="h-7 w-7" />
                        </div>
                    </Card>

                    {/* Interview CTA */}
                    <Link to="/dashboard/interview" className="block">
                        <Card className="p-6 flex items-center justify-between hover:border-primary transition-colors cursor-pointer group">
                            <div>
                                <div className="font-bold flex items-center gap-2 group-hover:text-primary transition-colors">
                                    <Brain className="h-5 w-5 text-primary" /> Start Mock Interview
                                </div>
                                <div className="text-xs text-text-secondary mt-1">AI-powered simulation with real-time feedback</div>
                            </div>
                            <ArrowRight className="h-5 w-5 text-text-secondary group-hover:text-primary transition-colors" />
                        </Card>
                    </Link>
                </div>
            </div>

            <div className="pt-4">
                <h2 className="text-xl font-display font-bold mb-4">Quick Actions</h2>
                <div className="grid md:grid-cols-3 gap-4">
                    <Link to="/dashboard/roadmap?new=true">
                        <Card className="p-4 hover:bg-surface transition-colors">
                            <Layers className="h-6 w-6 text-primary mb-2" />
                            <div className="font-bold">Generate New Roadmap</div>
                            <div className="text-xs text-text-secondary">Switch roles or change timeline</div>
                        </Card>
                    </Link>
                    <Link to="/dashboard/interview">
                        <Card className="p-4 hover:bg-surface transition-colors">
                            <Brain className="h-6 w-6 text-primary mb-2" />
                            <div className="font-bold">Practice Interview</div>
                            <div className="text-xs text-text-secondary">Test your knowledge under pressure</div>
                        </Card>
                    </Link>
                    <div className="opacity-50 cursor-not-allowed">
                        <Card className="p-4">
                            <Code2 className="h-6 w-6 text-text-secondary mb-2" />
                            <div className="font-bold">Code Sandbox</div>
                            <div className="text-xs text-text-secondary">Coming Soon</div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default DashboardHome;
