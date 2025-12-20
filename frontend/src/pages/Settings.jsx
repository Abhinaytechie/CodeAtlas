import { useState, useEffect } from 'react';
import { Save, Key, ShieldCheck, AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { motion } from 'framer-motion';

const Settings = () => {
    const [apiKey, setApiKey] = useState('');
    const [showKey, setShowKey] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const storedKey = localStorage.getItem('groq_api_key');
        if (storedKey) setApiKey(storedKey);
    }, []);

    const handleSave = () => {
        if (apiKey.trim()) {
            localStorage.setItem('groq_api_key', apiKey.trim());
        } else {
            localStorage.removeItem('groq_api_key');
        }
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="max-w-2xl mx-auto py-8">
            <h1 className="text-3xl font-display font-bold mb-6">Settings</h1>

            <Card className="p-6 space-y-6">
                <div>
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <Key className="text-primary h-5 w-5" /> AI Configuration
                    </h2>
                    <p className="text-text-secondary mt-1 text-sm">
                        To enable truly dynamic roadmap generation, please provide your Groq API Key.
                    </p>
                </div>

                <div className="bg-surface/50 p-4 rounded-lg border border-border space-y-3">
                    <div className="flex items-center gap-2 text-warning text-sm font-medium">
                        <AlertTriangle className="h-4 w-4" /> Privacy Note
                    </div>
                    <p className="text-xs text-text-secondary leading-relaxed">
                        Your API key is stored <strong>locally in your browser</strong>. It is never saved to our database.
                        It is sent securely to our backend only when generating a roadmap, and is discarded immediately after use.
                    </p>
                </div>

                <div className="space-y-3">
                    <label className="text-sm font-medium">Groq API Key</label>
                    <div className="relative">
                        <Input
                            type={showKey ? "text" : "password"}
                            placeholder="gsk_..."
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="pr-20"
                        />
                        <button
                            onClick={() => setShowKey(!showKey)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-primary font-medium hover:underline"
                        >
                            {showKey ? "Hide" : "Show"}
                        </button>
                    </div>
                    <p className="text-xs text-text-secondary">
                        Don't have one? <a href="https://console.groq.com/keys" target="_blank" className="text-primary hover:underline">Get a free key here</a>.
                    </p>
                </div>

                <div className="pt-4 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-success">
                        {saved && (
                            <motion.span
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-center gap-1"
                            >
                                <ShieldCheck className="h-4 w-4" /> Saved securely to browser
                            </motion.span>
                        )}
                    </div>
                    <Button onClick={handleSave} className="w-32">
                        {saved ? 'Saved!' : 'Save Key'}
                    </Button>
                </div>
            </Card>
        </div>
    );
};

export default Settings;
