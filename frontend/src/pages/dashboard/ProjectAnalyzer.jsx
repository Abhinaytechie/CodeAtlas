import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, Code2, Layers, BookOpen, MessageSquare, UserCheck, Play, BrainCircuit, CheckCircle, FileText, Download, Copy, Check, AlertTriangle, Wand2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import api from '../../lib/api';
import ReactMarkdown from 'react-markdown';
import MermaidController from '../../components/ui/MermaidDiagram';

const ProjectAnalyzer = () => {
    const [repoUrl, setRepoUrl] = useState('');
    const [status, setStatus] = useState('idle'); // idle, schema_loading, schema_ready, docs_loading, full_complete, error
    const [graphData, setGraphData] = useState('');
    const [jobId, setJobId] = useState(null);
    const [docs, setDocs] = useState(null);
    const [copied, setCopied] = useState(false);
    const [isGeneratingSpec, setIsGeneratingSpec] = useState(false);

    const handleCopy = async () => {
        if (!docs?.readme) return;
        try {
            await navigator.clipboard.writeText(docs.readme);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    const handleGenerateSpec = async () => {
        setIsGeneratingSpec(true);
        try {
            const apiKey = localStorage.getItem('groq_api_key');
            const res = await api.post('/project/generate-openapi', { repo_url: repoUrl }, {
                headers: apiKey ? { 'x-groq-api-key': apiKey } : {}
            });

            // Merge results
            if (res.data.spec_json) {
                setDocs(prev => ({
                    ...prev,
                    api_specs: res.data.routes,
                    warnings: ["⚠️ API Specification was AI-generated from source code. Verify accuracy."] // Overwrite old warning
                }));
            }
        } catch (error) {
            console.error("AI Spec Generation failed", error);
            alert("Failed to generate spec. Check logs.");
        } finally {
            setIsGeneratingSpec(false);
        }
        //new
    };

    // Step 1: Visualize Architecture
    const handleVisualize = async () => {
        if (!repoUrl) return;
        setStatus('schema_loading');

        try {
            const apiKey = localStorage.getItem('groq_api_key');
            const res = await api.post('/project/visualize', { repo_url: repoUrl }, {
                headers: apiKey ? { 'x-groq-api-key': apiKey } : {}
            });

            setGraphData(res.data.graph_data);
            setJobId(res.data.repo_path_id);
            setStatus('schema_ready');
        } catch (error) {
            console.error("Visualization failed", error);
            setStatus('error');
            alert("Failed to visualize repo. Check console.");
        }
    };

    // Step 2: Generate Docs
    const handleGenerateDocs = async () => {
        setStatus('docs_loading');
        try {
            const apiKey = localStorage.getItem('groq_api_key');
            const res = await api.post('/project/docs', { job_id: jobId }, {
                headers: apiKey ? { 'x-groq-api-key': apiKey } : {}
            });
            setDocs(res.data);
            setStatus('full_complete');
        } catch (e) {
            console.error("Docs generation failed", e);
            setStatus('error');
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8 pb-12">
            <div>
                <h1 className="text-3xl font-display font-bold">RepoMap Intelligence</h1>
                <p className="text-text-secondary mt-1 max-w-2xl">
                    Your interactive roadmap to understanding any codebase. Visualizing architecture, one commit at a time.
                </p>
            </div>

            {/* Input Section */}
            {(status === 'idle' || status === 'error') && (
                <Card className="p-8">
                    <div className="flex flex-col gap-4">
                        <Input
                            placeholder="Paste GitHub Repository URL"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            className="h-12 text-lg font-mono"
                        />
                        <Button onClick={handleVisualize} disabled={!repoUrl} className="h-12 text-lg">
                            <Layers className="h-5 w-5 mr-2" /> Map Architecture
                        </Button>
                    </div>
                </Card>
            )}

            {status === 'schema_loading' && (
                <div className="text-center py-20">
                    <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                    <h3 className="text-xl font-bold">Mapping System Architecture...</h3>
                    <p className="text-text-secondary">Parsing imports and file relationships.</p>
                </div>
            )}

            {/* Step 1 Result: Diagram */}
            {(status === 'schema_ready' || status === 'docs_loading' || status === 'full_complete') && graphData && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                    <Card className="p-6 border-l-4 border-l-blue-500">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="font-bold flex items-center gap-2 text-lg">
                                <BrainCircuit className="h-5 w-5 text-blue-500" /> System Architecture Map
                            </h3>
                            {status === 'schema_ready' && (
                                <Button onClick={handleGenerateDocs} size="sm" className="bg-success hover:bg-success/90 text-white">
                                    <FileText className="h-4 w-4 mr-2" /> Generate Docs
                                </Button>
                            )}
                        </div>
                        <MermaidController chart={graphData} />
                    </Card>
                </motion.div>
            )}

            {status === 'docs_loading' && (
                <div className="text-center py-20">
                    <Loader2 className="h-12 w-12 animate-spin text-purple-500 mx-auto mb-4" />
                    <h3 className="text-xl font-bold">Writing Professional Documentation...</h3>
                    <p className="text-text-secondary">Agents are writing your README and scanning API routes.</p>
                </div>
            )}

            {status === 'full_complete' && docs && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* README Preview */}
                    <Card className="p-6 h-[600px] overflow-y-auto">
                        <div className="flex justify-between items-center mb-4 sticky top-0 bg-surface/95 p-2 rounded backdrop-blur z-10">
                            <h3 className="font-bold flex items-center gap-2">
                                <BookOpen className="h-5 w-5 text-primary" /> Generated README.md
                            </h3>
                            <Button size="xs" variant="outline" onClick={handleCopy}>
                                {copied ? <Check className="h-4 w-4 text-green-500 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                                {copied ? "Copied!" : "Copy Markdown"}
                            </Button>
                        </div>
                        <div className="prose prose-invert prose-sm max-w-none">
                            <ReactMarkdown>{docs.readme}</ReactMarkdown>
                        </div>
                    </Card>

                    {/* API Specs */}
                    <Card className="p-6">
                        <h3 className="font-bold flex items-center gap-2 mb-6">
                            <Code2 className="h-5 w-5 text-primary" /> API Specification ({docs.api_specs.length} Endpoint detected)
                        </h3>

                        {docs.warnings && docs.warnings.length > 0 && (
                            <div className="mb-4 space-y-3">
                                {docs.warnings.map((warn, i) => (
                                    <div key={i} className="flex flex-col gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-200 text-sm">
                                        <div className="flex items-start gap-2">
                                            <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                                            <span>{warn}</span>
                                        </div>
                                        {/* Auto-Gen Button Trigger */}
                                        {warn.includes("OpenAPI specification not found") && (
                                            <Button
                                                onClick={handleGenerateSpec}
                                                disabled={isGeneratingSpec}
                                                size="sm"
                                                className="self-start mt-2 bg-purple-600 hover:bg-purple-700 text-white border-none"
                                            >
                                                {isGeneratingSpec ? (
                                                    <Loader2 className="h-3 w-3 animate-spin mr-2" />
                                                ) : (
                                                    <Wand2 className="h-3 w-3 mr-2" />
                                                )}
                                                Generate Standard OpenAPI with AI
                                            </Button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                        <div className="space-y-2">
                            {docs.api_specs.length > 0 ? docs.api_specs.map((route, i) => (
                                <div key={i} className="flex items-center gap-3 p-3 bg-surface rounded border border-border">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${route.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                                        route.method === 'POST' ? 'bg-green-500/20 text-green-400' :
                                            route.method === 'DELETE' ? 'bg-red-500/20 text-red-400' :
                                                'bg-gray-500/20 text-gray-400'
                                        }`}>
                                        {route.method}
                                    </span>
                                    <code className="text-sm font-mono flex-1">{route.url}</code>
                                </div>
                            )) : (
                                <p className="text-text-secondary italic">No explicit API routes detected.</p>
                            )}
                        </div>
                    </Card>
                </motion.div>
            )}

        </div>
    );
};

export default ProjectAnalyzer;
