import { createContext, useContext, useState, useEffect } from 'react';
import api from '../lib/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token exists on load
        const token = localStorage.getItem('token');
        if (token) {
            // Technically we should validate the token here via an API call /me
            // For now, we'll just assume they are logged in or decode the JWT if needed
            setUser({ token });
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const formData = new FormData();
        formData.append('username', email); // FastAPI OAuth2 expects 'username'
        formData.append('password', password);

        const response = await api.post('/auth/login/access-token', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        setUser({ token: access_token });
        return response.data;
    };

    const signup = async (userData) => {
        const response = await api.post('/auth/signup', userData);
        return response.data;
    };

    const logout = async () => {
        try {
            // Auto-cleanup non-bookmarked roadmaps on signout
            await api.delete('/roadmap/cleanup');
        } catch (e) {
            console.warn("Cleanup failed", e);
        } finally {
            localStorage.removeItem('token');
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
