import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, Table, ProgressBar, Alert, Spinner } from 'react-bootstrap';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface LanguageStats {
  total_files: number;
  project_count: number;
  projects: string[];
}

interface FrameworkStats {
  usage_count: number;
  project_count: number;
  projects: string[];
}

interface AIStats {
  models: { [key: string]: { project_count: number; projects: string[] } };
  libraries: { [key: string]: { project_count: number; projects: string[] } };
  runtimes: { [key: string]: { project_count: number; projects: string[] } };
  projects_with_ai: number;
  ai_projects: string[];
}

interface TechStackSummary {
  total_projects: number;
  language_summary: { [key: string]: number };
  framework_summary: { [key: string]: number };
  ai_summary: {
    projects_with_ai: number;
    ai_models: { [key: string]: number };
    ai_libraries: { [key: string]: number };
  };
  project_details: {
    [key: string]: {
      primary_language: string;
      language_count: number;
      framework_count: number;
      main_frameworks: string[];
      has_ai: boolean;
      ai_models: string[];
      ai_libraries: string[];
    };
  };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B', '#4ECDC4', '#45B7D1'];

const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<TechStackSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'languages' | 'frameworks' | 'ai'>('languages');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/analytics/tech-stack-summary');
      if (!response.ok) {
        throw new Error('获取数据失败');
      }
      
      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  const prepareLanguageChartData = () => {
    if (!summary) return [];
    
    return Object.entries(summary.language_summary)
      .map(([language, count]) => ({
        name: language,
        value: count,
        percentage: ((count / summary.total_projects) * 100).toFixed(1)
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
  };

  const prepareFrameworkChartData = () => {
    if (!summary) return [];
    
    return Object.entries(summary.framework_summary)
      .map(([framework, count]) => ({
        name: framework,
        value: count,
        percentage: ((count / summary.total_projects) * 100).toFixed(1)
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
  };

  const prepareAIChartData = () => {
    if (!summary) return [];
    
    const aiData = [
      ...Object.entries(summary.ai_summary.ai_models).map(([model, count]) => ({
        name: model,
        value: count,
        type: 'AI模型'
      })),
      ...Object.entries(summary.ai_summary.ai_libraries).map(([library, count]) => ({
        name: library,
        value: count,
        type: 'AI库'
      }))
    ];
    
    return aiData.sort((a, b) => b.value - a.value).slice(0, 10);
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">加载中...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>加载失败</Alert.Heading>
        <p>{error}</p>
        <button className="btn btn-outline-danger" onClick={fetchAnalyticsData}>
          重试
        </button>
      </Alert>
    );
  }

  if (!summary) {
    return <Alert variant="warning">暂无数据</Alert>;
  }

  return (
    <div className="container-fluid">
      <h2 className="mb-4">项目技术栈分析</h2>
      
      {/* 总体统计 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-primary">{summary.total_projects}</h3>
              <Card.Text>总项目数</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-success">{Object.keys(summary.language_summary).length}</h3>
              <Card.Text>使用语言种类</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-info">{Object.keys(summary.framework_summary).length}</h3>
              <Card.Text>使用框架种类</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-warning">{summary.ai_summary.projects_with_ai}</h3>
              <Card.Text>AI项目数量</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* 标签页导航 */}
      <Card className="mb-4">
        <Card.Header>
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'languages' ? 'active' : ''}`}
                onClick={() => setActiveTab('languages')}
              >
                编程语言
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'frameworks' ? 'active' : ''}`}
                onClick={() => setActiveTab('frameworks')}
              >
                框架和库
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'ai' ? 'active' : ''}`}
                onClick={() => setActiveTab('ai')}
              >
                AI技术
              </button>
            </li>
          </ul>
        </Card.Header>
        <Card.Body>
          {activeTab === 'languages' && (
            <div>
              <h4>编程语言分布</h4>
              <Row>
                <Col md={6}>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={prepareLanguageChartData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                                                 label={({ name }) => name}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {prepareLanguageChartData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Col>
                <Col md={6}>
                  <Table striped bordered hover>
                    <thead>
                      <tr>
                        <th>语言</th>
                        <th>项目数</th>
                        <th>占比</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prepareLanguageChartData().map((item, index) => (
                        <tr key={index}>
                          <td>
                            <Badge bg="primary" style={{ backgroundColor: COLORS[index % COLORS.length] }}>
                              {item.name}
                            </Badge>
                          </td>
                          <td>{item.value}</td>
                          <td>
                            <ProgressBar 
                              now={(item.value / summary.total_projects) * 100} 
                              label={`${item.percentage}%`}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Col>
              </Row>
            </div>
          )}

          {activeTab === 'frameworks' && (
            <div>
              <h4>框架和库使用情况</h4>
              <Row>
                <Col md={12}>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={prepareFrameworkChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" fill="#8884d8" name="项目数量" />
                    </BarChart>
                  </ResponsiveContainer>
                </Col>
              </Row>
              <Row className="mt-3">
                <Col md={12}>
                  <Table striped bordered hover>
                    <thead>
                      <tr>
                        <th>框架/库</th>
                        <th>项目数</th>
                        <th>占比</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prepareFrameworkChartData().map((item, index) => (
                        <tr key={index}>
                          <td>
                            <Badge bg="info">{item.name}</Badge>
                          </td>
                          <td>{item.value}</td>
                          <td>
                            <ProgressBar 
                              now={(item.value / summary.total_projects) * 100} 
                              label={`${item.percentage}%`}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Col>
              </Row>
            </div>
          )}

          {activeTab === 'ai' && (
            <div>
              <h4>AI技术使用情况</h4>
              <Row className="mb-4">
                <Col md={6}>
                  <Card>
                    <Card.Body>
                      <h5>AI项目统计</h5>
                      <p>使用AI技术的项目: <strong>{summary.ai_summary.projects_with_ai}</strong></p>
                      <p>AI项目占比: <strong>{((summary.ai_summary.projects_with_ai / summary.total_projects) * 100).toFixed(1)}%</strong></p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={6}>
                  <Card>
                    <Card.Body>
                      <h5>AI技术分布</h5>
                      <p>AI模型种类: <strong>{Object.keys(summary.ai_summary.ai_models).length}</strong></p>
                      <p>AI库种类: <strong>{Object.keys(summary.ai_summary.ai_libraries).length}</strong></p>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
              
              <Row>
                <Col md={6}>
                  <h5>AI模型使用情况</h5>
                  <Table striped bordered hover size="sm">
                    <thead>
                      <tr>
                        <th>模型</th>
                        <th>项目数</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(summary.ai_summary.ai_models)
                        .sort(([,a], [,b]) => b - a)
                        .map(([model, count]) => (
                          <tr key={model}>
                            <td><Badge bg="success">{model}</Badge></td>
                            <td>{count}</td>
                          </tr>
                        ))}
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <h5>AI库使用情况</h5>
                  <Table striped bordered hover size="sm">
                    <thead>
                      <tr>
                        <th>库</th>
                        <th>项目数</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(summary.ai_summary.ai_libraries)
                        .sort(([,a], [,b]) => b - a)
                        .map(([library, count]) => (
                          <tr key={library}>
                            <td><Badge bg="warning">{library}</Badge></td>
                            <td>{count}</td>
                          </tr>
                        ))}
                    </tbody>
                  </Table>
                </Col>
              </Row>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* 项目详情表格 */}
      <Card>
        <Card.Header>
          <h4>项目技术栈详情</h4>
        </Card.Header>
        <Card.Body>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>项目</th>
                <th>主要语言</th>
                <th>语言数量</th>
                <th>框架数量</th>
                <th>主要框架</th>
                <th>AI技术</th>
              </tr>
            </thead>
            <tbody>
              {summary.project_details && Object.entries(summary.project_details)
                .sort(([,a], [,b]) => b.framework_count - a.framework_count)
                .map(([project, details]) => (
                  <tr key={project}>
                    <td>{project}</td>
                    <td>
                      <Badge bg="primary">{details.primary_language}</Badge>
                    </td>
                    <td>{details.language_count}</td>
                    <td>{details.framework_count}</td>
                    <td>
                      {details.main_frameworks && details.main_frameworks.length > 0 ? (
                        details.main_frameworks.map((framework, index) => (
                          <Badge key={index} bg="info" className="me-1">
                            {framework}
                          </Badge>
                        ))
                      ) : (
                        <Badge bg="secondary">无</Badge>
                      )}
                    </td>
                    <td>
                      {details.has_ai ? (
                        <div>
                          {details.ai_models && details.ai_models.length > 0 && (
                            details.ai_models.map((model, index) => (
                              <Badge key={index} bg="success" className="me-1">
                                {model}
                              </Badge>
                            ))
                          )}
                          {details.ai_libraries && details.ai_libraries.length > 0 && (
                            details.ai_libraries.map((library, index) => (
                              <Badge key={index} bg="warning" className="me-1">
                                {library}
                              </Badge>
                            ))
                          )}
                        </div>
                      ) : (
                        <Badge bg="secondary">无</Badge>
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </div>
  );
};

export default Analytics; 