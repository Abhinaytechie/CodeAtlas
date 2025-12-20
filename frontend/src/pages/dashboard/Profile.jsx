import { useState, useEffect } from 'react';
import { User, Mail, Calendar, Target, Award } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const Profile = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get('/users/me');
                setProfile(res.data);
            } catch (err) {
                console.error("Failed to load profile", err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    if (loading) return <div className="p-8">Loading profile...</div>;
    if (!profile) return <div className="p-8">User not found</div>;

    return (
        <div className="max-w-2xl mx-auto py-12">
            <h1 className="text-3xl font-display font-bold mb-8">My Profile</h1>

            <Card className="p-8">
                <div className="flex items-center gap-6 mb-8">
                    <div className="h-20 w-20 rounded-full bg-primary/20 flex items-center justify-center text-primary text-2xl font-bold">
                        {profile.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">{profile.username}</h2>
                        <span className="inline-block mt-2 px-3 py-1 bg-surface rounded-full text-xs font-medium text-text-secondary border border-border">
                            {profile.target_role} Aspirant
                        </span>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="flex items-center gap-4 p-4 rounded-lg bg-surface/50 border border-border">
                        <Mail className="h-5 w-5 text-text-secondary" />
                        <div>
                            <p className="text-xs text-text-secondary">Email</p>
                            <p className="font-medium">{profile.email}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 rounded-lg bg-surface/50 border border-border">
                        <Target className="h-5 w-5 text-text-secondary" />
                        <div>
                            <p className="text-xs text-text-secondary">Target Role</p>
                            <p className="font-medium">{profile.target_role}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 rounded-lg bg-surface/50 border border-border">
                        <Calendar className="h-5 w-5 text-text-secondary" />
                        <div>
                            <p className="text-xs text-text-secondary">Joined</p>
                            <p className="font-medium">{profile.joined_at}</p>
                        </div>
                    </div>
                </div>

                <div className="mt-8 pt-6 border-t border-border flex justify-end">
                    <Button variant="outline" className="text-red-400 hover:text-red-500 hover:border-red-500/50">
                        Sign Out
                    </Button>
                </div>
            </Card>
        </div>
    );
};

export default Profile;
