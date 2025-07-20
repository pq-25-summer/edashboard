import React, { useState, useEffect } from 'react'
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Table, 
  Badge, 
  Button, 
  ProgressBar,
  Alert,
  Spinner,
  Modal,
  Form
} from 'react-bootstrap'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'

interface TestAnalysisData {
  project_name: string
  has_unit_tests: boolean
  has_test_plan: boolean
  has_test_documentation: boolean
  uses_tdd: boolean
  test_coverage: number
  test_files: string[]
  test_directories: string[]
  test_frameworks: string[]
  test_metrics: {
    total_test_files: number
    total_test_functions: number
    test_file_types: Record<string, number>
    test_documentation_files: string[]
  }
  analysis_time: string
}

interface TestSummary {
  summary: {
    total_projects: number
    projects_with_unit_tests: number
    projects_with_test_plan: number
    projects_with_test_docs: number
    projects_using_tdd: number
    avg_test_coverage: number
  }
  framework_distribution: Array<{
    framework: string
    project_count: number
  }>
  coverage_distribution: Array<{
    coverage_level: string
    project_count: number
  }>
}

const TestAnalysis: React.FC = () => {
  const [projects, setProjects] = useState<TestAnalysisData[]>([])
  const [summary, setSummary] = useState<TestSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<TestAnalysisData | null>(null)
  const [showModal, setShowModal] = useState(false)

  const API_BASE = 'http://localhost:8000/api'

  useEffect(() => {
    loadTestAnalysis()
  }, [])

  const loadTestAnalysis = async () => {
    try {
      setLoading(true)
      setError(null)

      // 加载项目列表
      const projectsResponse = await fetch(`${API_BASE}/test-analysis/projects`)
      if (!projectsResponse.ok) {
        throw new Error('Failed to load projects')
      }
      const projectsData = await projectsResponse.json()
      setProjects(projectsData)

      // 加载摘要
      const summaryResponse = await fetch(`${API_BASE}/test-analysis/summary`)
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json()
        setSummary(summaryData)
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const analyzeAllProjects = async () => {
    try {
      setAnalyzing(true)
      setError(null)

      const response = await fetch(`${API_BASE}/test-analysis/analyze-all`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('分析失败')
      }

      const result = await response.json()
      alert(result.message)
      
      // 重新加载数据
      await loadTestAnalysis()

    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败')
    } finally {
      setAnalyzing(false)
    }
  }

  const refreshProject = async (projectName: string) => {
    try {
      const response = await fetch(`${API_BASE}/test-analysis/refresh/${encodeURIComponent(projectName)}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('刷新失败')
      }

      const result = await response.json()
      alert(result.message)
      
      // 重新加载数据
      await loadTestAnalysis()

    } catch (err) {
      setError(err instanceof Error ? err.message : '刷新失败')
    }
  }

  const getStatusBadge = (status: boolean) => {
    return status ? (
      <Badge bg="success">是</Badge>
    ) : (
      <Badge bg="secondary">否</Badge>
    )
  }

  const getCoverageColor = (coverage: number) => {
    if (coverage >= 75) return 'success'
    if (coverage >= 50) return 'warning'
    if (coverage >= 25) return 'info'
    return 'danger'
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">加载中...</span>
        </Spinner>
        <p className="mt-3">正在加载测试分析数据...</p>
      </Container>
    )
  }

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2>项目测试情况分析</h2>
          <p className="text-muted">分析各项目的测试实践情况，包括单元测试、测试方案、文档和TDD实践</p>
        </Col>
        <Col xs="auto">
          <Button 
            variant="primary" 
            onClick={analyzeAllProjects}
            disabled={analyzing}
          >
            {analyzing ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                分析中...
              </>
            ) : (
              '重新分析所有项目'
            )}
          </Button>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 摘要统计 */}
      {summary && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <Card.Title>{summary.summary.total_projects}</Card.Title>
                <Card.Text>总项目数</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <Card.Title>{summary.summary.projects_with_unit_tests}</Card.Title>
                <Card.Text>有单元测试</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <Card.Title>{summary.summary.projects_with_test_plan}</Card.Title>
                <Card.Text>有测试方案</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <Card.Title>{summary.summary.projects_using_tdd}</Card.Title>
                <Card.Text>使用TDD</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* 图表 */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>测试框架使用情况</Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={summary?.framework_distribution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="framework" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="project_count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>测试覆盖率分布</Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={summary?.coverage_distribution || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="project_count"
                  >
                    {summary?.coverage_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* 项目列表 */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">项目测试详情</h5>
        </Card.Header>
        <Card.Body>
          <Table responsive striped hover>
            <thead>
              <tr>
                <th>项目名称</th>
                <th>单元测试</th>
                <th>测试方案</th>
                <th>测试文档</th>
                <th>TDD实践</th>
                <th>测试覆盖率</th>
                <th>测试框架</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.project_name}>
                  <td>
                    <Button
                      variant="link"
                      className="p-0"
                      onClick={() => {
                        setSelectedProject(project)
                        setShowModal(true)
                      }}
                    >
                      {project.project_name}
                    </Button>
                  </td>
                  <td>{getStatusBadge(project.has_unit_tests)}</td>
                  <td>{getStatusBadge(project.has_test_plan)}</td>
                  <td>{getStatusBadge(project.has_test_documentation)}</td>
                  <td>{getStatusBadge(project.uses_tdd)}</td>
                  <td>
                    <ProgressBar
                      now={project.test_coverage}
                      variant={getCoverageColor(project.test_coverage)}
                      label={`${project.test_coverage}%`}
                    />
                  </td>
                  <td>
                    {project.test_frameworks.map((framework) => (
                      <Badge key={framework} bg="info" className="me-1">
                        {framework}
                      </Badge>
                    ))}
                  </td>
                  <td>
                    <Button
                      size="sm"
                      variant="outline-primary"
                      onClick={() => refreshProject(project.project_name)}
                    >
                      刷新
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {/* 项目详情模态框 */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>项目测试详情 - {selectedProject?.project_name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedProject && (
            <div>
              <Row>
                <Col md={6}>
                  <h6>基本信息</h6>
                  <p><strong>单元测试:</strong> {getStatusBadge(selectedProject.has_unit_tests)}</p>
                  <p><strong>测试方案:</strong> {getStatusBadge(selectedProject.has_test_plan)}</p>
                  <p><strong>测试文档:</strong> {getStatusBadge(selectedProject.has_test_documentation)}</p>
                  <p><strong>TDD实践:</strong> {getStatusBadge(selectedProject.uses_tdd)}</p>
                  <p><strong>测试覆盖率:</strong> {selectedProject.test_coverage}%</p>
                </Col>
                <Col md={6}>
                  <h6>测试框架</h6>
                  {selectedProject.test_frameworks.length > 0 ? (
                    selectedProject.test_frameworks.map((framework) => (
                      <Badge key={framework} bg="info" className="me-1">
                        {framework}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-muted">未检测到测试框架</p>
                  )}
                </Col>
              </Row>
              
              <hr />
              
              <h6>测试文件 ({selectedProject.test_files.length})</h6>
              {selectedProject.test_files.length > 0 ? (
                <ul>
                  {selectedProject.test_files.slice(0, 10).map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                  {selectedProject.test_files.length > 10 && (
                    <li>... 还有 {selectedProject.test_files.length - 10} 个文件</li>
                  )}
                </ul>
              ) : (
                <p className="text-muted">未找到测试文件</p>
              )}
              
              <h6>测试目录 ({selectedProject.test_directories.length})</h6>
              {selectedProject.test_directories.length > 0 ? (
                <ul>
                  {selectedProject.test_directories.map((dir) => (
                    <li key={dir}>{dir}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted">未找到测试目录</p>
              )}
              
              <h6>测试指标</h6>
              <p><strong>测试文件总数:</strong> {selectedProject.test_metrics.total_test_files}</p>
              <p><strong>测试函数总数:</strong> {selectedProject.test_metrics.total_test_functions}</p>
              
              <h6>分析时间</h6>
              <p>{new Date(selectedProject.analysis_time).toLocaleString()}</p>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            关闭
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default TestAnalysis 