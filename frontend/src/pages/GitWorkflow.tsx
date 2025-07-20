import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, ProgressBar, Alert, Button, Spinner } from 'react-bootstrap';
import ReactECharts from 'echarts-for-react';

interface GitWorkflowStats {
  project_name: string;
  github_url: string;
  total_branches: number;
  main_branch_name: string;
  feature_branches: number;
  hotfix_branches: number;
  total_commits: number;
  commits_on_main: number;
  commits_on_branches: number;
  merge_commits: number;
  rebase_commits: number;
  has_pull_requests: boolean;
  pull_request_count: number;
  merged_pull_requests: number;
  uses_feature_branches: boolean;
  uses_main_branch_merges: boolean;
  uses_rebase: boolean;
  uses_pull_requests: boolean;
  workflow_score: number;
  workflow_style: string;
  analyzed_at: string;
}

interface WorkflowSummary {
  total_projects: number;
  workflow_statistics: {
    workflow_styles: Record<string, number>;
    feature_branch_usage: { count: number; percentage: number };
    merge_usage: { count: number; percentage: number };
    rebase_usage: { count: number; percentage: number };
    pull_request_usage: { count: number; percentage: number };
    average_score: number;
  };
  analysis_time: string;
}

const GitWorkflow: React.FC = () => {
  const [summary, setSummary] = useState<WorkflowSummary | null>(null);
  const [projects, setProjects] = useState<GitWorkflowStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 获取摘要数据
      const summaryResponse = await fetch('http://localhost:8000/api/git-workflow/summary');
      if (!summaryResponse.ok) {
        throw new Error('获取摘要数据失败');
      }
      const summaryData = await summaryResponse.json();
      setSummary(summaryData);

      // 获取项目详情数据
      const projectsResponse = await fetch('http://localhost:8000/api/git-workflow/projects');
      if (!projectsResponse.ok) {
        throw new Error('获取项目数据失败');
      }
      const projectsData = await projectsResponse.json();
      setProjects(projectsData.projects);

    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      const response = await fetch('http://localhost:8000/api/git-workflow/analyze', {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('分析失败');
      }
      
      // 重新获取数据
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败');
    } finally {
      setAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'info';
    if (score >= 40) return 'warning';
    return 'danger';
  };

  const getWorkflowStyleColor = (style: string) => {
    if (style.includes('Git Flow')) return 'primary';
    if (style.includes('Feature Branch')) return 'info';
    if (style.includes('Trunk Based')) return 'warning';
    return 'secondary';
  };

  // 工作流程风格饼图配置
  const getWorkflowStyleChartOption = () => {
    if (!summary) return {};

    const data = Object.entries(summary.workflow_statistics.workflow_styles).map(([style, count]) => ({
      name: style,
      value: count
    }));

    return {
      title: {
        text: '工作流程风格分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '工作流程风格',
          type: 'pie',
          radius: '50%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
  };

  // 功能使用情况柱状图配置
  const getFeatureUsageChartOption = () => {
    if (!summary) return {};

    const features = [
      '功能分支',
      '分支合并',
      'Rebase操作',
      'Pull Request'
    ];

    const percentages = [
      summary.workflow_statistics.feature_branch_usage.percentage,
      summary.workflow_statistics.merge_usage.percentage,
      summary.workflow_statistics.rebase_usage.percentage,
      summary.workflow_statistics.pull_request_usage.percentage
    ];

    return {
      title: {
        text: 'Git功能使用情况',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: features,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '使用率 (%)',
        max: 100
      },
      series: [
        {
          name: '使用率',
          type: 'bar',
          data: percentages,
          itemStyle: {
            color: function(params: any) {
              const colors = ['#91cc75', '#fac858', '#ee6666', '#73c0de'];
              return colors[params.dataIndex];
            }
          }
        }
      ]
    };
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">加载中...</span>
          </Spinner>
          <p className="mt-2">正在加载Git工作流程分析数据...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          <Alert.Heading>错误</Alert.Heading>
          <p>{error}</p>
          <Button onClick={fetchData} variant="outline-danger">
            重试
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <h2>Git工作流程分析</h2>
          <p className="text-muted">
            分析各项目的Git使用风格，包括分支使用、合并模式、Pull Request等
          </p>
        </Col>
        <Col xs="auto">
          <Button 
            onClick={handleAnalyze} 
            disabled={analyzing}
            variant="primary"
          >
            {analyzing ? (
              <>
                <Spinner as="span" animation="border" size="sm" className="me-2" />
                分析中...
              </>
            ) : (
              '重新分析'
            )}
          </Button>
        </Col>
      </Row>

      {summary && (
        <>
          {/* 总体统计卡片 */}
          <Row className="mb-4">
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3>{summary.total_projects}</h3>
                  <p className="text-muted mb-0">总项目数</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3>{summary.workflow_statistics.average_score}</h3>
                  <p className="text-muted mb-0">平均评分</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3>{summary.workflow_statistics.feature_branch_usage.count}</h3>
                  <p className="text-muted mb-0">使用功能分支</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3>{summary.workflow_statistics.pull_request_usage.count}</h3>
                  <p className="text-muted mb-0">使用Pull Request</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* 功能使用情况 */}
          <Row className="mb-4">
            <Col md={6}>
              <Card>
                <Card.Body>
                  <h5>功能分支使用情况</h5>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>使用功能分支的项目</span>
                    <span>{summary.workflow_statistics.feature_branch_usage.percentage}%</span>
                  </div>
                  <ProgressBar 
                    now={summary.workflow_statistics.feature_branch_usage.percentage} 
                    variant="success"
                  />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Body>
                  <h5>分支合并使用情况</h5>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>使用分支合并的项目</span>
                    <span>{summary.workflow_statistics.merge_usage.percentage}%</span>
                  </div>
                  <ProgressBar 
                    now={summary.workflow_statistics.merge_usage.percentage} 
                    variant="info"
                  />
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mb-4">
            <Col md={6}>
              <Card>
                <Card.Body>
                  <h5>Rebase操作使用情况</h5>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>使用Rebase的项目</span>
                    <span>{summary.workflow_statistics.rebase_usage.percentage}%</span>
                  </div>
                  <ProgressBar 
                    now={summary.workflow_statistics.rebase_usage.percentage} 
                    variant="warning"
                  />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Body>
                  <h5>Pull Request使用情况</h5>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>使用Pull Request的项目</span>
                    <span>{summary.workflow_statistics.pull_request_usage.percentage}%</span>
                  </div>
                  <ProgressBar 
                    now={summary.workflow_statistics.pull_request_usage.percentage} 
                    variant="primary"
                  />
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* 图表 */}
          <Row className="mb-4">
            <Col md={6}>
              <Card>
                <Card.Body>
                  <ReactECharts option={getWorkflowStyleChartOption()} style={{ height: '300px' }} />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Body>
                  <ReactECharts option={getFeatureUsageChartOption()} style={{ height: '300px' }} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* 项目详情表格 */}
      <Card>
        <Card.Header>
          <h5>项目Git工作流程详情</h5>
        </Card.Header>
        <Card.Body>
          <Table responsive striped hover>
            <thead>
              <tr>
                <th>项目名称</th>
                <th>工作流程风格</th>
                <th>评分</th>
                <th>分支数</th>
                <th>提交数</th>
                <th>功能分支</th>
                <th>合并提交</th>
                <th>Rebase</th>
                <th>Pull Request</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.project_name}>
                  <td>
                    <a href={project.github_url} target="_blank" rel="noopener noreferrer">
                      {project.project_name}
                    </a>
                  </td>
                  <td>
                    <Badge bg={getWorkflowStyleColor(project.workflow_style)}>
                      {project.workflow_style}
                    </Badge>
                  </td>
                  <td>
                    <Badge bg={getScoreColor(project.workflow_score)}>
                      {project.workflow_score}
                    </Badge>
                  </td>
                  <td>{project.total_branches}</td>
                  <td>{project.total_commits}</td>
                  <td>
                    {project.uses_feature_branches ? (
                      <Badge bg="success">是</Badge>
                    ) : (
                      <Badge bg="secondary">否</Badge>
                    )}
                  </td>
                  <td>
                    {project.uses_main_branch_merges ? (
                      <Badge bg="info">是</Badge>
                    ) : (
                      <Badge bg="secondary">否</Badge>
                    )}
                  </td>
                  <td>
                    {project.uses_rebase ? (
                      <Badge bg="warning">是</Badge>
                    ) : (
                      <Badge bg="secondary">否</Badge>
                    )}
                  </td>
                  <td>
                    {project.uses_pull_requests ? (
                      <Badge bg="primary">是</Badge>
                    ) : (
                      <Badge bg="secondary">否</Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {summary && (
        <div className="mt-3 text-muted text-center">
          <small>最后分析时间: {new Date(summary.analysis_time).toLocaleString()}</small>
        </div>
      )}
    </Container>
  );
};

export default GitWorkflow; 