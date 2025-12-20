import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, User, Bot, Play, Award, Loader2, Sparkles, StopCircle, FileText, UploadCloud, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import api from '../../lib/api';

const MockInterview = () => {
    const [status, setStatus] = useState('setup'); // setup, active, feedback
    const [loading, setLoading] = useState(false);

    // Setup State
    const [config, setConfig] = useState({
        role: 'Backend Developer',
        company: 'Product-based',
        type: 'DSA'
    });

    // Resume State
    const [useResume, setUseResume] = useState(false);
    const [resumeText, setResumeText] = useState('');
    const [resumeContext, setResumeContext] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
    const [fileName, setFileName] = useState('');
    const fileInputRef = useRef(null);

    // Session State
    const [sessionId, setSessionId] = useState(null);
    const [history, setHistory] = useState([]);
    const [currentInput, setCurrentInput] = useState('');
    const scrollRef = useRef(null);

    // Auto-scroll to bottom of chat
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (file.type !== 'application/pdf') {
            alert("Please upload a PDF file.");
            return;
        }

        setUploadStatus('uploading');
        setFileName(file.name);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const apiKey = localStorage.getItem('groq_api_key');
            const res = await api.post('/interview/resume/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    ...(apiKey ? { 'x-groq-api-key': apiKey } : {})
                }
            });
            setResumeText(res.data.resume_text);
            setResumeContext(res.data.resume_context);
            setUploadStatus('success');
        } catch (error) {
            console.error("Upload failed", error);
            setUploadStatus('error');
            alert("Failed to parse resume. Please try again.");
        }
    };

    const startSession = async () => {
        setLoading(true);
        try {
            const apiKey = localStorage.getItem('groq_api_key');

            const payload = { ...config };
            if (useResume) {
                if (resumeContext) payload.resume_context = resumeContext;
                if (resumeText) payload.resume_text = resumeText;
            }

            const res = await api.post('/interview/start', payload, {
                headers: apiKey ? { 'x-groq-api-key': apiKey } : {}
            });

            setSessionId(res.data.session_id);
            setHistory([{
                role: 'assistant',
                text: res.data.question,
                context: res.data.context
            }]);
            setStatus('active');
        } catch (error) {
            console.error("Failed to start", error);
            alert("Failed to start interview. Check API Key.");
        } finally {
            setLoading(false);
        }
    };

    const sendMessage = async () => {
        if (!currentInput.trim()) return;

        const userMsg = { role: 'user', text: currentInput };
        setHistory(prev => [...prev, userMsg]);
        setCurrentInput('');
        setLoading(true);

        try {
            const apiKey = localStorage.getItem('groq_api_key');
            const res = await api.post(`/interview/${sessionId}/reply`, {
                answer: userMsg.text
            }, {
                headers: apiKey ? { 'x-groq-api-key': apiKey } : {}
            });

            const aiMsg = {
                role: 'assistant',
                text: res.data.next_question,
                feedback: res.data.feedback_snapshot
            };
            setHistory(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error("Failed to reply", error);
        } finally {
            setLoading(false);
        }
    };

    const endSession = () => {
        setStatus('feedback');
    };

    if (status === 'setup') {
        return (
            <div className="max-w-2xl mx-auto py-12">
                <div className="text-center mb-10">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="inline-flex p-4 rounded-full bg-primary/10 text-primary mb-4"
                    >
                        <Bot className="h-10 w-10" />
                    </motion.div>
                    <h1 className="text-3xl font-display font-bold mb-2">AI Interview Simulator</h1>
                    <p className="text-text-secondary">
                        Practice with a context-aware AI that adapts to your answers.
                    </p>
                </div>

                <Card className="p-8 space-y-6">
                    <div className="space-y-3">
                        <label className="text-sm font-medium">Target Role</label>
                        <select
                            className="w-full bg-background border border-border rounded-lg p-3 focus:border-primary focus:outline-none"
                            value={config.role}
                            onChange={(e) => setConfig({ ...config, role: e.target.value })}
                        >
                            <option>Backend Developer</option>
                            <option>Frontend Developer</option>
                            <option>Full Stack Engineer</option>
                            <option>Data Scientist</option>
                            <option>AI/ML Engineer</option>
                        </select>
                    </div>

                    <div className="space-y-3">
                        <label className="text-sm font-medium">Company Style</label>
                        <div className="grid grid-cols-3 gap-3">
                            {['Product-based', 'Service-based', 'Startup'].map(c => (
                                <button
                                    key={c}
                                    onClick={() => setConfig({ ...config, company: c })}
                                    className={`p-3 rounded-lg border text-sm font-medium transition-colors ${config.company === c
                                        ? 'bg-primary/10 border-primary text-primary'
                                        : 'bg-background border-border hover:bg-surface'
                                        }`}
                                >
                                    {c}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="text-sm font-medium">Interview Focus</label>
                        <div className="grid grid-cols-3 gap-3">
                            {['DSA', 'System Design', 'Behavioral'].map(t => (
                                <button
                                    key={t}
                                    onClick={() => setConfig({ ...config, type: t })}
                                    className={`p-3 rounded-lg border text-sm font-medium transition-colors ${config.type === t
                                        ? 'bg-primary/10 border-primary text-primary'
                                        : 'bg-background border-border hover:bg-surface'
                                        }`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-3 pt-4 border-t border-border">
                        <div className="flex items-center justify-between">
                            <label className="text-sm font-bold flex items-center gap-2">
                                <FileText className="h-4 w-4 text-primary" /> Target My Resume
                            </label>
                            <div
                                onClick={() => setUseResume(!useResume)}
                                className={`w-10 h-6 rounded-full p-1 cursor-pointer transition-colors ${useResume ? 'bg-primary' : 'bg-surface border border-border'}`}
                            >
                                <motion.div
                                    className="w-4 h-4 bg-white rounded-full"
                                    animate={{ x: useResume ? 16 : 0 }}
                                />
                            </div>
                        </div>

                        <AnimatePresence>
                            {useResume && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden"
                                >
                                    <p className="text-xs text-text-secondary mb-2">Upload your resume (PDF only). We'll analyze it to tailor questions.</p>

                                    {!resumeContext ? (
                                        <div
                                            className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-colors ${uploadStatus === 'error' ? 'border-red-500/50 bg-red-500/5' :
                                                    uploadStatus === 'uploading' ? 'border-primary/50 bg-primary/5' :
                                                        'border-border hover:border-primary/50 hover:bg-surface'
                                                }`}
                                            onClick={() => fileInputRef.current?.click()}
                                        >
                                            <input
                                                type="file"
                                                ref={fileInputRef}
                                                className="hidden"
                                                accept="application/pdf"
                                                onChange={handleFileUpload}
                                            />

                                            {uploadStatus === 'uploading' ? (
                                                <>
                                                    <Loader2 className="h-8 w-8 text-primary animate-spin mb-2" />
                                                    <span className="text-sm font-medium">Parsing PDF...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <UploadCloud className="h-8 w-8 text-text-secondary mb-2" />
                                                    <span className="text-sm font-medium">Click to Upload PDF</span>
                                                </>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="bg-success/10 border border-success/20 rounded-lg p-3 flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 bg-success text-white rounded-full">
                                                    <CheckCircle className="h-4 w-4" />
                                                </div>
                                                <div>
                                                    <div className="text-sm font-bold text-success">Resume Parsed</div>
                                                    <div className="text-xs text-text-secondary">{fileName}</div>
                                                </div>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-xs h-8"
                                                onClick={() => {
                                                    setResumeContext(null);
                                                    setResumeText('');
                                                    setUploadStatus('idle');
                                                }}
                                            >
                                                Change
                                            </Button>
                                        </div>
                                    )}

                                    {resumeContext && (
                                        <div className="mt-2 text-xs text-text-secondary">
                                            Found: {resumeContext.skills?.length || 0} Skills, {resumeContext.projects?.length || 0} Projects
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <Button
                        className="w-full h-12 text-lg mt-6"
                        onClick={startSession}
                        disabled={loading}
                    >
                        {loading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Play className="h-5 w-5 mr-2" />}
                        Start Interview
                    </Button>
                </Card>
            </div>
        );
    }

    if (status === 'active') {
        return (
            <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col gap-4">
                {/* Header */}
                <div className="flex items-center justify-between bg-surface/50 p-4 rounded-xl border border-border">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                            <Bot className="h-6 w-6" />
                        </div>
                        <div>
                            <div className="font-bold">{config.company} Interviewer</div>
                            <div className="text-xs text-text-secondary">{config.role} • {config.type}</div>
                        </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={endSession} className="text-warning hover:text-warning hover:bg-warning/10 border-warning/20">
                        <StopCircle className="h-4 w-4 mr-2" /> End Session
                    </Button>
                </div>

                {/* Chat Area */}
                <div
                    ref={scrollRef}
                    className="flex-1 overflow-y-auto space-y-6 p-4 rounded-xl bg-surface/30 border border-border/50"
                >
                    {history.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            <div className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-primary text-background' : 'bg-surface border border-border text-primary'
                                }`}>
                                {msg.role === 'user' ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                            </div>

                            <div className={`max-w-[80%] space-y-2`}>
                                <div className={`p-4 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                    ? 'bg-primary text-background'
                                    : 'bg-surface border border-border text-text-primary shadow-sm'
                                    }`}>
                                    {msg.text}
                                </div>
                                {msg.role === 'assistant' && msg.feedback && (
                                    <div className="text-xs text-text-secondary flex items-center gap-1 ml-2">
                                        <Sparkles className="h-3 w-3 text-warning" />
                                        <span>Feedback: {msg.feedback}</span>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                    {loading && (
                        <div className="flex gap-4">
                            <div className="h-8 w-8 rounded-full bg-surface border border-border text-primary flex items-center justify-center">
                                <Bot className="h-5 w-5" />
                            </div>
                            <div className="bg-surface border border-border p-4 rounded-2xl flex items-center gap-2">
                                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                                <span className="text-xs text-text-secondary">Thinking...</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <Card className="p-4 flex gap-3">
                    <textarea
                        value={currentInput}
                        onChange={(e) => setCurrentInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                sendMessage();
                            }
                        }}
                        placeholder="Type your answer here... (Shift+Enter for new line)"
                        className="flex-1 bg-background border border-border rounded-lg p-3 text-sm focus:border-primary focus:outline-none resize-none min-h-[80px]"
                    />
                    <Button
                        onClick={sendMessage}
                        disabled={!currentInput.trim() || loading}
                        className="h-auto w-20 flex flex-col items-center justify-center gap-1"
                    >
                        <Send className="h-5 w-5" />
                        <span className="text-[10px]">Send</span>
                    </Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto py-12 text-center">
            <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                className="inline-flex p-6 rounded-full bg-success/10 text-success mb-6"
            >
                <Award className="h-16 w-16" />
            </motion.div>
            <h1 className="text-3xl font-display font-bold mb-4">Session Completed</h1>
            <p className="text-text-secondary mb-8">
                Great job! Review your feedback in the dashboard history.
            </p>
            <div className="grid grid-cols-2 gap-4 text-left mb-8">
                <Card className="p-4">
                    <div className="text-sm text-text-secondary mb-1">Total Turns</div>
                    <div className="text-2xl font-bold">{Math.floor(history.length / 2)}</div>
                </Card>
                <Card className="p-4">
                    <div className="text-sm text-text-secondary mb-1">Focus Area</div>
                    <div className="text-2xl font-bold text-primary">{config.type}</div>
                </Card>
            </div>

            <Button onClick={() => setStatus('setup')} size="lg">
                Start New Session
            </Button>
        </div>
    );
};

export default MockInterview;
