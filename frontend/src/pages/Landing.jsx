import { ArrowRight, BarChart2, Brain, Code2, Layers } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Link } from 'react-router-dom';

const Hero = () => (
    <section className="relative px-6 py-24 md:py-32 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background opacity-50" />

        <div className="relative z-10">
            <span className="inline-block px-4 py-1.5 mb-6 rounded-full border border-primary/20 bg-primary/5 text-sm font-medium text-primary">
                New: AI Mock Interview Simulator
            </span>
            <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight mb-8 bg-gradient-to-br from-text-primary to-text-secondary bg-clip-text text-transparent">
                Master Skills. <br /> Crack the Interview.
            </h1>
            <p className="text-xl text-text-secondary mb-10 max-w-2xl mx-auto leading-relaxed">
                A complete personalized ecosystem: Skill-based Roadmaps, Progress Tracking, and Realistic AI Mock Interviews.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/signup">
                    <Button size="lg" className="w-full sm:w-auto">
                        Start Your Journey
                        <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                </Link>
                <Link to="/demo">
                    <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                        See How It Works
                    </Button>
                </Link>
            </div>
        </div>

        {/* Abstract UI Preview */}
        <div className="mt-20 w-full max-w-5xl rounded-xl border border-border bg-surface/50 p-2 shadow-2xl backdrop-blur-sm">
            <div className="rounded-lg bg-background border border-border aspect-[16/9] overflow-hidden flex items-center justify-center relative">
                <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:32px_32px]" />
                <div className="text-center space-y-4">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary border border-primary/20">
                        <Brain className="h-4 w-4" /> AI Personalized
                    </div>
                    <p className="text-text-secondary">Dashboard Preview</p>
                </div>
            </div>
        </div>
    </section>
);

const FeatureCard = ({ icon: Icon, title, description }) => (
    <Card className="hover:border-primary/30 transition-colors cursor-default">
        <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-6">
            <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-xl font-display font-bold mb-3">{title}</h3>
        <p className="text-text-secondary leading-relaxed">
            {description}
        </p>
    </Card>
);

const Features = () => (
    <section className="px-6 py-24 bg-surface/20 border-y border-border/50">
        <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
                    The Complete Prep Ecosystem
                </h2>
                <p className="text-text-secondary max-w-2xl mx-auto">
                    Move beyond random problem solving.
                </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                <FeatureCard
                    icon={Layers}
                    title="Skill-Based Roadmaps"
                    description="Forget 'Day 1, Day 2'. Our AI builds a hierarchy of Beginner, Intermediate, and Advanced skills tailored to your role."
                />
                <FeatureCard
                    icon={BarChart2}
                    title="Mastery Tracking"
                    description="Track specific skills like 'Graph Traversals' or 'System Scalability' instead of just counting problems."
                />
                <FeatureCard
                    icon={Brain}
                    title="AI Mock Interviews"
                    description="Chat with an AI interviewer that adapts to your responses, asks follow-ups, and rates your answers."
                />
                <FeatureCard
                    icon={Code2}
                    title="Manual Progress Control"
                    description="You control your data. Draft your progress and save explicitly when you are ready to commit."
                />
                <FeatureCard
                    icon={Brain}
                    title="Smart Resource Finder"
                    description="We don't just list topics. We find the best free YouTube videos and articles for every single skill."
                />
                <FeatureCard
                    icon={Layers}
                    title="Role-Specific Tracks"
                    description="Backend, Frontend, or AI/ML. Get a curriculum that matches the exact job description you want."
                />
            </div>
        </div>
    </section>
);

const Landing = () => {
    return (
        <div className="flex flex-col">
            <Hero />
            <Features />
            <footer className="py-12 text-center text-text-secondary border-t border-border">
                <p>© 2024 CodeAtlas. Built for serious engineers.</p>
            </footer>
        </div>
    );
};

export default Landing;
