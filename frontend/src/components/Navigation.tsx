import React from 'react'
import { Navbar, Nav, Container } from 'react-bootstrap'
import { Link, useLocation } from 'react-router-dom'

const Navigation: React.FC = () => {
  const location = useLocation()

  return (
    <Navbar bg="light" expand="lg" className="shadow-sm">
      <Container>
        <Navbar.Brand as={Link} to="/">
          软件工程课看板系统
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link 
              as={Link} 
              to="/" 
              active={location.pathname === '/'}
            >
              仪表板
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/projects" 
              active={location.pathname === '/projects'}
            >
              项目管理
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/students" 
              active={location.pathname === '/students'}
            >
              学生管理
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/project-status" 
              active={location.pathname === '/project-status'}
            >
              项目状态
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/analytics" 
              active={location.pathname === '/analytics'}
            >
              技术分析
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/test-analysis" 
              active={location.pathname === '/test-analysis'}
            >
              测试分析
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/git-workflow" 
              active={location.pathname === '/git-workflow'}
            >
              Git工作流程
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}

export default Navigation 