import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { useAuth } from '../context/AuthContext';

const Signup = () => {
    const navigate = useNavigate();
    const { signup, login } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        // Basic Validation
        if (data.password.length < 6) {
            setError("Password must be at least 6 characters");
            setLoading(false);
            return;
        }

        try {
            await signup({
                email: data.email,
                password: data.password,
                full_name: `${data.firstName} ${data.lastName}`,
                target_role: 'Backend' // Default for now
            });
            // Auto login after signup
            await login(data.email, data.password);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create account');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
            <Card className="w-full max-w-md p-8" glass>
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-display font-bold mb-2">Create an account</h1>
                    <p className="text-text-secondary text-sm">
                        Start your journey to becoming interview-ready
                    </p>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-lg text-center">
                        {error}
                    </div>
                )}

                <form className="space-y-4" onSubmit={handleSubmit}>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium" htmlFor="firstName">
                                First name
                            </label>
                            <Input id="firstName" name="firstName" placeholder="John" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium" htmlFor="lastName">
                                Last name
                            </label>
                            <Input id="lastName" name="lastName" placeholder="Doe" required />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium" htmlFor="email">
                            Email
                        </label>
                        <Input id="email" name="email" type="email" placeholder="name@example.com" required />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium" htmlFor="password">
                            Password
                        </label>
                        <Input id="password" name="password" type="password" placeholder="••••••••" required />
                    </div>

                    <Button className="w-full mt-6" size="lg" disabled={loading}>
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </Button>
                </form>

                <div className="mt-6 text-center text-sm text-text-secondary">
                    Already have an account?{' '}
                    <Link to="/login" className="text-primary hover:text-primary-hover font-medium">
                        Sign in
                    </Link>
                </div>
            </Card>
        </div>
    );
};

export default Signup;
