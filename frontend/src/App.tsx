import { Routes, Route } from 'react-router-dom'
import { Container } from 'react-bootstrap'
import Navigation from './components/Navigation'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Students from './pages/Students'
import ProjectStatus from './pages/ProjectStatus'
import Analytics from './pages/Analytics'
import './App.css'

function App() {
  return (
    <div className="App">
      <Navigation />
      <Container fluid className="mt-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/students" element={<Students />} />
          <Route path="/project-status" element={<ProjectStatus />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Container>
    </div>
  )
}

export default App 