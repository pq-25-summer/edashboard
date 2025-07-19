import React, { useState, useEffect } from 'react'
import { Table, Button, Modal, Form } from 'react-bootstrap'
import axios from 'axios'

interface Project {
  id: number
  name: string
  github_url: string
  description: string
  created_at: string
  updated_at: string
}

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    github_url: '',
    description: ''
  })

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects')
      setProjects(response.data)
    } catch (error) {
      console.error('获取项目列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingProject) {
        await axios.put(`/api/projects/${editingProject.id}`, formData)
      } else {
        await axios.post('/api/projects', formData)
      }
      setShowModal(false)
      setEditingProject(null)
      setFormData({ name: '', github_url: '', description: '' })
      fetchProjects()
    } catch (error) {
      console.error('保存项目失败:', error)
    }
  }

  const handleEdit = (project: Project) => {
    setEditingProject(project)
    setFormData({
      name: project.name,
      github_url: project.github_url,
      description: project.description || ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('确定要删除这个项目吗？')) {
      try {
        await axios.delete(`/api/projects/${id}`)
        fetchProjects()
      } catch (error) {
        console.error('删除项目失败:', error)
      }
    }
  }

  if (loading) {
    return <div>加载中...</div>
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>项目管理</h2>
        <Button 
          variant="primary" 
          onClick={() => {
            setEditingProject(null)
            setFormData({ name: '', github_url: '', description: '' })
            setShowModal(true)
          }}
        >
          添加项目
        </Button>
      </div>

      <div className="table-responsive">
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>项目名称</th>
              <th>GitHub地址</th>
              <th>描述</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id}>
                <td>{project.id}</td>
                <td>{project.name}</td>
                <td>
                  <a href={project.github_url} target="_blank" rel="noopener noreferrer">
                    {project.github_url}
                  </a>
                </td>
                <td>{project.description}</td>
                <td>{new Date(project.created_at).toLocaleDateString()}</td>
                <td>
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="me-2"
                    onClick={() => handleEdit(project)}
                  >
                    编辑
                  </Button>
                  <Button 
                    variant="outline-danger" 
                    size="sm"
                    onClick={() => handleDelete(project.id)}
                  >
                    删除
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      {/* 添加/编辑项目模态框 */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingProject ? '编辑项目' : '添加项目'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>项目名称</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>GitHub地址</Form.Label>
              <Form.Control
                type="url"
                value={formData.github_url}
                onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>描述</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              取消
            </Button>
            <Button variant="primary" type="submit">
              {editingProject ? '更新' : '创建'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  )
}

export default Projects 