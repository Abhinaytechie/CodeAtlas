import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import DashboardLayout from './layouts/DashboardLayout';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import DashboardOverview from './pages/dashboard/Overview';
import Roadmap from './pages/dashboard/Roadmap';
import RoadmapList from './pages/dashboard/RoadmapList';
import ProblemSolver from './pages/dashboard/ProblemSolver';
import Analytics from './pages/dashboard/Analytics';
import MockInterview from './pages/dashboard/MockInterview';
import ProjectAnalyzer from './pages/dashboard/ProjectAnalyzer';
import Settings from './pages/Settings';
import Profile from './pages/dashboard/Profile';
import Vault from './pages/dashboard/Vault';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Route>

          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardOverview />} />
            <Route path="roadmap" element={<Roadmap />} />
            <Route path="roadmaps" element={<RoadmapList />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="vault" element={<Vault />} />
            <Route path="project-intelligence" element={<ProjectAnalyzer />} />
            <Route path="interview" element={<MockInterview />} />
            <Route path="settings" element={<Settings />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
