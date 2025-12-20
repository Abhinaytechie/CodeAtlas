import { useState, useEffect } from 'react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend
} from 'recharts';
import { Activity, TrendingUp, Award, Brain, Target, Sparkles } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import api from '../../lib/api';

const Analytics = () => {
    const [kpis, setKpis] = useState(null);
    const [skillsData, setSkillsData] = useState([]);
    const [interviewData, setInterviewData] = useState([]);
    const [feedback, setFeedback] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [kpiRes, skillRes, interviewRes, feedbackRes] = await Promise.all([
                    api.get('/analytics/kpis'),
                    api.get('/analytics/skills'),
                    api.get('/analytics/interviews'),
                    api.get('/analytics/feedback')
                ]);
                setKpis(kpiRes.data);
                setSkillsData(skillRes.data);
                setInterviewData(interviewRes.data);
                setFeedback(feedbackRes.data);
            } catch (e) {
                console.error("Failed to fetch analytics", e);
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, []);

    if (loading) return <div className="p-8 text-center text-text-secondary">Loading Insights...</div>;

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-display font-bold">Performance Analytics</h1>
                    <p className="text-text-secondary mt-1">
                        Track your growth across Skills and Interview Readiness.
                    </p>
                </div>
            </div>

            {/* High Level KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-primary/10 rounded text-primary">
                            <Activity className="h-5 w-5" />
                        </div>
                        <span className="text-sm font-medium text-text-secondary">Skills Mastered</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">{kpis?.skills_mastered || 0}</div>
                </Card>
                <Card className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-warning/10 rounded text-warning">
                            <Target className="h-5 w-5" />
                        </div>
                        <span className="text-sm font-medium text-text-secondary">Current Streak</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">{kpis?.streak || 0} <span className="text-sm font-sans font-normal text-text-secondary">Days</span></div>
                </Card>
                <Card className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-purple-500/10 rounded text-purple-500">
                            <Award className="h-5 w-5" />
                        </div>
                        <span className="text-sm font-medium text-text-secondary">Mastery XP</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">{kpis?.mastery_score || 0}</div>
                </Card>
                <Card className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-success/10 rounded text-success">
                            <Brain className="h-5 w-5" />
                        </div>
                        <span className="text-sm font-medium text-text-secondary">Interview Readiness</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">{kpis?.interview_readiness}%</div>
                </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Interview Performance Chart */}
                <Card className="p-6 h-[400px] flex flex-col">
                    <h3 className="font-bold mb-6 flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-text-secondary" />
                        Interview Score Trend
                    </h3>
                    <div className="flex-1 min-h-0">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={interviewData}>
                                <defs>
                                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="date" stroke="#555" tick={{ fill: '#888', fontSize: 12 }} />
                                <YAxis stroke="#555" tick={{ fill: '#888', fontSize: 12 }} />
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="score" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorScore)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                {/* Skill Balance Radar */}
                <Card className="p-6 h-[400px] flex flex-col">
                    <h3 className="font-bold mb-6 flex items-center gap-2">
                        <Target className="h-5 w-5 text-text-secondary" />
                        Skill Distribution
                    </h3>
                    <div className="flex-1 min-h-0">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={skillsData}>
                                <PolarGrid stroke="#333" />
                                <PolarAngleAxis dataKey="name" tick={{ fill: '#888', fontSize: 12 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                <Radar
                                    name="Proficiency"
                                    dataKey="value"
                                    stroke="#10b981"
                                    fill="#10b981"
                                    fillOpacity={0.5}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            {/* Recent Qualitative Feedback */}
            <Card className="p-6">
                <h3 className="font-bold mb-6 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-warning" />
                    AI Interviewer Insights
                </h3>
                <div className="space-y-4">
                    {feedback.length > 0 ? (
                        feedback.map((item, i) => (
                            <div key={i} className="flex gap-4 p-4 rounded-lg bg-surface border border-border">
                                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 text-primary font-bold">
                                    {i + 1}
                                </div>
                                <p className="text-text-secondary text-sm leading-relaxed">"{item}"</p>
                            </div>
                        ))
                    ) : (
                        <div className="text-center text-text-secondary py-8">
                            No feedback yet. Complete a Mock Interview to get insights!
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
};

export default Analytics;
