import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { Play, CheckCircle, ChevronLeft, RotateCcw, Maximize2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';

const ProblemSolver = () => {
    const { problemId } = useParams();
    const navigate = useNavigate();
    const [code, setCode] = useState('// Write your solution here\nclass Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}');
    const [output, setOutput] = useState(null);
    const [isRunning, setIsRunning] = useState(false);

    // Mock Problem Data (Eventually fetch from API)
    const problem = {
        title: "Two Sum",
        difficulty: "Easy",
        description: `Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.`,
        examples: [
            { input: "nums = [2,7,11,15], target = 9", output: "[0,1]", explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]." },
            { input: "nums = [3,2,4], target = 6", output: "[1,2]" }
        ]
    };

    const handleRun = () => {
        setIsRunning(true);
        // Simulate API call
        setTimeout(() => {
            setIsRunning(false);
            setOutput({
                status: 'Accepted',
                runtime: '2ms',
                memory: '42.3MB',
                passed: true
            });
        }, 1500);
    };

    return (
        <div className="h-[calc(100vh-64px)] flex flex-col md:flex-row overflow-hidden">
            {/* Left Panel: Description */}
            <div className="w-full md:w-1/2 p-4 overflow-y-auto border-r border-border bg-background">
                <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-4 pl-0 hover:pl-2 transition-all">
                    <ChevronLeft className="h-4 w-4 mr-1" /> Back
                </Button>

                <h1 className="text-2xl font-display font-bold mb-2 flex items-center gap-3">
                    {problemId ? `Problem ${problemId}` : problem.title}
                    <span className="px-2 py-0.5 rounded text-xs bg-surface border border-border text-success font-medium">
                        {problem.difficulty}
                    </span>
                </h1>

                <div className="prose prose-invert max-w-none text-text-secondary mt-6">
                    <p className="whitespace-pre-wrap">{problem.description}</p>

                    <h3 className="text-text-primary font-bold mt-6 mb-2">Examples</h3>
                    {problem.examples.map((ex, i) => (
                        <div key={i} className="bg-surface rounded-lg p-3 mb-3 border border-border">
                            <div className="text-sm"><span className="font-semibold text-text-primary">Input:</span> {ex.input}</div>
                            <div className="text-sm mt-1"><span className="font-semibold text-text-primary">Output:</span> {ex.output}</div>
                            {ex.explanation && (
                                <div className="text-sm mt-1 text-text-secondary"><span className="font-semibold text-text-primary">Explanation:</span> {ex.explanation}</div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Right Panel: Editor */}
            <div className="w-full md:w-1/2 flex flex-col bg-[#1e1e1e]">
                {/* Toolbar */}
                <div className="h-12 bg-surface border-b border-border flex items-center justify-between px-4">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-text-secondary">Java</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button size="sm" variant="secondary" onClick={() => setCode('')}>
                            <RotateCcw className="h-3 w-3 mr-1" /> Reset
                        </Button>
                        <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white" onClick={handleRun} disabled={isRunning}>
                            {isRunning ? 'Running...' : (
                                <>
                                    <Play className="h-3 w-3 mr-1" /> Run Code
                                </>
                            )}
                        </Button>
                    </div>
                </div>

                {/* Editor */}
                <div className="flex-1">
                    <Editor
                        height="100%"
                        defaultLanguage="java"
                        theme="vs-dark"
                        value={code}
                        onChange={setCode}
                        options={{
                            minimap: { enabled: false },
                            fontSize: 14,
                            lineNumbers: 'on',
                            scrollBeyondLastLine: false,
                            automaticLayout: true,
                            padding: { top: 16 }
                        }}
                    />
                </div>

                {/* Output Panel (Collapsible/Fixed height) */}
                {output && (
                    <div className="h-64 bg-surface border-t border-border p-4 overflow-y-auto animate-in slide-in-from-bottom-5">
                        <div className="flex items-center justify-between mb-3">
                            <span className="font-bold text-sm">Output</span>
                            <Button variant="ghost" size="sm" onClick={() => setOutput(null)}><Maximize2 className="h-3 w-3" /></Button>
                        </div>

                        <div className={`p-4 rounded-lg border ${output.passed ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                            <div className={`font-bold text-lg mb-2 ${output.passed ? 'text-green-400' : 'text-red-400'}`}>
                                {output.status}
                            </div>
                            <div className="flex gap-6 text-sm">
                                <div>
                                    <span className="text-text-secondary block text-xs">Runtime</span>
                                    <span className="font-mono">{output.runtime}</span>
                                </div>
                                <div>
                                    <span className="text-text-secondary block text-xs">Memory</span>
                                    <span className="font-mono">{output.memory}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProblemSolver;
