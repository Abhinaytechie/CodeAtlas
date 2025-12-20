import React, { useEffect } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    securityLevel: 'loose',
    fontFamily: 'monospace'
});

const MermaidController = ({ chart }) => {
    useEffect(() => {
        mermaid.contentLoaded();
    }, [chart]);

    return (
        <div className="mermaid flex justify-center p-6 bg-surface/30 rounded-lg overflow-x-auto">
            {chart}
        </div>
    );
};

export default MermaidController;
