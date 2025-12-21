import { createContext, useContext, useState, useEffect } from 'react';
import api from '../lib/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token exists on load
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const { data } = await api.get('/users/me');
                    setUser({ token, ...data });
                } catch (error) {
                    console.error("Failed to fetch user profile", error);
                    // Optionally logout if token is invalid
                    if (error.response && error.response.status === 401) {
                        localStorage.removeItem('token');
                        setUser(null);
                    }
                }
            }
            setLoading(false);
        };
        initAuth();
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

        // Fetch user profile immediately
        try {
            const userResponse = await api.get('/users/me');
            setUser({ token: access_token, ...userResponse.data });
        } catch (e) {
            console.error("Login successful but failed to fetch profile", e);
            setUser({ token: access_token });
        }

        return response.data;
    };

    const signup = async (userData) => {
        const response = await api.post('/auth/signup', userData);
        // Auto-login after signup if desired, or just return
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
