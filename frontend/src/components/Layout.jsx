import { Link, useLocation, Outlet } from 'react-router-dom';
import { cn } from '../lib/utils';
import { Button } from './ui/Button';

const Layout = () => {
    const location = useLocation();
    const isDashboard = location.pathname.startsWith('/dashboard');

    return (
        <div className="min-h-screen bg-background text-text-primary font-sans selection:bg-primary/30">
            {!isDashboard && (
                <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
                    <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                        <Link to="/" className="text-xl font-display font-bold tracking-tight">
                            Code<span className="text-primary">Atlas</span>
                        </Link>
                        <div className="flex items-center gap-4">
                            <Link to="/login" className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                                Log in
                            </Link>
                            <Link to="/signup">
                                <Button size="sm">Get Started</Button>
                            </Link>
                        </div>
                    </div>
                </nav>
            )}
            <main className={cn(!isDashboard && "pt-16")}>
                <Outlet />
            </main>
        </div>
    );
};

export default Layout;
