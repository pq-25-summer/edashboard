import React, { useState, useEffect } from 'react'
import { Table, Button, Modal, Form } from 'react-bootstrap'
import axios from 'axios'

interface Student {
  id: number
  name: string
  github_username: string
  email: string
  project_id: number
  created_at: string
  updated_at: string
}

interface Project {
  id: number
  name: string
}

const Students: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingStudent, setEditingStudent] = useState<Student | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    github_username: '',
    email: '',
    project_id: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [studentsResponse, projectsResponse] = await Promise.all([
        axios.get('/api/students'),
        axios.get('/api/projects')
      ])
      setStudents(studentsResponse.data)
      setProjects(projectsResponse.data)
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const submitData = {
        ...formData,
        project_id: formData.project_id ? parseInt(formData.project_id) : null
      }
      
      if (editingStudent) {
        await axios.put(`/api/students/${editingStudent.id}`, submitData)
      } else {
        await axios.post('/api/students', submitData)
      }
      setShowModal(false)
      setEditingStudent(null)
      setFormData({ name: '', github_username: '', email: '', project_id: '' })
      fetchData()
    } catch (error) {
      console.error('保存学生失败:', error)
    }
  }

  const handleEdit = (student: Student) => {
    setEditingStudent(student)
    setFormData({
      name: student.name,
      github_username: student.github_username || '',
      email: student.email || '',
      project_id: student.project_id ? student.project_id.toString() : ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('确定要删除这个学生吗？')) {
      try {
        await axios.delete(`/api/students/${id}`)
        fetchData()
      } catch (error) {
        console.error('删除学生失败:', error)
      }
    }
  }

  const getProjectName = (projectId: number) => {
    const project = projects.find(p => p.id === projectId)
    return project ? project.name : '未知项目'
  }

  if (loading) {
    return <div>加载中...</div>
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>学生管理</h2>
        <Button 
          variant="primary" 
          onClick={() => {
            setEditingStudent(null)
            setFormData({ name: '', github_username: '', email: '', project_id: '' })
            setShowModal(true)
          }}
        >
          添加学生
        </Button>
      </div>

      <div className="table-responsive">
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>姓名</th>
              <th>GitHub用户名</th>
              <th>邮箱</th>
              <th>所属项目</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>{student.id}</td>
                <td>{student.name}</td>
                <td>
                  {student.github_username && (
                    <a 
                      href={`https://github.com/${student.github_username}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {student.github_username}
                    </a>
                  )}
                </td>
                <td>{student.email}</td>
                <td>{getProjectName(student.project_id)}</td>
                <td>{new Date(student.created_at).toLocaleDateString()}</td>
                <td>
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="me-2"
                    onClick={() => handleEdit(student)}
                  >
                    编辑
                  </Button>
                  <Button 
                    variant="outline-danger" 
                    size="sm"
                    onClick={() => handleDelete(student.id)}
                  >
                    删除
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      {/* 添加/编辑学生模态框 */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingStudent ? '编辑学生' : '添加学生'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>姓名</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>GitHub用户名</Form.Label>
              <Form.Control
                type="text"
                value={formData.github_username}
                onChange={(e) => setFormData({ ...formData, github_username: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>邮箱</Form.Label>
              <Form.Control
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>所属项目</Form.Label>
              <Form.Select
                value={formData.project_id}
                onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
              >
                <option value="">选择项目</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              取消
            </Button>
            <Button variant="primary" type="submit">
              {editingStudent ? '更新' : '创建'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  )
}

export default Students 