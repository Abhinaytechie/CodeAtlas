import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    Map,
    Layers,
    Code2,
    BarChart2,
    Settings,
    LogOut,
    Menu,
    X,
    Clock,
    BrainCircuit
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '../lib/utils';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';

const SidebarItem = ({ icon: Icon, label, to, active }) => (
    <Link to={to}>
        <div className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors mb-1",
            active
                ? "bg-primary/10 text-primary font-medium"
                : "text-text-secondary hover:text-text-primary hover:bg-surface"
        )}>
            <Icon className="h-5 w-5" />
            <span>{label}</span>
        </div>
    </Link>
);

const DashboardLayout = () => {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const location = useLocation();
    const path = location.pathname;
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    return (
        <div className="min-h-screen bg-background text-text-primary flex">
            {/* Sidebar */}
            <motion.aside
                className={cn(
                    "fixed inset-y-0 left-0 z-40 w-64 border-r border-border bg-background/95 backdrop-blur-md transform transition-transform duration-300 md:translate-x-0 md:static",
                    !sidebarOpen && "-translate-x-full md:w-20"
                )}
            >
                <div className="h-16 flex items-center justify-between px-6 border-b border-border">
                    <span className={cn("font-display font-bold text-xl", !sidebarOpen && "md:hidden")}>
                        Code<span className="text-primary">Atlas</span>
                    </span>
                    <Button variant="ghost" size="sm" className="md:hidden" onClick={() => setSidebarOpen(false)}>
                        <X className="h-5 w-5" />
                    </Button>
                    {/* Desktop Collapse Toggle could go here */}
                </div>

                <div className="p-4 flex flex-col h-[calc(100vh-64px)] justify-between">
                    <nav className="space-y-1">
                        <SidebarItem icon={LayoutDashboard} label="Overview" to="/dashboard" active={path === '/dashboard'} />
                        <SidebarItem icon={Map} label="My Roadmap" to="/dashboard/roadmap" active={path === '/dashboard/roadmap'} />
                        <SidebarItem icon={Layers} label="Your Roadmaps" to="/dashboard/roadmaps" active={path.includes('roadmaps')} />
                        <SidebarItem icon={BarChart2} label="Analytics" to="/dashboard/analytics" active={path.includes('analytics')} />
                        <SidebarItem icon={Layers} label="Vault" to="/dashboard/vault" active={path.includes('vault')} />
                        <SidebarItem icon={BrainCircuit} label="RepoMap Intelligence" to="/dashboard/project-intelligence" active={path.includes('project-intelligence')} />
                        <SidebarItem icon={Clock} label="Mock Interview" to="/dashboard/interview" active={path.includes('interview')} />
                        <div className="pt-4 mt-4 border-t border-border">
                            <SidebarItem icon={Settings} label="Settings" to="/dashboard/settings" active={path.includes('settings')} />
                        </div>
                    </nav>

                    <Button
                        variant="ghost"
                        className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-400/10"
                        onClick={handleLogout}
                    >
                        <LogOut className="h-5 w-5 mr-3" />
                        <span className={cn(!sidebarOpen && "md:hidden")}>Sign Out</span>
                    </Button>
                </div>
            </motion.aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-16 border-b border-border bg-background/50 backdrop-blur-sm sticky top-0 z-30 flex items-center px-6 justify-between md:justify-end">
                    <Button variant="ghost" size="sm" className="md:hidden" onClick={() => setSidebarOpen(true)}>
                        <Menu className="h-5 w-5" />
                    </Button>
                    <div className="flex items-center gap-4">
                        <Link to="/dashboard/profile">
                            <div className="h-8 w-8 rounded-full bg-primary/20 border border-primary/50 text-primary flex items-center justify-center text-sm font-medium hover:bg-primary/30 transition-colors cursor-pointer">
                                JD
                            </div>
                        </Link>
                    </div>
                </header>

                <main className="flex-1 p-6 md:p-8 overflow-y-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;

